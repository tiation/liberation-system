#!/usr/bin/env python3
"""
Advanced Node Discovery Caching System
Implements comprehensive caching for nodes already discovered with persistence,
TTL management, and detailed statistics.
"""

import asyncio
import logging
import time
import json
import pickle
import os
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import hashlib


class CacheStrategy(Enum):
    """Different caching strategies available"""
    MEMORY_ONLY = "memory_only"
    PERSISTENT = "persistent"
    HYBRID = "hybrid"


class NodeStatus(Enum):
    """Node status in cache"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class NodeCacheEntry:
    """Enhanced cache entry for discovered nodes"""
    node_id: str
    host: str
    port: int
    node_type: str = "standard"
    location: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    
    # Cache metadata
    discovered_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    last_successful_connection: Optional[float] = None
    
    # Discovery statistics
    probe_count: int = 0
    connection_attempts: int = 0
    successful_connections: int = 0
    failed_connections: int = 0
    
    # Performance metrics
    average_latency: float = 0.0
    best_latency: float = float('inf')
    worst_latency: float = 0.0
    reliability_score: float = 1.0
    
    # Discovery context
    discovery_method: str = "unknown"
    discovery_source: str = "unknown"
    tags: Set[str] = field(default_factory=set)
    
    # Cache behavior
    ttl: int = 3600  # 1 hour default
    priority: int = 1  # Higher priority = keep longer
    status: NodeStatus = NodeStatus.UNKNOWN
    
    def update_metrics(self, latency: float, success: bool = True):
        """Update node metrics with new measurement"""
        self.probe_count += 1
        self.last_updated = time.time()
        
        if success:
            self.last_seen = time.time()
            self.successful_connections += 1
            self.last_successful_connection = time.time()
            
            # Update latency statistics
            if latency < float('inf'):
                self.best_latency = min(self.best_latency, latency)
                self.worst_latency = max(self.worst_latency, latency)
                
                # Calculate rolling average
                if self.average_latency == 0.0:
                    self.average_latency = latency
                else:
                    self.average_latency = (self.average_latency * 0.8) + (latency * 0.2)
            
            self.status = NodeStatus.ACTIVE
        else:
            self.failed_connections += 1
            if self.failed_connections > 3:
                self.status = NodeStatus.FAILED
            elif time.time() - self.last_seen > 600:  # 10 minutes
                self.status = NodeStatus.INACTIVE
        
        # Update reliability score
        if self.connection_attempts > 0:
            self.reliability_score = self.successful_connections / self.connection_attempts
        
        self.connection_attempts += 1
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return time.time() - self.last_updated > self.ttl
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['tags'] = list(self.tags)  # Convert set to list
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeCacheEntry':
        """Create from dictionary"""
        data['tags'] = set(data.get('tags', []))
        data['status'] = NodeStatus(data.get('status', NodeStatus.UNKNOWN.value))
        return cls(**data)


class NodeDiscoveryCache:
    """Advanced caching system for node discovery"""
    
    def __init__(self, 
                 cache_dir: str = "cache",
                 cache_file: str = "node_discovery_cache.pkl",
                 json_backup_file: str = "node_discovery_cache.json",
                 strategy: CacheStrategy = CacheStrategy.HYBRID,
                 max_cache_size: int = 1000,
                 default_ttl: int = 3600,
                 cleanup_interval: int = 300):
        
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, cache_file)
        self.json_backup_file = os.path.join(cache_dir, json_backup_file)
        self.strategy = strategy
        self.max_cache_size = max_cache_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        
        # In-memory cache
        self.cache: Dict[str, NodeCacheEntry] = {}
        self.cache_stats = defaultdict(int)
        
        # Index for fast lookups
        self.host_port_index: Dict[str, str] = {}  # "host:port" -> node_id
        self.location_index: Dict[str, Set[str]] = defaultdict(set)  # "country:region" -> set of node_ids
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)  # tag -> set of node_ids
        
        self.logger = logging.getLogger(__name__)
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load existing cache
        self._load_cache()
        
        # Start cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start the periodic cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired entries"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self.cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic cleanup: {e}")
    
    def _load_cache(self):
        """Load cache from persistent storage"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    data = pickle.load(f)
                    
                    # Load cache entries
                    for node_id, entry_data in data.get('cache', {}).items():
                        try:
                            entry = NodeCacheEntry.from_dict(entry_data)
                            self.cache[node_id] = entry
                            self._update_indexes(node_id, entry)
                        except Exception as e:
                            self.logger.warning(f"Failed to load cache entry {node_id}: {e}")
                    
                    # Load statistics
                    self.cache_stats.update(data.get('stats', {}))
                    
                    self.logger.info(f"Loaded {len(self.cache)} nodes from cache")
                    
        except Exception as e:
            self.logger.error(f"Failed to load cache: {e}")
            # Try to load from JSON backup
            self._load_json_backup()
    
    def _load_json_backup(self):
        """Load cache from JSON backup file"""
        try:
            if os.path.exists(self.json_backup_file):
                with open(self.json_backup_file, 'r') as f:
                    data = json.load(f)
                    
                    for node_id, entry_data in data.get('cache', {}).items():
                        try:
                            entry = NodeCacheEntry.from_dict(entry_data)
                            self.cache[node_id] = entry
                            self._update_indexes(node_id, entry)
                        except Exception as e:
                            self.logger.warning(f"Failed to load JSON cache entry {node_id}: {e}")
                    
                    self.logger.info(f"Loaded {len(self.cache)} nodes from JSON backup")
                    
        except Exception as e:
            self.logger.error(f"Failed to load JSON backup: {e}")
    
    def _save_cache(self):
        """Save cache to persistent storage"""
        if self.strategy == CacheStrategy.MEMORY_ONLY:
            return
        
        try:
            # Prepare data for serialization
            cache_data = {}
            for node_id, entry in self.cache.items():
                cache_data[node_id] = entry.to_dict()
            
            data = {
                'cache': cache_data,
                'stats': dict(self.cache_stats),
                'last_saved': time.time(),
                'version': '1.0'
            }
            
            # Save as pickle
            with open(self.cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            # Save JSON backup
            with open(self.json_backup_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.debug(f"Saved {len(self.cache)} nodes to cache")
            
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")
    
    def _update_indexes(self, node_id: str, entry: NodeCacheEntry):
        """Update indexes for fast lookups"""
        # Host:port index
        host_port_key = f"{entry.host}:{entry.port}"
        self.host_port_index[host_port_key] = node_id
        
        # Location index
        if entry.location:
            location_key = f"{entry.location.get('country', '')}:{entry.location.get('region', '')}"
            self.location_index[location_key].add(node_id)
        
        # Tag index
        for tag in entry.tags:
            self.tag_index[tag].add(node_id)
    
    def _remove_from_indexes(self, node_id: str, entry: NodeCacheEntry):
        """Remove from indexes"""
        # Host:port index
        host_port_key = f"{entry.host}:{entry.port}"
        if host_port_key in self.host_port_index:
            del self.host_port_index[host_port_key]
        
        # Location index
        if entry.location:
            location_key = f"{entry.location.get('country', '')}:{entry.location.get('region', '')}"
            if location_key in self.location_index:
                self.location_index[location_key].discard(node_id)
                if not self.location_index[location_key]:
                    del self.location_index[location_key]
        
        # Tag index
        for tag in entry.tags:
            if tag in self.tag_index:
                self.tag_index[tag].discard(node_id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
    
    def cache_node(self, node_id: str, host: str, port: int, **kwargs) -> NodeCacheEntry:
        """Cache a discovered node"""
        entry = NodeCacheEntry(
            node_id=node_id,
            host=host,
            port=port,
            ttl=kwargs.get('ttl', self.default_ttl),
            **{k: v for k, v in kwargs.items() if k != 'ttl'}
        )
        
        # Check if we need to evict entries
        if len(self.cache) >= self.max_cache_size:
            self._evict_entries()
        
        # Update existing entry or add new one
        if node_id in self.cache:
            old_entry = self.cache[node_id]
            self._remove_from_indexes(node_id, old_entry)
            self.cache_stats['cache_updates'] += 1
        else:
            self.cache_stats['cache_adds'] += 1
        
        self.cache[node_id] = entry
        self._update_indexes(node_id, entry)
        
        self.logger.debug(f"Cached node {node_id} ({host}:{port})")
        return entry
    
    def get_node(self, node_id: str) -> Optional[NodeCacheEntry]:
        """Get a cached node by ID"""
        if node_id in self.cache:
            entry = self.cache[node_id]
            if not entry.is_expired():
                self.cache_stats['cache_hits'] += 1
                return entry
            else:
                # Remove expired entry
                self.remove_node(node_id)
                self.cache_stats['cache_expired'] += 1
        
        self.cache_stats['cache_misses'] += 1
        return None
    
    def get_node_by_host_port(self, host: str, port: int) -> Optional[NodeCacheEntry]:
        """Get a cached node by host and port"""
        host_port_key = f"{host}:{port}"
        if host_port_key in self.host_port_index:
            node_id = self.host_port_index[host_port_key]
            return self.get_node(node_id)
        return None
    
    def get_nodes_by_location(self, country: str = None, region: str = None) -> List[NodeCacheEntry]:
        """Get cached nodes by location"""
        location_key = f"{country or ''}:{region or ''}"
        
        if location_key in self.location_index:
            nodes = []
            for node_id in self.location_index[location_key]:
                entry = self.get_node(node_id)
                if entry:
                    nodes.append(entry)
            return nodes
        return []
    
    def get_nodes_by_tag(self, tag: str) -> List[NodeCacheEntry]:
        """Get cached nodes by tag"""
        if tag in self.tag_index:
            nodes = []
            for node_id in self.tag_index[tag]:
                entry = self.get_node(node_id)
                if entry:
                    nodes.append(entry)
            return nodes
        return []
    
    def update_node_metrics(self, node_id: str, latency: float, success: bool = True):
        """Update node metrics"""
        entry = self.get_node(node_id)
        if entry:
            entry.update_metrics(latency, success)
            self.cache_stats['metrics_updates'] += 1
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from cache"""
        if node_id in self.cache:
            entry = self.cache[node_id]
            self._remove_from_indexes(node_id, entry)
            del self.cache[node_id]
            self.cache_stats['cache_removes'] += 1
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_nodes = []
        
        for node_id, entry in self.cache.items():
            if entry.is_expired():
                expired_nodes.append(node_id)
        
        for node_id in expired_nodes:
            self.remove_node(node_id)
        
        if expired_nodes:
            self.logger.info(f"Cleaned up {len(expired_nodes)} expired cache entries")
        
        return len(expired_nodes)
    
    def _evict_entries(self):
        """Evict least valuable entries when cache is full"""
        if len(self.cache) < self.max_cache_size:
            return
        
        # Calculate eviction scores (lower = more likely to evict)
        entries_with_scores = []
        current_time = time.time()
        
        for node_id, entry in self.cache.items():
            # Score based on:
            # - Age (older = lower score)
            # - Reliability (lower reliability = lower score)
            # - Priority (lower priority = lower score)
            # - Recent activity (less recent = lower score)
            
            age_score = max(0, 1 - (current_time - entry.discovered_at) / 86400)  # 1 day
            reliability_score = entry.reliability_score
            priority_score = entry.priority / 10.0  # Normalize
            activity_score = max(0, 1 - (current_time - entry.last_seen) / 3600)  # 1 hour
            
            total_score = (age_score + reliability_score + priority_score + activity_score) / 4
            entries_with_scores.append((total_score, node_id))
        
        # Sort by score (lowest first)
        entries_with_scores.sort(key=lambda x: x[0])
        
        # Evict 10% of entries
        evict_count = max(1, len(entries_with_scores) // 10)
        
        for i in range(evict_count):
            _, node_id = entries_with_scores[i]
            self.remove_node(node_id)
            self.cache_stats['cache_evictions'] += 1
        
        self.logger.info(f"Evicted {evict_count} entries from cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get detailed cache statistics"""
        current_time = time.time()
        
        # Calculate additional statistics
        total_nodes = len(self.cache)
        active_nodes = sum(1 for entry in self.cache.values() if entry.status == NodeStatus.ACTIVE)
        failed_nodes = sum(1 for entry in self.cache.values() if entry.status == NodeStatus.FAILED)
        
        # Calculate average metrics
        avg_latency = 0.0
        avg_reliability = 0.0
        if total_nodes > 0:
            avg_latency = sum(entry.average_latency for entry in self.cache.values()) / total_nodes
            avg_reliability = sum(entry.reliability_score for entry in self.cache.values()) / total_nodes
        
        # Hit rate
        total_requests = self.cache_stats['cache_hits'] + self.cache_stats['cache_misses']
        hit_rate = (self.cache_stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': total_nodes,
            'max_cache_size': self.max_cache_size,
            'active_nodes': active_nodes,
            'failed_nodes': failed_nodes,
            'hit_rate': hit_rate,
            'avg_latency': avg_latency,
            'avg_reliability': avg_reliability,
            'index_sizes': {
                'host_port': len(self.host_port_index),
                'location': len(self.location_index),
                'tag': len(self.tag_index)
            },
            'stats': dict(self.cache_stats)
        }
    
    def export_cache_data(self, format: str = 'json') -> str:
        """Export cache data in specified format"""
        if format == 'json':
            cache_data = {}
            for node_id, entry in self.cache.items():
                cache_data[node_id] = entry.to_dict()
            return json.dumps(cache_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_cache_data(self, data: str, format: str = 'json'):
        """Import cache data from string"""
        if format == 'json':
            cache_data = json.loads(data)
            for node_id, entry_data in cache_data.items():
                try:
                    entry = NodeCacheEntry.from_dict(entry_data)
                    self.cache[node_id] = entry
                    self._update_indexes(node_id, entry)
                except Exception as e:
                    self.logger.warning(f"Failed to import cache entry {node_id}: {e}")
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def clear_cache(self):
        """Clear all cache data"""
        self.cache.clear()
        self.host_port_index.clear()
        self.location_index.clear()
        self.tag_index.clear()
        self.cache_stats.clear()
        
        # Remove cache files
        for file_path in [self.cache_file, self.json_backup_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        self.logger.info("Cache cleared")
    
    def save_cache(self):
        """Manually save cache to persistent storage"""
        self._save_cache()
    
    def shutdown(self):
        """Shutdown the cache system"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Save cache before shutdown
        self._save_cache()
        
        self.logger.info("Cache system shutdown")


# Integration with existing AdvancedNodeDiscovery
class CachedAdvancedNodeDiscovery:
    """Enhanced AdvancedNodeDiscovery with comprehensive caching"""
    
    def __init__(self, cache_config: Dict[str, Any] = None):
        from .Advanced_Node_Discovery import AdvancedNodeDiscovery
        
        # Initialize base discovery
        self.discovery = AdvancedNodeDiscovery()
        
        # Initialize cache
        cache_config = cache_config or {}
        self.cache = NodeDiscoveryCache(**cache_config)
        
        self.logger = logging.getLogger(__name__)
    
    async def discover_nodes(self, local_node, use_cache: bool = True) -> List[Any]:
        """Discover nodes with caching support"""
        discovered = []
        
        if use_cache:
            # First, try to get nodes from cache
            cached_nodes = []
            for node_id in list(self.cache.cache.keys()):
                entry = self.cache.get_node(node_id)
                if entry and entry.status == NodeStatus.ACTIVE:
                    # Convert cache entry back to AdvancedMeshNode
                    from .Advanced_Node_Discovery import AdvancedMeshNode, GeoLocation, NetworkMetrics, NodeCapabilities
                    
                    location = None
                    if entry.location:
                        location = GeoLocation(**entry.location)
                    
                    node = AdvancedMeshNode(
                        id=entry.node_id,
                        host=entry.host,
                        port=entry.port,
                        location=location,
                        metrics=NetworkMetrics(**entry.metrics),
                        capabilities=NodeCapabilities(**entry.capabilities),
                        last_seen=entry.last_seen,
                        trust_score=entry.reliability_score
                    )
                    cached_nodes.append(node)
            
            discovered.extend(cached_nodes)
            self.logger.info(f"Retrieved {len(cached_nodes)} nodes from cache")
        
        # Discover new nodes
        new_nodes = await self.discovery.discover_nodes(local_node)
        
        # Cache newly discovered nodes
        for node in new_nodes:
            location_dict = None
            if node.location:
                location_dict = {
                    'latitude': node.location.latitude,
                    'longitude': node.location.longitude,
                    'country': node.location.country,
                    'city': node.location.city,
                    'region': node.location.region
                }
            
            self.cache.cache_node(
                node_id=node.id,
                host=node.host,
                port=node.port,
                location=location_dict,
                metrics={
                    'latency': node.metrics.latency,
                    'bandwidth': node.metrics.bandwidth,
                    'uptime': node.metrics.uptime
                },
                capabilities={
                    'max_connections': node.capabilities.max_connections,
                    'supported_protocols': node.capabilities.supported_protocols
                },
                discovery_method="advanced_discovery",
                tags={'discovered', 'active'}
            )
        
        discovered.extend(new_nodes)
        
        # Save cache
        self.cache.save_cache()
        
        return discovered
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_cache_stats()
    
    def clear_cache(self):
        """Clear cache"""
        self.cache.clear_cache()


# Example usage
async def main():
    """Example usage of the caching system"""
    logging.basicConfig(level=logging.INFO)
    
    # Create cached discovery service
    cached_discovery = CachedAdvancedNodeDiscovery({
        'max_cache_size': 100,
        'default_ttl': 1800,  # 30 minutes
        'strategy': CacheStrategy.HYBRID
    })
    
    # Mock local node
    from .Advanced_Node_Discovery import AdvancedMeshNode
    local_node = AdvancedMeshNode(
        id="local_test",
        host="127.0.0.1",
        port=8000
    )
    
    print("🔄 Testing Node Discovery Cache")
    print("=" * 50)
    
    # First discovery (should cache nodes)
    nodes = await cached_discovery.discover_nodes(local_node)
    print(f"First discovery: {len(nodes)} nodes")
    
    # Second discovery (should use cache)
    nodes = await cached_discovery.discover_nodes(local_node)
    print(f"Second discovery: {len(nodes)} nodes")
    
    # Show cache statistics
    stats = cached_discovery.get_cache_stats()
    print(f"\nCache Statistics:")
    print(f"  Cache Size: {stats['cache_size']}")
    print(f"  Hit Rate: {stats['hit_rate']:.1f}%")
    print(f"  Active Nodes: {stats['active_nodes']}")
    print(f"  Average Latency: {stats['avg_latency']:.1f}ms")
    print(f"  Average Reliability: {stats['avg_reliability']:.3f}")
    
    print("\n✅ Cache testing complete!")


if __name__ == "__main__":
    asyncio.run(main())
