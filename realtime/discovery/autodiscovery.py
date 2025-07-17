import asyncio
import socket
import json
import logging
import time
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
import aiohttp
import platform

@dataclass
class PeerNode:
    """Represents a discovered peer node"""
    id: str
    address: str
    port: int
    service_type: str
    capabilities: List[str]
    last_seen: float
    version: str
    platform: str
    status: str = "discovered"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def is_stale(self, timeout: float = 30.0) -> bool:
        """Check if peer is stale based on last seen time"""
        return time.time() - self.last_seen > timeout

@dataclass 
class ServiceAnnouncement:
    """Service announcement for broadcasting"""
    node_id: str
    service_type: str
    address: str
    port: int
    capabilities: List[str]
    version: str
    platform: str
    timestamp: float
    
    def to_dict(self) -> Dict:
        return asdict(self)

class AutoDiscoveryService:
    """Auto-discovery service for finding and connecting to peers"""
    
    def __init__(self, node_id: str = None, service_port: int = 8000):
        self.node_id = node_id or str(uuid.uuid4())
        self.service_port = service_port
        self.discovery_port = 8001
        self.multicast_group = "224.0.0.251"
        self.multicast_port = 8002
        
        self.peers: Dict[str, PeerNode] = {}
        self.connections: Dict[str, aiohttp.ClientSession] = {}
        self.logger = logging.getLogger(__name__)
        
        self.discovery_interval = 5.0  # seconds
        self.cleanup_interval = 30.0   # seconds
        self.connection_timeout = 10.0 # seconds
        
        self.running = False
        self.discovery_task = None
        self.cleanup_task = None
        self.announcement_task = None
        
        # Service capabilities
        self.capabilities = [
            "resource_distribution",
            "truth_spreading", 
            "mesh_networking",
            "websocket_realtime",
            "event_system"
        ]
        
        # Network interfaces to scan
        self.scan_ranges = [
            "192.168.1.0/24",
            "192.168.0.0/24", 
            "10.0.0.0/24",
            "172.16.0.0/24"
        ]
        
    async def start(self):
        """Start the auto-discovery service"""
        if self.running:
            return
            
        self.running = True
        self.logger.info(f"Starting auto-discovery service for node {self.node_id}")
        
        # Start discovery tasks
        self.discovery_task = asyncio.create_task(self._discovery_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.announcement_task = asyncio.create_task(self._announcement_loop())
        
        # Start multicast listener
        asyncio.create_task(self._multicast_listener())
        
        self.logger.info("Auto-discovery service started")
    
    async def stop(self):
        """Stop the auto-discovery service"""
        if not self.running:
            return
            
        self.running = False
        self.logger.info("Stopping auto-discovery service")
        
        # Cancel tasks
        if self.discovery_task:
            self.discovery_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.announcement_task:
            self.announcement_task.cancel()
            
        # Close connections
        for session in self.connections.values():
            await session.close()
        self.connections.clear()
        
        self.logger.info("Auto-discovery service stopped")
    
    async def _discovery_loop(self):
        """Main discovery loop"""
        while self.running:
            try:
                await self._discover_peers()
                await asyncio.sleep(self.discovery_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Discovery loop error: {e}")
                await asyncio.sleep(1)
    
    async def _cleanup_loop(self):
        """Clean up stale peers"""
        while self.running:
            try:
                await self._cleanup_stale_peers()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(1)
    
    async def _announcement_loop(self):
        """Announce our service via multicast"""
        while self.running:
            try:
                await self._announce_service()
                await asyncio.sleep(self.discovery_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Announcement loop error: {e}")
                await asyncio.sleep(1)
    
    async def _discover_peers(self):
        """Discover peers using multiple methods"""
        # Method 1: Network scanning
        await self._scan_network()
        
        # Method 2: DNS-SD/Bonjour (if available)
        await self._dns_sd_discovery()
        
        # Method 3: Known service ports
        await self._port_scan_discovery()
    
    async def _scan_network(self):
        """Scan network ranges for Liberation System services"""
        tasks = []
        
        for network_range in self.scan_ranges:
            task = asyncio.create_task(self._scan_range(network_range))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _scan_range(self, network_range: str):
        """Scan a specific network range"""
        try:
            # Parse network range (simplified for common cases)
            if "/24" in network_range:
                base_ip = network_range.split("/")[0].rsplit(".", 1)[0]
                
                # Scan first 50 IPs to avoid being too aggressive
                tasks = []
                for i in range(1, 51):
                    ip = f"{base_ip}.{i}"
                    task = asyncio.create_task(self._check_host(ip))
                    tasks.append(task)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            self.logger.debug(f"Network scan error for {network_range}: {e}")
    
    async def _check_host(self, ip: str):
        """Check if a host is running Liberation System"""
        try:
            # Try common ports
            ports = [8000, 8080, 3000, 5000, 8001]
            
            for port in ports:
                try:
                    async with aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=2)
                    ) as session:
                        async with session.get(f"http://{ip}:{port}/") as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # Check if it's a Liberation System service
                                if self._is_liberation_service(data):
                                    await self._add_discovered_peer(ip, port, data)
                                    break
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Host check error for {ip}: {e}")
    
    def _is_liberation_service(self, data: Dict) -> bool:
        """Check if response indicates Liberation System service"""
        message = data.get("message", "").lower()
        features = data.get("features", [])
        
        return (
            "liberation" in message or
            "19t" in message or
            "19 trillion" in message or
            any("liberation" in str(f).lower() for f in features)
        )
    
    async def _add_discovered_peer(self, ip: str, port: int, service_data: Dict):
        """Add a discovered peer to our peer list"""
        try:
            peer_id = service_data.get("node_id", f"{ip}:{port}")
            
            if peer_id == self.node_id:
                return  # Don't add ourselves
            
            peer = PeerNode(
                id=peer_id,
                address=ip,
                port=port,
                service_type="liberation_system",
                capabilities=service_data.get("features", []),
                last_seen=time.time(),
                version=service_data.get("version", "unknown"),
                platform=platform.system(),
                status="discovered"
            )
            
            self.peers[peer_id] = peer
            self.logger.info(f"Discovered peer: {peer_id} at {ip}:{port}")
            
            # Attempt to connect
            await self._connect_to_peer(peer)
            
        except Exception as e:
            self.logger.error(f"Error adding peer {ip}:{port}: {e}")
    
    async def _connect_to_peer(self, peer: PeerNode):
        """Establish connection to a peer"""
        if peer.id in self.connections:
            return  # Already connected
            
        try:
            session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.connection_timeout)
            )
            
            # Test connection
            async with session.get(f"http://{peer.address}:{peer.port}/api/v1/system/status") as response:
                if response.status == 200:
                    self.connections[peer.id] = session
                    peer.status = "connected"
                    
                    self.logger.info(f"Connected to peer: {peer.id}")
                    
                    # Register with peer
                    await self._register_with_peer(peer)
                else:
                    await session.close()
                    
        except Exception as e:
            self.logger.error(f"Failed to connect to peer {peer.id}: {e}")
            peer.status = "failed"
    
    async def _register_with_peer(self, peer: PeerNode):
        """Register our node with a peer"""
        try:
            if peer.id not in self.connections:
                return
                
            session = self.connections[peer.id]
            
            registration_data = {
                "node_id": self.node_id,
                "address": self._get_local_ip(),
                "port": self.service_port,
                "capabilities": self.capabilities,
                "version": "1.0.0",
                "platform": platform.system()
            }
            
            async with session.post(
                f"http://{peer.address}:{peer.port}/api/v1/mesh/register",
                json=registration_data
            ) as response:
                if response.status == 200:
                    self.logger.info(f"Registered with peer: {peer.id}")
                else:
                    self.logger.warning(f"Failed to register with peer {peer.id}: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Registration error with peer {peer.id}: {e}")
    
    async def _dns_sd_discovery(self):
        """Discover services using DNS-SD (if available)"""
        try:
            # This would use libraries like python-zeroconf
            # For now, we'll implement a basic version
            pass
        except Exception as e:
            self.logger.debug(f"DNS-SD discovery error: {e}")
    
    async def _port_scan_discovery(self):
        """Scan for services on known ports"""
        try:
            # Get local network interfaces
            local_ips = self._get_network_interfaces()
            
            for local_ip in local_ips:
                # Scan local subnet
                network_base = ".".join(local_ip.split(".")[:-1])
                
                # Quick scan of nearby IPs
                for i in range(1, 11):  # Scan first 10 IPs
                    ip = f"{network_base}.{i}"
                    if ip != local_ip:
                        asyncio.create_task(self._check_host(ip))
                        
        except Exception as e:
            self.logger.debug(f"Port scan discovery error: {e}")
    
    def _get_network_interfaces(self) -> List[str]:
        """Get local network interface IPs"""
        interfaces = []
        try:
            # Get all network interfaces
            import netifaces
            
            for interface in netifaces.interfaces():
                addresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addresses:
                    for addr in addresses[netifaces.AF_INET]:
                        ip = addr['addr']
                        if not ip.startswith('127.') and not ip.startswith('169.254.'):
                            interfaces.append(ip)
        except ImportError:
            # Fallback method
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            interfaces.append(local_ip)
        except Exception as e:
            self.logger.debug(f"Network interface discovery error: {e}")
            
        return interfaces
    
    def _get_local_ip(self) -> str:
        """Get primary local IP address"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
            return local_ip
        except:
            return "127.0.0.1"
    
    async def _announce_service(self):
        """Announce our service via multicast"""
        try:
            announcement = ServiceAnnouncement(
                node_id=self.node_id,
                service_type="liberation_system",
                address=self._get_local_ip(),
                port=self.service_port,
                capabilities=self.capabilities,
                version="1.0.0",
                platform=platform.system(),
                timestamp=time.time()
            )
            
            message = json.dumps(announcement.to_dict())
            
            # Send multicast announcement
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            
            sock.sendto(message.encode(), (self.multicast_group, self.multicast_port))
            sock.close()
            
        except Exception as e:
            self.logger.debug(f"Service announcement error: {e}")
    
    async def _multicast_listener(self):
        """Listen for multicast service announcements"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", self.multicast_port))
            
            # Join multicast group
            mreq = socket.inet_aton(self.multicast_group) + socket.inet_aton("0.0.0.0")
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            sock.setblocking(False)
            
            while self.running:
                try:
                    data, addr = sock.recvfrom(1024)
                    await self._handle_multicast_message(data, addr)
                except socket.error:
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            self.logger.debug(f"Multicast listener error: {e}")
    
    async def _handle_multicast_message(self, data: bytes, addr: Tuple[str, int]):
        """Handle received multicast message"""
        try:
            message = json.loads(data.decode())
            
            # Check if it's a service announcement
            if message.get("service_type") == "liberation_system":
                node_id = message.get("node_id")
                
                if node_id and node_id != self.node_id:
                    # Add as discovered peer
                    await self._add_discovered_peer(
                        message.get("address", addr[0]),
                        message.get("port", 8000),
                        {
                            "node_id": node_id,
                            "features": message.get("capabilities", []),
                            "version": message.get("version", "unknown"),
                            "message": "liberation system service"
                        }
                    )
                    
        except Exception as e:
            self.logger.debug(f"Multicast message handling error: {e}")
    
    async def _cleanup_stale_peers(self):
        """Remove stale peers from the peer list"""
        stale_peers = []
        
        for peer_id, peer in self.peers.items():
            if peer.is_stale():
                stale_peers.append(peer_id)
        
        for peer_id in stale_peers:
            self.logger.info(f"Removing stale peer: {peer_id}")
            
            # Close connection if exists
            if peer_id in self.connections:
                await self.connections[peer_id].close()
                del self.connections[peer_id]
            
            del self.peers[peer_id]
    
    async def send_to_peer(self, peer_id: str, endpoint: str, data: Dict) -> Optional[Dict]:
        """Send data to a specific peer"""
        if peer_id not in self.connections or peer_id not in self.peers:
            return None
            
        try:
            session = self.connections[peer_id]
            peer = self.peers[peer_id]
            
            url = f"http://{peer.address}:{peer.port}{endpoint}"
            
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.warning(f"Peer {peer_id} returned status {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error sending to peer {peer_id}: {e}")
            return None
    
    async def broadcast_to_peers(self, endpoint: str, data: Dict) -> Dict[str, Optional[Dict]]:
        """Broadcast data to all connected peers"""
        results = {}
        
        tasks = []
        for peer_id in self.connections:
            task = asyncio.create_task(self.send_to_peer(peer_id, endpoint, data))
            tasks.append((peer_id, task))
        
        for peer_id, task in tasks:
            try:
                result = await task
                results[peer_id] = result
            except Exception as e:
                self.logger.error(f"Broadcast error to peer {peer_id}: {e}")
                results[peer_id] = None
        
        return results
    
    def get_peer_stats(self) -> Dict:
        """Get statistics about discovered peers"""
        connected_peers = sum(1 for p in self.peers.values() if p.status == "connected")
        
        return {
            "node_id": self.node_id,
            "total_peers": len(self.peers),
            "connected_peers": connected_peers,
            "active_connections": len(self.connections),
            "peer_details": [peer.to_dict() for peer in self.peers.values()]
        }
    
    def get_connected_peers(self) -> List[PeerNode]:
        """Get list of connected peers"""
        return [peer for peer in self.peers.values() if peer.status == "connected"]

# Global auto-discovery instance
auto_discovery = AutoDiscoveryService()
