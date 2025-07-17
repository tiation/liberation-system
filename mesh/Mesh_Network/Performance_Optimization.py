#!/usr/bin/env python3
"""
Advanced Performance Optimization and Caching for Liberation System Mesh Network
"""

import asyncio
import functools
import hashlib
import threading
import time
from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from weakref import WeakValueDictionary

from Sharding_Strategy import ShardingStrategy
from Advanced_Node_Discovery import AdvancedNodeDiscovery

# Cache Configuration
CACHE_TTL = 60  # Default cache time-to-live in seconds
MAX_CACHE_SIZE = 10000  # Maximum cache entries
CACHE_CLEANUP_INTERVAL = 300  # Cleanup interval in seconds
PREFETCH_THRESHOLD = 0.8  # Prefetch when cache hit ratio drops below this

@dataclass
class CacheEntry:
    """Enhanced cache entry with metadata"""
    value: Any
    timestamp: float
    access_count: int = 0
    last_access: float = 0
    size: int = 0
    priority: int = 0

@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    memory_usage: int = 0
    avg_access_time: float = 0.0

class AdvancedCache:
    """Multi-level caching system with intelligent eviction and prefetching"""
    
    def __init__(self, ttl: int = CACHE_TTL, max_size: int = MAX_CACHE_SIZE):
        self.ttl = ttl
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = CacheStats()
        self.lock = threading.RLock()
        self.cleanup_thread = None
        self.start_cleanup_thread()
        
        # Hot cache for frequently accessed items
        self.hot_cache: Dict[str, CacheEntry] = {}
        self.hot_cache_size = max_size // 10  # 10% of total cache size
        
        # Access patterns for intelligent prefetching
        self.access_patterns: Dict[str, List[str]] = defaultdict(list)
        self.pattern_lock = threading.Lock()
    
    def start_cleanup_thread(self):
        """Start background cleanup thread"""
        if self.cleanup_thread is None or not self.cleanup_thread.is_alive():
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_expired_entries, daemon=True
            )
            self.cleanup_thread.start()
    
    def get(self, key: str) -> Any:
        """Get item from cache with intelligent access tracking"""
        start_time = time.time()
        
        with self.lock:
            # Check hot cache first
            if key in self.hot_cache:
                entry = self.hot_cache[key]
                if time.time() - entry.timestamp < self.ttl:
                    entry.access_count += 1
                    entry.last_access = time.time()
                    self.stats.hits += 1
                    self._update_access_time(time.time() - start_time)
                    return entry.value
                else:
                    del self.hot_cache[key]
            
            # Check main cache
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry.timestamp < self.ttl:
                    entry.access_count += 1
                    entry.last_access = time.time()
                    
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                    
                    # Promote to hot cache if frequently accessed
                    if entry.access_count > 5 and len(self.hot_cache) < self.hot_cache_size:
                        self.hot_cache[key] = entry
                    
                    self.stats.hits += 1
                    self._update_access_time(time.time() - start_time)
                    return entry.value
                else:
                    del self.cache[key]
            
            self.stats.misses += 1
            self._update_access_time(time.time() - start_time)
            return None
    
    def set(self, key: str, value: Any, priority: int = 0):
        """Set item in cache with intelligent eviction"""
        with self.lock:
            # Calculate entry size (approximate)
            size = len(str(value))
            
            # Create cache entry
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                access_count=1,
                last_access=time.time(),
                size=size,
                priority=priority
            )
            
            # Evict if necessary
            while len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[key] = entry
            self.stats.size = len(self.cache)
            self.stats.memory_usage += size
    
    def _evict_lru(self):
        """Evict least recently used item with priority consideration"""
        if not self.cache:
            return
        
        # Find candidate for eviction (lowest priority, oldest access)
        min_priority = float('inf')
        oldest_access = float('inf')
        evict_key = None
        
        for key, entry in self.cache.items():
            if entry.priority < min_priority or (
                entry.priority == min_priority and entry.last_access < oldest_access
            ):
                min_priority = entry.priority
                oldest_access = entry.last_access
                evict_key = key
        
        if evict_key:
            evicted_entry = self.cache.pop(evict_key)
            self.stats.evictions += 1
            self.stats.memory_usage -= evicted_entry.size
            
            # Remove from hot cache if present
            if evict_key in self.hot_cache:
                del self.hot_cache[evict_key]
    
    def _cleanup_expired_entries(self):
        """Background cleanup of expired entries"""
        while True:
            time.sleep(CACHE_CLEANUP_INTERVAL)
            current_time = time.time()
            
            with self.lock:
                expired_keys = []
                for key, entry in self.cache.items():
                    if current_time - entry.timestamp > self.ttl:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    entry = self.cache.pop(key)
                    self.stats.memory_usage -= entry.size
                    if key in self.hot_cache:
                        del self.hot_cache[key]
                
                # Cleanup hot cache
                expired_hot_keys = []
                for key, entry in self.hot_cache.items():
                    if current_time - entry.timestamp > self.ttl:
                        expired_hot_keys.append(key)
                
                for key in expired_hot_keys:
                    del self.hot_cache[key]
    
    def _update_access_time(self, access_time: float):
        """Update average access time statistics"""
        total_requests = self.stats.hits + self.stats.misses
        if total_requests > 0:
            self.stats.avg_access_time = (
                (self.stats.avg_access_time * (total_requests - 1) + access_time) / total_requests
            )
    
    def prefetch_related(self, key: str, related_keys: List[str]):
        """Prefetch related items based on access patterns"""
        with self.pattern_lock:
            self.access_patterns[key].extend(related_keys)
            
            # Limit pattern history
            if len(self.access_patterns[key]) > 50:
                self.access_patterns[key] = self.access_patterns[key][-25:]
    
    def get_stats(self) -> CacheStats:
        """Get current cache statistics"""
        with self.lock:
            self.stats.size = len(self.cache)
            return self.stats
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.hot_cache.clear()
            self.stats = CacheStats()

