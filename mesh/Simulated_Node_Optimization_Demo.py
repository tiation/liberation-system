#!/usr/bin/env python3
"""
Simulated Node Optimization Demo
Creates mock nodes to demonstrate the full optimization and monitoring functionality
"""

import asyncio
import logging
import time
import random
from datetime import datetime
from typing import Dict, List, Any

# Import our advanced discovery system
from Mesh_Network.Advanced_Node_Discovery import (
    AdvancedNodeDiscovery,
    AdvancedMeshNode,
    NodeType,
    NetworkMetrics,
    GeoLocation
)

# Import dynamic load balancer
from Dynamic_Load_Balancer import LoadBalancer

class MockNodeFactory:
    """Factory to create mock nodes for testing"""
    
    def __init__(self):
        self.cities = [
            ("New York", "US", 40.7128, -74.0060),
            ("London", "UK", 51.5074, -0.1278),
            ("Tokyo", "JP", 35.6762, 139.6503),
            ("Sydney", "AU", -33.8688, 151.2093),
            ("São Paulo", "BR", -23.5505, -46.6333),
            ("Mumbai", "IN", 19.0760, 72.8777),
            ("Berlin", "DE", 52.5200, 13.4050),
            ("Toronto", "CA", 43.6532, -79.3832),
            ("Singapore", "SG", 1.3521, 103.8198),
            ("Dubai", "AE", 25.2048, 55.2708)
        ]
        self.node_counter = 0
    
    def create_mock_node(self, node_type: NodeType = NodeType.STANDARD) -> AdvancedMeshNode:
        """Create a mock node with realistic data"""
        self.node_counter += 1
        
        # Select random city
        city_name, country, lat, lon = random.choice(self.cities)
        
        # Create realistic metrics
        metrics = NetworkMetrics(
            latency=random.uniform(10, 500),  # 10-500ms
            bandwidth=random.uniform(10, 1000),  # 10-1000 Mbps
            packet_loss=random.uniform(0, 5),  # 0-5%
            jitter=random.uniform(1, 50),  # 1-50ms
            uptime=random.uniform(95, 100),  # 95-100%
            cpu_usage=random.uniform(10, 80),  # 10-80%
            memory_usage=random.uniform(20, 90),  # 20-90%
            network_load=random.uniform(5, 70),  # 5-70%
            last_updated=datetime.now()
        )
        
        # Create geolocation
        location = GeoLocation(
            latitude=lat + random.uniform(-0.1, 0.1),
            longitude=lon + random.uniform(-0.1, 0.1),
            city=city_name,
            country=country,
            region=f"{city_name} Region",
            timezone=f"UTC{random.randint(-12, 12)}",
            isp=f"ISP-{random.randint(1, 100)}"
        )
        
        # Create node
        node = AdvancedMeshNode(
            id=f"mock_node_{self.node_counter:03d}",
            host=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            port=8000 + self.node_counter,
            node_type=node_type,
            location=location,
            metrics=metrics,
            last_seen=time.time(),
            status="active",
            trust_score=random.uniform(0.7, 1.0)
        )
        
        # Add some mock connections
        if random.random() > 0.3:  # 70% chance of having connections
            for i in range(random.randint(1, 3)):
                conn_id = f"connection_{random.randint(1000, 9999)}"
                node.connections[conn_id] = {
                    "host": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    "port": random.randint(8000, 9000),
                    "status": random.choice(["connected", "connecting", "disconnected"]),
                    "last_ping": time.time() - random.randint(0, 300)
                }
        
        return node

