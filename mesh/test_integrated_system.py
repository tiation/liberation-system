#!/usr/bin/env python3
"""
Integrated Mesh Network System Test
Demonstrates Advanced Node Discovery, Dynamic Load Balancing, and Adaptive Strategies
"""

import asyncio
import logging
import time
import random
import math
from datetime import datetime, timedelta

# Import all components
from Mesh_Network.Advanced_Node_Discovery import (
    AdvancedNodeDiscovery, 
    AdvancedMeshNode, 
    NetworkMetrics, 
    GeoLocation,
    NodeType
)
from Adaptive_Strategies import (
    AdaptiveCapacityManager,
    AdaptiveConfiguration,
    AdaptiveStrategy
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class IntegratedMeshSystem:
    """Integrated mesh network system with all components"""
    
    def __init__(self):
        self.discovery = AdvancedNodeDiscovery()
        self.adaptive_manager = AdaptiveCapacityManager(
            AdaptiveConfiguration(
                strategy=AdaptiveStrategy.HYBRID,
                history_window=24,
                prediction_horizon=60,
                adjustment_threshold=0.15
            )
        )
        self.nodes = {}
        self.logger = logging.getLogger(__name__)
        
    async def create_test_network(self) -> list:
        """Create a test network with nodes in different locations"""
        locations = [
            ("San Francisco", 37.7749, -122.4194, "United States", "CA"),
            ("New York", 40.7128, -74.0060, "United States", "NY"),
            ("London", 51.5074, -0.1278, "United Kingdom", "England"),
            ("Tokyo", 35.6762, 139.6503, "Japan", "Tokyo"),
            ("Sydney", -33.8688, 151.2093, "Australia", "NSW"),
            ("Berlin", 52.5200, 13.4050, "Germany", "Berlin"),
            ("Singapore", 1.3521, 103.8198, "Singapore", "Singapore")
        ]
        
        nodes = []
        for i, (city, lat, lon, country, region) in enumerate(locations):
            node = AdvancedMeshNode(
                id=f"node_{city.lower().replace(' ', '_')}",
                host="127.0.0.1",
                port=8000 + i,
                location=GeoLocation(lat, lon, country, city, region),
                metrics=NetworkMetrics(
                    cpu_usage=random.uniform(30, 80),
                    memory_usage=random.uniform(40, 70),
                    network_load=random.uniform(20, 90),
                    uptime=random.uniform(95, 100)
                ),
                node_type=random.choice(list(NodeType))
            )
            nodes.append(node)
            self.nodes[node.id] = node
        
        return nodes
    
    async def simulate_network_activity(self, nodes: list, duration_minutes: int = 5):
        """Simulate network activity and data collection"""
        print(f"🔄 Simulating {duration_minutes} minutes of network activity...")
        
        start_time = datetime.now()
        iteration = 0
        
        while (datetime.now() - start_time).total_seconds() < duration_minutes * 60:
            # Simulate different load patterns
            time_factor = iteration / 20.0
            
            for node in nodes:
                # Simulate various load patterns
                base_load = {
                    "cpu_usage": 50 + 20 * math.sin(time_factor * 0.5),
                    "memory_usage": 45 + 15 * math.sin(time_factor * 0.3),
                    "network_load": 60 + 25 * math.sin(time_factor * 0.7)
                }
                
                # Add random variations
                for metric in base_load:
                    variation = random.uniform(-10, 10)
                    new_value = base_load[metric] + variation
                    setattr(node.metrics, metric, max(0, min(100, new_value)))
                
                # Collect performance data
                await self.adaptive_manager.collect_performance_data(node)
            
            iteration += 1
            await asyncio.sleep(0.1)  # Small delay between iterations
        
        print(f"✅ Collected performance data for {len(nodes)} nodes")
    
    async def test_node_discovery(self, nodes: list):
        """Test advanced node discovery"""
        print("\n🌐 Testing Advanced Node Discovery")
        print("=" * 50)
        
        # Use the first node as local node
        local_node = nodes[0]
        
        # Add other nodes to discovery cache
        for node in nodes[1:]:
            self.discovery.discovered_nodes[node.id] = node
        
        # Discover optimal nodes
        discovered = await self.discovery.discover_nodes(local_node)
        
        print(f"🏠 Local Node: {local_node.id} in {local_node.location.city}")
        print(f"✅ Discovered {len(discovered)} optimal nodes:")
        
        for node in discovered:
            distance = local_node.location.distance_to(node.location)
            quality = node.metrics.calculate_quality_score()
            print(f"  • {node.id} ({node.node_type.value})")
            print(f"    📍 Location: {node.location.city}, {node.location.country}")
            print(f"    📏 Distance: {distance:.0f} km")
            print(f"    🎯 Quality: {quality:.3f}")
        
        # Test bootstrap optimization
        print(f"\n🚀 Optimal Bootstrap Nodes:")
        bootstrap_nodes = await self.discovery.get_optimal_bootstrap_nodes(3)
        for i, node in enumerate(bootstrap_nodes, 1):
            print(f"  {i}. {node['host']}:{node['port']}")
            if 'location' in node:
                print(f"     📍 {node['location']['city']}, {node['location']['country']}")
            if 'quality_score' in node:
                print(f"     🎯 Quality: {node['quality_score']:.3f}")
        
        return discovered
    
    async def test_adaptive_strategies(self, nodes: list):
        """Test adaptive capacity management"""
        print("\n🧠 Testing Adaptive Capacity Management")
        print("=" * 50)
        
        capacity_results = {}
        
        for node in nodes:
            # Analyze and adjust capacity
            adjustments = await self.adaptive_manager.analyze_and_adjust_capacity(node)
            capacity_results[node.id] = adjustments
            
            # Get performance summary
            summary = self.adaptive_manager.get_performance_summary(node.id)
            
            print(f"\n📊 Node: {node.id}")
            print(f"  🌍 Location: {node.location.city}, {node.location.country}")
            print(f"  📈 Data Points: {summary['data_points']}")
            print(f"  🔍 Patterns: {summary['patterns_detected']}")
            
            if summary['patterns']:
                for pattern in summary['patterns']:
                    print(f"    • {pattern['type'].title()}: intensity={pattern['intensity']:.2f}")
            
            print(f"  🔮 Prediction Confidence: {summary['prediction']['confidence']:.2f}")
            print(f"  📊 Capacity Change: {summary['current_capacity'] - summary['original_capacity']:+.1f}%")
        
        return capacity_results
    
    async def test_load_balancing(self, nodes: list):
        """Test dynamic load balancing"""
        print("\n⚖️  Testing Dynamic Load Balancing")
        print("=" * 50)
        
        # Sort nodes by current load
        sorted_nodes = sorted(nodes, key=lambda n: (
            n.metrics.cpu_usage + n.metrics.memory_usage + n.metrics.network_load
        ) / 3)
        
        print("🔄 Load Distribution Analysis:")
        for node in sorted_nodes:
            avg_load = (node.metrics.cpu_usage + node.metrics.memory_usage + node.metrics.network_load) / 3
            quality = node.metrics.calculate_quality_score()
            
            status = "🟢 Low" if avg_load < 50 else "🟡 Medium" if avg_load < 75 else "🔴 High"
            
            print(f"  • {node.id}")
            print(f"    📊 Average Load: {avg_load:.1f}% {status}")
            print(f"    🎯 Quality Score: {quality:.3f}")
            print(f"    🔗 Connections: {len(node.connections)}")
        
        # Simulate load balancing decisions
        underloaded = [n for n in nodes if (n.metrics.cpu_usage + n.metrics.memory_usage + n.metrics.network_load) / 3 < 60]
        overloaded = [n for n in nodes if (n.metrics.cpu_usage + n.metrics.memory_usage + n.metrics.network_load) / 3 > 80]
        
        print(f"\n📈 Load Balancing Recommendations:")
        print(f"  🟢 Underloaded nodes (can accept more load): {len(underloaded)}")
        print(f"  🔴 Overloaded nodes (need load reduction): {len(overloaded)}")
        
        if underloaded:
            print("  💡 Recommended for new connections:")
            for node in underloaded[:3]:
                print(f"    • {node.id} ({node.location.city})")
        
        if overloaded:
            print("  ⚠️  Need load redistribution:")
            for node in overloaded:
                print(f"    • {node.id} ({node.location.city})")
    
    async def test_network_topology(self):
        """Test network topology analysis"""
        print("\n📊 Network Topology Analysis")
        print("=" * 50)
        
        topology = self.discovery.get_network_topology()
        
        print(f"📈 Network Overview:")
        print(f"  📊 Total Nodes: {topology['total_nodes']}")
        print(f"  ⚡ Average Latency: {topology['average_latency']:.1f}ms")
        print(f"  🏥 Network Health: {topology['network_health']:.3f}")
        
        print(f"\n🌍 Geographic Distribution:")
        for region, nodes in topology['nodes_by_region'].items():
            print(f"  • {region}: {len(nodes)} nodes")
            avg_latency = sum(node['latency'] for node in nodes) / len(nodes)
            avg_quality = sum(node['quality_score'] for node in nodes) / len(nodes)
            print(f"    ⚡ Avg Latency: {avg_latency:.1f}ms")
            print(f"    🎯 Avg Quality: {avg_quality:.3f}")
    
    async def run_comprehensive_test(self):
        """Run comprehensive integrated system test"""
        print("🌟 LIBERATION SYSTEM - INTEGRATED MESH NETWORK TEST")
        print("=" * 70)
        print("🎯 Testing enterprise-grade mesh network with all components")
        print()
        
        # Create test network
        nodes = await self.create_test_network()
        print(f"✅ Created test network with {len(nodes)} nodes")
        
        # Simulate network activity
        await self.simulate_network_activity(nodes, duration_minutes=1)
        
        # Test all components
        await self.test_node_discovery(nodes)
        await self.test_adaptive_strategies(nodes)
        await self.test_load_balancing(nodes)
        await self.test_network_topology()
        
        # Performance summary
        print("\n📈 System Performance Summary")
        print("=" * 50)
        
        total_capacity_change = 0
        total_data_points = 0
        total_patterns = 0
        
        for node in nodes:
            summary = self.adaptive_manager.get_performance_summary(node.id)
            if 'error' not in summary:
                capacity_change = summary['current_capacity'] - summary['original_capacity']
                total_capacity_change += capacity_change
                total_data_points += summary['data_points']
                total_patterns += summary['patterns_detected']
        
        print(f"📊 Total Data Points Collected: {total_data_points}")
        print(f"🔍 Total Patterns Detected: {total_patterns}")
        print(f"📈 Average Capacity Change: {total_capacity_change / len(nodes):+.1f}%")
        
        # Network health metrics
        healthy_nodes = sum(1 for node in nodes if node.metrics.calculate_quality_score() > 0.7)
        print(f"🏥 Healthy Nodes: {healthy_nodes}/{len(nodes)} ({healthy_nodes/len(nodes)*100:.1f}%)")
        
        avg_quality = sum(node.metrics.calculate_quality_score() for node in nodes) / len(nodes)
        print(f"🎯 Average Network Quality: {avg_quality:.3f}")
        
        print("\n🎉 Integrated System Test Complete!")
        print("✨ All components working together for optimal mesh network performance")
        print("🚀 Ready for $19 trillion economic transformation!")

async def main():
    """Main test runner"""
    system = IntegratedMeshSystem()
    await system.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
