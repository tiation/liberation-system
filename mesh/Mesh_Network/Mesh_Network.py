# Liberation System - Enterprise P2P Mesh Network
import logging
import asyncio
import socket
import json
import time
import hashlib
import random
from typing import Tuple, Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime
import uuid

@dataclass
class GeoLocation:
    """Geographical location data for nodes"""
    latitude: float
    longitude: float
    country: str = ""
    city: str = ""
    region: str = ""
    timezone: str = ""
    isp: str = ""
    
    def distance_to(self, other: 'GeoLocation') -> float:
        """Calculate distance between two locations in kilometers using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

@dataclass
class NetworkMetrics:
    """Network performance metrics for nodes"""
    latency: float = 0.0  # milliseconds
    bandwidth: float = 0.0  # Mbps
    packet_loss: float = 0.0  # percentage
    jitter: float = 0.0  # milliseconds
    uptime: float = 0.0  # percentage
    cpu_usage: float = 0.0  # percentage
    memory_usage: float = 0.0  # percentage
    network_load: float = 0.0  # percentage
    last_updated: datetime = field(default_factory=datetime.now)
    
    def calculate_quality_score(self) -> float:
        """Calculate overall network quality score (0-1)"""
        # Weighted quality calculation
        latency_score = max(0, 1 - (self.latency / 1000))  # Lower latency is better
        bandwidth_score = min(1, self.bandwidth / 100)  # Higher bandwidth is better
        loss_score = max(0, 1 - (self.packet_loss / 100))  # Lower packet loss is better
        uptime_score = self.uptime / 100  # Higher uptime is better
        
        # Weighted average
        quality = (latency_score * 0.3 + bandwidth_score * 0.25 + 
                  loss_score * 0.25 + uptime_score * 0.2)
        
        return min(1.0, max(0.0, quality))

@dataclass
class NodeCapabilities:
    """Node capabilities and resource information"""
    max_connections: int = 50
    storage_capacity: int = 1000  # MB
    processing_power: float = 1.0  # relative scale
    supported_protocols: List[str] = field(default_factory=lambda: ['tcp', 'udp', 'websocket'])
    trust_level: float = 1.0  # 0-1 scale
    specializations: List[str] = field(default_factory=list)  # e.g., ['relay', 'storage', 'compute']
    
class GeolocationService:
    """Service to fetch geolocation data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        
    async def get_location_by_ip(self, ip_address: str) -> Optional[GeoLocation]:
        """Get geolocation data for an IP address"""
        # Check cache first
        if ip_address in self.cache:
            cached_data, timestamp = self.cache[ip_address]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        try:
            # Use ipapi.co for geolocation (free tier)
            async with aiohttp.ClientSession() as session:
                url = f"https://ipapi.co/{ip_address}/json/"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        location = GeoLocation(
                            latitude=float(data.get('latitude', 0)),
                            longitude=float(data.get('longitude', 0)),
                            country=data.get('country_name', ''),
                            city=data.get('city', ''),
                            region=data.get('region', ''),
                            timezone=data.get('timezone', ''),
                            isp=data.get('org', '')
                        )
                        
                        # Cache the result
                        self.cache[ip_address] = (location, time.time())
                        return location
                        
        except Exception as e:
            logging.error(f"Failed to get geolocation for {ip_address}: {e}")
            
        return None
    
    async def get_local_location(self) -> Optional[GeoLocation]:
        """Get current system's geolocation"""
        try:
            # Get public IP first
            async with aiohttp.ClientSession() as session:
                async with session.get('https://ipapi.co/ip/') as response:
                    if response.status == 200:
                        public_ip = await response.text()
                        return await self.get_location_by_ip(public_ip.strip())
        except Exception as e:
            logging.error(f"Failed to get local location: {e}")
            
        return None