class SimulatedOptimizationDemo:
    """Enhanced demo with simulated nodes"""
    
    def __init__(self):
        self.discovery = AdvancedNodeDiscovery()
        self.load_balancer = LoadBalancer(self.discovery)
        self.factory = MockNodeFactory()
        self.logger = logging.getLogger(__name__)
        
    async def populate_mock_nodes(self, count: int = 15):
        """Populate the network with mock nodes"""
        print(f"🏗️  Creating {count} mock nodes...")
        
        node_types = [NodeType.STANDARD, NodeType.RELAY, NodeType.STORAGE, NodeType.COMPUTE, NodeType.GATEWAY]
        
        for i in range(count):
            node_type = random.choice(node_types)
            node = self.factory.create_mock_node(node_type)
            self.discovery.discovered_nodes[node.id] = node
            
            print(f"  ✅ Created {node.id} - {node.location.city}, {node.location.country} "
                  f"({node_type.value})")
        
        print(f"📊 Network populated with {len(self.discovery.discovered_nodes)} nodes")
    
    async def run_comprehensive_demo(self):
        """Run comprehensive optimization demonstration"""
        print("🚀 Starting Comprehensive Node Optimization Demo")
        print("=" * 70)
        
        # Populate network with mock nodes
        await self.populate_mock_nodes(20)
        
        # Create local node
        local_node = AdvancedMeshNode(
            id="local_gateway_node",
            host="127.0.0.1",
            port=8000,
            node_type=NodeType.GATEWAY,
            location=GeoLocation(37.7749, -122.4194, "San Francisco", "US"),
            metrics=NetworkMetrics(
                latency=5.0,
                bandwidth=1000.0,
                uptime=99.9,
                cpu_usage=25.0,
                memory_usage=40.0,
                network_load=30.0
            )
        )
        
        # Add local node to discovered nodes
        self.discovery.discovered_nodes[local_node.id] = local_node
        
        # Phase 1: Network Analysis
        print("\n📊 Phase 1: Network Analysis")
        print("-" * 50)
        
        topology = self.discovery.get_network_topology()
        print(f"🌐 Network Topology:")
        print(f"   Total Nodes: {topology['total_nodes']}")
        print(f"   Average Latency: {topology['average_latency']:.2f}ms")
        print(f"   Network Health: {topology['network_health']:.3f}")
        print(f"   Regions: {len(topology['nodes_by_region'])}")
        
        # Display regional breakdown
        for region, nodes in topology['nodes_by_region'].items():
            avg_quality = sum(node['quality_score'] for node in nodes) / len(nodes)
            print(f"   📍 {region}: {len(nodes)} nodes (avg quality: {avg_quality:.3f})")
        
        # Phase 2: Node Optimization
        print("\n⚡ Phase 2: Node Connection Optimization")
        print("-" * 50)
        
        candidates = list(self.discovery.discovered_nodes.values())
        optimized_nodes = await self.discovery._optimize_node_selection(local_node, candidates)
        
        print(f"🎯 Optimized {len(optimized_nodes)} connections:")
        for i, node in enumerate(optimized_nodes, 1):
            score = await self.discovery._calculate_node_score(local_node, node)
            distance = local_node.location.distance_to(node.location)
            print(f"  {i:2d}. {node.id} - {node.location.city}, {node.location.country}")
            print(f"      Score: {score:.3f}, Distance: {distance:.0f}km, "
                  f"Latency: {node.metrics.latency:.1f}ms, "
                  f"Quality: {node.metrics.calculate_quality_score():.3f}")
        
        # Phase 3: Replication Monitoring
        print("\n🔄 Phase 3: Replication and Sharding Analysis")
        print("-" * 50)
        
        # Create replication monitor
        from Node_Optimization_Demo import ReplicationShardingMonitor
        monitor = ReplicationShardingMonitor(self.discovery)
        
        # Monitor replication health
        replication_health = await monitor.monitor_replication_health()
        print(f"📊 Replication Health: {replication_health['health_score']:.2f}")
        print(f"   Active Replicas: {replication_health['active_replicas']}")
        print(f"   Replication Factor: {replication_health['replication_factor']}")
        
        # Monitor shard distribution
        shard_distribution = await monitor.monitor_shard_distribution()
        print(f"🗂️  Shard Distribution: {shard_distribution['shard_balance']:.2f}")
        print(f"   Assigned Shards: {shard_distribution['assigned_shards']}")
        print(f"   Total Shards: {shard_distribution['total_shards']}")
        
        # Show shard assignments
        if shard_distribution['shard_assignments']:
            print("   📋 Shard Assignments:")
            for shard_id, assignment in shard_distribution['shard_assignments'].items():
                print(f"      {shard_id}: {assignment['node_id']} "
                      f"({assignment['region']}, quality: {assignment['quality_score']:.3f})")
        
        # Phase 4: Load Balancing
        print("\n⚖️  Phase 4: Dynamic Load Balancing")
        print("-" * 50)
        
        # Update load balancer with current nodes
        nodes_list = list(self.discovery.discovered_nodes.values())
        await self.load_balancer.distribute_load(nodes_list)
        
        # Show load distribution
        print("📈 Load Distribution:")
        for node_id, load_metric in self.load_balancer.load_metrics.items():
            node = self.discovery.discovered_nodes.get(node_id)
            if node:
                print(f"   {node.id}: {load_metric.current_load:.1f}% load, "
                      f"{load_metric.connections} connections")
        
        # Phase 5: Performance Optimization
        print("\n🚀 Phase 5: Performance Optimization")
        print("-" * 50)
        
        # Optimize for replication and sharding
        optimization_results = await monitor.optimize_for_replication_sharding(local_node)
        
        print(f"🔧 Optimizations Applied: {optimization_results['optimizations_applied']}")
        
        if optimization_results['performance_improvements']:
            improvements = optimization_results['performance_improvements']
            print(f"📈 Performance Improvements:")
            print(f"   Network Health Change: {improvements['network_health_change']:+.3f}")
            print(f"   Average Latency Change: {improvements['average_latency_change']:+.2f}ms")
            print(f"   Total Connections: {improvements['total_connections']}")
        
        # Phase 6: Quality Assessment
        print("\n📊 Phase 6: Network Quality Assessment")
        print("-" * 50)
        
        # Calculate network statistics
        total_nodes = len(self.discovery.discovered_nodes)
        high_quality_nodes = sum(1 for node in self.discovery.discovered_nodes.values() 
                                if node.metrics.calculate_quality_score() > 0.7)
        low_latency_nodes = sum(1 for node in self.discovery.discovered_nodes.values() 
                               if node.metrics.latency < 100)
        
        print(f"🎯 Network Quality Metrics:")
        print(f"   Total Nodes: {total_nodes}")
        print(f"   High Quality Nodes (>0.7): {high_quality_nodes} ({high_quality_nodes/total_nodes*100:.1f}%)")
        print(f"   Low Latency Nodes (<100ms): {low_latency_nodes} ({low_latency_nodes/total_nodes*100:.1f}%)")
        
        # Regional quality breakdown
        print("   📍 Regional Quality:")
        for region, nodes in topology['nodes_by_region'].items():
            region_quality = sum(node['quality_score'] for node in nodes) / len(nodes)
            region_latency = sum(node['latency'] for node in nodes) / len(nodes)
            print(f"      {region}: Quality {region_quality:.3f}, "
                  f"Avg Latency {region_latency:.1f}ms")
        
        # Phase 7: Final Recommendations
        print("\n💡 Phase 7: Optimization Recommendations")
        print("-" * 50)
        
        recommendations = []
        
        # Analyze and provide recommendations
        if replication_health['health_score'] < 0.8:
            recommendations.append("🔄 Increase replication factor or add more nodes for better fault tolerance")
        
        if shard_distribution['shard_balance'] < 0.9:
            recommendations.append("🗂️  Improve shard distribution across regions")
        
        if topology['network_health'] < 0.7:
            recommendations.append("📊 Improve overall network health by upgrading low-quality nodes")
        
        if topology['average_latency'] > 200:
            recommendations.append("⚡ Optimize routing to reduce average network latency")
        
        if not recommendations:
            recommendations.append("✅ Network is well-optimized!")
        
        print("📋 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        print("\n🎯 Comprehensive Optimization Demo Complete!")
        print("=" * 70)
        
        return {
            "total_nodes": total_nodes,
            "optimized_connections": len(optimized_nodes),
            "replication_health": replication_health,
            "shard_distribution": shard_distribution,
            "network_topology": topology,
            "recommendations": recommendations
        }

async def main():
    """Main demonstration function"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        demo = SimulatedOptimizationDemo()
        results = await demo.run_comprehensive_demo()
        
        print(f"\n📊 Demo Results Summary:")
        print(f"   Nodes Created: {results['total_nodes']}")
        print(f"   Optimized Connections: {results['optimized_connections']}")
        print(f"   Replication Health: {results['replication_health']['health_score']:.2f}")
        print(f"   Shard Balance: {results['shard_distribution']['shard_balance']:.2f}")
        print(f"   Network Health: {results['network_topology']['network_health']:.3f}")
        print(f"   Recommendations: {len(results['recommendations'])}")
        
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        logging.error(f"Demo error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
