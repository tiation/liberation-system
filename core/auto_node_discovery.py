# core/auto_node_discovery.py

import asyncio
import logging
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import socket
from pathlib import Path
import aiofiles

from core.dynamic_load_balancer import NodeCapacity, LoadBalancingManager
from core.system_integration import SystemNode, IntegratedHealthMonitor
from mesh.Mesh_Network.Mesh_Network import MeshNode, NetworkMessage, MessageType
from core.resource_distribution import SystemCore as ResourceSystem

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

class NodeDiscoveryMethod(Enum):
    BROADCAST = "broadcast"
    MULTICAST = "multicast"
    MESH_ANNOUNCEMENT = "mesh_announcement"
    HEARTBEAT_DISCOVERY = "heartbeat_discovery"
    PEER_REFERRAL = "peer_referral"

class NodeRegistrationStatus(Enum):
    DISCOVERED = "discovered"
    VALIDATING = "validating"
    REGISTERED = "registered"
    FAILED = "failed"
    REJECTED = "rejected"

@dataclass
class NodeAnnouncement:
    """Node announcement message structure"""
    node_id: str
    node_type: str
    host: str
    port: int
    capabilities: List[str]
    load_balancer_compatible: bool
    mesh_compatible: bool
    system_version: str
    timestamp: float
    discovery_method: NodeDiscoveryMethod
    health_endpoint: str = "/health"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PendingNode:
    """Pending node registration"""
    announcement: NodeAnnouncement
    discovery_time: float
    validation_attempts: int = 0
    status: NodeRegistrationStatus = NodeRegistrationStatus.DISCOVERED
    last_validation: Optional[float] = None
    validation_errors: List[str] = field(default_factory=list)

