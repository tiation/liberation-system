#!/usr/bin/env python3
"""
Liberation System - Mesh Network P2P Communication Test
Tests the actual P2P communication between mesh nodes
"""

import asyncio
import logging
import time
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'mesh', 'Mesh_Network'))
from mesh_network_clean import MeshNode, NetworkMessage, MessageType

# Configure logging with dark theme colors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class MeshNetworkTest:
    """Test suite for mesh network P2P communication"""
    
    def __init__(self):
        self.nodes = []
        self.test_results = {
            "node_creation": False,
            "server_startup": False,
            "peer_connection": False,
            "message_broadcast": False,
            "resource_distribution": False,
            "truth_propagation": False,
            "network_stats": False,
            "cleanup": False
        }
        self.logger = logging.getLogger("MeshNetworkTest")
    
    async def test_node_creation(self):
        """Test creating mesh nodes"""
        try:
            self.logger.info("🔧 Testing node creation...")
            
            # Create test nodes
            node1 = MeshNode("node_1", "localhost", 9001)
            node2 = MeshNode("node_2", "localhost", 9002)
            node3 = MeshNode("node_3", "localhost", 9003)
            
            self.nodes = [node1, node2, node3]
            
            # Verify nodes are created properly
            for node in self.nodes:
                assert node.id is not None
                assert node.host == "localhost"
                assert node.port > 0
                assert node.status == "active"
                assert node.is_healthy()
            
            self.test_results["node_creation"] = True
            self.logger.info("✅ Node creation test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Node creation test failed: {e}")
            return False
        
        return True
    
    async def test_server_startup(self):
        """Test starting P2P servers"""
        try:
            self.logger.info("🚀 Testing server startup...")
            
            # Start servers for all nodes
            server_tasks = []
            for node in self.nodes:
                task = asyncio.create_task(node.start_server())
                server_tasks.append(task)
            
            # Give servers time to start
            await asyncio.sleep(2)
            
            # Check if servers are running
            for node in self.nodes:
                assert node.server_socket is not None
                assert node.status == "active"
            
            self.test_results["server_startup"] = True
            self.logger.info("✅ Server startup test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Server startup test failed: {e}")
            return False
        
        return True
    
    async def test_peer_connection(self):
        """Test peer-to-peer connections"""
        try:
            self.logger.info("🤝 Testing peer connections...")
            
            # Connect node1 to node2
            success1 = await self.nodes[0].connect_to_peer("localhost", 9002)
            await asyncio.sleep(1)
            
            # Connect node2 to node3
            success2 = await self.nodes[1].connect_to_peer("localhost", 9003)
            await asyncio.sleep(1)
            
            # Connect node3 to node1 (complete the mesh)
            success3 = await self.nodes[2].connect_to_peer("localhost", 9001)
            await asyncio.sleep(1)
            
            # Verify connections
            assert success1 and success2 and success3
            
            # Check connection counts
            for node in self.nodes:
                assert len(node.connections) > 0
                self.logger.info(f"Node {node.id} has {len(node.connections)} connections")
            
            self.test_results["peer_connection"] = True
            self.logger.info("✅ Peer connection test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Peer connection test failed: {e}")
            return False
        
        return True
    
    async def test_message_broadcast(self):
        """Test message broadcasting"""
        try:
            self.logger.info("📡 Testing message broadcasting...")
            
            # Create test message
            test_message = NetworkMessage(
                id="test_msg_001",
                type=MessageType.DATA,
                source_node="node_1",
                target_node=None,
                payload={
                    "key": "test_data",
                    "value": "Hello from node_1",
                    "timestamp": time.time()
                },
                timestamp=time.time()
            )
            
            # Broadcast from node1
            await self.nodes[0].broadcast_message(test_message)
            await asyncio.sleep(2)
            
            # Check if message was received by other nodes
            received_count = 0
            for node in self.nodes[1:]:  # Skip sender
                if "test_data" in node.data_store:
                    received_count += 1
                    self.logger.info(f"Node {node.id} received message")
            
            assert received_count > 0
            
            self.test_results["message_broadcast"] = True
            self.logger.info("✅ Message broadcast test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Message broadcast test failed: {e}")
            return False
        
        return True
    
    async def test_resource_distribution(self):
        """Test resource distribution messaging"""
        try:
            self.logger.info("💰 Testing resource distribution...")
            
            # Create resource distribution message
            resource_msg = NetworkMessage(
                id="resource_msg_001",
                type=MessageType.RESOURCE_BROADCAST,
                source_node="node_2",
                target_node=None,
                payload={
                    "amount": 800.00,
                    "recipient": "human_123",
                    "transaction_id": "tx_001",
                    "timestamp": time.time()
                },
                timestamp=time.time()
            )
            
            # Send from node2
            await self.nodes[1].broadcast_message(resource_msg)
            await asyncio.sleep(2)
            
            # Check network stats
            stats = self.nodes[1].get_network_stats()
            assert stats["messages_sent"] > 0
            
            self.test_results["resource_distribution"] = True
            self.logger.info("✅ Resource distribution test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Resource distribution test failed: {e}")
            return False
        
        return True
    
    async def test_truth_propagation(self):
        """Test truth spreading functionality"""
        try:
            self.logger.info("🌐 Testing truth propagation...")
            
            # Create truth message
            truth_msg = NetworkMessage(
                id="truth_msg_001",
                type=MessageType.TRUTH_PROPAGATION,
                source_node="node_3",
                target_node=None,
                payload={
                    "content": "The $19T economic reform is happening now",
                    "priority": 1,
                    "reach": 1000000,
                    "timestamp": time.time()
                },
                timestamp=time.time()
            )
            
            # Send from node3
            await self.nodes[2].broadcast_message(truth_msg)
            await asyncio.sleep(2)
            
            # Verify propagation
            propagated_count = 0
            for node in self.nodes:
                if node.network_stats["messages_received"] > 0:
                    propagated_count += 1
            
            assert propagated_count > 0
            
            self.test_results["truth_propagation"] = True
            self.logger.info("✅ Truth propagation test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Truth propagation test failed: {e}")
            return False
        
        return True
    
    async def test_network_stats(self):
        """Test network statistics collection"""
        try:
            self.logger.info("📊 Testing network statistics...")
            
            # Get stats from all nodes
            for node in self.nodes:
                stats = node.get_network_stats()
                self.logger.info(f"Node {node.id} stats: {stats}")
                
                # Verify stats structure
                assert "messages_sent" in stats
                assert "messages_received" in stats
                assert "bytes_transferred" in stats
                assert "connections_active" in stats
                assert isinstance(stats["connections_active"], int)
            
            self.test_results["network_stats"] = True
            self.logger.info("✅ Network statistics test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Network statistics test failed: {e}")
            return False
        
        return True
    
    async def test_cleanup(self):
        """Test proper cleanup of resources"""
        try:
            self.logger.info("🧹 Testing cleanup...")
            
            # Test heartbeat functionality
            await self.nodes[0].send_heartbeat()
            await asyncio.sleep(1)
            
            # Test stale connection cleanup
            await self.nodes[0].cleanup_stale_connections()
            
            # Shutdown all nodes
            for node in self.nodes:
                await node.shutdown()
            
            # Verify shutdown
            for node in self.nodes:
                assert node.status == "shutting_down"
            
            self.test_results["cleanup"] = True
            self.logger.info("✅ Cleanup test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup test failed: {e}")
            return False
        
        return True
    
    async def run_all_tests(self):
        """Run all mesh network tests"""
        self.logger.info("🚀 Starting Liberation System Mesh Network Tests")
        self.logger.info("=" * 60)
        
        # Run tests in sequence
        tests = [
            self.test_node_creation,
            self.test_server_startup,
            self.test_peer_connection,
            self.test_message_broadcast,
            self.test_resource_distribution,
            self.test_truth_propagation,
            self.test_network_stats,
            self.test_cleanup
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
                await asyncio.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                self.logger.error(f"Test execution failed: {e}")
        
        # Print results
        self.logger.info("=" * 60)
        self.logger.info("🎯 TEST RESULTS SUMMARY")
        self.logger.info("=" * 60)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
        
        self.logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            self.logger.info("🎉 All tests passed! Mesh network is working correctly.")
        else:
            self.logger.warning(f"⚠️  {total - passed} tests failed. Check implementation.")
        
        return passed == total

async def main():
    """Main test runner"""
    test_suite = MeshNetworkTest()
    
    try:
        success = await test_suite.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        logging.info("Tests interrupted by user")
        return 1
    except Exception as e:
        logging.error(f"Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