class ShardAssignmentCache:
    """Specialized cache for shard assignments with intelligent invalidation"""
    
    def __init__(self):
        self.cache = AdvancedCache(ttl=120, max_size=5000)  # Longer TTL for shard assignments
        self.node_shard_map: Dict[str, Set[str]] = defaultdict(set)  # node_id -> shard_keys
        self.shard_node_map: Dict[str, Set[str]] = defaultdict(set)  # shard_id -> node_keys
        self.lock = threading.RLock()
    
    def get_shard_assignment(self, data: str) -> Optional[Dict[str, Any]]:
        """Get cached shard assignment for data"""
        key = f"shard_assignment_{data}"
        return self.cache.get(key)
    
    def set_shard_assignment(self, data: str, assignment: Dict[str, Any]):
        """Cache shard assignment with relationship tracking"""
        key = f"shard_assignment_{data}"
        self.cache.set(key, assignment, priority=10)  # High priority for shard assignments
        
        with self.lock:
            shard_id = assignment.get('shard_id')
            nodes = assignment.get('nodes', [])
            
            if shard_id:
                self.shard_node_map[shard_id].add(key)
                
                for node_id in nodes:
                    self.node_shard_map[node_id].add(key)
    
    def invalidate_node_assignments(self, node_id: str):
        """Invalidate all assignments involving a specific node"""
        with self.lock:
            if node_id in self.node_shard_map:
                for cache_key in self.node_shard_map[node_id]:
                    self.cache.cache.pop(cache_key, None)
                del self.node_shard_map[node_id]
    
    def invalidate_shard_assignments(self, shard_id: str):
        """Invalidate all assignments for a specific shard"""
        with self.lock:
            if shard_id in self.shard_node_map:
                for cache_key in self.shard_node_map[shard_id]:
                    self.cache.cache.pop(cache_key, None)
                del self.shard_node_map[shard_id]

