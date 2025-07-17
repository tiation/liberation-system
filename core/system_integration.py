# core/system_integration.py

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import uuid

# Import our core components
from core.dynamic_load_balancer import (
    LoadBalancingManager, NodeCapacity, LoadBalancingTask, 
    LoadBalancingStrategy, NodeState, NodeMetrics
)
from core.resource_distribution import SystemCore as ResourceSystem
from mesh.Mesh_Network.Mesh_Network import MeshNode, EnhancedMesh, NetworkMessage, MessageType
from core.auto_node_discovery import AutoNodeDiscovery, NodeDiscoveryMethod

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

@dataclass
class SystemNode:
    """Unified system node representation"""
    node_id: str
    node_type: str  # 'resource', 'mesh', 'truth', 'load_balancer'
    host: str
    port: int
    capabilities: List[str]
    health_endpoint: str
    load_balancer_compatible: bool = True
    mesh_compatible: bool = True
    
class IntegratedHealthMonitor:
    """Integrated health monitoring across all system components"""
    
    def __init__(self):
        self.mesh_nodes: Dict[str, MeshNode] = {}
        self.resource_systems: Dict[str, ResourceSystem] = {}
        self.system_metrics: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
        self.console = Console()
    
    async def register_mesh_node(self, node_id: str, mesh_node: MeshNode):
        """Register a mesh node for monitoring"""
        self.mesh_nodes[node_id] = mesh_node
        self.logger.info(f"Registered mesh node {node_id} for health monitoring")
    
    async def register_resource_system(self, node_id: str, resource_system: ResourceSystem):
        """Register a resource system for monitoring"""
        self.resource_systems[node_id] = resource_system
        self.logger.info(f"Registered resource system {node_id} for health monitoring")
    
    async def mesh_node_health_check(self, node_id: str) -> Dict[str, Any]:
        """Comprehensive health check for mesh nodes"""
        if node_id not in self.mesh_nodes:
            return {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'response_time': 999999.0,
                'error_rate': 100.0,
                'active_connections': 0
            }
        
        mesh_node = self.mesh_nodes[node_id]
        
        try:
            # Get mesh node statistics
            stats = mesh_node.get_network_stats()
            
            # Simulate system resource metrics (in real implementation, these would come from system monitoring)
            cpu_usage = min(95.0, (stats['messages_sent'] + stats['messages_received']) / 100.0)
            memory_usage = min(90.0, stats['bytes_transferred'] / 1024.0 / 1024.0)  # MB
            response_time = 100.0 if mesh_node.is_healthy() else 5000.0
            error_rate = 0.0 if mesh_node.is_healthy() else 10.0
            
            health_data = {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'response_time': response_time,
                'error_rate': error_rate,
                'active_connections': stats['connections_active'],
                'messages_sent': stats['messages_sent'],
                'messages_received': stats['messages_received'],
                'bytes_transferred': stats['bytes_transferred'],
                'node_healthy': mesh_node.is_healthy()
            }
            
            self.system_metrics[node_id] = health_data
            return health_data
            
        except Exception as e:
            self.logger.error(f"Health check failed for mesh node {node_id}: {e}")
            return {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'response_time': 999999.0,
                'error_rate': 100.0,
                'active_connections': 0
            }
    
    async def resource_system_health_check(self, node_id: str) -> Dict[str, Any]:
        """Comprehensive health check for resource systems"""
        if node_id not in self.resource_systems:
            return {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'response_time': 999999.0,
                'error_rate': 100.0,
                'active_connections': 0
            }
        
        resource_system = self.resource_systems[node_id]
        
        try:
            # Get resource system statistics
            stats = await resource_system.get_system_stats()
            
            # Calculate health metrics based on system performance
            total_humans = stats.get('total_humans', 0)
            active_humans = stats.get('active_humans', 0)
            
            # Simple health calculation based on system activity
            cpu_usage = min(85.0, (total_humans / 1000.0) * 100)  # Scale based on load
            memory_usage = min(80.0, (stats.get('total_distributed', 0) / 1000000.0) * 100)
            response_time = 50.0 if resource_system.running else 10000.0
            error_rate = 0.0 if resource_system.running else 50.0
            
            health_data = {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'response_time': response_time,
                'error_rate': error_rate,
                'active_connections': active_humans,
                'total_humans': total_humans,
                'resources_distributed': stats.get('total_distributed', 0),
                'system_running': resource_system.running
            }
            
            self.system_metrics[node_id] = health_data
            return health_data
            
        except Exception as e:
            self.logger.error(f"Health check failed for resource system {node_id}: {e}")
            return {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'response_time': 999999.0,
                'error_rate': 100.0,
                'active_connections': 0
            }
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        overview = {
            'total_nodes': len(self.mesh_nodes) + len(self.resource_systems),
            'mesh_nodes': len(self.mesh_nodes),
            'resource_systems': len(self.resource_systems),
            'healthy_nodes': 0,
            'total_connections': 0,
            'total_messages': 0,
            'total_resources_distributed': 0.0
        }
        
        for node_id, metrics in self.system_metrics.items():
            if metrics.get('error_rate', 100) < 5.0:  # Consider healthy if error rate < 5%
                overview['healthy_nodes'] += 1
            
            overview['total_connections'] += metrics.get('active_connections', 0)
            overview['total_messages'] += metrics.get('messages_sent', 0) + metrics.get('messages_received', 0)
            overview['total_resources_distributed'] += metrics.get('resources_distributed', 0)
        
        return overview