class NetworkMetricsCollector:
    """Collect network performance metrics"""
    
    def __init__(self):
        self.metrics_history = []
        self.max_history = 100
        
    async def measure_latency(self, target_ip: str, port: int = 80) -> float:
        """Measure network latency to a target"""
        try:
            start_time = time.time()
            
            # Create a socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            result = sock.connect_ex((target_ip, port))
            
            end_time = time.time()
            sock.close()
            
            if result == 0:
                return (end_time - start_time) * 1000  # Convert to milliseconds
            else:
                return float('inf')  # Connection failed
                
        except Exception as e:
            logging.error(f"Latency measurement failed for {target_ip}: {e}")
            return float('inf')
    
    async def measure_bandwidth(self, target_url: str) -> float:
        """Measure network bandwidth using HTTP download test"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(target_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        end_time = time.time()
                        
                        # Calculate bandwidth in Mbps
                        size_mb = len(content) / (1024 * 1024)
                        time_seconds = end_time - start_time
                        bandwidth = (size_mb * 8) / time_seconds  # Convert to Mbps
                        
                        return bandwidth
                        
        except Exception as e:
            logging.error(f"Bandwidth measurement failed for {target_url}: {e}")
            
        return 0.0
    
    def get_system_metrics(self) -> NetworkMetrics:
        """Get current system network metrics"""
        try:
            # Get CPU and memory usage
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            
            # Get network stats
            net_io = psutil.net_io_counters()
            
            # Calculate network load (simplified)
            network_load = min(100, (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024) * 10)
            
            return NetworkMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                network_load=network_load,
                uptime=100.0,  # Simplified - could be calculated from boot time
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logging.error(f"Failed to get system metrics: {e}")
            return NetworkMetrics()

class MessageType(Enum):
    DISCOVERY = "discovery"
    HANDSHAKE = "handshake"
    DATA = "data"
    HEARTBEAT = "heartbeat"
    RESOURCE_BROADCAST = "resource_broadcast"
    TRUTH_PROPAGATION = "truth_propagation"
    MESH_OPTIMIZATION = "mesh_optimization"
    SYSTEM_STATUS = "system_status"

@dataclass
class NetworkMessage:
    """Standard message format for P2P communication"""
    id: str
    type: MessageType
    source_node: str
    target_node: Optional[str]
    payload: Dict[str, Any]
    timestamp: float
    ttl: int = 10
    signature: Optional[str] = None

class MeshNode:
    """Enhanced mesh node with real P2P communication"""
    
    def __init__(self, id: str, host: str = "localhost", port: int = None):
        self.id = id
        self.host = host
        self.port = port or self._find_available_port()
        self.connections: Dict[str, Dict] = {}  # node_id -> connection_info
        self.data_store: Dict[str, Any] = {}
        self.transmission_power = 1.0
        self.status = "active"
        self.last_seen = time.time()
        self.server_socket = None
        self.client_sockets: Dict[str, socket.socket] = {}
        self.message_cache: Set[str] = set()
        self.routing_table: Dict[str, List[str]] = {}
        self.network_stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "bytes_transferred": 0,
            "connections_active": 0
        }
        self.logger = logging.getLogger(f"MeshNode-{self.id}")
        
    def _find_available_port(self) -> int:
        """Find an available port for the node"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def is_healthy(self) -> bool:
        """Check if node is functioning properly"""
        return (
            self.status == "active" and 
            self.transmission_power > 0.5 and
            time.time() - self.last_seen < 300  # 5 minute timeout
        )
    
    async def start_server(self):
        """Start the P2P server for incoming connections"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.server_socket.setblocking(False)
            
            self.logger.info(f"Node {self.id} started server on {self.host}:{self.port}")
            
            while self.status == "active":
                try:
                    client_socket, address = await asyncio.get_event_loop().sock_accept(self.server_socket)
                    asyncio.create_task(self._handle_client(client_socket, address))
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Server error: {e}")
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
    
    async def _handle_client(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Handle incoming client connection"""
        try:
            while True:
                data = await asyncio.get_event_loop().sock_recv(client_socket, 4096)
                if not data:
                    break
                    
                try:
                    message_data = json.loads(data.decode())
                    message = NetworkMessage(**message_data)
                    await self._process_message(message, client_socket)
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    
        except Exception as e:
            self.logger.error(f"Client handler error: {e}")
        finally:
            client_socket.close()
    
    async def connect_to_peer(self, peer_host: str, peer_port: int) -> bool:
        """Connect to a peer node"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            
            await asyncio.get_event_loop().sock_connect(sock, (peer_host, peer_port))
            
            # Send handshake
            handshake = NetworkMessage(
                id=str(uuid.uuid4()),
                type=MessageType.HANDSHAKE,
                source_node=self.id,
                target_node=None,
                payload={
                    "host": self.host,
                    "port": self.port,
                    "capabilities": ["resource_distribution", "truth_spreading", "mesh_routing"]
                },
                timestamp=time.time()
            )
            
            await self._send_message(sock, handshake)
            
            # Store connection
            peer_id = f"{peer_host}:{peer_port}"
            self.connections[peer_id] = {
                "host": peer_host,
                "port": peer_port,
                "socket": sock,
                "last_ping": time.time(),
                "status": "connected"
            }
            self.client_sockets[peer_id] = sock
            
            self.logger.info(f"Connected to peer {peer_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {peer_host}:{peer_port}: {e}")
            return False
    
    async def _send_message(self, sock: socket.socket, message: NetworkMessage):
        """Send a message through a socket"""
        try:
            message_json = json.dumps(asdict(message))
            await asyncio.get_event_loop().sock_sendall(sock, message_json.encode())
            self.network_stats["messages_sent"] += 1
            self.network_stats["bytes_transferred"] += len(message_json)
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
    
    async def broadcast_message(self, message: NetworkMessage):
        """Broadcast a message to all connected peers"""
        if message.id in self.message_cache:
            return  # Prevent message loops
        
        self.message_cache.add(message.id)
        
        # Clean old messages from cache
        if len(self.message_cache) > 1000:
            self.message_cache = set(list(self.message_cache)[-500:])
        
        for peer_id, connection in self.connections.items():
            if connection["status"] == "connected":
                try:
                    await self._send_message(connection["socket"], message)
                except Exception as e:
                    self.logger.error(f"Failed to send to {peer_id}: {e}")
                    connection["status"] = "disconnected"
    
    async def _process_message(self, message: NetworkMessage, sender_socket: socket.socket):
        """Process incoming message"""
        self.network_stats["messages_received"] += 1
        
        if message.type == MessageType.HANDSHAKE:
            await self._handle_handshake(message, sender_socket)
        elif message.type == MessageType.DISCOVERY:
            await self._handle_discovery(message)
        elif message.type == MessageType.DATA:
            await self._handle_data(message)
        elif message.type == MessageType.HEARTBEAT:
            await self._handle_heartbeat(message)
        elif message.type == MessageType.RESOURCE_BROADCAST:
            await self._handle_resource_broadcast(message)
        elif message.type == MessageType.TRUTH_PROPAGATION:
            await self._handle_truth_propagation(message)
        
        # Forward message if it's not for us and TTL > 0
        if message.target_node and message.target_node != self.id and message.ttl > 0:
            message.ttl -= 1
            await self._forward_message(message)
    
    async def _handle_handshake(self, message: NetworkMessage, sender_socket: socket.socket):
        """Handle handshake message"""
        peer_info = message.payload
        peer_id = message.source_node
        
        self.connections[peer_id] = {
            "host": peer_info["host"],
            "port": peer_info["port"],
            "socket": sender_socket,
            "last_ping": time.time(),
            "status": "connected",
            "capabilities": peer_info.get("capabilities", [])
        }
        
        self.logger.info(f"Handshake received from {peer_id}")
    
    async def _handle_discovery(self, message: NetworkMessage):
        """Handle node discovery message"""
        # Respond with our node info
        response = NetworkMessage(
            id=str(uuid.uuid4()),
            type=MessageType.HANDSHAKE,
            source_node=self.id,
            target_node=message.source_node,
            payload={
                "host": self.host,
                "port": self.port,
                "capabilities": ["resource_distribution", "truth_spreading", "mesh_routing"]
            },
            timestamp=time.time()
        )
        await self.broadcast_message(response)
    
    async def _handle_data(self, message: NetworkMessage):
        """Handle data message"""
        # Store data in local store
        key = message.payload.get("key")
        value = message.payload.get("value")
        if key and value:
            self.data_store[key] = value
            self.logger.info(f"Stored data: {key}")
    
    async def _handle_heartbeat(self, message: NetworkMessage):
        """Handle heartbeat message"""
        if message.source_node in self.connections:
            self.connections[message.source_node]["last_ping"] = time.time()
    
    async def _handle_resource_broadcast(self, message: NetworkMessage):
        """Handle resource distribution broadcast"""
        resource_info = message.payload
        self.logger.info(f"Resource broadcast received: {resource_info}")
        # Forward to other nodes
        await self.broadcast_message(message)
    
    async def _handle_truth_propagation(self, message: NetworkMessage):
        """Handle truth spreading message"""
        truth_content = message.payload
        self.logger.info(f"Truth propagation received: {truth_content}")
        # Forward to other nodes
        await self.broadcast_message(message)
    
    async def _forward_message(self, message: NetworkMessage):
        """Forward message to appropriate node"""
        # Simple forwarding - could be enhanced with routing table
        await self.broadcast_message(message)
    
    async def send_heartbeat(self):
        """Send heartbeat to all connected peers"""
        heartbeat = NetworkMessage(
            id=str(uuid.uuid4()),
            type=MessageType.HEARTBEAT,
            source_node=self.id,
            target_node=None,
            payload={"timestamp": time.time()},
            timestamp=time.time()
        )
        await self.broadcast_message(heartbeat)
    
    async def cleanup_stale_connections(self):
        """Clean up stale connections"""
        current_time = time.time()
        stale_connections = []
        
        for peer_id, connection in self.connections.items():
            if current_time - connection["last_ping"] > 300:  # 5 minutes
                stale_connections.append(peer_id)
        
        for peer_id in stale_connections:
            self.logger.info(f"Removing stale connection: {peer_id}")
            connection = self.connections.pop(peer_id, None)
            if connection and connection["socket"]:
                try:
                    connection["socket"].close()
                except:
                    pass
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        self.network_stats["connections_active"] = len([
            c for c in self.connections.values() if c["status"] == "connected"
        ])
        return self.network_stats.copy()
    
    async def shutdown(self):
        """Shutdown the node"""
        self.status = "shutting_down"
        
        # Close all client connections
        for sock in self.client_sockets.values():
            try:
                sock.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.logger.info(f"Node {self.id} shut down")

class ResilientMesh:
    def __init__(self):
        self.nodes: Dict[str, MeshNode] = {}
        self.routes: Dict[str, List[str]] = {}
        self.active_transfers = set()
        self.logger = logging.getLogger(__name__)

    async def _discover_nodes(self):
        try:
            for i in range(random.randint(1, 5)):
                node_id = f"node_{len(self.nodes)}"
                new_node = MeshNode(node_id)
                self.nodes[node_id] = new_node
                self.logger.info(f"Discovered new node: {node_id}")
        except Exception as e:
            self.logger.error(f"Node discovery failed: {e}")

    async def _optimize_connections(self):
        try:
            for node in self.nodes.values():
                if not node.is_healthy():
                    continue
                nearby = self._find_nearby_nodes(node.id)
                optimal = self._calculate_optimal_connections(nearby)
                node.connections.update(optimal)
        except Exception as e:
            self.logger.error(f"Connection optimization failed: {e}")
    
    def _find_nearby_nodes(self, node_id: str) -> List[str]:
        """Find nearby nodes for connection optimization"""
        # Simple implementation - return random subset of nodes
        other_nodes = [n for n in self.nodes.keys() if n != node_id]
        return random.sample(other_nodes, min(3, len(other_nodes)))
    
    def _calculate_optimal_connections(self, nearby_nodes: List[str]) -> set:
        """Calculate optimal connections for a node"""
        return set(nearby_nodes[:2])  # Connect to 2 nearest nodes

class NeuralMesh:
    def __init__(self):
        self.mesh = ResilientMesh()
        self.patterns = {}
        self.learning_rate = 0.01
        self.performance_history = []

    async def _observe_patterns(self):
        """Enhanced pattern observation"""
        current_performance = await self._measure_network_performance()
        self.performance_history.append(current_performance)
        
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]

    async def _measure_network_performance(self) -> float:
        """Measure overall network performance"""
        active_nodes = sum(1 for node in self.mesh.nodes.values() if node.is_healthy())
        total_nodes = len(self.mesh.nodes)
        return active_nodes / total_nodes if total_nodes > 0 else 0.0

class EnhancedMesh:
    def __init__(self):
        self.neural = NeuralMesh()
        self.features = {
            "self_repair": True,
            "load_balancing": True,
            "path_optimization": True,
            "knowledge_sharing": True
        }
        self.metrics = {
            "uptime": 0.0,
            "reliability": 0.0,
            "efficiency": 0.0
        }

    async def run_enhanced(self):
        """Enhanced run with metrics and monitoring"""
        try:
            await asyncio.gather(
                self._run_mesh(),
                self._run_learning(),
                self._run_optimization(),
                self._run_sharing(),
                self._monitor_health()
            )
        except Exception as e:
            logging.error(f"Enhanced mesh operation failed: {e}")

    async def _monitor_health(self):
        """New method to monitor system health"""
        while True:
            health_status = await self._check_system_health()
            if not health_status[0]:
                logging.warning(f"System health issue: {health_status[1]}")
            await asyncio.sleep(5)

    async def _check_system_health(self) -> Tuple[bool, str]:
        """Check overall system health"""
        if not self.neural.mesh.nodes:
            return False, "No nodes in network"
        return True, "System healthy"
    
    async def _run_mesh(self):
        """Run mesh network operations"""
        while True:
            await self.neural.mesh._discover_nodes()
            await self.neural.mesh._optimize_connections()
            await asyncio.sleep(60)
    
    async def _run_learning(self):
        """Run learning algorithms"""
        while True:
            await self.neural._observe_patterns()
            await asyncio.sleep(30)
    
    async def _run_optimization(self):
        """Run optimization processes"""
        while True:
            # Placeholder for optimization logic
            await asyncio.sleep(45)
    
    async def _run_sharing(self):
        """Run knowledge sharing"""
        while True:
            # Placeholder for sharing logic
            await asyncio.sleep(90)
