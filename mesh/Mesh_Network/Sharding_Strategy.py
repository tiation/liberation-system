#!/usr/bin/env python3
"""
Advanced Sharding Strategy for Liberation System Mesh Network
Implements role-based sharding with RELAY, STORAGE, and COMPUTE nodes
"""

import asyncio
import logging
import time
import json
import hashlib
import uuid
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import random

from Advanced_Node_Discovery import (
    AdvancedMeshNode, 
    NodeType, 
    GeoLocation, 
    NetworkMetrics,
    NodeCapabilities
)

class ShardType(Enum):
    """Types of shards in the network"""
    DATA = "data"
    COMPUTE = "compute"
    RELAY = "relay"
    BOOTSTRAP = "bootstrap"
    HYBRID = "hybrid"

@dataclass
class ShardInfo:
    """Information about a network shard"""
    shard_id: str
    shard_type: ShardType
    hash_range: Tuple[int, int]  # Start and end of hash range
    nodes: List[str] = field(default_factory=list)  # Node IDs in this shard
    primary_node: Optional[str] = None
    replica_nodes: List[str] = field(default_factory=list)
    load_factor: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_rebalanced: datetime = field(default_factory=datetime.now)

@dataclass
class NodeShard:
    """Node's shard assignment and capabilities"""
    node_id: str
    assigned_shards: List[str] = field(default_factory=list)
    primary_shards: List[str] = field(default_factory=list)
    replica_shards: List[str] = field(default_factory=list)
    shard_capacity: int = 5  # Maximum shards per node
    current_load: float = 0.0

