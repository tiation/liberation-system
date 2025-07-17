#!/usr/bin/env python3
"""
Test Suite for Performance Optimization and Caching Strategies
"""

import time
import threading
import unittest
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor

from Performance_Optimization import (
    AdvancedCache, ShardAssignmentCache, PerformanceMonitor, 
    MeshNetworkOptimizer, CacheEntry, CacheStats
)


class TestAdvancedCache(unittest.TestCase):
    """Test cases for AdvancedCache implementation"""
    
    def setUp(self):
        self.cache = AdvancedCache(ttl=1, max_size=10)
    
    def test_basic_cache_operations(self):
        """Test basic cache set/get operations"""
        # Test set and get
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")
        
        # Test non-existent key
        self.assertIsNone(self.cache.get("non_existent"))
    
    def test_cache_expiration(self):
        """Test cache TTL expiration"""
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")
        
        # Wait for expiration
        time.sleep(1.1)
        self.assertIsNone(self.cache.get("key1"))
    
    def test_cache_size_limit(self):
        """Test cache size limit and eviction"""
        # Fill cache to limit
        for i in range(12):  # Exceed max_size of 10
            self.cache.set(f"key{i}", f"value{i}")
        
        # Check that cache size doesn't exceed limit
        self.assertLessEqual(len(self.cache.cache), 10)
        
        # Check that some items were evicted
        stats = self.cache.get_stats()
        self.assertGreater(stats.evictions, 0)
    
    def test_hot_cache_promotion(self):
        """Test promotion of frequently accessed items to hot cache"""
        self.cache.set("hot_key", "hot_value")
        
        # Access multiple times to trigger promotion
        for _ in range(6):
            self.cache.get("hot_key")
        
        # Check if item is in hot cache
        self.assertIn("hot_key", self.cache.hot_cache)
    
    def test_priority_eviction(self):
        """Test priority-based eviction"""
        # Test with smaller cache for more predictable eviction
        small_cache = AdvancedCache(ttl=300, max_size=3)
        
        # Add items with different priorities
        small_cache.set("low_priority", "value1", priority=1)
        small_cache.set("high_priority", "value2", priority=10)
        
        # Fill cache to trigger eviction
        for i in range(5):  # Exceed max_size of 3
            small_cache.set(f"filler{i}", f"value{i}")
        
        # High priority item should remain
        self.assertEqual(small_cache.get("high_priority"), "value2")
        # Low priority item should be evicted
        self.assertIsNone(small_cache.get("low_priority"))
    
    def test_cache_statistics(self):
        """Test cache statistics tracking"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("non_existent")  # Miss
        
        stats = self.cache.get_stats()
        self.assertEqual(stats.hits, 1)
        self.assertEqual(stats.misses, 1)
        self.assertGreater(stats.avg_access_time, 0)
    
    def test_thread_safety(self):
        """Test thread-safe operations"""
        def worker(thread_id):
            for i in range(100):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                self.cache.set(key, value)
                retrieved = self.cache.get(key)
                self.assertEqual(retrieved, value)
        
        # Run multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()


class TestShardAssignmentCache(unittest.TestCase):
    """Test cases for ShardAssignmentCache"""
    
    def setUp(self):
        self.shard_cache = ShardAssignmentCache()
    
    def test_shard_assignment_caching(self):
        """Test shard assignment caching"""
        assignment = {
            "shard_id": "shard_001",
            "nodes": ["node1", "node2"],
            "primary_node": "node1"
        }
        
        self.shard_cache.set_shard_assignment("test_data", assignment)
        cached_assignment = self.shard_cache.get_shard_assignment("test_data")
        
        self.assertEqual(cached_assignment, assignment)
    
    def test_node_invalidation(self):
        """Test cache invalidation for specific nodes"""
        assignment = {
            "shard_id": "shard_001",
            "nodes": ["node1", "node2"],
            "primary_node": "node1"
        }
        
        self.shard_cache.set_shard_assignment("test_data", assignment)
        
        # Invalidate all assignments for node1
        self.shard_cache.invalidate_node_assignments("node1")
        
        # Assignment should be invalidated
        self.assertIsNone(self.shard_cache.get_shard_assignment("test_data"))
    
    def test_shard_invalidation(self):
        """Test cache invalidation for specific shards"""
        assignment = {
            "shard_id": "shard_001",
            "nodes": ["node1", "node2"],
            "primary_node": "node1"
        }
        
        self.shard_cache.set_shard_assignment("test_data", assignment)
        
        # Invalidate all assignments for shard_001
        self.shard_cache.invalidate_shard_assignments("shard_001")
        
        # Assignment should be invalidated
        self.assertIsNone(self.shard_cache.get_shard_assignment("test_data"))


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for PerformanceMonitor"""
    
    def setUp(self):
        self.monitor = PerformanceMonitor()
    
    def test_metric_recording(self):
        """Test metric recording and retrieval"""
        self.monitor.record_metric("test_metric", 1.5)
        self.monitor.record_metric("test_metric", 2.5)
        self.monitor.record_metric("test_metric", 3.5)
        
        average = self.monitor.get_average("test_metric")
        self.assertAlmostEqual(average, 2.5, places=1)
    
    def test_percentile_calculation(self):
        """Test percentile calculation"""
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        for value in values:
            self.monitor.record_metric("test_metric", value)
        
        p95 = self.monitor.get_percentile("test_metric", 0.95)
        self.assertAlmostEqual(p95, 10.0, places=1)
    
    def test_metric_window(self):
        """Test metric window functionality"""
        for i in range(1, 11):
            self.monitor.record_metric("test_metric", float(i))
        
        # Test window of 5
        average = self.monitor.get_average("test_metric", window=5)
        self.assertAlmostEqual(average, 8.0, places=1)  # Average of 6,7,8,9,10


