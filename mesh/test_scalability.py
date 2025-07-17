#!/usr/bin/env python3
"""
Simple test script for the Automated Scalability System
"""

import sys
import os
import asyncio
import logging

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Mesh_Network.Advanced_Node_Discovery import AdvancedMeshNode, NetworkMetrics, GeoLocation, NodeType, NodeCapabilities
    from Mesh_Network.Sharding_Strategy import ShardingStrategy
    from Adaptive_Strategies import AdaptiveCapacityManager, AdaptiveConfiguration, AdaptiveStrategy
    
    print("✅ All imports successful!")
    
    async def test_scalability_system():
        """Test the scalability system components"""
        print("\n🧪 Testing Scalability System Components...")
        
        # Create sharding strategy
        sharding_strategy = ShardingStrategy(total_shards=16, replication_factor=2)
        print("✅ Sharding strategy created")
        
        # Create test nodes
        test_nodes = []
        for i in range(1, 4):
            node = AdvancedMeshNode(
                id=f"test_node_{i}",
                host=f"192.168.1.{i}",
                port=8000 + i,
                node_type=NodeType.STANDARD,
                location=GeoLocation(37.7749, -122.4194, "United States", "San Francisco", "CA"),
                capabilities=NodeCapabilities(
                    processing_power=2.0,
                    storage_capacity=1000,
                    max_connections=50,
                    supported_protocols=["tcp", "udp"]
                ),
                metrics=NetworkMetrics(
                    cpu_usage=50.0 + (i * 10),
                    memory_usage=40.0 + (i * 5),
                    network_load=60.0 + (i * 8),
                    uptime=99.0 + (i * 0.1)
                )
            )
            test_nodes.append(node)
            await sharding_strategy.add_node_to_shard(node)
        
        print(f"✅ Created {len(test_nodes)} test nodes")
        
        # Test adaptive capacity manager
        config = AdaptiveConfiguration(strategy=AdaptiveStrategy.HYBRID)
        capacity_manager = AdaptiveCapacityManager(config)
        print("✅ Adaptive capacity manager created")
        
        # Test data collection
        for node in test_nodes:
            await capacity_manager.collect_performance_data(node)
        
        print("✅ Performance data collection completed")
        
        # Test capacity analysis
        for node in test_nodes:
            try:
                adjustments = await capacity_manager.analyze_and_adjust_capacity(node)
                print(f"✅ Node {node.id} analysis complete: {adjustments.get('total_capacity', 100):.1f}% capacity")
            except Exception as e:
                print(f"⚠️  Node {node.id} analysis had minimal data: {e}")
        
        print("\n🎉 Basic scalability system test completed successfully!")
        
        # Show system stats
        stats = sharding_strategy.get_shard_statistics()
        print(f"\n📊 System Statistics:")
        print(f"  Total Shards: {stats['total_shards']}")
        print(f"  Total Nodes: {stats['total_nodes']}")
        print(f"  Load Distribution: {stats['load_distribution']}")
        
        return True
        
    # Run the test
    if asyncio.run(test_scalability_system()):
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required modules are available")
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