class AutoNodeDiscovery:
    """Automatic node discovery and registration system"""
    
    def __init__(self, system_integrator=None):
        self.system_integrator = system_integrator
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
        # Discovery configuration
        self.discovery_enabled = True
        self.auto_register_enabled = True
        self.validation_required = True
        self.max_validation_attempts = 3
        self.validation_timeout = 30.0
        
        # Node tracking
        self.pending_nodes: Dict[str, PendingNode] = {}
        self.registered_nodes: Dict[str, SystemNode] = {}
        self.discovery_history: List[NodeAnnouncement] = []
        
        # Network configuration
        self.broadcast_port = 8888
        self.multicast_group = '224.0.0.100'
        self.multicast_port = 8889
        
        # Message handlers
        self.announcement_handlers = {
            NodeDiscoveryMethod.BROADCAST: self._handle_broadcast_announcement,
            NodeDiscoveryMethod.MULTICAST: self._handle_multicast_announcement,
            NodeDiscoveryMethod.MESH_ANNOUNCEMENT: self._handle_mesh_announcement,
            NodeDiscoveryMethod.HEARTBEAT_DISCOVERY: self._handle_heartbeat_discovery,
            NodeDiscoveryMethod.PEER_REFERRAL: self._handle_peer_referral
        }
        
        # Statistics
        self.discovery_stats = {
            'total_discoveries': 0,
            'successful_registrations': 0,
            'failed_registrations': 0,
            'validation_failures': 0,
            'duplicate_discoveries': 0
        }
    
    async def start_discovery_services(self):
        """Start all discovery services"""
        try:
            self.console.print("🔍 [cyan]Starting automatic node discovery services...[/cyan]")
            
            # Start discovery listeners
            asyncio.create_task(self._broadcast_listener())
            asyncio.create_task(self._multicast_listener())
            asyncio.create_task(self._mesh_announcement_listener())
            asyncio.create_task(self._heartbeat_discovery_listener())
            
            # Start node validation and registration process
            asyncio.create_task(self._node_validation_processor())
            
            # Start periodic cleanup
            asyncio.create_task(self._cleanup_expired_nodes())
            
            self.console.print("✅ [green]Auto node discovery services started[/green]")
            
        except Exception as e:
            self.logger.error(f"Failed to start discovery services: {e}")
            raise
    
    async def _broadcast_listener(self):
        """Listen for broadcast node announcements"""
        try:
            # Create UDP socket for broadcast listening
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', self.broadcast_port))
            sock.setblocking(False)
            
            self.logger.info(f"Broadcast listener started on port {self.broadcast_port}")
            
            while self.discovery_enabled:
                try:
                    data, addr = await asyncio.get_event_loop().sock_recvfrom(sock, 4096)
                    
                    # Parse announcement
                    announcement_data = json.loads(data.decode())
                    announcement = NodeAnnouncement(**announcement_data)
                    announcement.discovery_method = NodeDiscoveryMethod.BROADCAST
                    
                    # Process announcement
                    await self._process_node_announcement(announcement, addr)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Broadcast listener error: {e}")
                    await asyncio.sleep(0.1)
            
            sock.close()
            
        except Exception as e:
            self.logger.error(f"Broadcast listener failed: {e}")
    
    async def _multicast_listener(self):
        """Listen for multicast node announcements"""
        try:
            # Create UDP socket for multicast listening
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Join multicast group
            import struct
            mreq = struct.pack("4sl", socket.inet_aton(self.multicast_group), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            sock.bind(('', self.multicast_port))
            sock.setblocking(False)
            
            self.logger.info(f"Multicast listener started on {self.multicast_group}:{self.multicast_port}")
            
            while self.discovery_enabled:
                try:
                    data, addr = await asyncio.get_event_loop().sock_recvfrom(sock, 4096)
                    
                    # Parse announcement
                    announcement_data = json.loads(data.decode())
                    announcement = NodeAnnouncement(**announcement_data)
                    announcement.discovery_method = NodeDiscoveryMethod.MULTICAST
                    
                    # Process announcement
                    await self._process_node_announcement(announcement, addr)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Multicast listener error: {e}")
                    await asyncio.sleep(0.1)
            
            sock.close()
            
        except Exception as e:
            self.logger.error(f"Multicast listener failed: {e}")
    
    async def _mesh_announcement_listener(self):
        """Listen for mesh network node announcements"""
        try:
            # This integrates with the existing mesh network to listen for announcements
            # We'll process mesh messages that contain node announcement data
            
            while self.discovery_enabled:
                try:
                    # Check if we have access to mesh nodes through system integrator
                    if self.system_integrator and hasattr(self.system_integrator, 'health_monitor'):
                        mesh_nodes = self.system_integrator.health_monitor.mesh_nodes
                        
                        for node_id, mesh_node in mesh_nodes.items():
                            # Check for new connection announcements
                            for peer_id, connection in mesh_node.connections.items():
                                if connection.get('status') == 'connected':
                                    # Create announcement from peer connection
                                    announcement = NodeAnnouncement(
                                        node_id=peer_id,
                                        node_type='mesh',
                                        host=connection.get('host', 'unknown'),
                                        port=connection.get('port', 0),
                                        capabilities=connection.get('capabilities', []),
                                        load_balancer_compatible=True,
                                        mesh_compatible=True,
                                        system_version='1.0.0',
                                        timestamp=time.time(),
                                        discovery_method=NodeDiscoveryMethod.MESH_ANNOUNCEMENT
                                    )
                                    
                                    await self._process_node_announcement(announcement, None)
                    
                    await asyncio.sleep(10)  # Check every 10 seconds
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Mesh announcement listener error: {e}")
                    await asyncio.sleep(5)
            
        except Exception as e:
            self.logger.error(f"Mesh announcement listener failed: {e}")
    
    async def _heartbeat_discovery_listener(self):
        """Discover nodes through heartbeat messages"""
        try:
            while self.discovery_enabled:
                try:
                    # Monitor heartbeat messages for new nodes
                    if self.system_integrator and hasattr(self.system_integrator, 'health_monitor'):
                        mesh_nodes = self.system_integrator.health_monitor.mesh_nodes
                        
                        for node_id, mesh_node in mesh_nodes.items():
                            # Process heartbeat messages that might contain node info
                            # This is a simplified approach - in practice, you'd hook into the message processing
                            pass
                    
                    await asyncio.sleep(15)  # Check every 15 seconds
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Heartbeat discovery listener error: {e}")
                    await asyncio.sleep(5)
            
        except Exception as e:
            self.logger.error(f"Heartbeat discovery listener failed: {e}")
    
    async def _process_node_announcement(self, announcement: NodeAnnouncement, source_addr):
        """Process a node announcement"""
        try:
            # Check if this is a duplicate discovery
            if announcement.node_id in self.registered_nodes:
                self.discovery_stats['duplicate_discoveries'] += 1
                return
            
            # Check if already pending
            if announcement.node_id in self.pending_nodes:
                # Update existing pending node
                self.pending_nodes[announcement.node_id].announcement = announcement
                self.pending_nodes[announcement.node_id].discovery_time = time.time()
                return
            
            # Create new pending node
            pending_node = PendingNode(
                announcement=announcement,
                discovery_time=time.time(),
                status=NodeRegistrationStatus.DISCOVERED
            )
            
            self.pending_nodes[announcement.node_id] = pending_node
            self.discovery_history.append(announcement)
            self.discovery_stats['total_discoveries'] += 1
            
            self.console.print(
                f"🔍 [yellow]Discovered new node: {announcement.node_id} "
                f"({announcement.node_type}) via {announcement.discovery_method.value}[/yellow]"
            )
            
            # Log discovery details
            self.logger.info(
                f"Node discovered: {announcement.node_id} at {announcement.host}:{announcement.port} "
                f"with capabilities: {announcement.capabilities}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to process node announcement: {e}")
    
    async def _node_validation_processor(self):
        """Process pending nodes for validation and registration"""
        try:
            while self.discovery_enabled:
                try:
                    # Process pending nodes
                    for node_id, pending_node in list(self.pending_nodes.items()):
                        if pending_node.status == NodeRegistrationStatus.DISCOVERED:
                            await self._validate_and_register_node(pending_node)
                        elif pending_node.status == NodeRegistrationStatus.VALIDATING:
                            # Check if validation timed out
                            if (pending_node.last_validation and 
                                time.time() - pending_node.last_validation > self.validation_timeout):
                                await self._handle_validation_timeout(pending_node)
                    
                    await asyncio.sleep(5)  # Process every 5 seconds
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Node validation processor error: {e}")
                    await asyncio.sleep(1)
            
        except Exception as e:
            self.logger.error(f"Node validation processor failed: {e}")
    
    async def _validate_and_register_node(self, pending_node: PendingNode):
        """Validate and register a pending node"""
        try:
            pending_node.status = NodeRegistrationStatus.VALIDATING
            pending_node.last_validation = time.time()
            pending_node.validation_attempts += 1
            
            announcement = pending_node.announcement
            
            # Perform validation checks
            validation_passed = True
            validation_errors = []
            
            # Check if validation is required
            if self.validation_required:
                # 1. Network connectivity validation
                if not await self._validate_network_connectivity(announcement):
                    validation_passed = False
                    validation_errors.append("Network connectivity failed")
                
                # 2. Health endpoint validation
                if not await self._validate_health_endpoint(announcement):
                    validation_passed = False
                    validation_errors.append("Health endpoint validation failed")
                
                # 3. Capability validation
                if not await self._validate_capabilities(announcement):
                    validation_passed = False
                    validation_errors.append("Capability validation failed")
                
                # 4. System compatibility validation
                if not await self._validate_system_compatibility(announcement):
                    validation_passed = False
                    validation_errors.append("System compatibility validation failed")
            
            if validation_passed:
                await self._register_validated_node(pending_node)
            else:
                await self._handle_validation_failure(pending_node, validation_errors)
                
        except Exception as e:
            self.logger.error(f"Node validation failed for {pending_node.announcement.node_id}: {e}")
            await self._handle_validation_failure(pending_node, [str(e)])
    
    async def _validate_network_connectivity(self, announcement: NodeAnnouncement) -> bool:
        """Validate network connectivity to the node"""
        try:
            # Simple TCP connection test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            result = sock.connect_ex((announcement.host, announcement.port))
            sock.close()
            
            return result == 0
            
        except Exception as e:
            self.logger.error(f"Network connectivity validation failed: {e}")
            return False
    
    async def _validate_health_endpoint(self, announcement: NodeAnnouncement) -> bool:
        """Validate the health endpoint of the node"""
        try:
            # This would typically make an HTTP request to the health endpoint
            # For now, we'll simulate a successful validation
            return True
            
        except Exception as e:
            self.logger.error(f"Health endpoint validation failed: {e}")
            return False
    
    async def _validate_capabilities(self, announcement: NodeAnnouncement) -> bool:
        """Validate the capabilities claimed by the node"""
        try:
            # Check if capabilities are valid
            valid_capabilities = [
                'resource_distribution', 'truth_spreading', 'mesh_routing',
                'load_balancing', 'data_storage', 'message_relay'
            ]
            
            for capability in announcement.capabilities:
                if capability not in valid_capabilities:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Capability validation failed: {e}")
            return False
    
    async def _validate_system_compatibility(self, announcement: NodeAnnouncement) -> bool:
        """Validate system compatibility"""
        try:
            # Check system version compatibility
            # For now, we'll accept all versions
            return True
            
        except Exception as e:
            self.logger.error(f"System compatibility validation failed: {e}")
            return False
    
    async def _register_validated_node(self, pending_node: PendingNode):
        """Register a validated node with the system"""
        try:
            announcement = pending_node.announcement
            
            # Create system node
            system_node = SystemNode(
                node_id=announcement.node_id,
                node_type=announcement.node_type,
                host=announcement.host,
                port=announcement.port,
                capabilities=announcement.capabilities,
                health_endpoint=announcement.health_endpoint,
                load_balancer_compatible=announcement.load_balancer_compatible,
                mesh_compatible=announcement.mesh_compatible
            )
            
            # Register with system integrator if available
            if self.system_integrator:
                await self._register_with_system_integrator(system_node, announcement)
            
            # Update status
            pending_node.status = NodeRegistrationStatus.REGISTERED
            self.registered_nodes[announcement.node_id] = system_node
            
            # Update statistics
            self.discovery_stats['successful_registrations'] += 1
            
            self.console.print(
                f"✅ [green]Node registered successfully: {announcement.node_id} "
                f"({announcement.node_type}) with capabilities: {announcement.capabilities}[/green]"
            )
            
            # Remove from pending nodes
            del self.pending_nodes[announcement.node_id]
            
        except Exception as e:
            self.logger.error(f"Failed to register node {pending_node.announcement.node_id}: {e}")
            await self._handle_validation_failure(pending_node, [str(e)])
    
    async def _register_with_system_integrator(self, system_node: SystemNode, announcement: NodeAnnouncement):
        """Register the node with the system integrator"""
        try:
            # Create appropriate system component based on node type
            if announcement.node_type == 'mesh':
                # Create mesh node
                mesh_node = MeshNode(
                    id=announcement.node_id,
                    host=announcement.host,
                    port=announcement.port
                )
                
                # Register with health monitor
                await self.system_integrator.health_monitor.register_mesh_node(
                    announcement.node_id, mesh_node
                )
                
                # Start mesh node
                asyncio.create_task(mesh_node.start_server())
                
            elif announcement.node_type == 'resource':
                # Create resource system
                resource_system = ResourceSystem()
                await resource_system.initialize()
                
                # Register with health monitor
                await self.system_integrator.health_monitor.register_resource_system(
                    announcement.node_id, resource_system
                )
            
            # Create node capacity configuration
            node_capacity = NodeCapacity(
                node_id=announcement.node_id,
                max_connections=announcement.metadata.get('max_connections', 1000),
                max_cpu_usage=announcement.metadata.get('max_cpu_usage', 80.0),
                max_memory_usage=announcement.metadata.get('max_memory_usage', 85.0),
                weight=announcement.metadata.get('weight', 1.0)
            )
            
            # Register with load balancer
            if announcement.node_type == 'mesh':
                health_check_func = lambda: self.system_integrator.health_monitor.mesh_node_health_check(announcement.node_id)
            else:
                health_check_func = lambda: self.system_integrator.health_monitor.resource_system_health_check(announcement.node_id)
            
            await self.system_integrator.load_balancer_manager.add_node(
                announcement.node_id, node_capacity, health_check_func
            )
            
            # Add to system nodes
            self.system_integrator.system_nodes[announcement.node_id] = system_node
            
        except Exception as e:
            self.logger.error(f"Failed to register with system integrator: {e}")
            raise
    
    async def _handle_validation_failure(self, pending_node: PendingNode, errors: List[str]):
        """Handle validation failure"""
        try:
            pending_node.validation_errors.extend(errors)
            
            if pending_node.validation_attempts >= self.max_validation_attempts:
                # Mark as failed
                pending_node.status = NodeRegistrationStatus.FAILED
                self.discovery_stats['failed_registrations'] += 1
                
                self.console.print(
                    f"❌ [red]Node registration failed: {pending_node.announcement.node_id} "
                    f"- Max attempts reached. Errors: {', '.join(errors)}[/red]"
                )
                
                # Remove from pending nodes
                del self.pending_nodes[pending_node.announcement.node_id]
            else:
                # Reset for retry
                pending_node.status = NodeRegistrationStatus.DISCOVERED
                self.discovery_stats['validation_failures'] += 1
                
                self.console.print(
                    f"⚠️ [yellow]Node validation failed: {pending_node.announcement.node_id} "
                    f"- Attempt {pending_node.validation_attempts}/{self.max_validation_attempts}. "
                    f"Errors: {', '.join(errors)}[/yellow]"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to handle validation failure: {e}")
    
    async def _handle_validation_timeout(self, pending_node: PendingNode):
        """Handle validation timeout"""
        try:
            await self._handle_validation_failure(pending_node, ["Validation timeout"])
            
        except Exception as e:
            self.logger.error(f"Failed to handle validation timeout: {e}")
    
    async def _cleanup_expired_nodes(self):
        """Clean up expired pending nodes"""
        try:
            cleanup_interval = 300  # 5 minutes
            
            while self.discovery_enabled:
                try:
                    current_time = time.time()
                    expired_nodes = []
                    
                    for node_id, pending_node in self.pending_nodes.items():
                        # Remove nodes that have been pending for too long
                        if current_time - pending_node.discovery_time > cleanup_interval:
                            expired_nodes.append(node_id)
                    
                    for node_id in expired_nodes:
                        del self.pending_nodes[node_id]
                        self.logger.info(f"Cleaned up expired pending node: {node_id}")
                    
                    await asyncio.sleep(60)  # Clean up every minute
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Cleanup process error: {e}")
                    await asyncio.sleep(5)
            
        except Exception as e:
            self.logger.error(f"Cleanup process failed: {e}")
    
    async def announce_node(self, node_info: Dict[str, Any], method: NodeDiscoveryMethod = NodeDiscoveryMethod.BROADCAST):
        """Announce a node to the network"""
        try:
            # Create announcement
            announcement = NodeAnnouncement(
                node_id=node_info['node_id'],
                node_type=node_info['node_type'],
                host=node_info['host'],
                port=node_info['port'],
                capabilities=node_info['capabilities'],
                load_balancer_compatible=node_info.get('load_balancer_compatible', True),
                mesh_compatible=node_info.get('mesh_compatible', True),
                system_version=node_info.get('system_version', '1.0.0'),
                timestamp=time.time(),
                discovery_method=method,
                health_endpoint=node_info.get('health_endpoint', '/health'),
                metadata=node_info.get('metadata', {})
            )
            
            # Send announcement based on method
            if method == NodeDiscoveryMethod.BROADCAST:
                await self._send_broadcast_announcement(announcement)
            elif method == NodeDiscoveryMethod.MULTICAST:
                await self._send_multicast_announcement(announcement)
            
            self.console.print(f"📢 [cyan]Node announced: {announcement.node_id} via {method.value}[/cyan]")
            
        except Exception as e:
            self.logger.error(f"Failed to announce node: {e}")
    
    async def _send_broadcast_announcement(self, announcement: NodeAnnouncement):
        """Send broadcast announcement"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            announcement_data = json.dumps(announcement.__dict__, default=str)
            sock.sendto(announcement_data.encode(), ('<broadcast>', self.broadcast_port))
            sock.close()
            
        except Exception as e:
            self.logger.error(f"Failed to send broadcast announcement: {e}")
    
    async def _send_multicast_announcement(self, announcement: NodeAnnouncement):
        """Send multicast announcement"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            
            announcement_data = json.dumps(announcement.__dict__, default=str)
            sock.sendto(announcement_data.encode(), (self.multicast_group, self.multicast_port))
            sock.close()
            
        except Exception as e:
            self.logger.error(f"Failed to send multicast announcement: {e}")
    
    def get_discovery_statistics(self) -> Dict[str, Any]:
        """Get discovery statistics"""
        return {
            'discovery_stats': self.discovery_stats.copy(),
            'pending_nodes': len(self.pending_nodes),
            'registered_nodes': len(self.registered_nodes),
            'discovery_history': len(self.discovery_history),
            'discovery_enabled': self.discovery_enabled,
            'auto_register_enabled': self.auto_register_enabled
        }
    
    def display_discovery_dashboard(self):
        """Display discovery dashboard"""
        try:
            # Main statistics table
            table = Table(title="🔍 Auto Node Discovery Dashboard", style="cyan")
            table.add_column("Metric", style="green")
            table.add_column("Value", style="yellow")
            table.add_column("Details", style="magenta")
            
            stats = self.get_discovery_statistics()
            
            table.add_row("Discovery Status", "🟢 Active" if self.discovery_enabled else "🔴 Inactive", "Service status")
            table.add_row("Total Discoveries", str(stats['discovery_stats']['total_discoveries']), "Nodes discovered")
            table.add_row("Successful Registrations", str(stats['discovery_stats']['successful_registrations']), "Nodes registered")
            table.add_row("Failed Registrations", str(stats['discovery_stats']['failed_registrations']), "Registration failures")
            table.add_row("Pending Nodes", str(stats['pending_nodes']), "Awaiting registration")
            table.add_row("Registered Nodes", str(stats['registered_nodes']), "Active nodes")
            table.add_row("Validation Failures", str(stats['discovery_stats']['validation_failures']), "Validation attempts failed")
            table.add_row("Duplicate Discoveries", str(stats['discovery_stats']['duplicate_discoveries']), "Already known nodes")
            
            self.console.print(table)
            
            # Pending nodes table
            if self.pending_nodes:
                pending_table = Table(title="Pending Node Registrations", style="yellow")
                pending_table.add_column("Node ID", style="green")
                pending_table.add_column("Type", style="cyan")
                pending_table.add_column("Status", style="yellow")
                pending_table.add_column("Attempts", style="magenta")
                pending_table.add_column("Discovery Method", style="blue")
                
                for node_id, pending_node in self.pending_nodes.items():
                    pending_table.add_row(
                        node_id,
                        pending_node.announcement.node_type,
                        pending_node.status.value,
                        str(pending_node.validation_attempts),
                        pending_node.announcement.discovery_method.value
                    )
                
                self.console.print(pending_table)
            
        except Exception as e:
            self.logger.error(f"Dashboard display error: {e}")
    
    async def shutdown(self):
        """Shutdown the discovery system"""
        self.discovery_enabled = False
        self.console.print("🛑 [yellow]Auto node discovery system shutting down...[/yellow]")

# Example usage
async def main():
    """Example usage of the auto node discovery system"""
    logging.basicConfig(level=logging.INFO)
    
    # Create discovery system
    discovery = AutoNodeDiscovery()
    
    # Start discovery services
    await discovery.start_discovery_services()
    
    # Announce a test node
    await discovery.announce_node({
        'node_id': 'test_node_001',
        'node_type': 'mesh',
        'host': 'localhost',
        'port': 8001,
        'capabilities': ['mesh_communication', 'truth_spreading'],
        'metadata': {'max_connections': 500}
    })
    
    # Display dashboard
    discovery.display_discovery_dashboard()
    
    # Keep running
    await asyncio.sleep(60)
    
    # Shutdown
    await discovery.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