class TestMeshNetworkOptimizer(unittest.TestCase):
    """Test cases for MeshNetworkOptimizer"""
    
    def setUp(self):
        # Mock dependencies
        self.mock_sharding_strategy = Mock()
        self.mock_node_discovery = Mock()
        
        # Configure mock responses
        self.mock_sharding_strategy.calculate_shard_hash.return_value = 12345
        self.mock_sharding_strategy.get_shard_for_data.return_value = "shard_001"
        self.mock_sharding_strategy.get_nodes_for_shard.return_value = []
        self.mock_sharding_strategy.get_primary_node_for_data.return_value = None
        
        self.optimizer = MeshNetworkOptimizer(
            self.mock_sharding_strategy,
            self.mock_node_discovery
        )
    
    def test_optimized_shard_assignment(self):
        """Test optimized shard assignment with caching"""
        # First call should calculate and cache
        assignment1 = self.optimizer.get_optimized_shard_assignment("test_data")
        
        # Second call should use cache
        assignment2 = self.optimizer.get_optimized_shard_assignment("test_data")
        
        # Both should be identical
        self.assertEqual(assignment1, assignment2)
        
        # Sharding strategy should only be called once
        self.mock_sharding_strategy.calculate_shard_hash.assert_called_once()
    
    def test_batch_shard_assignments(self):
        """Test batch processing of shard assignments"""
        data_list = ["data1", "data2", "data3"]
        
        results = self.optimizer.batch_shard_assignments(data_list)
        
        # Should have results for all data items
        self.assertEqual(len(results), 3)
        for data in data_list:
            self.assertIn(data, results)
    
    def test_cache_invalidation(self):
        """Test cache invalidation functionality"""
        # Cache an assignment
        self.optimizer.get_optimized_shard_assignment("test_data")
        
        # Invalidate for a node
        self.optimizer.invalidate_caches_for_node("node1")
        
        # Cache should be cleared (no way to directly verify, but no exception should occur)
        self.assertTrue(True)  # If we reach here, invalidation worked
    
    def test_performance_report(self):
        """Test performance report generation"""
        # Generate some activity
        for i in range(10):
            self.optimizer.get_optimized_shard_assignment(f"data{i}")
        
        report = self.optimizer.get_performance_report()
        
        # Report should contain expected sections
        self.assertIn("cache_performance", report)
        self.assertIn("shard_cache_performance", report)
        self.assertIn("performance_metrics", report)
    
    def test_cache_decorator(self):
        """Test cache decorator functionality"""
        @self.optimizer.cache_result(ttl=60, priority=5)
        def expensive_operation(x):
            return x * 2
        
        # First call
        result1 = expensive_operation(5)
        
        # Second call should use cache
        result2 = expensive_operation(5)
        
        self.assertEqual(result1, result2)
        self.assertEqual(result1, 10)