class ShardingStrategy:
    """Advanced sharding strategy with role-based distribution"""
    
    def __init__(self, total_shards: int = 256, replication_factor: int = 3):
        self.total_shards = total_shards
        self.replication_factor = replication_factor
        self.shards: Dict[str, ShardInfo] = {}
        self.node_shards: Dict[str, NodeShard] = {}
        self.nodes: Dict[str, AdvancedMeshNode] = {}
        self.hash_ring: List[Tuple[int, str]] = []  # (hash_value, shard_id)
        self.logger = logging.getLogger(__name__)
        
        # Performance metrics
        self.shard_metrics = {
            "total_operations": 0,
            "rebalance_count": 0,
            "last_rebalance": datetime.now(),
            "avg_response_time": 0.0
        }
        
        self._initialize_shards()
    
    def _initialize_shards(self):
        """Initialize the sharding system with empty shards"""
        hash_range_size = (2**32) // self.total_shards
        
        for i in range(self.total_shards):
            start_hash = i * hash_range_size
            end_hash = (i + 1) * hash_range_size - 1 if i < self.total_shards - 1 else 2**32 - 1
            
            shard_id = f"shard_{i:04d}"
            shard = ShardInfo(
                shard_id=shard_id,
                shard_type=ShardType.DATA,  # Default type
                hash_range=(start_hash, end_hash)
            )
            
            self.shards[shard_id] = shard
            self.hash_ring.append((start_hash, shard_id))
        
        # Sort hash ring for efficient lookups
        self.hash_ring.sort(key=lambda x: x[0])
        
        self.logger.info(f"Initialized {self.total_shards} shards")
    
    def calculate_shard_hash(self, data: str) -> int:
        """Calculate hash for data to determine shard placement"""
        return int(hashlib.md5(data.encode()).hexdigest(), 16) % (2**32)
    
    def get_shard_for_data(self, data: str) -> str:
        """Get the shard ID for given data"""
        data_hash = self.calculate_shard_hash(data)
        
        # Binary search in hash ring
        left, right = 0, len(self.hash_ring) - 1
        
        while left <= right:
            mid = (left + right) // 2
            if self.hash_ring[mid][0] <= data_hash:
                if mid == len(self.hash_ring) - 1 or self.hash_ring[mid + 1][0] > data_hash:
                    return self.hash_ring[mid][1]
                left = mid + 1
            else:
                right = mid - 1
        
        # Fallback to first shard
        return self.hash_ring[0][1]
    
    async def add_node_to_shard(self, node: AdvancedMeshNode) -> bool:
        """Add a node to the appropriate shard based on its type and capabilities"""
        try:
            # Initialize node shard assignment
            if node.id not in self.node_shards:
                self.node_shards[node.id] = NodeShard(
                    node_id=node.id,
                    shard_capacity=self._calculate_node_capacity(node)
                )
            
            self.nodes[node.id] = node
            
            # Determine optimal shard assignments based on node type
            assigned_shards = await self._assign_node_to_shards(node)
            
            if assigned_shards:
                self.node_shards[node.id].assigned_shards.extend(assigned_shards)
                self.logger.info(f"Node {node.id} assigned to {len(assigned_shards)} shards")
                
                # Update shard information
                for shard_id in assigned_shards:
                    if shard_id in self.shards:
                        self.shards[shard_id].nodes.append(node.id)
                        self._update_shard_roles(shard_id, node)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to add node {node.id} to shard: {e}")
            return False
    
    def _calculate_node_capacity(self, node: AdvancedMeshNode) -> int:
        """Calculate how many shards a node can handle based on its capabilities"""
        base_capacity = 3
        
        # Adjust based on node type
        if node.node_type == NodeType.STORAGE:
            base_capacity = 8
        elif node.node_type == NodeType.COMPUTE:
            base_capacity = 6
        elif node.node_type == NodeType.RELAY:
            base_capacity = 4
        elif node.node_type == NodeType.GATEWAY:
            base_capacity = 10
        
        # Adjust based on hardware capabilities
        if node.capabilities.processing_power > 2.0:
            base_capacity += 2
        if node.capabilities.storage_capacity > 5000:
            base_capacity += 1
        if node.capabilities.max_connections > 100:
            base_capacity += 1
        
        # Adjust based on network quality
        quality_score = node.metrics.calculate_quality_score()
        if quality_score > 0.8:
            base_capacity += 1
        elif quality_score < 0.5:
            base_capacity = max(1, base_capacity - 1)
        
        return base_capacity
    
    async def _assign_node_to_shards(self, node: AdvancedMeshNode) -> List[str]:
        """Assign node to optimal shards based on type and network conditions"""
        assigned_shards = []
        node_capacity = self._calculate_node_capacity(node)
        
        # Get underloaded shards that match node capabilities
        candidate_shards = self._get_candidate_shards(node)
        
        # Sort by priority (load factor, geographic distribution, etc.)
        candidate_shards.sort(key=lambda s: self._calculate_shard_priority(s, node))
        
        # Assign shards up to node capacity
        for shard_id in candidate_shards:
            if len(assigned_shards) >= node_capacity:
                break
                
            shard = self.shards[shard_id]
            if len(shard.nodes) < self.replication_factor * 2:  # Allow over-replication
                assigned_shards.append(shard_id)
        
        return assigned_shards
    
    def _get_candidate_shards(self, node: AdvancedMeshNode) -> List[str]:
        """Get shards that are candidates for the given node"""
        candidates = []
        
        for shard_id, shard in self.shards.items():
            # Check if shard needs more nodes
            if len(shard.nodes) < self.replication_factor * 2:
                # Check if node type is compatible with shard type
                if self._is_node_compatible_with_shard(node, shard):
                    candidates.append(shard_id)
        
        return candidates
    
    def _is_node_compatible_with_shard(self, node: AdvancedMeshNode, shard: ShardInfo) -> bool:
        """Check if a node is compatible with a shard"""
        # All nodes can handle DATA shards
        if shard.shard_type == ShardType.DATA:
            return True
        
        # COMPUTE shards need COMPUTE or HYBRID nodes
        if shard.shard_type == ShardType.COMPUTE:
            return node.node_type in [NodeType.COMPUTE, NodeType.GATEWAY]
        
        # RELAY shards need RELAY or GATEWAY nodes
        if shard.shard_type == ShardType.RELAY:
            return node.node_type in [NodeType.RELAY, NodeType.GATEWAY]
        
        # BOOTSTRAP shards need high-reliability nodes
        if shard.shard_type == ShardType.BOOTSTRAP:
            return node.node_type in [NodeType.GATEWAY, NodeType.BOOTSTRAP] and \
                   node.metrics.uptime > 99.0
        
        return True
    
    def _calculate_shard_priority(self, shard_id: str, node: AdvancedMeshNode) -> float:
        """Calculate priority score for assigning a node to a shard"""
        shard = self.shards[shard_id]
        priority = 0.0
        
        # Lower load factor = higher priority
        priority += (1.0 - shard.load_factor) * 0.4
        
        # Fewer nodes = higher priority
        node_ratio = len(shard.nodes) / (self.replication_factor * 2)
        priority += (1.0 - node_ratio) * 0.3
        
        # Geographic diversity bonus
        if self._provides_geographic_diversity(shard, node):
            priority += 0.2
        
        # Node type compatibility bonus
        if self._is_optimal_node_type(shard, node):
            priority += 0.1
        
        return priority
    
    def _provides_geographic_diversity(self, shard: ShardInfo, node: AdvancedMeshNode) -> bool:
        """Check if adding this node provides geographic diversity"""
        if not node.location:
            return False
        
        # Check if node is in a different region than existing nodes
        node_region = f"{node.location.country}:{node.location.region}"
        
        for existing_node_id in shard.nodes:
            if existing_node_id in self.nodes:
                existing_node = self.nodes[existing_node_id]
                if existing_node.location:
                    existing_region = f"{existing_node.location.country}:{existing_node.location.region}"
                    if existing_region == node_region:
                        return False
        
        return True
    
    def _is_optimal_node_type(self, shard: ShardInfo, node: AdvancedMeshNode) -> bool:
        """Check if node type is optimal for shard type"""
        optimal_types = {
            ShardType.DATA: [NodeType.STORAGE, NodeType.STANDARD],
            ShardType.COMPUTE: [NodeType.COMPUTE],
            ShardType.RELAY: [NodeType.RELAY],
            ShardType.BOOTSTRAP: [NodeType.BOOTSTRAP, NodeType.GATEWAY]
        }
        
        return node.node_type in optimal_types.get(shard.shard_type, [])
    
    def _update_shard_roles(self, shard_id: str, node: AdvancedMeshNode):
        """Update shard roles based on node capabilities"""
        shard = self.shards[shard_id]
        
        # Assign primary node if none exists
        if not shard.primary_node:
            shard.primary_node = node.id
            self.node_shards[node.id].primary_shards.append(shard_id)
        else:
            # Add as replica
            if node.id not in shard.replica_nodes:
                shard.replica_nodes.append(node.id)
                self.node_shards[node.id].replica_shards.append(shard_id)
    
    async def remove_node_from_shard(self, node_id: str) -> bool:
        """Remove a node from all its shards"""
        try:
            if node_id not in self.node_shards:
                return False
            
            node_shard = self.node_shards[node_id]
            
            # Remove from all assigned shards
            for shard_id in node_shard.assigned_shards:
                if shard_id in self.shards:
                    shard = self.shards[shard_id]
                    
                    # Remove from shard's node list
                    if node_id in shard.nodes:
                        shard.nodes.remove(node_id)
                    
                    # Handle primary node removal
                    if shard.primary_node == node_id:
                        await self._reassign_primary_node(shard_id)
                    
                    # Remove from replica nodes
                    if node_id in shard.replica_nodes:
                        shard.replica_nodes.remove(node_id)
            
            # Clean up node shard assignment
            del self.node_shards[node_id]
            if node_id in self.nodes:
                del self.nodes[node_id]
            
            self.logger.info(f"Node {node_id} removed from all shards")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove node {node_id} from shards: {e}")
            return False
    
    async def _reassign_primary_node(self, shard_id: str):
        """Reassign primary node for a shard"""
        shard = self.shards[shard_id]
        
        if shard.replica_nodes:
            # Choose the best replica as new primary
            best_replica = None
            best_score = -1
            
            for replica_id in shard.replica_nodes:
                if replica_id in self.nodes:
                    node = self.nodes[replica_id]
                    score = node.metrics.calculate_quality_score()
                    
                    if score > best_score:
                        best_score = score
                        best_replica = replica_id
            
            if best_replica:
                # Update primary assignment
                shard.primary_node = best_replica
                shard.replica_nodes.remove(best_replica)
                
                # Update node shard assignments
                if best_replica in self.node_shards:
                    self.node_shards[best_replica].primary_shards.append(shard_id)
                    if shard_id in self.node_shards[best_replica].replica_shards:
                        self.node_shards[best_replica].replica_shards.remove(shard_id)
        else:
            shard.primary_node = None
    
    async def rebalance_shards(self) -> bool:
        """Rebalance shards across the network"""
        try:
            self.logger.info("Starting shard rebalancing...")
            
            # Calculate current load distribution
            load_distribution = self._calculate_load_distribution()
            
            # Identify overloaded and underloaded nodes
            overloaded_nodes = []
            underloaded_nodes = []
            
            for node_id, load in load_distribution.items():
                if node_id in self.nodes:
                    node = self.nodes[node_id]
                    capacity = self._calculate_node_capacity(node)
                    
                    if load > capacity * 0.8:  # 80% capacity threshold
                        overloaded_nodes.append((node_id, load))
                    elif load < capacity * 0.4:  # 40% capacity threshold
                        underloaded_nodes.append((node_id, load))
            
            # Move shards from overloaded to underloaded nodes
            moves_made = 0
            for overloaded_node_id, _ in overloaded_nodes:
                if not underloaded_nodes:
                    break
                
                # Find shards to move
                shards_to_move = self._find_movable_shards(overloaded_node_id)
                
                for shard_id in shards_to_move:
                    if not underloaded_nodes:
                        break
                    
                    # Find best target node
                    target_node_id = self._find_best_target_node(shard_id, underloaded_nodes)
                    
                    if target_node_id:
                        await self._move_shard_assignment(shard_id, overloaded_node_id, target_node_id)
                        moves_made += 1
                        
                        # Update load tracking
                        for i, (node_id, load) in enumerate(underloaded_nodes):
                            if node_id == target_node_id:
                                underloaded_nodes[i] = (node_id, load + 1)
                                if load + 1 >= self._calculate_node_capacity(self.nodes[node_id]) * 0.4:
                                    underloaded_nodes.pop(i)
                                break
            
            # Update metrics
            self.shard_metrics["rebalance_count"] += 1
            self.shard_metrics["last_rebalance"] = datetime.now()
            
            self.logger.info(f"Rebalancing completed: {moves_made} shard assignments moved")
            return True
            
        except Exception as e:
            self.logger.error(f"Shard rebalancing failed: {e}")
            return False
    
    def _calculate_load_distribution(self) -> Dict[str, int]:
        """Calculate current load distribution across nodes"""
        load_distribution = {}
        
        for node_id in self.nodes:
            load_distribution[node_id] = 0
        
        for shard in self.shards.values():
            for node_id in shard.nodes:
                if node_id in load_distribution:
                    load_distribution[node_id] += 1
        
        return load_distribution
    
    def _find_movable_shards(self, node_id: str) -> List[str]:
        """Find shards that can be moved from an overloaded node"""
        if node_id not in self.node_shards:
            return []
        
        node_shard = self.node_shards[node_id]
        movable_shards = []
        
        # Prefer moving replica shards over primary shards
        for shard_id in node_shard.replica_shards:
            if shard_id in self.shards:
                shard = self.shards[shard_id]
                if len(shard.nodes) > self.replication_factor:  # Has enough replicas
                    movable_shards.append(shard_id)
        
        return movable_shards
    
    def _find_best_target_node(self, shard_id: str, underloaded_nodes: List[Tuple[str, int]]) -> Optional[str]:
        """Find the best target node for moving a shard"""
        shard = self.shards[shard_id]
        best_node = None
        best_score = -1
        
        for node_id, load in underloaded_nodes:
            if node_id in self.nodes and node_id not in shard.nodes:
                node = self.nodes[node_id]
                
                # Check compatibility
                if self._is_node_compatible_with_shard(node, shard):
                    # Calculate score based on various factors
                    score = self._calculate_target_node_score(node, shard, load)
                    
                    if score > best_score:
                        best_score = score
                        best_node = node_id
        
        return best_node
    
    def _calculate_target_node_score(self, node: AdvancedMeshNode, shard: ShardInfo, current_load: int) -> float:
        """Calculate score for a target node"""
        score = 0.0
        
        # Network quality (40%)
        score += node.metrics.calculate_quality_score() * 0.4
        
        # Load factor (30%) - lower load is better
        capacity = self._calculate_node_capacity(node)
        load_factor = current_load / capacity
        score += (1.0 - load_factor) * 0.3
        
        # Geographic diversity (20%)
        if self._provides_geographic_diversity(shard, node):
            score += 0.2
        
        # Node type compatibility (10%)
        if self._is_optimal_node_type(shard, node):
            score += 0.1
        
        return score
    
    async def _move_shard_assignment(self, shard_id: str, source_node_id: str, target_node_id: str):
        """Move a shard assignment from source to target node"""
        shard = self.shards[shard_id]
        
        # Remove from source node
        if source_node_id in shard.nodes:
            shard.nodes.remove(source_node_id)
        
        if source_node_id in shard.replica_nodes:
            shard.replica_nodes.remove(source_node_id)
        
        if source_node_id in self.node_shards:
            node_shard = self.node_shards[source_node_id]
            if shard_id in node_shard.assigned_shards:
                node_shard.assigned_shards.remove(shard_id)
            if shard_id in node_shard.replica_shards:
                node_shard.replica_shards.remove(shard_id)
        
        # Add to target node
        shard.nodes.append(target_node_id)
        shard.replica_nodes.append(target_node_id)
        
        if target_node_id in self.node_shards:
            self.node_shards[target_node_id].assigned_shards.append(shard_id)
            self.node_shards[target_node_id].replica_shards.append(shard_id)
    
    def get_nodes_for_shard(self, shard_id: str) -> List[AdvancedMeshNode]:
        """Get all nodes assigned to a specific shard"""
        if shard_id not in self.shards:
            return []
        
        shard = self.shards[shard_id]
        nodes = []
        
        for node_id in shard.nodes:
            if node_id in self.nodes:
                nodes.append(self.nodes[node_id])
        
        return nodes
    
    def get_nodes_for_data(self, data: str) -> List[AdvancedMeshNode]:
        """Get nodes responsible for storing/processing specific data"""
        shard_id = self.get_shard_for_data(data)
        return self.get_nodes_for_shard(shard_id)
    
    def get_primary_node_for_data(self, data: str) -> Optional[AdvancedMeshNode]:
        """Get the primary node responsible for specific data"""
        shard_id = self.get_shard_for_data(data)
        
        if shard_id in self.shards:
            shard = self.shards[shard_id]
            if shard.primary_node and shard.primary_node in self.nodes:
                return self.nodes[shard.primary_node]
        
        return None
    
    def get_shard_statistics(self) -> Dict[str, Any]:
        """Get comprehensive sharding statistics"""
        stats = {
            "total_shards": len(self.shards),
            "total_nodes": len(self.nodes),
            "replication_factor": self.replication_factor,
            "shards_per_node": {},
            "load_distribution": self._calculate_load_distribution(),
            "shard_types": {},
            "geographic_distribution": {},
            "performance_metrics": self.shard_metrics.copy()
        }
        
        # Calculate shard type distribution
        for shard in self.shards.values():
            shard_type = shard.shard_type.value
            stats["shard_types"][shard_type] = stats["shard_types"].get(shard_type, 0) + 1
        
        # Calculate geographic distribution
        for node in self.nodes.values():
            if node.location:
                country = node.location.country
                stats["geographic_distribution"][country] = \
                    stats["geographic_distribution"].get(country, 0) + 1
        
        return stats
    
    def visualize_shard_distribution(self) -> str:
        """Generate a text visualization of shard distribution"""
        output = []
        output.append("🌐 MESH NETWORK SHARD DISTRIBUTION")
        output.append("=" * 50)
        
        stats = self.get_shard_statistics()
        
        output.append(f"📊 Total Shards: {stats['total_shards']}")
        output.append(f"🔗 Total Nodes: {stats['total_nodes']}")
        output.append(f"⚡ Replication Factor: {stats['replication_factor']}")
        output.append("")
        
        output.append("🏷️ Shard Types:")
        for shard_type, count in stats["shard_types"].items():
            output.append(f"  • {shard_type}: {count} shards")
        output.append("")
        
        output.append("🌍 Geographic Distribution:")
        for country, count in stats["geographic_distribution"].items():
            output.append(f"  • {country}: {count} nodes")
        output.append("")
        
        output.append("📈 Load Distribution:")
        for node_id, load in stats["load_distribution"].items():
            if node_id in self.nodes:
                node = self.nodes[node_id]
                capacity = self._calculate_node_capacity(node)
                utilization = (load / capacity) * 100 if capacity > 0 else 0
                output.append(f"  • {node_id}: {load}/{capacity} shards ({utilization:.1f}%)")
        
        return "\n".join(output)
