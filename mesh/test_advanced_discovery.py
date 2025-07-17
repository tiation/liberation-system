#!/usr/bin/env python3
"""
Test Advanced Node Discovery System
Demonstrates geolocation and network metrics optimization
"""

import asyncio
import logging
import time
from Mesh_Network.Advanced_Node_Discovery import (
    AdvancedNodeDiscovery,
    AdvancedMeshNode,
    GeoLocation,
    NetworkMetrics,
    NodeCapabilities,
    NodeType
)

# Configure logging with dark theme colors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class TestAdvancedDiscovery:
    """Test suite for Advanced Node Discovery"""
    
    def __init__(self):
        self.discovery = AdvancedNodeDiscovery()
        self.logger = logging.getLogger(__name__)
        
    async def test_node_discovery(self):
        """Test advanced node discovery with geolocation"""
        print("\n🌐 Testing Advanced Node Discovery")
        print("=" * 50)
        
        # Create test nodes with different locations
        test_nodes = [
            AdvancedMeshNode(
                id="node_nyc",
                host="127.0.0.1",
                port=8000,
                location=GeoLocation(40.7128, -74.0060, "United States", "New York", "NY"),
                metrics=NetworkMetrics(latency=50.0, bandwidth=100.0, uptime=99.5),
                node_type=NodeType.GATEWAY
            ),
            AdvancedMeshNode(
                id="node_london",
                host="127.0.0.1", 
                port=8001,
                location=GeoLocation(51.5074, -0.1278, "United Kingdom", "London", "England"),
                metrics=NetworkMetrics(latency=80.0, bandwidth=150.0, uptime=99.8),
                node_type=NodeType.RELAY
            ),
            AdvancedMeshNode(
                id="node_tokyo",
                host="127.0.0.1",
                port=8002,
                location=GeoLocation(35.6762, 139.6503, "Japan", "Tokyo", "Tokyo"),
                metrics=NetworkMetrics(latency=120.0, bandwidth=200.0, uptime=99.9),
                node_type=NodeType.COMPUTE
            ),
            AdvancedMeshNode(
                id="node_sydney",
                host="127.0.0.1",
                port=8003,
                location=GeoLocation(-33.8688, 151.2093, "Australia", "Sydney", "NSW"),
                metrics=NetworkMetrics(latency=200.0, bandwidth=80.0, uptime=98.5),
                node_type=NodeType.STORAGE
            )
        ]
        
        # Add nodes to discovery cache
        for node in test_nodes:
            self.discovery.discovered_nodes[node.id] = node
        
        # Create local node
        local_node = AdvancedMeshNode(
            id="local_node",
            host="127.0.0.1",
            port=8100,
            location=GeoLocation(37.7749, -122.4194, "United States", "San Francisco", "CA"),
            metrics=NetworkMetrics(latency=0.0, bandwidth=1000.0, uptime=100.0)
        )
        
        print(f"🏠 Local Node: {local_node.id} in {local_node.location.city}, {local_node.location.country}")
        
        # Test node discovery
        discovered = await self.discovery.discover_nodes(local_node)
        
        print(f"\n✅ Discovered {len(discovered)} nodes:")
        for node in discovered:
            distance = local_node.location.distance_to(node.location)
            quality = node.metrics.calculate_quality_score()
            print(f"  • {node.id} ({node.node_type.value})")
            print(f"    📍 Location: {node.location.city}, {node.location.country}")
            print(f"    📏 Distance: {distance:.0f} km")
            print(f"    ⚡ Latency: {node.metrics.latency:.1f}ms")
            print(f"    🎯 Quality: {quality:.2f}")
            print(f"    🔧 Type: {node.node_type.value}")
            print()
        
        return discovered
    
    async def test_node_scoring(self):
        """Test node scoring algorithm"""
        print("\n🎯 Testing Node Scoring Algorithm")
        print("=" * 50)
        
        # Create local node
        local_node = AdvancedMeshNode(
            id="local_node",
            host="127.0.0.1",
            port=8100,
            location=GeoLocation(37.7749, -122.4194, "United States", "San Francisco", "CA")
        )
        
        # Test different candidate nodes
        candidates = [
            # High quality, close distance
            AdvancedMeshNode(
                id="node_optimal",
                host="127.0.0.1",
                port=8001,
                location=GeoLocation(37.7849, -122.4094, "United States", "San Francisco", "CA"),
                metrics=NetworkMetrics(latency=10.0, bandwidth=200.0, uptime=99.9),
                trust_score=1.0
            ),
            # Low quality, close distance
            AdvancedMeshNode(
                id="node_close_poor",
                host="127.0.0.1",
                port=8002,
                location=GeoLocation(37.7649, -122.4294, "United States", "San Francisco", "CA"),
                metrics=NetworkMetrics(latency=500.0, bandwidth=10.0, uptime=80.0),
                trust_score=0.5
            ),
            # High quality, far distance
            AdvancedMeshNode(
                id="node_far_good",
                host="127.0.0.1",
                port=8003,
                location=GeoLocation(35.6762, 139.6503, "Japan", "Tokyo", "Tokyo"),
                metrics=NetworkMetrics(latency=150.0, bandwidth=300.0, uptime=99.8),
                trust_score=1.0
            )
        ]
        
        print("📊 Node Scoring Results:")
        for candidate in candidates:
            score = await self.discovery._calculate_node_score(local_node, candidate)
            distance = local_node.location.distance_to(candidate.location)
            quality = candidate.metrics.calculate_quality_score()
            
            print(f"  • {candidate.id}")
            print(f"    🎯 Overall Score: {score:.3f}")
            print(f"    📏 Distance: {distance:.0f} km")
            print(f"    ⚡ Network Quality: {quality:.3f}")
            print(f"    🔒 Trust Score: {candidate.trust_score:.3f}")
            print(f"    📍 Location: {candidate.location.city}, {candidate.location.country}")
            print()
    
    async def test_bootstrap_optimization(self):
        """Test bootstrap node optimization"""
        print("\n🚀 Testing Bootstrap Node Optimization")
        print("=" * 50)
        
        # Create diverse set of nodes
        nodes = [
            AdvancedMeshNode(
                id="node_us_east",
                host="127.0.0.1",
                port=8001,
                location=GeoLocation(40.7128, -74.0060, "United States", "New York", "NY"),
                metrics=NetworkMetrics(latency=50.0, bandwidth=100.0, uptime=99.5)
            ),
            AdvancedMeshNode(
                id="node_us_west",
                host="127.0.0.1",
                port=8002,
                location=GeoLocation(37.7749, -122.4194, "United States", "San Francisco", "CA"),
                metrics=NetworkMetrics(latency=45.0, bandwidth=150.0, uptime=99.8)
            ),
            AdvancedMeshNode(
                id="node_europe",
                host="127.0.0.1",
                port=8003,
                location=GeoLocation(51.5074, -0.1278, "United Kingdom", "London", "England"),
                metrics=NetworkMetrics(latency=80.0, bandwidth=200.0, uptime=99.9)
            ),
            AdvancedMeshNode(
                id="node_asia",
                host="127.0.0.1",
                port=8004,
                location=GeoLocation(35.6762, 139.6503, "Japan", "Tokyo", "Tokyo"),
                metrics=NetworkMetrics(latency=120.0, bandwidth=180.0, uptime=99.7)
            ),
            AdvancedMeshNode(
                id="node_oceania",
                host="127.0.0.1",
                port=8005,
                location=GeoLocation(-33.8688, 151.2093, "Australia", "Sydney", "NSW"),
                metrics=NetworkMetrics(latency=200.0, bandwidth=120.0, uptime=99.2)
            )
        ]
        
        # Add to discovery cache
        for node in nodes:
            self.discovery.discovered_nodes[node.id] = node
        
        # Get optimal bootstrap nodes
        bootstrap_nodes = await self.discovery.get_optimal_bootstrap_nodes(3)
        
        print("🌟 Optimal Bootstrap Nodes:")
        for i, node in enumerate(bootstrap_nodes, 1):
            print(f"  {i}. {node['host']}:{node['port']}")
            if 'location' in node:
                print(f"     📍 Location: {node['location']['city']}, {node['location']['country']}")
            if 'quality_score' in node:
                print(f"     🎯 Quality: {node['quality_score']:.3f}")
            print()
    
    async def test_network_topology(self):
        """Test network topology analysis"""
        print("\n📊 Testing Network Topology Analysis")
        print("=" * 50)
        
        # Create nodes in different regions
        regions = [
            ("North America", [
                AdvancedMeshNode("node_na_1", "127.0.0.1", 8001, 
                               location=GeoLocation(40.7128, -74.0060, "United States", "New York", "NY"),
                               metrics=NetworkMetrics(latency=50.0, bandwidth=100.0, uptime=99.5)),
                AdvancedMeshNode("node_na_2", "127.0.0.1", 8002,
                               location=GeoLocation(37.7749, -122.4194, "United States", "San Francisco", "CA"),
                               metrics=NetworkMetrics(latency=45.0, bandwidth=150.0, uptime=99.8))
            ]),
            ("Europe", [
                AdvancedMeshNode("node_eu_1", "127.0.0.1", 8003,
                               location=GeoLocation(51.5074, -0.1278, "United Kingdom", "London", "England"),
                               metrics=NetworkMetrics(latency=80.0, bandwidth=200.0, uptime=99.9)),
                AdvancedMeshNode("node_eu_2", "127.0.0.1", 8004,
                               location=GeoLocation(48.8566, 2.3522, "France", "Paris", "Île-de-France"),
                               metrics=NetworkMetrics(latency=85.0, bandwidth=180.0, uptime=99.6))
            ]),
            ("Asia", [
                AdvancedMeshNode("node_as_1", "127.0.0.1", 8005,
                               location=GeoLocation(35.6762, 139.6503, "Japan", "Tokyo", "Tokyo"),
                               metrics=NetworkMetrics(latency=120.0, bandwidth=180.0, uptime=99.7)),
                AdvancedMeshNode("node_as_2", "127.0.0.1", 8006,
                               location=GeoLocation(1.3521, 103.8198, "Singapore", "Singapore", "Singapore"),
                               metrics=NetworkMetrics(latency=100.0, bandwidth=160.0, uptime=99.4))
            ])
        ]
        
        # Add all nodes to discovery
        for region_name, nodes in regions:
            for node in nodes:
                self.discovery.discovered_nodes[node.id] = node
        
        # Get topology
        topology = self.discovery.get_network_topology()
        
        print("🗺️ Network Topology:")
        print(f"  📊 Total Nodes: {topology['total_nodes']}")
        print(f"  ⚡ Average Latency: {topology['average_latency']:.1f}ms")
        print(f"  🏥 Network Health: {topology['network_health']:.3f}")
        print()
        
        print("🌍 Nodes by Region:")
        for region, nodes in topology['nodes_by_region'].items():
            print(f"  • {region}: {len(nodes)} nodes")
            for node in nodes:
                print(f"    - {node['id']} (latency: {node['latency']:.1f}ms, quality: {node['quality_score']:.3f})")
        
        return topology
    
    async def test_metrics_collection(self):
        """Test network metrics collection"""
        print("\n📈 Testing Network Metrics Collection")
        print("=" * 50)
        
        # Test system metrics
        system_metrics = self.discovery.metrics_collector.get_system_metrics()
        
        print("💻 System Metrics:")
        print(f"  🖥️  CPU Usage: {system_metrics.cpu_usage:.1f}%")
        print(f"  🧠 Memory Usage: {system_metrics.memory_usage:.1f}%")
        print(f"  🌐 Network Load: {system_metrics.network_load:.1f}%")
        print(f"  ⏱️  Uptime: {system_metrics.uptime:.1f}%")
        print(f"  🎯 Quality Score: {system_metrics.calculate_quality_score():.3f}")
        print()
        
        # Test latency measurement
        print("⚡ Latency Tests:")
        test_targets = [
            ("localhost", 80),
            ("127.0.0.1", 22),
            ("8.8.8.8", 53)  # Google DNS
        ]
        
        for host, port in test_targets:
            latency = await self.discovery.metrics_collector.measure_latency(host, port)
            if latency == float('inf'):
                print(f"  ❌ {host}:{port} - Connection failed")
            else:
                print(f"  ✅ {host}:{port} - {latency:.1f}ms")
        
        return system_metrics
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🌟 LIBERATION SYSTEM - ADVANCED NODE DISCOVERY TESTS")
        print("=" * 70)
        print("🎯 Testing enterprise-grade mesh network with geolocation optimization")
        print()
        
        # Run all tests
        await self.test_node_discovery()
        await self.test_node_scoring()
        await self.test_bootstrap_optimization()
        await self.test_network_topology()
        await self.test_metrics_collection()
        
        print("\n🎉 All Advanced Node Discovery Tests Complete!")
        print("✨ Mesh network ready for $19 trillion economic transformation")

async def main():
    """Main test runner"""
    test_suite = TestAdvancedDiscovery()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