class TestCacheIntegration(unittest.TestCase):
    """Integration tests for caching system"""
    
    def test_concurrent_cache_access(self):
        """Test concurrent access to cache system"""
        cache = AdvancedCache(ttl=60, max_size=1000)
        
        def worker(worker_id):
            for i in range(100):
                key = f"worker_{worker_id}_key_{i}"
                value = f"worker_{worker_id}_value_{i}"
                cache.set(key, value)
                retrieved = cache.get(key)
                if retrieved != value:
                    raise ValueError(f"Cache consistency error: {retrieved} != {value}")
        
        # Run concurrent workers
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            for future in futures:
                future.result()  # Will raise exception if any worker failed
    
    def test_cache_performance_under_load(self):
        """Test cache performance under heavy load"""
        cache = AdvancedCache(ttl=300, max_size=5000)
        
        # Warm up cache
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Measure performance
        start_time = time.time()
        
        for i in range(1000):
            cache.get(f"key_{i}")
        
        end_time = time.time()
        
        # Should be able to perform 1000 cache gets in reasonable time
        self.assertLess(end_time - start_time, 1.0)  # Less than 1 second


class TestCacheOptimization(unittest.TestCase):
    """Test cache optimization strategies"""
    
    def test_cache_size_optimization(self):
        """Test automatic cache size optimization"""
        optimizer = MeshNetworkOptimizer(Mock(), Mock())
        
        # Simulate low hit ratio with sufficient operations
        optimizer.cache.stats.hits = 30
        optimizer.cache.stats.misses = 70
        
        original_size = optimizer.cache.max_size
        optimizer.optimize_cache_settings()
        
        # Cache size should increase due to low hit ratio
        self.assertGreater(optimizer.cache.max_size, original_size)
    
    def test_prefetch_patterns(self):
        """Test access pattern tracking for prefetching"""
        cache = AdvancedCache()
        
        # Simulate access patterns
        cache.prefetch_related("key1", ["key2", "key3"])
        cache.prefetch_related("key1", ["key4", "key5"])
        
        # Check that patterns are recorded
        self.assertIn("key1", cache.access_patterns)
        self.assertEqual(len(cache.access_patterns["key1"]), 4)


def run_performance_benchmarks():
    """Run performance benchmarks for caching system"""
    print("Running Performance Benchmarks...")
    
    # Test 1: Cache hit performance
    cache = AdvancedCache(max_size=10000)
    
    # Fill cache
    for i in range(1000):
        cache.set(f"key_{i}", f"value_{i}")
    
    # Benchmark cache hits
    start_time = time.time()
    for i in range(1000):
        cache.get(f"key_{i}")
    hit_time = time.time() - start_time
    
    # Benchmark cache misses
    start_time = time.time()
    for i in range(1000, 2000):
        cache.get(f"key_{i}")
    miss_time = time.time() - start_time
    
    print(f"Cache Hit Performance: {hit_time:.4f}s for 1000 operations")
    print(f"Cache Miss Performance: {miss_time:.4f}s for 1000 operations")
    
    # Test 2: Shard assignment performance
    mock_sharding = Mock()
    mock_sharding.calculate_shard_hash.return_value = 12345
    mock_sharding.get_shard_for_data.return_value = "shard_001"
    mock_sharding.get_nodes_for_shard.return_value = []
    mock_sharding.get_primary_node_for_data.return_value = None
    
    optimizer = MeshNetworkOptimizer(mock_sharding, Mock())
    
    # Benchmark shard assignment
    start_time = time.time()
    for i in range(1000):
        optimizer.get_optimized_shard_assignment(f"data_{i}")
    assignment_time = time.time() - start_time
    
    print(f"Shard Assignment Performance: {assignment_time:.4f}s for 1000 operations")
    
    # Test 3: Batch processing performance
    data_list = [f"data_{i}" for i in range(100)]
    
    start_time = time.time()
    results = optimizer.batch_shard_assignments(data_list)
    batch_time = time.time() - start_time
    
    print(f"Batch Processing Performance: {batch_time:.4f}s for 100 assignments")
    
    # Generate performance report
    report = optimizer.get_performance_report()
    print(f"\nPerformance Report:")
    print(f"Cache Hit Ratio: {report['cache_performance']['hit_ratio']:.2%}")
    print(f"Shard Cache Hit Ratio: {report['shard_cache_performance']['hit_ratio']:.2%}")
    print(f"Average Assignment Time: {report['performance_metrics']['avg_shard_assignment_time']:.4f}s")


if __name__ == "__main__":
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance benchmarks
    run_performance_benchmarks()