class PerformanceMonitor:
    """Monitor and analyze performance metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.Lock()
    
    def record_metric(self, metric_name: str, value: float):
        """Record a performance metric"""
        with self.lock:
            self.metrics[metric_name].append(value)
            
            # Keep only recent metrics
            if len(self.metrics[metric_name]) > 1000:
                self.metrics[metric_name] = self.metrics[metric_name][-500:]
    
    def get_average(self, metric_name: str, window: int = 100) -> float:
        """Get average value for a metric over a window"""
        with self.lock:
            if metric_name not in self.metrics:
                return 0.0
            
            values = self.metrics[metric_name][-window:]
            return sum(values) / len(values) if values else 0.0
    
    def get_percentile(self, metric_name: str, percentile: float = 0.95) -> float:
        """Get percentile value for a metric"""
        with self.lock:
            if metric_name not in self.metrics:
                return 0.0
            
            values = sorted(self.metrics[metric_name])
            if not values:
                return 0.0
            
            index = int(len(values) * percentile)
            return values[min(index, len(values) - 1)]

class MeshNetworkOptimizer:
    """Advanced mesh network optimizer with comprehensive caching and performance monitoring"""
    
    def __init__(self, sharding_strategy: ShardingStrategy, node_discovery: AdvancedNodeDiscovery):
        self.sharding_strategy = sharding_strategy
        self.node_discovery = node_discovery
        
        # Caching components
        self.cache = AdvancedCache()
        self.shard_cache = ShardAssignmentCache()
        self.hash_cache = AdvancedCache(ttl=300, max_size=1000)  # Cache for hash calculations
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Weak references to avoid memory leaks
        self.node_refs = WeakValueDictionary()
    
    def get_optimized_shard_assignment(self, data: str) -> Dict[str, Any]:
        """Get optimized shard assignment with comprehensive caching"""
        start_time = time.time()
        
        # Check cache first
        cached_assignment = self.shard_cache.get_shard_assignment(data)
        if cached_assignment:
            self.performance_monitor.record_metric('shard_assignment_time', time.time() - start_time)
            return cached_assignment
        
        # Calculate assignment
        assignment = self._calculate_shard_assignment(data)
        
        # Cache the result
        self.shard_cache.set_shard_assignment(data, assignment)
        
        # Record performance metrics
        self.performance_monitor.record_metric('shard_assignment_time', time.time() - start_time)
        
        return assignment
    
    def _calculate_shard_assignment(self, data: str) -> Dict[str, Any]:
        """Calculate shard assignment with cached hash computation"""
        # Use cached hash if available
        hash_key = f"hash_{data}"
        data_hash = self.hash_cache.get(hash_key)
        
        if data_hash is None:
            data_hash = self.sharding_strategy.calculate_shard_hash(data)
            self.hash_cache.set(hash_key, data_hash)
        
        shard_id = self.sharding_strategy.get_shard_for_data(data)
        nodes = self.sharding_strategy.get_nodes_for_shard(shard_id)
        primary_node = self.sharding_strategy.get_primary_node_for_data(data)
        
        return {
            "shard_id": shard_id,
            "nodes": [node.id for node in nodes],
            "primary_node": primary_node.id if primary_node else None,
            "hash": data_hash,
            "timestamp": time.time()
        }
    
    @functools.lru_cache(maxsize=256)
    def get_cached_node_capacity(self, node_id: str) -> int:
        """Get cached node capacity calculation"""
        if node_id in self.sharding_strategy.nodes:
            node = self.sharding_strategy.nodes[node_id]
            return self.sharding_strategy._calculate_node_capacity(node)
        return 0
    
    def cache_result(self, ttl: int = CACHE_TTL, priority: int = 0):
        """Advanced decorator for caching function results"""
        def decorator(function: Callable) -> Callable:
            @functools.wraps(function)
            def wrapped_function(*args, **kwargs):
                key = self._generate_cache_key(function.__name__, *args, **kwargs)
                cached_value = self.cache.get(key)
                
                if cached_value is not None:
                    return cached_value
                
                start_time = time.time()
                result = function(*args, **kwargs)
                
                # Record execution time
                execution_time = time.time() - start_time
                self.performance_monitor.record_metric(f'{function.__name__}_execution_time', execution_time)
                
                # Cache with custom TTL and priority
                cache_entry = AdvancedCache(ttl=ttl)
                cache_entry.set(key, result, priority=priority)
                self.cache.set(key, result, priority=priority)
                
                return result
            
            return wrapped_function
        return decorator
    
    def batch_shard_assignments(self, data_list: List[str]) -> Dict[str, Dict[str, Any]]:
        """Efficiently process multiple shard assignments in batch"""
        results = {}
        uncached_data = []
        
        # Check cache for each item
        for data in data_list:
            cached_assignment = self.shard_cache.get_shard_assignment(data)
            if cached_assignment:
                results[data] = cached_assignment
            else:
                uncached_data.append(data)
        
        # Process uncached items in parallel
        if uncached_data:
            futures = []
            for data in uncached_data:
                future = self.executor.submit(self._calculate_shard_assignment, data)
                futures.append((data, future))
            
            for data, future in futures:
                try:
                    assignment = future.result(timeout=5.0)
                    results[data] = assignment
                    self.shard_cache.set_shard_assignment(data, assignment)
                except Exception as e:
                    results[data] = {"error": str(e)}
        
        return results
    
    def invalidate_caches_for_node(self, node_id: str):
        """Invalidate all caches related to a specific node"""
        self.shard_cache.invalidate_node_assignments(node_id)
        self.get_cached_node_capacity.cache_clear()
    
    def invalidate_caches_for_shard(self, shard_id: str):
        """Invalidate all caches related to a specific shard"""
        self.shard_cache.invalidate_shard_assignments(shard_id)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        cache_stats = self.cache.get_stats()
        shard_cache_stats = self.shard_cache.cache.get_stats()
        
        return {
            "cache_performance": {
                "hits": cache_stats.hits,
                "misses": cache_stats.misses,
                "hit_ratio": cache_stats.hits / (cache_stats.hits + cache_stats.misses) if (cache_stats.hits + cache_stats.misses) > 0 else 0,
                "evictions": cache_stats.evictions,
                "memory_usage": cache_stats.memory_usage,
                "avg_access_time": cache_stats.avg_access_time
            },
            "shard_cache_performance": {
                "hits": shard_cache_stats.hits,
                "misses": shard_cache_stats.misses,
                "hit_ratio": shard_cache_stats.hits / (shard_cache_stats.hits + shard_cache_stats.misses) if (shard_cache_stats.hits + shard_cache_stats.misses) > 0 else 0,
                "size": shard_cache_stats.size
            },
            "performance_metrics": {
                "avg_shard_assignment_time": self.performance_monitor.get_average('shard_assignment_time'),
                "p95_shard_assignment_time": self.performance_monitor.get_percentile('shard_assignment_time', 0.95),
                "avg_calculation_time": self.performance_monitor.get_average('_calculate_shard_assignment_execution_time'),
            }
        }
    
    def optimize_cache_settings(self):
        """Automatically optimize cache settings based on usage patterns"""
        cache_stats = self.cache.get_stats()
        
        # Adjust cache size based on hit ratio
        if cache_stats.hits + cache_stats.misses > 100:
            hit_ratio = cache_stats.hits / (cache_stats.hits + cache_stats.misses)
            
            if hit_ratio < 0.7:  # Low hit ratio, increase cache size
                self.cache.max_size = int(min(self.cache.max_size * 1.2, 50000))
            elif hit_ratio > 0.95:  # Very high hit ratio, can reduce cache size
                self.cache.max_size = int(max(self.cache.max_size * 0.9, 1000))
    
    def _generate_cache_key(self, function_name: str, *args, **kwargs) -> str:
        """Generate a unique cache key with improved hashing"""
        key_parts = [function_name]
        
        # Hash complex arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}={v}")
            else:
                key_parts.append(f"{k}={hashlib.md5(str(v).encode()).hexdigest()[:8]}")
        
        return "_".join(key_parts)
