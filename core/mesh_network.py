"""
Liberation System - Mesh Network Module
Handles mesh network operations, node discovery, and peer-to-peer communication.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import socket
import uuid


@dataclass
class MeshNode:
    """Data structure representing a mesh network node"""
    node_id: str
    ip_address: str
    port: int
    status: str = "active"
    last_seen: Optional[datetime] = None
    capabilities: List[str] = field(default_factory=list)
    trust_level: float = 1.0
    

@dataclass
class MeshConnection:
    """Data structure representing a connection between mesh nodes"""
    connection_id: str
    source_node: str
    target_node: str
    established_at: datetime
    status: str = "active"
    bandwidth: float = 0.0
    latency: float = 0.0


class MeshNetworkManager:
    """Manages mesh network operations and node discovery"""
    
    def __init__(self):
        self.nodes: Dict[str, MeshNode] = {}
        self.connections: Dict[str, MeshConnection] = {}
        self.local_node_id: str = str(uuid.uuid4())
        self.max_nodes: int = 1000
        self.auto_discovery_enabled: bool = True
        self.discovery_port: int = 8001
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the mesh network manager"""
        self.logger.info("🔄 Initializing Mesh Network Manager")
        
        # Create local node
        local_ip = self._get_local_ip()
        self.local_node = MeshNode(
            node_id=self.local_node_id,
            ip_address=local_ip,
            port=self.discovery_port,
            status="active",
            last_seen=datetime.now(),
            capabilities=["resource_distribution", "truth_spreading", "data_sync"]
        )
        
        # Add local node to network
        self.nodes[self.local_node_id] = self.local_node
        
        self.logger.info(f"🌐 Local node initialized: {self.local_node_id}")
        self.logger.info(f"📡 Discovery port: {self.discovery_port}")
        
        # Start auto-discovery if enabled
        if self.auto_discovery_enabled:
            asyncio.create_task(self._auto_discovery_loop())
            
    def _get_local_ip(self) -> str:
        """Get the local IP address"""
        try:
            # Connect to a remote address to determine the local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
            return local_ip
        except Exception:
            return "127.0.0.1"
            
    async def discover_nodes(self) -> List[MeshNode]:
        """Discover nodes in the mesh network"""
        try:
            discovered_nodes = []
            
            # Simulate network discovery
            # In a real implementation, this would use UDP broadcast or multicast
            self.logger.info("🔍 Discovering mesh network nodes...")
            
            # Add some simulated nodes for demonstration
            if len(self.nodes) < 5:  # Only add if we don't have many nodes
                for i in range(1, 4):
                    node_id = f"node-{i:03d}"
                    if node_id not in self.nodes:
                        node = MeshNode(
                            node_id=node_id,
                            ip_address=f"192.168.1.{100 + i}",
                            port=8001 + i,
                            status="active",
                            last_seen=datetime.now(),
                            capabilities=["resource_distribution", "truth_spreading"]
                        )
                        discovered_nodes.append(node)
                        self.nodes[node_id] = node
                        
            self.logger.info(f"🎯 Discovered {len(discovered_nodes)} new nodes")
            return discovered_nodes
            
        except Exception as e:
            self.logger.error(f"❌ Error discovering nodes: {e}")
            return []
            
    async def connect_to_node(self, node_id: str) -> bool:
        """Establish connection to a node"""
        try:
            if node_id not in self.nodes:
                self.logger.error(f"❌ Node {node_id} not found in network")
                return False
                
            # Check if connection already exists
            existing_connection = next(
                (conn for conn in self.connections.values() 
                 if conn.source_node == self.local_node_id and conn.target_node == node_id),
                None
            )
            
            if existing_connection:
                self.logger.info(f"🔗 Connection to {node_id} already exists")
                return True
                
            # Create new connection
            connection_id = f"{self.local_node_id}-{node_id}"
            connection = MeshConnection(
                connection_id=connection_id,
                source_node=self.local_node_id,
                target_node=node_id,
                established_at=datetime.now(),
                status="active",
                bandwidth=100.0,  # Simulated bandwidth
                latency=0.05  # Simulated latency
            )
            
            self.connections[connection_id] = connection
            self.logger.info(f"✅ Connected to node {node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error connecting to node {node_id}: {e}")
            return False
            
    async def disconnect_from_node(self, node_id: str) -> bool:
        """Disconnect from a node"""
        try:
            connection_id = f"{self.local_node_id}-{node_id}"
            
            if connection_id in self.connections:
                del self.connections[connection_id]
                self.logger.info(f"🔌 Disconnected from node {node_id}")
                return True
            else:
                self.logger.warning(f"⚠️ No connection to node {node_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error disconnecting from node {node_id}: {e}")
            return False
            
    async def broadcast_message(self, message: Dict[str, Any]) -> int:
        """Broadcast a message to all connected nodes"""
        try:
            sent_count = 0
            
            for connection in self.connections.values():
                if connection.status == "active":
                    # Simulate sending message
                    self.logger.info(f"📡 Broadcasting to {connection.target_node}: {message.get('type', 'unknown')}")
                    sent_count += 1
                    
            self.logger.info(f"📢 Message broadcast to {sent_count} nodes")
            return sent_count
            
        except Exception as e:
            self.logger.error(f"❌ Error broadcasting message: {e}")
            return 0
            
    async def send_message(self, node_id: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific node"""
        try:
            connection_id = f"{self.local_node_id}-{node_id}"
            
            if connection_id not in self.connections:
                self.logger.error(f"❌ No connection to node {node_id}")
                return False
                
            connection = self.connections[connection_id]
            if connection.status != "active":
                self.logger.error(f"❌ Connection to {node_id} is not active")
                return False
                
            # Simulate sending message
            self.logger.info(f"📤 Sending message to {node_id}: {message.get('type', 'unknown')}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error sending message to {node_id}: {e}")
            return False
            
    async def get_network_status(self) -> Dict[str, Any]:
        """Get current network status"""
        active_nodes = sum(1 for node in self.nodes.values() if node.status == "active")
        active_connections = sum(1 for conn in self.connections.values() if conn.status == "active")
        
        return {
            "local_node_id": self.local_node_id,
            "total_nodes": len(self.nodes),
            "active_nodes": active_nodes,
            "total_connections": len(self.connections),
            "active_connections": active_connections,
            "auto_discovery_enabled": self.auto_discovery_enabled,
            "max_nodes": self.max_nodes
        }
        
    async def get_node_list(self) -> List[Dict[str, Any]]:
        """Get list of all nodes in the network"""
        return [
            {
                "node_id": node.node_id,
                "ip_address": node.ip_address,
                "port": node.port,
                "status": node.status,
                "last_seen": node.last_seen.isoformat() if node.last_seen else None,
                "capabilities": node.capabilities,
                "trust_level": node.trust_level
            }
            for node in self.nodes.values()
        ]
        
    async def get_connection_list(self) -> List[Dict[str, Any]]:
        """Get list of all connections"""
        return [
            {
                "connection_id": conn.connection_id,
                "source_node": conn.source_node,
                "target_node": conn.target_node,
                "established_at": conn.established_at.isoformat(),
                "status": conn.status,
                "bandwidth": conn.bandwidth,
                "latency": conn.latency
            }
            for conn in self.connections.values()
        ]
        
    async def _auto_discovery_loop(self):
        """Background task for auto-discovery"""
        while self.auto_discovery_enabled:
            try:
                await self.discover_nodes()
                await asyncio.sleep(30)  # Discovery every 30 seconds
            except Exception as e:
                self.logger.error(f"❌ Error in auto-discovery loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
                
    async def cleanup_inactive_nodes(self):
        """Remove inactive nodes from the network"""
        try:
            now = datetime.now()
            inactive_nodes = []
            
            for node_id, node in self.nodes.items():
                if node.last_seen and (now - node.last_seen).total_seconds() > 300:  # 5 minutes
                    inactive_nodes.append(node_id)
                    
            for node_id in inactive_nodes:
                if node_id != self.local_node_id:  # Don't remove local node
                    del self.nodes[node_id]
                    # Also remove associated connections
                    connections_to_remove = [
                        conn_id for conn_id, conn in self.connections.items()
                        if conn.source_node == node_id or conn.target_node == node_id
                    ]
                    for conn_id in connections_to_remove:
                        del self.connections[conn_id]
                        
            if inactive_nodes:
                self.logger.info(f"🧹 Cleaned up {len(inactive_nodes)} inactive nodes")
                
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up inactive nodes: {e}")


# Global mesh network manager instance
mesh_manager = MeshNetworkManager()


async def initialize_mesh_network():
    """Initialize the global mesh network manager"""
    await mesh_manager.initialize()


async def main():
    """Main function for testing"""
    await initialize_mesh_network()
    
    # Test node discovery
    nodes = await mesh_manager.discover_nodes()
    print(f"Discovered {len(nodes)} nodes")
    
    # Test network status
    status = await mesh_manager.get_network_status()
    print(f"Network status: {json.dumps(status, indent=2)}")
    
    # Test connecting to a node
    if len(mesh_manager.nodes) > 1:
        node_ids = list(mesh_manager.nodes.keys())
        target_node = next(node_id for node_id in node_ids if node_id != mesh_manager.local_node_id)
        success = await mesh_manager.connect_to_node(target_node)
        print(f"Connection successful: {success}")
        
        # Test sending a message
        message = {"type": "test", "data": "Hello from mesh network!"}
        success = await mesh_manager.send_message(target_node, message)
        print(f"Message sent: {success}")


if __name__ == "__main__":
    asyncio.run(main())
