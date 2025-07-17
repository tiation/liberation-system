#!/usr/bin/env python3
"""
Demo script for the Automated Scalability System
"""

import sys
import os
import asyncio
import logging
import math
import random
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    from Mesh_Network.Advanced_Node_Discovery import AdvancedMeshNode, NetworkMetrics, GeoLocation, NodeType, NodeCapabilities
    from Mesh_Network.Sharding_Strategy import ShardingStrategy
    from Adaptive_Strategies import AdaptiveCapacityManager, AdaptiveConfiguration, AdaptiveStrategy
    from Automated_Scalability_System import AutomatedScalabilitySystem
    
    print("✅ All imports successful!")
    
    async def demo_automated_scalability():
        """Demo the complete automated scalability system"""
        print("\n🌐 LIBERATION SYSTEM - AUTOMATED SCALABILITY DEMO")
        print("=" * 60)
        print("🚀 Initializing predictive scaling system...")
        print()
        
        # Create sharding strategy
        sharding_strategy = ShardingStrategy(total_shards=16, replication_factor=2)
        
        # Create test nodes
        test_nodes = []
        for i in range(1, 4):
            node = AdvancedMeshNode(
                id=f"demo_node_{i}",
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
        
        print(f"✅ System initialized with {len(test_nodes)} nodes")
        
        # Create automated scalability system
        config = AdaptiveConfiguration(
            strategy=AdaptiveStrategy.HYBRID,
            history_window=1,  # 1 hour for demo
            prediction_horizon=30,  # 30 minutes
        )
        
        scalability_system = AutomatedScalabilitySystem(
            sharding_strategy=sharding_strategy,
            config=config,
            monitoring_interval=3  # 3 seconds for demo
        )
        
        print(f"🧠 Strategy: {config.strategy.value}")
        print(f"⏱️  Monitoring interval: {scalability_system.monitoring_interval} seconds")
        print()
        
        # Simulate some historical data first
        print("📊 Simulating historical data collection...")
        capacity_manager = scalability_system.capacity_manager
        
        for i in range(20):  # Simulate 20 data points
            for node in test_nodes:
                # Simulate varying load patterns
                time_factor = i / 5.0
                daily_cycle = 20 * abs(math.sin(time_factor * 0.5))
                random_variation = random.uniform(-10, 10)
                
                # Update node metrics
                node.metrics.cpu_usage = max(0, min(100, 50 + daily_cycle + random_variation))
                node.metrics.memory_usage = max(0, min(100, 40 + daily_cycle * 0.8 + random_variation * 0.5))
                node.metrics.network_load = max(0, min(100, 60 + daily_cycle * 1.2 + random_variation))
                
                # Collect performance data
                await capacity_manager.collect_performance_data(node)
            
            await asyncio.sleep(0.01)  # Small delay
        
        print(f"✅ Generated historical data for pattern detection")
        print()
        
        # Start system for a short demo
        print("🔄 Starting automated scalability system...")
        print("   (Running for 15 seconds for demonstration)")
        print()
        
        # Start the system
        system_task = asyncio.create_task(scalability_system.start())
        
        # Let it run for 15 seconds
        await asyncio.sleep(15)
        
        # Stop the system
        await scalability_system.stop()
        
        # Show results
        print("\n📊 SYSTEM PERFORMANCE SUMMARY")
        print("=" * 60)
        
        status = scalability_system.get_system_status()
        
        if "system_metrics" in status:
            metrics = status["system_metrics"]
            print(f"🏗️  Total Nodes: {metrics['total_nodes']}")
            print(f"✅ Active Nodes: {metrics['active_nodes']}")
            print(f"💻 Average CPU: {metrics['average_cpu']:.1f}%")
            print(f"🧠 Average Memory: {metrics['average_memory']:.1f}%")
            print(f"🌐 Average Network: {metrics['average_network']:.1f}%")
            print(f"🔗 Total Connections: {metrics['total_connections']}")
            print(f"💚 System Health: {metrics['system_health']:.2f}")
            print(f"🎯 Prediction Accuracy: {metrics['prediction_accuracy']:.2f}")
            
            print(f"\n🔄 Current Strategy: {status['current_strategy']}")
            print(f"📈 Recent Scaling Decisions: {len(status['recent_decisions'])}")
            
            for decision in status['recent_decisions']:
                print(f"  • {decision['node_id']}: {decision['action']} - {decision['rationale']}")
        
        # Export performance data
        scalability_system.export_performance_data("demo_scalability_performance.json")
        
        print("\n🎉 Automated Scalability System Demo Complete!")
        print("✨ System successfully demonstrated predictive scaling capabilities")
        print("📁 Performance data exported to demo_scalability_performance.json")
        
        return True
        
    # Run the demo
    if asyncio.run(demo_automated_scalability()):
        print("\n✅ Demo completed successfully!")
    else:
        print("\n❌ Demo failed!")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required modules are available")
except Exception as e:
    print(f"❌ Error during demo: {e}")
    import traceback
    traceback.print_exc()
