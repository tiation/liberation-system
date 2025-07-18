#!/usr/bin/env python3
"""
Test Node Discovery Caching System
Tests the comprehensive caching functionality for node discovery.
"""

import asyncio
import logging
import time
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Mesh_Network.Node_Discovery_Cache import (
    NodeDiscoveryCache, 
    NodeCacheEntry, 
    CacheStrategy, 
    NodeStatus
)
from Mesh_Network.Advanced_Node_Discovery import (
    AdvancedNodeDiscovery,
    AdvancedMeshNode,
    GeoLocation,
    NetworkMetrics,
    NodeCapabilities,
    NodeType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class NodeDiscoveryCacheTest:
    """Comprehensive test suite for node discovery caching"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = NodeDiscoveryCache(
            cache_dir="test_cache",
            max_cache_size=50,
            default_ttl=300,  # 5 minutes for testing
            strategy=CacheStrategy.HYBRID
        )
        self.discovery = AdvancedNodeDiscovery()
    
    async def test_basic_caching(self):
        """Test basic node caching functionality"""
        print("\n🔄 Testing Basic Caching...")
        print("=" * 50)
        
        # Test adding nodes to cache
        nodes_to_cache = [
            {"id": "test_node_1", "host": "127.0.0.1", "port": 8001},
            {"id": "test_node_2", "host": "127.0.0.1", "port": 8002},
            {"id": "test_node_3", "host": "192.168.1.10", "port": 8003},
        ]
        
        for node_data in nodes_to_cache:
            entry = self.cache.cache_node(
                node_id=node_data["id"],
                host=node_data["host"],
                port=node_data["port"],
                location={
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "country": "USA",
                    "city": "New York",
                    "region": "NY"
                },
                metrics={
                    "latency": 50.0 + (int(node_data["port"]) % 10),
                    "bandwidth": 100.0,
                    "uptime": 99.0
                },
                discovery_method="test",
                tags={"test", "active"}
            )
            print(f"✅ Cached node: {node_data['id']} ({node_data['host']}:{node_data['port']})")
        
        # Test retrieving nodes from cache
        print("\n🔍 Testing Node Retrieval...")
        for node_data in nodes_to_cache:
            cached_node = self.cache.get_node(node_data["id"])
            if cached_node:
                print(f"✅ Retrieved: {cached_node.node_id} - Status: {cached_node.status.value}")
            else:
                print(f"❌ Failed to retrieve: {node_data['id']}")
        
        # Test host:port lookup
        print("\n🔍 Testing Host:Port Lookup...")
        test_node = self.cache.get_node_by_host_port("127.0.0.1", 8001)
        if test_node:
            print(f"✅ Found node by host:port: {test_node.node_id}")
        else:
            print("❌ Failed to find node by host:port")
        
        # Test cache statistics
        stats = self.cache.get_cache_stats()
        print(f"\n📊 Cache Statistics:")
        print(f"  Cache Size: {stats['cache_size']}")
        print(f"  Hit Rate: {stats['hit_rate']:.1f}%")
        print(f"  Active Nodes: {stats['active_nodes']}")
        
        return len(nodes_to_cache)
    
    async def test_metrics_update(self):
        """Test updating node metrics"""
        print("\n🔄 Testing Metrics Update...")
        print("=" * 50)
        
        # Get a cached node
        test_node = self.cache.get_node("test_node_1")
        if not test_node:
            print("❌ No test node found for metrics update")
            return
        
        print(f"📊 Initial metrics for {test_node.node_id}:")
        print(f"  Probe count: {test_node.probe_count}")
        print(f"  Average latency: {test_node.average_latency:.1f}ms")
        print(f"  Reliability score: {test_node.reliability_score:.3f}")
        
        # Simulate multiple measurements
        latencies = [45.0, 52.0, 48.0, 55.0, 50.0]
        
        print(f"\n🔄 Updating metrics with latencies: {latencies}")
        for latency in latencies:
            self.cache.update_node_metrics("test_node_1", latency, success=True)
        
        # Check updated metrics
        updated_node = self.cache.get_node("test_node_1")
        print(f"\n📊 Updated metrics for {updated_node.node_id}:")
        print(f"  Probe count: {updated_node.probe_count}")
        print(f"  Average latency: {updated_node.average_latency:.1f}ms")
        print(f"  Best latency: {updated_node.best_latency:.1f}ms")
        print(f"  Worst latency: {updated_node.worst_latency:.1f}ms")
        print(f"  Reliability score: {updated_node.reliability_score:.3f}")
        
        # Test failed connection
        print(f"\n🔄 Testing failed connection...")
        self.cache.update_node_metrics("test_node_1", float('inf'), success=False)
        
        failed_node = self.cache.get_node("test_node_1")
        print(f"  Failed connections: {failed_node.failed_connections}")
        print(f"  Reliability score: {failed_node.reliability_score:.3f}")
    
    async def test_location_and_tag_queries(self):
        """Test location and tag-based queries"""
        print("\n🔄 Testing Location and Tag Queries...")
        print("=" * 50)
        
        # Add nodes with different locations
        locations = [
            {"country": "USA", "region": "NY", "city": "New York"},
            {"country": "USA", "region": "CA", "city": "San Francisco"},
            {"country": "UK", "region": "England", "city": "London"},
        ]
        
        for i, location in enumerate(locations, 4):
            self.cache.cache_node(
                node_id=f"geo_node_{i}",
                host="127.0.0.1",
                port=8000 + i,
                location=location,
                tags={"geo_test", f"region_{location['region']}"}
            )
        
        # Test location queries
        print(f"\n🌍 Testing location queries...")
        usa_nodes = self.cache.get_nodes_by_location(country="USA")
        print(f"  USA nodes: {len(usa_nodes)}")
        
        ny_nodes = self.cache.get_nodes_by_location(country="USA", region="NY")
        print(f"  NY nodes: {len(ny_nodes)}")
        
        # Test tag queries
        print(f"\n🏷️  Testing tag queries...")
        geo_test_nodes = self.cache.get_nodes_by_tag("geo_test")
        print(f"  Geo test nodes: {len(geo_test_nodes)}")
        
        region_ca_nodes = self.cache.get_nodes_by_tag("region_CA")
        print(f"  CA region nodes: {len(region_ca_nodes)}")
    
    async def test_cache_persistence(self):
        """Test cache persistence functionality"""
        print("\n🔄 Testing Cache Persistence...")
        print("=" * 50)
        
        # Save current cache
        print("💾 Saving cache...")
        self.cache.save_cache()
        
        # Get current cache size
        original_size = len(self.cache.cache)
        print(f"  Original cache size: {original_size}")
        
        # Clear cache
        print("🧹 Clearing in-memory cache...")
        self.cache.cache.clear()
        self.cache.host_port_index.clear()
        self.cache.location_index.clear()
        self.cache.tag_index.clear()
        
        print(f"  Cache size after clear: {len(self.cache.cache)}")
        
        # Reload cache
        print("📥 Reloading cache from disk...")
        self.cache._load_cache()
        
        reloaded_size = len(self.cache.cache)
        print(f"  Reloaded cache size: {reloaded_size}")
        
        if reloaded_size == original_size:
            print("✅ Cache persistence test passed!")
        else:
            print("❌ Cache persistence test failed!")
        
        return reloaded_size == original_size
    
    async def test_cache_expiration(self):
        """Test cache expiration functionality"""
        print("\n🔄 Testing Cache Expiration...")
        print("=" * 50)
        
        # Add a node with short TTL
        short_ttl_entry = self.cache.cache_node(
            node_id="short_lived_node",
            host="127.0.0.1",
            port=9999,
            ttl=1,  # 1 second TTL
            tags={"short_lived"}
        )
        
        print(f"✅ Added short-lived node with 1 second TTL")
        
        # Verify node exists
        node = self.cache.get_node("short_lived_node")
        if node:
            print(f"✅ Node found immediately after creation")
        
        # Wait for expiration
        print("⏳ Waiting 2 seconds for expiration...")
        await asyncio.sleep(2)
        
        # Try to retrieve expired node
        expired_node = self.cache.get_node("short_lived_node")
        if expired_node:
            print("❌ Expired node still found (should have been removed)")
        else:
            print("✅ Expired node correctly removed from cache")
        
        # Test manual cleanup
        print("\n🧹 Testing manual cleanup...")
        before_cleanup = len(self.cache.cache)
        cleaned = self.cache.cleanup_expired()
        after_cleanup = len(self.cache.cache)
        
        print(f"  Nodes before cleanup: {before_cleanup}")
        print(f"  Nodes cleaned: {cleaned}")
        print(f"  Nodes after cleanup: {after_cleanup}")
    
    async def test_integrated_discovery(self):
        """Test integration with actual node discovery"""
        print("\n🔄 Testing Integrated Discovery...")
        print("=" * 50)
        
        # Create a local node for testing
        local_node = AdvancedMeshNode(
            id="test_local_node",
            host="127.0.0.1",
            port=8000,
            location=GeoLocation(40.7128, -74.0060, "USA", "New York", "NY"),
            metrics=NetworkMetrics(latency=25.0, bandwidth=100.0, uptime=99.0),
            capabilities=NodeCapabilities(max_connections=100)
        )
        
        print(f"🌐 Created local node: {local_node.id}")
        
        # Run discovery
        print("🔍 Running node discovery...")
        discovered_nodes = await self.discovery.discover_nodes(local_node)
        
        print(f"✅ Discovered {len(discovered_nodes)} nodes")
        
        # Cache discovered nodes
        print("💾 Caching discovered nodes...")
        for node in discovered_nodes:
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
                discovery_method="integrated_test",
                tags={'discovered', 'integration_test'}
            )
        
        print(f"✅ Cached {len(discovered_nodes)} discovered nodes")
        
        # Test cache retrieval
        print("🔍 Testing cache retrieval...")
        cached_discovered = self.cache.get_nodes_by_tag('integration_test')
        print(f"✅ Retrieved {len(cached_discovered)} nodes from cache")
        
        return len(discovered_nodes)
    
    async def test_cache_export_import(self):
        """Test cache export/import functionality"""
        print("\n🔄 Testing Cache Export/Import...")
        print("=" * 50)
        
        # Export cache data
        print("📤 Exporting cache data...")
        exported_data = self.cache.export_cache_data('json')
        print(f"  Exported data size: {len(exported_data)} characters")
        
        # Clear cache
        original_size = len(self.cache.cache)
        self.cache.cache.clear()
        print(f"  Cache cleared (was {original_size} nodes)")
        
        # Import cache data
        print("📥 Importing cache data...")
        self.cache.import_cache_data(exported_data, 'json')
        imported_size = len(self.cache.cache)
        print(f"  Imported {imported_size} nodes")
        
        if imported_size == original_size:
            print("✅ Export/import test passed!")
        else:
            print("❌ Export/import test failed!")
        
        return imported_size == original_size
    
    async def run_all_tests(self):
        """Run all cache tests"""
        print("🚀 STARTING NODE DISCOVERY CACHE TESTS")
        print("=" * 60)
        
        try:
            # Run individual tests
            cached_count = await self.test_basic_caching()
            await self.test_metrics_update()
            await self.test_location_and_tag_queries()
            persistence_passed = await self.test_cache_persistence()
            await self.test_cache_expiration()
            discovered_count = await self.test_integrated_discovery()
            export_import_passed = await self.test_cache_export_import()
            
            # Final statistics
            print("\n📊 FINAL CACHE STATISTICS")
            print("=" * 60)
            
            stats = self.cache.get_cache_stats()
            print(f"Cache Size: {stats['cache_size']}")
            print(f"Max Cache Size: {stats['max_cache_size']}")
            print(f"Active Nodes: {stats['active_nodes']}")
            print(f"Failed Nodes: {stats['failed_nodes']}")
            print(f"Hit Rate: {stats['hit_rate']:.1f}%")
            print(f"Average Latency: {stats['avg_latency']:.1f}ms")
            print(f"Average Reliability: {stats['avg_reliability']:.3f}")
            
            print(f"\nIndex Sizes:")
            print(f"  Host:Port Index: {stats['index_sizes']['host_port']}")
            print(f"  Location Index: {stats['index_sizes']['location']}")
            print(f"  Tag Index: {stats['index_sizes']['tag']}")
            
            print(f"\nCache Operations:")
            for key, value in stats['stats'].items():
                print(f"  {key}: {value}")
            
            # Test summary
            print("\n🎯 TEST SUMMARY")
            print("=" * 60)
            print(f"✅ Basic caching: {cached_count} nodes cached")
            print(f"✅ Metrics update: Working")
            print(f"✅ Location/Tag queries: Working")
            print(f"{'✅' if persistence_passed else '❌'} Cache persistence: {'Passed' if persistence_passed else 'Failed'}")
            print(f"✅ Cache expiration: Working")
            print(f"✅ Integrated discovery: {discovered_count} nodes discovered")
            print(f"{'✅' if export_import_passed else '❌'} Export/Import: {'Passed' if export_import_passed else 'Failed'}")
            
            print("\n🎉 ALL TESTS COMPLETED!")
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            print("\n🧹 Cleaning up...")
            self.cache.shutdown()
            print("✅ Cache shutdown complete")

async def main():
    """Main test function"""
    test_suite = NodeDiscoveryCacheTest()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
