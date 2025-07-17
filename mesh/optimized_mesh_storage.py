#!/usr/bin/env python3
"""
Optimized Mesh Network Data Storage
Implements NoSQL patterns, caching, and distributed storage for mesh node data
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid

try:
    import pymongo
    from pymongo import MongoClient
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    print("Installing MongoDB dependencies...")
    import subprocess
    subprocess.check_call(["pip", "install", "pymongo", "motor"])
    import pymongo
    from pymongo import MongoClient
    from motor.motor_asyncio import AsyncIOMotorClient

from .Mesh_Network.Advanced_Node_Discovery import AdvancedMeshNode, GeoLocation, NetworkMetrics, NodeCapabilities
from ..core.database_optimization import CacheManager, CacheConfig
from rich.console import Console


@dataclass
class MeshStorageConfig:
    """Configuration for mesh network storage"""
    # MongoDB settings
    mongo_uri: str = "mongodb://localhost:27017/"
    mongo_database: str = "liberation_mesh"
    
    # Collection names
    nodes_collection: str = "mesh_nodes"
    metrics_collection: str = "node_metrics"
    connections_collection: str = "node_connections"
    topology_collection: str = "network_topology"
    
    # Performance settings
    enable_sharding: bool = True
    batch_size: int = 1000
    index_ttl: int = 86400  # 24 hours for time-based indexes
    
    # Cache settings
    cache_ttl: int = 300  # 5 minutes
    metrics_cache_ttl: int = 60  # 1 minute for metrics


class OptimizedMeshStorage:
    """Optimized storage system for mesh network data"""
    
    def __init__(self, config: MeshStorageConfig, cache_manager: CacheManager):
        self.config = config
        self.cache_manager = cache_manager
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
        # Collections
        self.nodes_collection = None
        self.metrics_collection = None
        self.connections_collection = None
        self.topology_collection = None
        
    async def initialize(self) -> None:
        """Initialize MongoDB connection and collections"""
        try:
            self.console.print("[cyan]🔗 Initializing optimized mesh storage...[/cyan]")
            
            # Initialize MongoDB connection
            self.mongo_client = AsyncIOMotorClient(self.config.mongo_uri)
            self.database = self.mongo_client[self.config.mongo_database]
            
            # Test connection
            await self.mongo_client.admin.command('ping')
            
            # Initialize collections
            await self._initialize_collections()
            
            # Create indexes for performance
            await self._create_indexes()
            
            # Setup sharding if enabled
            if self.config.enable_sharding:
                await self._setup_sharding()
            
            self.console.print("[green]✅ Optimized mesh storage initialized successfully[/green]")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize mesh storage: {e}")
            self.console.print(f"[red]❌ Mesh storage initialization failed: {e}[/red]")
            raise
    
    async def _initialize_collections(self) -> None:
        """Initialize MongoDB collections"""
        self.nodes_collection = self.database[self.config.nodes_collection]
        self.metrics_collection = self.database[self.config.metrics_collection]
        self.connections_collection = self.database[self.config.connections_collection]
        self.topology_collection = self.database[self.config.topology_collection]
    
    async def _create_indexes(self) -> None:
        """Create optimized indexes for mesh data"""
        try:
            # Nodes collection indexes
            await self.nodes_collection.create_index([
                ("node_id", 1),
                ("status", 1),
                ("last_seen", -1)
            ])
            
            await self.nodes_collection.create_index([
                ("location.country", 1),
                ("location.region", 1)
            ])
            
            await self.nodes_collection.create_index([
                ("node_type", 1),
                ("trust_score", -1)
            ])
            
            # Metrics collection indexes with TTL
            await self.metrics_collection.create_index([
                ("node_id", 1),
                ("timestamp", -1)
            ])
            
            await self.metrics_collection.create_index(
                "timestamp",
                expireAfterSeconds=self.config.index_ttl
            )
            
            # Connections collection indexes
            await self.connections_collection.create_index([
                ("source_node", 1),
                ("target_node", 1),
                ("timestamp", -1)
            ])
            
            await self.connections_collection.create_index([
                ("quality_score", -1),
                ("status", 1)
            ])
            
            # Topology collection indexes
            await self.topology_collection.create_index([
                ("snapshot_time", -1),
                ("region", 1)
            ])
            
            self.logger.info("Mesh storage indexes created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create indexes: {e}")
    
    async def _setup_sharding(self) -> None:
        """Setup sharding for large-scale deployments"""
        try:
            # Enable sharding on database
            admin_db = self.mongo_client.admin
            
            # Shard nodes collection by node_id
            await admin_db.command({
                "shardCollection": f"{self.config.mongo_database}.{self.config.nodes_collection}",
                "key": {"node_id": 1}
            })
            
            # Shard metrics collection by node_id and timestamp
            await admin_db.command({
                "shardCollection": f"{self.config.mongo_database}.{self.config.metrics_collection}",
                "key": {"node_id": 1, "timestamp": 1}
            })
            
            self.logger.info("Sharding setup completed")
            
        except Exception as e:
            self.logger.warning(f"Sharding setup failed (may not be configured): {e}")
    
    async def store_node(self, node: AdvancedMeshNode) -> bool:
        """Store or update a mesh node with caching - Trust-by-default: All nodes accepted"""
        try:
            # Prepare node document - Trust-by-default: No verification required
            node_doc = {
                "node_id": node.id,
                "host": node.host,
                "port": node.port,
                "node_type": node.node_type.value,
                "location": asdict(node.location) if node.location else None,
                "metrics": asdict(node.metrics),
                "capabilities": asdict(node.capabilities),
                "connections": node.connections,
                "last_seen": node.last_seen,
                "status": node.status,
                "trust_score": node.trust_score,  # Trust-first principle
                "updated_at": datetime.utcnow(),
                "version": 1
            }
            
            # Update or insert node
            await self.nodes_collection.replace_one(
                {"node_id": node.id},
                node_doc,
                upsert=True
            )
            
            # Cache the node data
            cache_key = f"node_{node.id}"
            await self.cache_manager.set(cache_key, node_doc, ttl=self.config.cache_ttl)
            
            # Store metrics separately for time-series analysis
            await self._store_node_metrics(node)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store node {node.id}: {e}")
            return False
    
    async def _store_node_metrics(self, node: AdvancedMeshNode) -> None:
        """Store node metrics for time-series analysis"""
        try:
            metrics_doc = {
                "node_id": node.id,
                "timestamp": datetime.utcnow(),
                "metrics": asdict(node.metrics),
                "location": asdict(node.location) if node.location else None,
                "quality_score": node.metrics.calculate_quality_score(),
                "trust_score": node.trust_score
            }
            
            await self.metrics_collection.insert_one(metrics_doc)
            
        except Exception as e:
            self.logger.error(f"Failed to store metrics for node {node.id}: {e}")
    
    async def get_node(self, node_id: str) -> Optional[AdvancedMeshNode]:
        """Get a mesh node with caching"""
        try:
            # Try cache first
            cache_key = f"node_{node_id}"
            cached_node = await self.cache_manager.get(cache_key)
            
            if cached_node:
                return self._doc_to_node(cached_node)
            
            # Query from database
            node_doc = await self.nodes_collection.find_one({"node_id": node_id})
            
            if node_doc:
                # Cache the result
                await self.cache_manager.set(cache_key, node_doc, ttl=self.config.cache_ttl)
                return self._doc_to_node(node_doc)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get node {node_id}: {e}")
            return None
    
    async def get_nodes_by_region(self, country: str, region: str = None) -> List[AdvancedMeshNode]:
        """Get nodes by geographical region with caching"""
        try:
            # Create cache key
            cache_key = f"nodes_region_{country}_{region or 'all'}"
            cached_nodes = await self.cache_manager.get(cache_key)
            
            if cached_nodes:
                return [self._doc_to_node(doc) for doc in cached_nodes]
            
            # Build query
            query = {"location.country": country}
            if region:
                query["location.region"] = region
            
            # Query from database
            cursor = self.nodes_collection.find(query).sort("trust_score", -1)
            nodes_docs = await cursor.to_list(length=1000)
            
            # Cache the results
            if nodes_docs:
                await self.cache_manager.set(cache_key, nodes_docs, ttl=self.config.cache_ttl)
            
            return [self._doc_to_node(doc) for doc in nodes_docs]
            
        except Exception as e:
            self.logger.error(f"Failed to get nodes by region {country}/{region}: {e}")
            return []
    
    async def get_active_nodes(self, limit: int = 100) -> List[AdvancedMeshNode]:
        """Get active nodes with caching"""
        try:
            cache_key = f"active_nodes_{limit}"
            cached_nodes = await self.cache_manager.get(cache_key)
            
            if cached_nodes:
                return [self._doc_to_node(doc) for doc in cached_nodes]
            
            # Query active nodes
            five_minutes_ago = time.time() - 300
            query = {
                "status": "active",
                "last_seen": {"$gte": five_minutes_ago}
            }
            
            cursor = self.nodes_collection.find(query).sort("last_seen", -1).limit(limit)
            nodes_docs = await cursor.to_list(length=limit)
            
            # Cache the results
            if nodes_docs:
                await self.cache_manager.set(cache_key, nodes_docs, ttl=60)  # Short TTL for active nodes
            
            return [self._doc_to_node(doc) for doc in nodes_docs]
            
        except Exception as e:
            self.logger.error(f"Failed to get active nodes: {e}")
            return []
    
    async def get_node_metrics_history(self, node_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get node metrics history with caching"""
        try:
            cache_key = f"metrics_history_{node_id}_{hours}h"
            cached_metrics = await self.cache_manager.get(cache_key)
            
            if cached_metrics:
                return cached_metrics
            
            # Query metrics history
            start_time = datetime.utcnow() - timedelta(hours=hours)
            query = {
                "node_id": node_id,
                "timestamp": {"$gte": start_time}
            }
            
            cursor = self.metrics_collection.find(query).sort("timestamp", -1)
            metrics_docs = await cursor.to_list(length=1000)
            
            # Convert to list of dicts
            metrics_list = []
            for doc in metrics_docs:
                doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
                metrics_list.append(doc)
            
            # Cache the results
            if metrics_list:
                await self.cache_manager.set(cache_key, metrics_list, ttl=self.config.metrics_cache_ttl)
            
            return metrics_list
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics history for node {node_id}: {e}")
            return []
    
    async def store_connection(self, source_node: str, target_node: str, connection_info: Dict[str, Any]) -> bool:
        """Store connection information"""
        try:
            connection_doc = {
                "source_node": source_node,
                "target_node": target_node,
                "connection_info": connection_info,
                "timestamp": datetime.utcnow(),
                "quality_score": connection_info.get("quality_score", 0.5),
                "status": connection_info.get("status", "active"),
                "latency": connection_info.get("latency", 0),
                "bandwidth": connection_info.get("bandwidth", 0)
            }
            
            await self.connections_collection.insert_one(connection_doc)
            
            # Invalidate related caches
            await self.cache_manager.clear_pattern(f"connections_{source_node}*")
            await self.cache_manager.clear_pattern(f"topology_*")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store connection {source_node} -> {target_node}: {e}")
            return False
    
    async def get_node_connections(self, node_id: str) -> List[Dict[str, Any]]:
        """Get connections for a specific node with caching"""
        try:
            cache_key = f"connections_{node_id}"
            cached_connections = await self.cache_manager.get(cache_key)
            
            if cached_connections:
                return cached_connections
            
            # Query connections
            query = {"$or": [{"source_node": node_id}, {"target_node": node_id}]}
            cursor = self.connections_collection.find(query).sort("timestamp", -1)
            connections_docs = await cursor.to_list(length=1000)
            
            # Convert to list of dicts
            connections_list = []
            for doc in connections_docs:
                doc["_id"] = str(doc["_id"])
                connections_list.append(doc)
            
            # Cache the results
            if connections_list:
                await self.cache_manager.set(cache_key, connections_list, ttl=self.config.cache_ttl)
            
            return connections_list
            
        except Exception as e:
            self.logger.error(f"Failed to get connections for node {node_id}: {e}")
            return []
    
    async def get_network_topology(self) -> Dict[str, Any]:
        """Get network topology with caching"""
        try:
            cache_key = "network_topology"
            cached_topology = await self.cache_manager.get(cache_key)
            
            if cached_topology:
                return cached_topology
            
            # Aggregate topology data
            pipeline = [
                {
                    "$match": {
                        "status": "active",
                        "last_seen": {"$gte": time.time() - 300}  # Last 5 minutes
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "country": "$location.country",
                            "region": "$location.region"
                        },
                        "node_count": {"$sum": 1},
                        "avg_latency": {"$avg": "$metrics.latency"},
                        "avg_bandwidth": {"$avg": "$metrics.bandwidth"},
                        "avg_trust_score": {"$avg": "$trust_score"},
                        "nodes": {"$push": {
                            "node_id": "$node_id",
                            "host": "$host",
                            "port": "$port",
                            "trust_score": "$trust_score"
                        }}
                    }
                },
                {
                    "$sort": {"node_count": -1}
                }
            ]
            
            cursor = self.nodes_collection.aggregate(pipeline)
            topology_data = await cursor.to_list(length=None)
            
            # Build topology summary
            topology = {
                "total_nodes": len(topology_data),
                "regions": topology_data,
                "timestamp": datetime.utcnow().isoformat(),
                "generated_at": time.time()
            }
            
            # Cache the topology
            await self.cache_manager.set(cache_key, topology, ttl=120)  # 2 minutes TTL
            
            return topology
            
        except Exception as e:
            self.logger.error(f"Failed to get network topology: {e}")
            return {}
    
    async def cleanup_old_data(self, days: int = 7) -> None:
        """Cleanup old data to maintain performance"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Clean up old metrics
            result = await self.metrics_collection.delete_many({
                "timestamp": {"$lt": cutoff_time}
            })
            
            # Clean up old connections
            result = await self.connections_collection.delete_many({
                "timestamp": {"$lt": cutoff_time}
            })
            
            # Remove inactive nodes
            inactive_cutoff = time.time() - (days * 24 * 3600)
            result = await self.nodes_collection.delete_many({
                "last_seen": {"$lt": inactive_cutoff},
                "status": {"$ne": "active"}
            })
            
            self.logger.info(f"Cleaned up old data older than {days} days")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
    
    def _doc_to_node(self, doc: Dict[str, Any]) -> AdvancedMeshNode:
        """Convert MongoDB document to AdvancedMeshNode"""
        try:
            from .Mesh_Network.Advanced_Node_Discovery import NodeType
            
            location = None
            if doc.get("location"):
                location = GeoLocation(**doc["location"])
            
            metrics = NetworkMetrics()
            if doc.get("metrics"):
                metrics = NetworkMetrics(**doc["metrics"])
            
            capabilities = NodeCapabilities()
            if doc.get("capabilities"):
                capabilities = NodeCapabilities(**doc["capabilities"])
            
            return AdvancedMeshNode(
                id=doc["node_id"],
                host=doc["host"],
                port=doc["port"],
                node_type=NodeType(doc.get("node_type", "standard")),
                location=location,
                metrics=metrics,
                capabilities=capabilities,
                connections=doc.get("connections", {}),
                last_seen=doc.get("last_seen", time.time()),
                status=doc.get("status", "active"),
                trust_score=doc.get("trust_score", 1.0)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to convert document to node: {e}")
            raise
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        try:
            stats = {}
            
            # Collection statistics
            stats["nodes_count"] = await self.nodes_collection.count_documents({})
            stats["metrics_count"] = await self.metrics_collection.count_documents({})
            stats["connections_count"] = await self.connections_collection.count_documents({})
            
            # Active nodes statistics
            five_minutes_ago = time.time() - 300
            stats["active_nodes"] = await self.nodes_collection.count_documents({
                "status": "active",
                "last_seen": {"$gte": five_minutes_ago}
            })
            
            # Database statistics
            db_stats = await self.database.command("dbStats")
            stats["database_size"] = db_stats.get("dataSize", 0)
            stats["index_size"] = db_stats.get("indexSize", 0)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get performance stats: {e}")
            return {}
    
    async def close(self) -> None:
        """Close MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
            self.console.print("[yellow]🔒 Mesh storage connection closed[/yellow]")


# Global mesh storage instance
mesh_storage: Optional[OptimizedMeshStorage] = None


async def get_mesh_storage() -> OptimizedMeshStorage:
    """Get or create optimized mesh storage instance"""
    global mesh_storage
    
    if mesh_storage is None:
        from ..core.database_optimization import CacheManager, CacheConfig
        
        storage_config = MeshStorageConfig()
        cache_config = CacheConfig()
        cache_manager = CacheManager(cache_config)
        
        await cache_manager.initialize()
        
        mesh_storage = OptimizedMeshStorage(storage_config, cache_manager)
        await mesh_storage.initialize()
    
    return mesh_storage


async def close_mesh_storage() -> None:
    """Close mesh storage"""
    global mesh_storage
    
    if mesh_storage:
        await mesh_storage.close()
        mesh_storage = None
