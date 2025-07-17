#!/usr/bin/env python3
"""
Network Connection Manager for Liberation System
Implements actual node connections with network operations for connection allocation
"""

import logging
import asyncio
import socket
import json
import time
import random
import threading
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque
import uuid

# Import existing mesh network components
from Mesh_Network.Mesh_Network import MeshNode, NetworkMessage, MessageType
from Mesh_Network.Advanced_Node_Discovery import (
    AdvancedMeshNode, 
    NetworkMetrics, 
    GeoLocation, 
    NodeCapabilities,
    GeolocationService,
    NetworkMetricsCollector
)

class ConnectionStatus(Enum):
    """Connection status enumeration"""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    FAILED = "failed"

class ConnectionPriority(Enum):
    """Connection priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ConnectionMetrics:
    """Metrics for individual connections"""
    latency: float = 0.0
    throughput: float = 0.0
    packet_loss: float = 0.0
    connection_time: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)
    bytes_sent: int = 0
    bytes_received: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    
    def calculate_health_score(self) -> float:
        """Calculate connection health score (0-1)"""
        latency_score = max(0, 1 - (self.latency / 1000))
        throughput_score = min(1, self.throughput / 100)
        loss_score = max(0, 1 - (self.packet_loss / 100))
        
        # Activity score based on recent activity
        time_since_activity = (datetime.now() - self.last_activity).total_seconds()
        activity_score = max(0, 1 - (time_since_activity / 300))  # 5 minutes max
        
        return (latency_score * 0.3 + throughput_score * 0.25 + 
                loss_score * 0.25 + activity_score * 0.2)

@dataclass
class ManagedConnection:
    """Managed connection with metrics and lifecycle"""
    id: str
    node_id: str
    socket: socket.socket
    status: ConnectionStatus = ConnectionStatus.IDLE
    priority: ConnectionPriority = ConnectionPriority.NORMAL
    metrics: ConnectionMetrics = field(default_factory=ConnectionMetrics)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    max_idle_time: int = 300  # 5 minutes
    retry_count: int = 0
    max_retries: int = 3
    
    def is_stale(self) -> bool:
        """Check if connection is stale and should be closed"""
        idle_time = (datetime.now() - self.last_used).total_seconds()
        return idle_time > self.max_idle_time
    
    def is_healthy(self) -> bool:
        """Check if connection is healthy"""
        return (self.status in [ConnectionStatus.IDLE, ConnectionStatus.ACTIVE] and
                self.metrics.calculate_health_score() > 0.5 and
                not self.is_stale())

class ConnectionPool:
    """Connection pool for managing multiple connections to nodes"""
    
    def __init__(self, max_connections: int = 50):
        self.max_connections = max_connections
        self.connections: Dict[str, ManagedConnection] = {}
        self.node_connections: Dict[str, Set[str]] = {}  # node_id -> connection_ids
        self.idle_connections: deque = deque()
        self.active_connections: Set[str] = set()
        self.lock = threading.RLock()
        self.logger = logging.getLogger(f"{__name__}.ConnectionPool")
        
    async def acquire_connection(self, node_id: str, priority: ConnectionPriority = ConnectionPriority.NORMAL) -> Optional[ManagedConnection]:
        """Acquire a connection from the pool"""
        with self.lock:
            # Try to find an existing idle connection to the node
            if node_id in self.node_connections:
                for conn_id in self.node_connections[node_id]:
                    if conn_id in self.connections:
                        conn = self.connections[conn_id]
                        if conn.status == ConnectionStatus.IDLE and conn.is_healthy():
                            conn.status = ConnectionStatus.ACTIVE
                            conn.last_used = datetime.now()
                            self.active_connections.add(conn_id)
                            try:
                                self.idle_connections.remove(conn_id)
                            except ValueError:
                                pass
                            self.logger.info(f"Acquired existing connection {conn_id} to node {node_id}")
                            return conn
            
            # No suitable connection found, return None to indicate new connection needed
            return None
    
    def add_connection(self, connection: ManagedConnection):
        """Add a new connection to the pool"""
        with self.lock:
            if len(self.connections) >= self.max_connections:
                self._evict_oldest_connection()
            
            self.connections[connection.id] = connection
            
            # Track by node
            if connection.node_id not in self.node_connections:
                self.node_connections[connection.node_id] = set()
            self.node_connections[connection.node_id].add(connection.id)
            
            if connection.status == ConnectionStatus.IDLE:
                self.idle_connections.append(connection.id)
            elif connection.status == ConnectionStatus.ACTIVE:
                self.active_connections.add(connection.id)
                
            self.logger.info(f"Added connection {connection.id} to node {connection.node_id}")
    
    def release_connection(self, connection_id: str):
        """Release a connection back to the pool"""
        with self.lock:
            if connection_id in self.connections:
                conn = self.connections[connection_id]
                if conn.is_healthy():
                    conn.status = ConnectionStatus.IDLE
                    conn.last_used = datetime.now()
                    self.active_connections.discard(connection_id)
                    self.idle_connections.append(connection_id)
                    self.logger.info(f"Released connection {connection_id}")
                else:
                    self.remove_connection(connection_id)
    
    def remove_connection(self, connection_id: str):
        """Remove a connection from the pool"""
        with self.lock:
            if connection_id in self.connections:
                conn = self.connections[connection_id]
                
                # Close the socket
                try:
                    conn.socket.close()
                except:
                    pass
                
                # Remove from tracking
                del self.connections[connection_id]
                self.active_connections.discard(connection_id)
                try:
                    self.idle_connections.remove(connection_id)
                except ValueError:
                    pass
                
                # Remove from node tracking
                if conn.node_id in self.node_connections:
                    self.node_connections[conn.node_id].discard(connection_id)
                    if not self.node_connections[conn.node_id]:
                        del self.node_connections[conn.node_id]
                
                self.logger.info(f"Removed connection {connection_id}")
    
    def _evict_oldest_connection(self):
        """Evict the oldest idle connection"""
        if self.idle_connections:
            oldest_id = self.idle_connections.popleft()
            self.remove_connection(oldest_id)
    
    def cleanup_stale_connections(self):
        """Clean up stale connections"""
        with self.lock:
            stale_connections = []
            for conn_id, conn in self.connections.items():
                if conn.is_stale() or not conn.is_healthy():
                    stale_connections.append(conn_id)
            
            for conn_id in stale_connections:
                self.remove_connection(conn_id)
                
            self.logger.info(f"Cleaned up {len(stale_connections)} stale connections")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self.lock:
            return {
                "total_connections": len(self.connections),
                "active_connections": len(self.active_connections),
                "idle_connections": len(self.idle_connections),
                "nodes_connected": len(self.node_connections),
                "max_connections": self.max_connections,
                "utilization": len(self.connections) / self.max_connections
            }

class NetworkConnectionManager:
    """Advanced network connection manager with actual node connections"""
    
    def __init__(self, local_node: AdvancedMeshNode, max_connections: int = 100):
        self.local_node = local_node
        self.connection_pool = ConnectionPool(max_connections)
        self.geolocation_service = GeolocationService()
        self.metrics_collector = NetworkMetricsCollector()
        self.logger = logging.getLogger(f"{__name__}.NetworkConnectionManager")
        
        # Connection allocation strategies
        self.allocation_strategies = {
            "round_robin": self._round_robin_allocation,
            "least_loaded": self._least_loaded_allocation,
            "geographic": self._geographic_allocation,
            "quality_based": self._quality_based_allocation
        }
        
        self.current_strategy = "quality_based"
        
        # Node tracking
        self.known_nodes: Dict[str, AdvancedMeshNode] = {}
        self.node_metrics: Dict[str, NetworkMetrics] = {}
        
        # Connection statistics
        self.connection_stats = {
            "total_connections_made": 0,
            "successful_connections": 0,
            "failed_connections": 0,
            "bytes_transferred": 0,
            "messages_sent": 0,
            "messages_received": 0
        }
        
        # Start background tasks
        self.running = True
        self.background_tasks = []
        
    async def start(self):
        """Start the connection manager"""
        self.logger.info("Starting Network Connection Manager")
        
        # Start background tasks
        self.background_tasks = [
            asyncio.create_task(self._periodic_cleanup()),
            asyncio.create_task(self._periodic_metrics_update()),
            asyncio.create_task(self._periodic_node_discovery())
        ]
        
        self.logger.info("Network Connection Manager started")
    
    async def stop(self):
        """Stop the connection manager"""
        self.logger.info("Stopping Network Connection Manager")
        self.running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close all connections
        with self.connection_pool.lock:
            for conn in list(self.connection_pool.connections.values()):
                try:
                    conn.socket.close()
                except:
                    pass
        
        self.logger.info("Network Connection Manager stopped")
    
    async def allocate_connection(self, target_node_id: str, priority: ConnectionPriority = ConnectionPriority.NORMAL) -> Optional[ManagedConnection]:
        """Allocate a connection to a target node"""
        if target_node_id not in self.known_nodes:
            self.logger.warning(f"Unknown node {target_node_id}")
            return None
        
        target_node = self.known_nodes[target_node_id]
        
        # Try to get existing connection from pool
        connection = await self.connection_pool.acquire_connection(target_node_id, priority)
        if connection:
            return connection
        
        # Create new connection
        connection = await self._create_connection(target_node, priority)
        if connection:
            self.connection_pool.add_connection(connection)
            self.connection_stats["total_connections_made"] += 1
            self.connection_stats["successful_connections"] += 1
            return connection
        
        self.connection_stats["failed_connections"] += 1
        return None
    
    async def _create_connection(self, target_node: AdvancedMeshNode, priority: ConnectionPriority) -> Optional[ManagedConnection]:
        """Create a new connection to a target node"""
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Set socket options based on priority
            if priority == ConnectionPriority.CRITICAL:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_PRIORITY, 6)
            elif priority == ConnectionPriority.HIGH:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_PRIORITY, 4)
            
            # Measure connection time
            start_time = time.time()
            
            # Connect to target node
            await asyncio.get_event_loop().sock_connect(sock, (target_node.host, target_node.port))
            
            connection_time = time.time() - start_time
            
            # Create managed connection
            connection = ManagedConnection(
                id=str(uuid.uuid4()),
                node_id=target_node.id,
                socket=sock,
                status=ConnectionStatus.ACTIVE,
                priority=priority,
                metrics=ConnectionMetrics(connection_time=connection_time)
            )
            
            # Send handshake
            await self._send_handshake(connection, target_node)
            
            # Measure initial latency
            latency = await self.metrics_collector.measure_latency(target_node.host, target_node.port)
            connection.metrics.latency = latency
            
            self.logger.info(f"Created connection {connection.id} to node {target_node.id} (latency: {latency:.2f}ms)")
            
            return connection
            
        except Exception as e:
            self.logger.error(f"Failed to create connection to {target_node.id}: {e}")
            try:
                sock.close()
            except:
                pass
            return None
    
    async def _send_handshake(self, connection: ManagedConnection, target_node: AdvancedMeshNode):
        """Send handshake message to establish connection"""
        handshake_message = NetworkMessage(
            id=str(uuid.uuid4()),
            type=MessageType.HANDSHAKE,
            source_node=self.local_node.id,
            target_node=target_node.id,
            payload={
                "host": self.local_node.host,
                "port": self.local_node.port,
                "capabilities": self.local_node.capabilities.supported_protocols,
                "node_type": self.local_node.node_type.value if hasattr(self.local_node, 'node_type') else 'standard'
            },
            timestamp=time.time()
        )
        
        await self._send_message(connection, handshake_message)
    
    async def _send_message(self, connection: ManagedConnection, message: NetworkMessage):
        """Send message through connection"""
        try:
            message_data = json.dumps({
                "id": message.id,
                "type": message.type.value,
                "source_node": message.source_node,
                "target_node": message.target_node,
                "payload": message.payload,
                "timestamp": message.timestamp,
                "ttl": message.ttl
            })
            
            await asyncio.get_event_loop().sock_sendall(connection.socket, message_data.encode())
            
            # Update metrics
            connection.metrics.bytes_sent += len(message_data)
            connection.metrics.messages_sent += 1
            connection.metrics.last_activity = datetime.now()
            
            self.connection_stats["messages_sent"] += 1
            self.connection_stats["bytes_transferred"] += len(message_data)
            
        except Exception as e:
            self.logger.error(f"Failed to send message on connection {connection.id}: {e}")
            connection.status = ConnectionStatus.FAILED
            raise
    
    async def send_message_to_node(self, target_node_id: str, message: NetworkMessage, priority: ConnectionPriority = ConnectionPriority.NORMAL) -> bool:
        """Send message to a specific node"""
        connection = await self.allocate_connection(target_node_id, priority)
        if not connection:
            return False
        
        try:
            await self._send_message(connection, message)
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message to {target_node_id}: {e}")
            return False
        finally:
            self.connection_pool.release_connection(connection.id)
    
    async def broadcast_message(self, message: NetworkMessage, priority: ConnectionPriority = ConnectionPriority.NORMAL) -> int:
        """Broadcast message to all known nodes"""
        successful_sends = 0
        
        tasks = []
        for node_id in self.known_nodes:
            if node_id != self.local_node.id:
                task = asyncio.create_task(self.send_message_to_node(node_id, message, priority))
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, bool) and result:
                successful_sends += 1
        
        self.logger.info(f"Broadcast message to {successful_sends}/{len(tasks)} nodes")
        return successful_sends
    
    def add_known_node(self, node: AdvancedMeshNode):
        """Add a node to the known nodes list"""
        self.known_nodes[node.id] = node
        self.node_metrics[node.id] = node.metrics
        self.logger.info(f"Added known node {node.id} at {node.host}:{node.port}")
    
    def remove_known_node(self, node_id: str):
        """Remove a node from known nodes"""
        if node_id in self.known_nodes:
            del self.known_nodes[node_id]
            del self.node_metrics[node_id]
            
            # Close all connections to this node
            if node_id in self.connection_pool.node_connections:
                for conn_id in list(self.connection_pool.node_connections[node_id]):
                    self.connection_pool.remove_connection(conn_id)
            
            self.logger.info(f"Removed known node {node_id}")
    
    def set_allocation_strategy(self, strategy: str):
        """Set the connection allocation strategy"""
        if strategy in self.allocation_strategies:
            self.current_strategy = strategy
            self.logger.info(f"Set allocation strategy to {strategy}")
        else:
            self.logger.warning(f"Unknown allocation strategy: {strategy}")
    
    # Allocation strategies
    async def _round_robin_allocation(self, nodes: List[AdvancedMeshNode]) -> AdvancedMeshNode:
        """Round-robin allocation strategy"""
        if not nodes:
            return None
        return nodes[self.connection_stats["total_connections_made"] % len(nodes)]
    
    async def _least_loaded_allocation(self, nodes: List[AdvancedMeshNode]) -> AdvancedMeshNode:
        """Least loaded allocation strategy"""
        if not nodes:
            return None
        
        def get_load(node):
            metrics = self.node_metrics.get(node.id, NetworkMetrics())
            return (metrics.cpu_usage + metrics.memory_usage + metrics.network_load) / 3
        
        return min(nodes, key=get_load)
    
    async def _geographic_allocation(self, nodes: List[AdvancedMeshNode]) -> AdvancedMeshNode:
        """Geographic proximity allocation strategy"""
        if not nodes:
            return None
        
        if not self.local_node.location:
            return nodes[0]
        
        def get_distance(node):
            if not node.location:
                return float('inf')
            return self.local_node.location.distance_to(node.location)
        
        return min(nodes, key=get_distance)
    
    async def _quality_based_allocation(self, nodes: List[AdvancedMeshNode]) -> AdvancedMeshNode:
        """Quality-based allocation strategy"""
        if not nodes:
            return None
        
        def get_quality_score(node):
            metrics = self.node_metrics.get(node.id, NetworkMetrics())
            return metrics.calculate_quality_score()
        
        return max(nodes, key=get_quality_score)
    
    # Background tasks
    async def _periodic_cleanup(self):
        """Periodic cleanup of stale connections"""
        while self.running:
            try:
                self.connection_pool.cleanup_stale_connections()
                await asyncio.sleep(60)  # Clean up every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic cleanup: {e}")
                await asyncio.sleep(60)
    
    async def _periodic_metrics_update(self):
        """Periodic update of node metrics"""
        while self.running:
            try:
                for node_id, node in self.known_nodes.items():
                    if node_id != self.local_node.id:
                        # Update latency measurement
                        latency = await self.metrics_collector.measure_latency(node.host, node.port)
                        if latency != float('inf'):
                            node.metrics.latency = latency
                
                await asyncio.sleep(30)  # Update every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic metrics update: {e}")
                await asyncio.sleep(30)
    
    async def _periodic_node_discovery(self):
        """Periodic node discovery"""
        while self.running:
            try:
                # Send discovery messages
                discovery_message = NetworkMessage(
                    id=str(uuid.uuid4()),
                    type=MessageType.DISCOVERY,
                    source_node=self.local_node.id,
                    target_node=None,
                    payload={
                        "host": self.local_node.host,
                        "port": self.local_node.port,
                        "timestamp": time.time()
                    },
                    timestamp=time.time()
                )
                
                await self.broadcast_message(discovery_message, ConnectionPriority.LOW)
                await asyncio.sleep(120)  # Discover every 2 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic node discovery: {e}")
                await asyncio.sleep(120)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        pool_stats = self.connection_pool.get_stats()
        
        return {
            "connection_pool": pool_stats,
            "connection_stats": self.connection_stats.copy(),
            "known_nodes": len(self.known_nodes),
            "current_strategy": self.current_strategy,
            "node_metrics": {
                node_id: {
                    "latency": metrics.latency,
                    "quality_score": metrics.calculate_quality_score()
                }
                for node_id, metrics in self.node_metrics.items()
            }
        }

# Example usage and testing
async def main():
    """Example usage of the Network Connection Manager"""
    logging.basicConfig(level=logging.INFO)
    
    # Create local node
    local_node = AdvancedMeshNode(
        id="local_node_001",
        host="127.0.0.1",
        port=8000
    )
    
    # Create connection manager
    connection_manager = NetworkConnectionManager(local_node)
    
    try:
        # Start the manager
        await connection_manager.start()
        
        # Add some test nodes
        test_nodes = [
            AdvancedMeshNode(id="node_001", host="127.0.0.1", port=8001),
            AdvancedMeshNode(id="node_002", host="127.0.0.1", port=8002),
            AdvancedMeshNode(id="node_003", host="127.0.0.1", port=8003)
        ]
        
        for node in test_nodes:
            connection_manager.add_known_node(node)
        
        # Test message sending
        test_message = NetworkMessage(
            id=str(uuid.uuid4()),
            type=MessageType.DATA,
            source_node=local_node.id,
            target_node="node_001",
            payload={"test": "data", "timestamp": time.time()},
            timestamp=time.time()
        )
        
        # Send message to specific node
        success = await connection_manager.send_message_to_node("node_001", test_message)
        print(f"Message sent to node_001: {success}")
        
        # Broadcast message
        broadcast_count = await connection_manager.broadcast_message(test_message)
        print(f"Broadcast to {broadcast_count} nodes")
        
        # Get statistics
        stats = connection_manager.get_statistics()
        print(f"Statistics: {json.dumps(stats, indent=2)}")
        
        # Run for a while to see background tasks
        await asyncio.sleep(10)
        
    finally:
        await connection_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())