class UnifiedTaskExecutor:
    """Unified task executor that can handle different types of system tasks"""
    
    def __init__(self, health_monitor: IntegratedHealthMonitor):
        self.health_monitor = health_monitor
        self.task_handlers = {}
        self.logger = logging.getLogger(__name__)
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a task handler for a specific task type"""
        self.task_handlers[task_type] = handler
        self.logger.info(f"Registered task handler for {task_type}")
    
    async def execute_task(self, task: LoadBalancingTask) -> bool:
        """Execute a task using the appropriate handler"""
        try:
            task_type = task.task_type
            
            if task_type not in self.task_handlers:
                self.logger.error(f"No handler registered for task type: {task_type}")
                return False
            
            handler = self.task_handlers[task_type]
            
            # Execute the task
            result = await handler(task)
            
            self.logger.info(f"Task {task.task_id} of type {task_type} executed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed for {task.task_id}: {e}")
            return False
    
    async def handle_resource_distribution_task(self, task: LoadBalancingTask) -> bool:
        """Handle resource distribution tasks"""
        try:
            human_id = task.payload.get('human_id')
            assigned_node = task.payload.get('assigned_node')
            
            if assigned_node in self.health_monitor.resource_systems:
                resource_system = self.health_monitor.resource_systems[assigned_node]
                
                # Add human to resource system if not already present
                if human_id:
                    await resource_system.add_human(human_id)
                
                # Trigger resource distribution
                await resource_system.resource_pool.distribute_weekly()
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Resource distribution task failed: {e}")
            return False
    
    async def handle_mesh_communication_task(self, task: LoadBalancingTask) -> bool:
        """Handle mesh network communication tasks"""
        try:
            message_data = task.payload.get('message_data')
            assigned_node = task.payload.get('assigned_node')
            
            if assigned_node in self.health_monitor.mesh_nodes:
                mesh_node = self.health_monitor.mesh_nodes[assigned_node]
                
                # Create and broadcast message
                message = NetworkMessage(
                    id=str(uuid.uuid4()),
                    type=MessageType(task.payload.get('message_type', 'data')),
                    source_node=assigned_node,
                    target_node=task.payload.get('target_node'),
                    payload=message_data,
                    timestamp=time.time()
                )
                
                await mesh_node.broadcast_message(message)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Mesh communication task failed: {e}")
            return False
    
    async def handle_truth_spreading_task(self, task: LoadBalancingTask) -> bool:
        """Handle truth spreading tasks"""
        try:
            truth_message = task.payload.get('truth_message')
            assigned_node = task.payload.get('assigned_node')
            
            if assigned_node in self.health_monitor.mesh_nodes:
                mesh_node = self.health_monitor.mesh_nodes[assigned_node]
                
                # Create truth propagation message
                message = NetworkMessage(
                    id=str(uuid.uuid4()),
                    type=MessageType.TRUTH_PROPAGATION,
                    source_node=assigned_node,
                    target_node=None,  # Broadcast to all
                    payload={'truth_content': truth_message},
                    timestamp=time.time()
                )
                
                await mesh_node.broadcast_message(message)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Truth spreading task failed: {e}")
            return False

class LiberationSystemIntegrator:
    """Main integration layer that coordinates all system components"""
    
    def __init__(self, config_path: str = "config/system_integration.json"):
        self.config_path = config_path
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.load_balancer_manager = LoadBalancingManager()
        self.health_monitor = IntegratedHealthMonitor()
        self.task_executor = UnifiedTaskExecutor(self.health_monitor)
        self.enhanced_mesh = EnhancedMesh()
        self.auto_discovery = AutoNodeDiscovery(system_integrator=self)
        
        # System state
        self.running = False
        self.system_nodes: Dict[str, SystemNode] = {}
        self.performance_metrics = {
            'system_uptime': 0,
            'total_tasks_processed': 0,
            'average_task_completion_time': 0.0,
            'system_efficiency': 0.0
        }
        
        # Setup task handlers
        self._setup_task_handlers()
    
    def _setup_task_handlers(self):
        """Setup task handlers for different task types"""
        self.task_executor.register_task_handler(
            'resource_distribution',
            self.task_executor.handle_resource_distribution_task
        )
        
        self.task_executor.register_task_handler(
            'mesh_communication',
            self.task_executor.handle_mesh_communication_task
        )
        
        self.task_executor.register_task_handler(
            'truth_spreading',
            self.task_executor.handle_truth_spreading_task
        )
    
    async def initialize(self):
        """Initialize the integrated system"""
        try:
            self.console.print("🚀 [cyan]Initializing Liberation System Integration...[/cyan]")
            
            # Load configuration
            await self._load_configuration()
            
            # Initialize load balancer
            await self.load_balancer_manager.initialize()
            
            # Initialize enhanced mesh
            asyncio.create_task(self.enhanced_mesh.run_enhanced())
            
            # Register system nodes
            await self._register_system_nodes()
            
            # Start integrated monitoring
            asyncio.create_task(self._run_integrated_monitoring())
            
            # Start auto node discovery
            await self.auto_discovery.start_discovery_services()
            
            self.running = True
            self.console.print("✅ [green]Liberation System Integration initialized successfully[/green]")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize integrated system: {e}")
            raise
    
    async def _load_configuration(self):
        """Load system configuration"""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                await self._create_default_configuration()
            
            # Load configuration (simplified for demo)
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
    
    async def _create_default_configuration(self):
        """Create default system configuration"""
        default_config = {
            "load_balancer": {
                "strategy": "adaptive",
                "health_check_interval": 10.0
            },
            "mesh_network": {
                "discovery_interval": 30.0,
                "optimization_interval": 60.0
            },
            "resource_distribution": {
                "distribution_interval": 3600.0,  # 1 hour
                "batch_size": 100
            },
            "monitoring": {
                "metrics_collection_interval": 5.0,
                "health_check_interval": 10.0
            }
        }
        
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to create default configuration: {e}")
    
    async def _register_system_nodes(self):
        """Register system nodes with load balancer"""
        try:
            # Create example mesh nodes
            for i in range(3):
                node_id = f"mesh_node_{i}"
                mesh_node = MeshNode(node_id, port=8000 + i)
                
                # Register with health monitor
                await self.health_monitor.register_mesh_node(node_id, mesh_node)
                
                # Start mesh node
                asyncio.create_task(mesh_node.start_server())
                
                # Create node capacity configuration
                node_capacity = NodeCapacity(
                    node_id=node_id,
                    max_connections=1000,
                    max_cpu_usage=80.0,
                    max_memory_usage=85.0,
                    weight=1.0
                )
                
                # Register with load balancer
                health_check_func = lambda nid=node_id: self.health_monitor.mesh_node_health_check(nid)
                await self.load_balancer_manager.add_node(node_id, node_capacity, health_check_func)
                
                self.system_nodes[node_id] = SystemNode(
                    node_id=node_id,
                    node_type='mesh',
                    host='localhost',
                    port=8000 + i,
                    capabilities=['mesh_communication', 'truth_spreading'],
                    health_endpoint=f'/health'
                )
            
            # Create resource distribution nodes
            for i in range(2):
                node_id = f"resource_node_{i}"
                resource_system = ResourceSystem()
                await resource_system.initialize()
                
                # Register with health monitor
                await self.health_monitor.register_resource_system(node_id, resource_system)
                
                # Create node capacity configuration
                node_capacity = NodeCapacity(
                    node_id=node_id,
                    max_connections=500,
                    max_cpu_usage=75.0,
                    max_memory_usage=80.0,
                    weight=0.8
                )
                
                # Register with load balancer
                health_check_func = lambda nid=node_id: self.health_monitor.resource_system_health_check(nid)
                await self.load_balancer_manager.add_node(node_id, node_capacity, health_check_func)
                
                self.system_nodes[node_id] = SystemNode(
                    node_id=node_id,
                    node_type='resource',
                    host='localhost',
                    port=9000 + i,
                    capabilities=['resource_distribution'],
                    health_endpoint=f'/health'
                )
            
            self.console.print(f"✅ [green]Registered {len(self.system_nodes)} system nodes[/green]")
            
        except Exception as e:
            self.logger.error(f"Failed to register system nodes: {e}")
            raise
    
    async def _run_integrated_monitoring(self):
        """Run integrated system monitoring"""
        start_time = time.time()
        
        while self.running:
            try:
                # Update system uptime
                self.performance_metrics['system_uptime'] = time.time() - start_time
                
                # Collect health metrics from all nodes
                for node_id in self.system_nodes:
                    if node_id in self.health_monitor.mesh_nodes:
                        await self.health_monitor.mesh_node_health_check(node_id)
                    elif node_id in self.health_monitor.resource_systems:
                        await self.health_monitor.resource_system_health_check(node_id)
                
                # Calculate system efficiency
                overview = await self.health_monitor.get_system_overview()
                self.performance_metrics['system_efficiency'] = (
                    overview['healthy_nodes'] / overview['total_nodes'] * 100
                    if overview['total_nodes'] > 0 else 0
                )
                
                await asyncio.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Integrated monitoring error: {e}")
                await asyncio.sleep(1)
    
    async def submit_system_task(self, task_type: str, payload: Dict[str, Any], priority: int = 1) -> Optional[str]:
        """Submit a task to the integrated system"""
        try:
            # Filter nodes based on task type capabilities
            compatible_nodes = [
                node for node in self.system_nodes.values()
                if task_type in node.capabilities
            ]
            
            if not compatible_nodes:
                self.logger.warning(f"No compatible nodes found for task type: {task_type}")
                return None
            
            # Submit task to load balancer
            task_id = await self.load_balancer_manager.submit_task(task_type, payload, priority)
            
            if task_id:
                self.performance_metrics['total_tasks_processed'] += 1
                self.console.print(f"📋 [green]System task {task_id} submitted successfully[/green]")
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit system task: {e}")
            return None
    
    async def announce_node_to_network(self, node_info: Dict[str, Any], method: NodeDiscoveryMethod = NodeDiscoveryMethod.BROADCAST) -> bool:
        """Announce a node to the network for automatic discovery"""
        try:
            await self.auto_discovery.announce_node(node_info, method)
            self.console.print(f"📢 [cyan]Node {node_info['node_id']} announced to network[/cyan]")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to announce node: {e}")
            return False
    
    async def get_discovery_stats(self) -> Dict[str, Any]:
        """Get node discovery statistics"""
        return self.auto_discovery.get_discovery_statistics()
    
    def display_discovery_dashboard(self):
        """Display node discovery dashboard"""
        self.auto_discovery.display_discovery_dashboard()
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Get load balancer statistics
            lb_stats = await self.load_balancer_manager.load_balancer.get_statistics()
            
            # Get health monitor overview
            health_overview = await self.health_monitor.get_system_overview()
            
            # Combine all metrics
            system_status = {
                'timestamp': datetime.now().isoformat(),
                'system_uptime': self.performance_metrics['system_uptime'],
                'total_nodes': len(self.system_nodes),
                'healthy_nodes': health_overview['healthy_nodes'],
                'load_balancer': lb_stats,
                'health_overview': health_overview,
                'performance_metrics': self.performance_metrics,
                'running': self.running
            }
            
            return system_status
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {'error': str(e)}
    
    def display_integrated_dashboard(self):
        """Display comprehensive integrated system dashboard"""
        try:
            layout = Layout()
            
            # System overview
            system_table = Table(title="🌟 Liberation System Overview", style="cyan")
            system_table.add_column("Component", style="green")
            system_table.add_column("Status", style="yellow")
            system_table.add_column("Details", style="magenta")
            
            status = asyncio.run(self.get_system_status())
            
            system_table.add_row("System Status", "🟢 Running" if self.running else "🔴 Stopped", f"Uptime: {status['system_uptime']:.0f}s")
            system_table.add_row("Total Nodes", str(status['total_nodes']), "Registered system nodes")
            system_table.add_row("Healthy Nodes", str(status['healthy_nodes']), "Operational nodes")
            system_table.add_row("Load Balancer", f"🔄 {status['load_balancer']['strategy']}", f"Queue: {status['load_balancer']['queue_size']}")
            system_table.add_row("Tasks Processed", str(self.performance_metrics['total_tasks_processed']), "Total completed")
            system_table.add_row("System Efficiency", f"{self.performance_metrics['system_efficiency']:.1f}%", "Overall health")
            
            self.console.print(system_table)
            
            # Node details
            node_table = Table(title="Node Details", style="cyan")
            node_table.add_column("Node ID", style="green")
            node_table.add_column("Type", style="yellow")
            node_table.add_column("Capabilities", style="magenta")
            node_table.add_column("Health", style="blue")
            
            for node_id, node in self.system_nodes.items():
                health_data = self.health_monitor.system_metrics.get(node_id, {})
                health_status = "🟢 Healthy" if health_data.get('error_rate', 100) < 5 else "🔴 Unhealthy"
                
                node_table.add_row(
                    node_id,
                    node.node_type,
                    ", ".join(node.capabilities),
                    health_status
                )
            
            self.console.print(node_table)
            
        except Exception as e:
            self.logger.error(f"Dashboard display error: {e}")
            self.console.print(f"[red]❌ Dashboard error: {e}[/red]")
    
    async def run_interactive_dashboard(self):
        """Run interactive dashboard with real-time updates"""
        while self.running:
            try:
                self.console.clear()
                self.display_integrated_dashboard()
                
                # Also display load balancer dashboard
                self.load_balancer_manager.load_balancer.display_dashboard()
                
                await asyncio.sleep(3)  # Update every 3 seconds
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"Interactive dashboard error: {e}")
                await asyncio.sleep(1)
    
    async def shutdown(self):
        """Shutdown the integrated system"""
        self.running = False
        
        self.console.print("🛑 [yellow]Shutting down Liberation System Integration...[/yellow]")
        
        # Shutdown load balancer
        await self.load_balancer_manager.shutdown()
        
        # Shutdown mesh nodes
        for mesh_node in self.health_monitor.mesh_nodes.values():
            await mesh_node.shutdown()
        
        # Shutdown resource systems
        for resource_system in self.health_monitor.resource_systems.values():
            resource_system.stop()
        
        self.console.print("✅ [green]Liberation System Integration shutdown complete[/green]")

# Example usage
async def main():
    """Example usage of the integrated system"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize integrated system
    integrator = LiberationSystemIntegrator()
    await integrator.initialize()
    
    # Submit example tasks
    await integrator.submit_system_task('resource_distribution', {'human_id': 'human_001'})
    await integrator.submit_system_task('truth_spreading', {'truth_message': 'Liberation is possible!'})
    await integrator.submit_system_task('mesh_communication', {
        'message_data': {'type': 'system_status', 'data': 'All systems operational'},
        'message_type': 'system_status'
    })
    
    # Run interactive dashboard
    await integrator.run_interactive_dashboard()

if __name__ == "__main__":
    asyncio.run(main())
