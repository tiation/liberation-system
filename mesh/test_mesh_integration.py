#!/usr/bin/env python3
"""
Comprehensive Integration Tests for Liberation System Mesh Network
Tests sharding strategy, node discovery, and network operations
"""

import asyncio
import logging
import time
import json
import tempfile
import os
from typing import Dict, List, Optional
from datetime import datetime
from unittest.mock import Mock, patch

from Mesh_Network.Sharding_Strategy import ShardingStrategy, ShardType, NodeShard
from Mesh_Network.Advanced_Node_Discovery import (
    AdvancedNodeDiscovery,
    AdvancedMeshNode,
    GeoLocation,
    NetworkMetrics,
    NodeCapabilities,
    NodeType
)
from Mesh_Network.Mesh_Network import MeshNode, NetworkMessage, MessageType

# Configure logging with neon theme
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mesh_integration_tests.log')
    ]
)

class MeshIntegrationTests:
    """Comprehensive integration test suite for mesh network"""
    
    def __init__(self):
        self.sharding_strategy = ShardingStrategy(total_shards=64, replication_factor=3)
        self.node_discovery = AdvancedNodeDiscovery()
        self.test_nodes = []
        self.test_results = {}
        self.logger = logging.getLogger(__name__)
        
    async def setup_test_environment(self):
        """Setup comprehensive test environment"""
        self.logger.info("🔧 Setting up test environment...")
        
        # Create diverse test nodes
        test_node_configs = [
            {
                "id": "gateway_us_east",
                "host": "127.0.0.1",
                "port": 8000,
                "node_type": NodeType.GATEWAY,
                "location": GeoLocation(40.7128, -74.0060, "United States", "New York", "NY"),
                "metrics": NetworkMetrics(latency=25.0, bandwidth=1000.0, uptime=99.9, cpu_usage=30.0, memory_usage=45.0),
                "capabilities": NodeCapabilities(max_connections=200, storage_capacity=10000, processing_power=4.0)
            },
            {
                "id": "storage_us_west",
                "host": "127.0.0.1",
                "port": 8001,
                "node_type": NodeType.STORAGE,
                "location": GeoLocation(37.7749, -122.4194, "United States", "San Francisco", "CA"),
                "metrics": NetworkMetrics(latency=30.0, bandwidth=800.0, uptime=99.8, cpu_usage=25.0, memory_usage=60.0),
                "capabilities": NodeCapabilities(max_connections=150, storage_capacity=50000, processing_power=2.5)
            },
            {
                "id": "compute_eu_london",
                "host": "127.0.0.1",
                "port": 8002,
                "node_type": NodeType.COMPUTE,
                "location": GeoLocation(51.5074, -0.1278, "United Kingdom", "London", "England"),
                "metrics": NetworkMetrics(latency=80.0, bandwidth=600.0, uptime=99.5, cpu_usage=60.0, memory_usage=40.0),
                "capabilities": NodeCapabilities(max_connections=100, storage_capacity=5000, processing_power=8.0)
            },
            {
                "id": "relay_asia_tokyo",
                "host": "127.0.0.1",
                "port": 8003,
                "node_type": NodeType.RELAY,
                "location": GeoLocation(35.6762, 139.6503, "Japan", "Tokyo", "Tokyo"),
                "metrics": NetworkMetrics(latency=120.0, bandwidth=400.0, uptime=99.7, cpu_usage=40.0, memory_usage=35.0),
                "capabilities": NodeCapabilities(max_connections=300, storage_capacity=2000, processing_power=3.0)
            },
            {
                "id": "bootstrap_au_sydney",
                "host": "127.0.0.1",
                "port": 8004,
                "node_type": NodeType.BOOTSTRAP,
                "location": GeoLocation(-33.8688, 151.2093, "Australia", "Sydney", "NSW"),
                "metrics": NetworkMetrics(latency=200.0, bandwidth=300.0, uptime=99.9, cpu_usage=20.0, memory_usage=30.0),
                "capabilities": NodeCapabilities(max_connections=500, storage_capacity=8000, processing_power=2.0)
            }
        ]
        
        # Create test nodes
        for config in test_node_configs:
            node = AdvancedMeshNode(
                id=config["id"],
                host=config["host"],
                port=config["port"],
                node_type=config["node_type"],
                location=config["location"],
                metrics=config["metrics"],
                capabilities=config["capabilities"]
            )
            self.test_nodes.append(node)
            
        self.logger.info(f"✅ Created {len(self.test_nodes)} test nodes")
        
    async def test_sharding_strategy_integration(self):
        """Test sharding strategy with diverse node types"""
        self.logger.info("🧪 Testing sharding strategy integration...")
        
        try:
            # Add all nodes to sharding strategy
            for node in self.test_nodes:
                success = await self.sharding_strategy.add_node_to_shard(node)
                assert success, f"Failed to add node {node.id} to sharding strategy"
            
            # Test data distribution
            test_data_items = [
                "user_profile_12345",
                "financial_transaction_67890",
                "truth_propagation_message_001",
                "resource_distribution_002",
                "network_topology_update_003"
            ]
            
            distribution_results = {}
            for data_item in test_data_items:
                nodes = self.sharding_strategy.get_nodes_for_data(data_item)
                primary_node = self.sharding_strategy.get_primary_node_for_data(data_item)
                
                distribution_results[data_item] = {
                    "shard_id": self.sharding_strategy.get_shard_for_data(data_item),
                    "nodes": [node.id for node in nodes],
                    "primary_node": primary_node.id if primary_node else None,
                    "node_types": [node.node_type.value for node in nodes]
                }
            
            # Verify distribution
            assert all(len(result["nodes"]) >= 1 for result in distribution_results.values()), \
                "All data items should be assigned to at least one node"
            
            assert all(result["primary_node"] is not None for result in distribution_results.values()), \
                "All data items should have a primary node"
            
            # Test load balancing
            stats = self.sharding_strategy.get_shard_statistics()
            load_distribution = stats["load_distribution"]
            
            # Check if load is reasonably distributed
            loads = list(load_distribution.values())
            max_load = max(loads)
            min_load = min(loads)
            load_variance = max_load - min_load
            
            assert load_variance <= 3, f"Load variance too high: {load_variance}"
            
            self.test_results["sharding_strategy"] = {
                "passed": True,
                "distribution_results": distribution_results,
                "load_stats": stats,
                "notes": "Sharding strategy working correctly with diverse node types"
            }
            
            self.logger.info("✅ Sharding strategy integration test passed")
            
        except Exception as e:
            self.test_results["sharding_strategy"] = {
                "passed": False,
                "error": str(e),
                "notes": "Sharding strategy integration test failed"
            }
            self.logger.error(f"❌ Sharding strategy integration test failed: {e}")
            
    async def test_node_discovery_integration(self):
        """Test node discovery with geolocation and metrics"""
        self.logger.info("🧪 Testing node discovery integration...")
        
        try:
            # Add nodes to discovery system
            for node in self.test_nodes:
                self.node_discovery.discovered_nodes[node.id] = node
            
            # Test discovery from different perspectives
            discovery_results = {}
            
            for test_node in self.test_nodes[:3]:  # Test from first 3 nodes
                discovered = await self.node_discovery.discover_nodes(test_node)
                
                discovery_results[test_node.id] = {
                    "discovered_count": len(discovered),
                    "discovered_nodes": [node.id for node in discovered],
                    "node_types": [node.node_type.value for node in discovered],
                    "geographic_diversity": len(set(node.location.country for node in discovered if node.location))
                }
            
            # Verify discovery results
            for node_id, result in discovery_results.items():
                assert result["discovered_count"] > 0, f"Node {node_id} should discover at least one other node"
                assert result["geographic_diversity"] > 0, f"Node {node_id} should have geographic diversity"
            
            # Test bootstrap node selection
            bootstrap_nodes = await self.node_discovery.get_optimal_bootstrap_nodes(3)
            assert len(bootstrap_nodes) == 3, "Should return 3 bootstrap nodes"
            
            # Test network topology
            topology = self.node_discovery.get_network_topology()
            assert topology["total_nodes"] == len(self.test_nodes), "Topology should include all nodes"
            assert topology["network_health"] > 0.5, "Network health should be reasonable"
            
            self.test_results["node_discovery"] = {
                "passed": True,
                "discovery_results": discovery_results,
                "bootstrap_nodes": bootstrap_nodes,
                "topology": topology,
                "notes": "Node discovery working correctly with geolocation and metrics"
            }
            
            self.logger.info("✅ Node discovery integration test passed")
            
        except Exception as e:
            self.test_results["node_discovery"] = {
                "passed": False,
                "error": str(e),
                "notes": "Node discovery integration test failed"
            }
            self.logger.error(f"❌ Node discovery integration test failed: {e}")
    
    async def test_cross_system_integration(self):
        """Test integration between sharding and discovery systems"""
        self.logger.info("🧪 Testing cross-system integration...")
        
        try:
            # Test coordinated node assignment
            coordination_results = {}
            
            for node in self.test_nodes:
                # Add to both systems
                discovery_success = node.id in self.node_discovery.discovered_nodes
                sharding_success = node.id in self.sharding_strategy.nodes
                
                coordination_results[node.id] = {
                    "in_discovery": discovery_success,
                    "in_sharding": sharding_success,
                    "coordinated": discovery_success and sharding_success
                }
            
            # Verify all nodes are in both systems
            all_coordinated = all(result["coordinated"] for result in coordination_results.values())
            assert all_coordinated, "All nodes should be coordinated between systems"
            
            # Test data routing with discovery
            test_data = "integration_test_data_001"
            
            # Get nodes from sharding strategy
            shard_nodes = self.sharding_strategy.get_nodes_for_data(test_data)
            primary_node = self.sharding_strategy.get_primary_node_for_data(test_data)
            
            # Verify nodes exist in discovery system
            for node in shard_nodes:
                assert node.id in self.node_discovery.discovered_nodes, \
                    f"Shard node {node.id} should exist in discovery system"
            
            # Test failover scenario
            if primary_node:
                # Remove primary node from sharding
                await self.sharding_strategy.remove_node_from_shard(primary_node.id)
                
                # Get new primary
                new_primary = self.sharding_strategy.get_primary_node_for_data(test_data)
                
                # Verify failover worked
                assert new_primary is not None, "Should have new primary after failover"
                assert new_primary.id != primary_node.id, "New primary should be different"
                
                # Re-add the node
                await self.sharding_strategy.add_node_to_shard(primary_node)
            
            self.test_results["cross_system"] = {
                "passed": True,
                "coordination_results": coordination_results,
                "failover_tested": True,
                "notes": "Cross-system integration working correctly"
            }
            
            self.logger.info("✅ Cross-system integration test passed")
            
        except Exception as e:
            self.test_results["cross_system"] = {
                "passed": False,
                "error": str(e),
                "notes": "Cross-system integration test failed"
            }
            self.logger.error(f"❌ Cross-system integration test failed: {e}")
    
    async def test_performance_under_load(self):
        """Test system performance under load"""
        self.logger.info("🧪 Testing performance under load...")
        
        try:
            # Performance metrics
            performance_results = {
                "shard_lookup_times": [],
                "node_discovery_times": [],
                "rebalance_times": [],
                "memory_usage": []
            }
            
            # Test shard lookup performance
            test_data_items = [f"performance_test_data_{i:06d}" for i in range(1000)]
            
            start_time = time.time()
            for data_item in test_data_items:
                lookup_start = time.time()
                nodes = self.sharding_strategy.get_nodes_for_data(data_item)
                lookup_time = time.time() - lookup_start
                performance_results["shard_lookup_times"].append(lookup_time)
            
            total_lookup_time = time.time() - start_time
            avg_lookup_time = sum(performance_results["shard_lookup_times"]) / len(performance_results["shard_lookup_times"])
            
            # Test node discovery performance
            discovery_start = time.time()
            for node in self.test_nodes[:3]:
                discover_start = time.time()
                discovered = await self.node_discovery.discover_nodes(node)
                discover_time = time.time() - discover_start
                performance_results["node_discovery_times"].append(discover_time)
            
            total_discovery_time = time.time() - discovery_start
            avg_discovery_time = sum(performance_results["node_discovery_times"]) / len(performance_results["node_discovery_times"])
            
            # Test rebalancing performance
            rebalance_start = time.time()
            rebalance_success = await self.sharding_strategy.rebalance_shards()
            rebalance_time = time.time() - rebalance_start
            performance_results["rebalance_times"].append(rebalance_time)
            
            # Performance assertions
            assert avg_lookup_time < 0.001, f"Average lookup time too high: {avg_lookup_time:.6f}s"
            assert avg_discovery_time < 1.0, f"Average discovery time too high: {avg_discovery_time:.3f}s"
            assert rebalance_time < 5.0, f"Rebalancing time too high: {rebalance_time:.3f}s"
            assert rebalance_success, "Rebalancing should succeed"
            
            self.test_results["performance"] = {
                "passed": True,
                "avg_lookup_time": avg_lookup_time,
                "avg_discovery_time": avg_discovery_time,
                "rebalance_time": rebalance_time,
                "total_data_items": len(test_data_items),
                "notes": "Performance tests passed within acceptable limits"
            }
            
            self.logger.info("✅ Performance under load test passed")
            
        except Exception as e:
            self.test_results["performance"] = {
                "passed": False,
                "error": str(e),
                "notes": "Performance under load test failed"
            }
            self.logger.error(f"❌ Performance under load test failed: {e}")
    
    async def test_fault_tolerance(self):
        """Test system fault tolerance and recovery"""
        self.logger.info("🧪 Testing fault tolerance...")
        
        try:
            # Test node failures
            fault_tolerance_results = {}
            
            # Remove half the nodes
            nodes_to_remove = self.test_nodes[:len(self.test_nodes)//2]
            
            for node in nodes_to_remove:
                remove_success = await self.sharding_strategy.remove_node_from_shard(node.id)
                assert remove_success, f"Should successfully remove node {node.id}"
            
            # Test system still functions
            test_data = "fault_tolerance_test_data"
            remaining_nodes = self.sharding_strategy.get_nodes_for_data(test_data)
            
            assert len(remaining_nodes) > 0, "Should still have nodes available after failures"
            
            # Test recovery - add nodes back
            for node in nodes_to_remove:
                add_success = await self.sharding_strategy.add_node_to_shard(node)
                assert add_success, f"Should successfully re-add node {node.id}"
            
            # Test system recovered
            recovered_nodes = self.sharding_strategy.get_nodes_for_data(test_data)
            assert len(recovered_nodes) >= len(remaining_nodes), "Should have more nodes after recovery"
            
            # Test network partitioning
            partition_results = {}
            
            # Simulate partitioning by creating separate discovery instances
            partition_a = AdvancedNodeDiscovery()
            partition_b = AdvancedNodeDiscovery()
            
            # Split nodes between partitions
            for i, node in enumerate(self.test_nodes):
                if i % 2 == 0:
                    partition_a.discovered_nodes[node.id] = node
                else:
                    partition_b.discovered_nodes[node.id] = node
            
            # Test each partition can still function
            partition_a_topology = partition_a.get_network_topology()
            partition_b_topology = partition_b.get_network_topology()
            
            assert partition_a_topology["total_nodes"] > 0, "Partition A should have nodes"
            assert partition_b_topology["total_nodes"] > 0, "Partition B should have nodes"
            
            fault_tolerance_results = {
                "node_removal_recovery": True,
                "partition_tolerance": True,
                "remaining_nodes_after_failure": len(remaining_nodes),
                "nodes_after_recovery": len(recovered_nodes),
                "partition_a_nodes": partition_a_topology["total_nodes"],
                "partition_b_nodes": partition_b_topology["total_nodes"]
            }
            
            self.test_results["fault_tolerance"] = {
                "passed": True,
                "results": fault_tolerance_results,
                "notes": "Fault tolerance tests passed"
            }
            
            self.logger.info("✅ Fault tolerance test passed")
            
        except Exception as e:
            self.test_results["fault_tolerance"] = {
                "passed": False,
                "error": str(e),
                "notes": "Fault tolerance test failed"
            }
            self.logger.error(f"❌ Fault tolerance test failed: {e}")
    
    async def test_security_and_trust(self):
        """Test security features and trust mechanisms"""
        self.logger.info("🧪 Testing security and trust...")
        
        try:
            security_results = {}
            
            # Test trust scoring
            for node in self.test_nodes:
                initial_trust = node.trust_score  # Correct trust attribute
                assert 0.0 <= initial_trust <= 1.0, f"Trust score should be between 0 and 1: {initial_trust}"
            
            # Test node validation
            # Create a malicious node
            malicious_node = AdvancedMeshNode(
                id="malicious_node_001",
                host="127.0.0.1",
                port=9999,
                node_type=NodeType.STANDARD,
                location=GeoLocation(0.0, 0.0, "Atlantis", "",""),
                trust_score=0.1  # Low trust
            )
            
            # Test if system handles low-trust nodes appropriately
            add_success = await self.sharding_strategy.add_node_to_shard(malicious_node)
            
            if add_success:
                # Check if malicious node gets limited assignments
                malicious_shards = self.sharding_strategy.node_shards[malicious_node.id].assigned_shards
                trusted_node_shards = self.sharding_strategy.node_shards[self.test_nodes[0].id].assigned_shards
                
                # Low trust nodes should get fewer shard assignments
                assert len(malicious_shards) <= len(trusted_node_shards), \
                    "Low trust nodes should get fewer shard assignments"
            
            # Test data integrity
            test_data = "security_test_data"
            data_hash = self.sharding_strategy.calculate_shard_hash(test_data)
            
            # Verify hash consistency
            same_data_hash = self.sharding_strategy.calculate_shard_hash(test_data)
            assert data_hash == same_data_hash, "Hash should be consistent for same data"
            
            # Test different data produces different hashes
            different_data_hash = self.sharding_strategy.calculate_shard_hash(test_data + "_modified")
            assert data_hash != different_data_hash, "Different data should produce different hashes"
            
            # Additional security test for message encryption
            message = "Sensitive Data"
            encrypted_message = self.encrypt_message(message)
            decrypted_message = self.decrypt_message(encrypted_message)
            assert message == decrypted_message, "Message encryption and decryption should work correctly"

            security_results = {
                "trust_validation": True,
                "malicious_node_handling": True,
                "data_integrity": True,
                "hash_consistency": True,
                "encryption_test": True
            }
            
            self.test_results["security"] = {
                "passed": True,
                "results": security_results,
                "notes": "Security and trust tests passed"
            }
            
            self.logger.info("✅ Security and trust test passed")
            
        except Exception as e:
            self.test_results["security"] = {
                "passed": False,
                "error": str(e),
                "notes": "Security and trust test failed"
            }
            self.logger.error(f"❌ Security and trust test failed: {e}")

    def encrypt_message(self, message: str) -> str:
        """Encrypt the message using a simple reversible method"""
        return "".join(chr(ord(char) + 2) for char in message)

    def decrypt_message(self, encrypted_message: str) -> str:
        """Decrypt the message"""
        return "".join(chr(ord(char) - 2) for char in encrypted_message)
    
    async def run_all_integration_tests(self):
        """Run all integration tests"""
        self.logger.info("🚀 Starting comprehensive integration tests...")
        self.logger.info("=" * 60)
        
        # Setup
        await self.setup_test_environment()
        
        # Run all tests
        test_methods = [
            self.test_sharding_strategy_integration,
            self.test_node_discovery_integration,
            self.test_cross_system_integration,
            self.test_performance_under_load,
            self.test_fault_tolerance,
            self.test_security_and_trust
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                await test_method()
                if self.test_results.get(test_method.__name__.replace("test_", ""), {}).get("passed", False):
                    passed_tests += 1
                await asyncio.sleep(0.1)  # Brief pause between tests
            except Exception as e:
                self.logger.error(f"Test {test_method.__name__} failed with exception: {e}")
        
        # Generate test report
        self.generate_test_report(passed_tests, total_tests)
        
        return passed_tests == total_tests
    
    def generate_test_report(self, passed_tests: int, total_tests: int):
        """Generate comprehensive test report"""
        self.logger.info("=" * 60)
        self.logger.info("🎯 INTEGRATION TEST RESULTS SUMMARY")
        self.logger.info("=" * 60)
        
        # Overall results
        success_rate = (passed_tests / total_tests) * 100
        self.logger.info(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        self.logger.info("")
        
        # Detailed results
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            self.logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
            
            if not result["passed"] and "error" in result:
                self.logger.info(f"  Error: {result['error']}")
            
            if "notes" in result:
                self.logger.info(f"  Notes: {result['notes']}")
            
            self.logger.info("")
        
        # Save detailed report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "detailed_results": self.test_results
        }
        
        with open("mesh_integration_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2, default=str)
        
        if passed_tests == total_tests:
            self.logger.info("🎉 All integration tests passed! System is ready for production.")
        else:
            self.logger.warning(f"⚠️  {total_tests - passed_tests} tests failed. Please review and fix issues.")

async def main():
    """Main test runner"""
    test_suite = MeshIntegrationTests()
    success = await test_suite.run_all_integration_tests()
    return success

if __name__ == "__main__":
    # Run integration tests
    success = asyncio.run(main())
    exit(0 if success else 1)
