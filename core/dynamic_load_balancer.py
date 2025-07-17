# core/dynamic_load_balancer.py

import asyncio
import logging
import json
import time
import statistics
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import uuid
import hashlib
from pathlib import Path
import aiofiles
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESOURCE_BASED = "resource_based"
    RESPONSE_TIME = "response_time"
    ADAPTIVE = "adaptive"

class NodeState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"
    MAINTENANCE = "maintenance"
    FAILED = "failed"

@dataclass
class NodeMetrics:
    """Comprehensive node performance metrics"""
    node_id: str
    timestamp: float
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: float = 0.0
    active_connections: int = 0
    response_time: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    custom_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class NodeCapacity:
    """Node capacity configuration"""
    node_id: str
    max_connections: int = 1000
    max_cpu_usage: float = 80.0
    max_memory_usage: float = 85.0
    max_response_time: float = 5000.0  # milliseconds
    max_error_rate: float = 5.0  # percentage
    weight: float = 1.0
    priority: int = 1

@dataclass
class LoadBalancingTask:
    """Task to be distributed across nodes"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: int = 1
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    timeout: float = 30.0
    created_at: float = field(default_factory=time.time)
    attempts: int = 0
    max_attempts: int = 3

class HealthMonitor:
    """Advanced health monitoring for nodes"""
    
    def __init__(self, check_interval: float = 10.0):
        self.check_interval = check_interval
        self.health_checks: Dict[str, Callable] = {}
        self.node_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'response_time': 5000.0,
            'error_rate': 5.0
        }
        self.logger = logging.getLogger(__name__)
    
    async def register_health_check(self, node_id: str, check_function: Callable):
        """Register a health check function for a node"""
        self.health_checks[node_id] = check_function
    
    async def perform_health_check(self, node_id: str) -> Tuple[NodeState, NodeMetrics]:
        """Perform comprehensive health check on a node"""
        try:
            if node_id not in self.health_checks:
                return NodeState.FAILED, NodeMetrics(node_id=node_id, timestamp=time.time())
            
            # Execute health check
            check_result = await self.health_checks[node_id]()
            
            if not check_result:
                return NodeState.FAILED, NodeMetrics(node_id=node_id, timestamp=time.time())
            
            # Create metrics from check result
            metrics = NodeMetrics(
                node_id=node_id,
                timestamp=time.time(),
                **check_result
            )
            
            # Store metrics for trend analysis
            self.node_metrics[node_id].append(metrics)
            
            # Determine node state based on metrics
            state = self._determine_node_state(metrics)
            
            return state, metrics
            
        except Exception as e:
            self.logger.error(f"Health check failed for node {node_id}: {e}")
            return NodeState.FAILED, NodeMetrics(node_id=node_id, timestamp=time.time())
    
    def _determine_node_state(self, metrics: NodeMetrics) -> NodeState:
        """Determine node state based on metrics"""
        # Check for critical failures
        if metrics.cpu_usage > 95 or metrics.memory_usage > 95:
            return NodeState.FAILED
        
        # Check for overload conditions
        if (metrics.cpu_usage > self.alert_thresholds['cpu_usage'] or
            metrics.memory_usage > self.alert_thresholds['memory_usage'] or
            metrics.response_time > self.alert_thresholds['response_time']):
            return NodeState.OVERLOADED
        
        # Check for degraded performance
        if (metrics.cpu_usage > 60 or
            metrics.memory_usage > 70 or
            metrics.error_rate > 2.0):
            return NodeState.DEGRADED
        
        return NodeState.HEALTHY
    
    async def get_node_trends(self, node_id: str) -> Dict[str, float]:
        """Get performance trends for a node"""
        if node_id not in self.node_metrics or len(self.node_metrics[node_id]) < 2:
            return {}
        
        metrics_list = list(self.node_metrics[node_id])
        
        trends = {}
        for metric in ['cpu_usage', 'memory_usage', 'response_time', 'error_rate']:
            values = [getattr(m, metric) for m in metrics_list[-10:]]  # Last 10 readings
            if len(values) > 1:
                # Calculate trend (positive = increasing, negative = decreasing)
                trends[f'{metric}_trend'] = (values[-1] - values[0]) / len(values)
        
        return trends

class LoadBalancer:
    """Enterprise-grade dynamic load balancer"""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ADAPTIVE):
        self.strategy = strategy
        self.nodes: Dict[str, NodeCapacity] = {}
        self.node_states: Dict[str, NodeState] = {}
        self.health_monitor = HealthMonitor()
        self.task_queue = asyncio.Queue()
        self.active_tasks: Dict[str, LoadBalancingTask] = {}
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.strategy_weights = {
            LoadBalancingStrategy.ROUND_ROBIN: 0.2,
            LoadBalancingStrategy.LEAST_CONNECTIONS: 0.3,
            LoadBalancingStrategy.RESOURCE_BASED: 0.4,
            LoadBalancingStrategy.RESPONSE_TIME: 0.1
        }
        self.current_node_index = 0
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.statistics = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'average_response_time': 0.0,
            'nodes_online': 0
        }
    
    async def register_node(self, node_id: str, capacity: NodeCapacity, health_check: Callable):
        """Register a new node with the load balancer"""
        self.nodes[node_id] = capacity
        self.node_states[node_id] = NodeState.HEALTHY
        await self.health_monitor.register_health_check(node_id, health_check)
        self.logger.info(f"Registered node {node_id} with capacity {capacity.max_connections}")
    
    async def unregister_node(self, node_id: str):
        """Unregister a node from the load balancer"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            del self.node_states[node_id]
            self.logger.info(f"Unregistered node {node_id}")
    
    async def get_optimal_node(self, task: LoadBalancingTask) -> Optional[str]:
        """Get the optimal node for a task based on current strategy"""
        healthy_nodes = [
            node_id for node_id, state in self.node_states.items()
            if state in [NodeState.HEALTHY, NodeState.DEGRADED]
        ]
        
        if not healthy_nodes:
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return await self._round_robin_selection(healthy_nodes)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return await self._least_connections_selection(healthy_nodes)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return await self._weighted_round_robin_selection(healthy_nodes)
        elif self.strategy == LoadBalancingStrategy.RESOURCE_BASED:
            return await self._resource_based_selection(healthy_nodes, task)
        elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
            return await self._response_time_selection(healthy_nodes)
        elif self.strategy == LoadBalancingStrategy.ADAPTIVE:
            return await self._adaptive_selection(healthy_nodes, task)
        
        return healthy_nodes[0] if healthy_nodes else None
    
    async def _round_robin_selection(self, nodes: List[str]) -> str:
        """Simple round-robin selection"""
        if not nodes:
            return None
        
        selected = nodes[self.current_node_index % len(nodes)]
        self.current_node_index += 1
        return selected
    
    async def _least_connections_selection(self, nodes: List[str]) -> str:
        """Select node with least active connections"""
        if not nodes:
            return None
        
        node_connections = {}
        for node_id in nodes:
            # Count active tasks for this node
            active_count = sum(1 for task in self.active_tasks.values() 
                             if task.payload.get('assigned_node') == node_id)
            node_connections[node_id] = active_count
        
        return min(node_connections, key=node_connections.get)
    
    async def _weighted_round_robin_selection(self, nodes: List[str]) -> str:
        """Weighted round-robin based on node capacity"""
        if not nodes:
            return None
        
        # Calculate weights based on node capacity
        weights = []
        for node_id in nodes:
            capacity = self.nodes[node_id]
            weight = capacity.weight * (capacity.max_connections / 1000)
            weights.append(weight)
        
        # Weighted selection
        total_weight = sum(weights)
        if total_weight == 0:
            return nodes[0]
        
        r = hash(str(time.time())) % int(total_weight)
        cumulative_weight = 0
        
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if r < cumulative_weight:
                return nodes[i]
        
        return nodes[0]
    
    async def _resource_based_selection(self, nodes: List[str], task: LoadBalancingTask) -> str:
        """Select node based on resource requirements and availability"""
        if not nodes:
            return None
        
        best_node = None
        best_score = float('inf')
        
        for node_id in nodes:
            # Get recent metrics
            _, metrics = await self.health_monitor.perform_health_check(node_id)
            
            # Calculate resource utilization score
            cpu_score = metrics.cpu_usage / 100.0
            memory_score = metrics.memory_usage / 100.0
            
            # Factor in task requirements
            task_cpu_req = task.resource_requirements.get('cpu', 0.1)
            task_memory_req = task.resource_requirements.get('memory', 0.1)
            
            # Calculate fit score (lower is better)
            fit_score = (cpu_score + task_cpu_req) + (memory_score + task_memory_req)
            
            if fit_score < best_score:
                best_score = fit_score
                best_node = node_id
        
        return best_node
    
    async def _response_time_selection(self, nodes: List[str]) -> str:
        """Select node with best response time"""
        if not nodes:
            return None
        
        best_node = None
        best_time = float('inf')
        
        for node_id in nodes:
            # Get recent metrics
            _, metrics = await self.health_monitor.perform_health_check(node_id)
            
            if metrics.response_time < best_time:
                best_time = metrics.response_time
                best_node = node_id
        
        return best_node or nodes[0]
    
    async def _adaptive_selection(self, nodes: List[str], task: LoadBalancingTask) -> str:
        """Adaptive selection combining multiple strategies"""
        if not nodes:
            return None
        
        # Get candidates from different strategies
        candidates = {}
        
        # Round robin candidate
        rr_candidate = await self._round_robin_selection(nodes)
        candidates[rr_candidate] = self.strategy_weights[LoadBalancingStrategy.ROUND_ROBIN]
        
        # Least connections candidate
        lc_candidate = await self._least_connections_selection(nodes)
        candidates[lc_candidate] = candidates.get(lc_candidate, 0) + self.strategy_weights[LoadBalancingStrategy.LEAST_CONNECTIONS]
        
        # Resource-based candidate
        rb_candidate = await self._resource_based_selection(nodes, task)
        candidates[rb_candidate] = candidates.get(rb_candidate, 0) + self.strategy_weights[LoadBalancingStrategy.RESOURCE_BASED]
        
        # Response time candidate
        rt_candidate = await self._response_time_selection(nodes)
        candidates[rt_candidate] = candidates.get(rt_candidate, 0) + self.strategy_weights[LoadBalancingStrategy.RESPONSE_TIME]
        
        # Select highest weighted candidate
        return max(candidates, key=candidates.get)
    
    async def submit_task(self, task: LoadBalancingTask) -> bool:
        """Submit a task for load balancing"""
        try:
            await self.task_queue.put(task)
            self.statistics['total_tasks'] += 1
            self.logger.info(f"Task {task.task_id} submitted for processing")
            return True
        except Exception as e:
            self.logger.error(f"Failed to submit task {task.task_id}: {e}")
            return False
    
    async def process_tasks(self):
        """Main task processing loop"""
        while True:
            try:
                # Get task from queue
                task = await self.task_queue.get()
                
                # Find optimal node
                node_id = await self.get_optimal_node(task)
                
                if not node_id:
                    self.logger.warning(f"No healthy nodes available for task {task.task_id}")
                    await asyncio.sleep(1)
                    continue
                
                # Assign task to node
                task.payload['assigned_node'] = node_id
                self.active_tasks[task.task_id] = task
                
                # Execute task
                asyncio.create_task(self._execute_task(task))
                
            except Exception as e:
                self.logger.error(f"Error processing tasks: {e}")
                await asyncio.sleep(1)
    
    async def _execute_task(self, task: LoadBalancingTask):
        """Execute a task on the assigned node"""
        start_time = time.time()
        
        try:
            node_id = task.payload['assigned_node']
            
            # Simulate task execution (replace with actual task execution)
            await asyncio.sleep(0.1)
            
            # Record successful completion
            execution_time = time.time() - start_time
            self.performance_history[node_id].append(execution_time)
            
            # Update statistics
            self.statistics['successful_tasks'] += 1
            self._update_average_response_time(execution_time)
            
            self.logger.info(f"Task {task.task_id} completed on node {node_id} in {execution_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Task {task.task_id} failed: {e}")
            self.statistics['failed_tasks'] += 1
            
            # Retry logic
            task.attempts += 1
            if task.attempts < task.max_attempts:
                await asyncio.sleep(2 ** task.attempts)  # Exponential backoff
                await self.task_queue.put(task)
        
        finally:
            # Clean up
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
    
    def _update_average_response_time(self, execution_time: float):
        """Update average response time with new measurement"""
        total_tasks = self.statistics['successful_tasks']
        if total_tasks == 1:
            self.statistics['average_response_time'] = execution_time
        else:
            # Running average
            current_avg = self.statistics['average_response_time']
            self.statistics['average_response_time'] = (
                (current_avg * (total_tasks - 1) + execution_time) / total_tasks
            )
    
    async def monitor_health(self):
        """Continuous health monitoring loop"""
        while True:
            try:
                healthy_count = 0
                
                for node_id in self.nodes:
                    state, metrics = await self.health_monitor.perform_health_check(node_id)
                    previous_state = self.node_states.get(node_id)
                    self.node_states[node_id] = state
                    
                    if state in [NodeState.HEALTHY, NodeState.DEGRADED]:
                        healthy_count += 1
                    
                    # Log state changes
                    if previous_state and previous_state != state:
                        self.logger.info(f"Node {node_id} state changed: {previous_state} -> {state}")
                
                self.statistics['nodes_online'] = healthy_count
                
                # Auto-adjust strategy weights based on performance
                await self._adjust_strategy_weights()
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _adjust_strategy_weights(self):
        """Dynamically adjust strategy weights based on performance"""
        if len(self.performance_history) < 2:
            return
        
        # Calculate average performance for each strategy
        strategy_performance = {}
        
        for strategy in LoadBalancingStrategy:
            if strategy == LoadBalancingStrategy.ADAPTIVE:
                continue
            
            # Simple performance metric: lower response time is better
            avg_response_time = statistics.mean([
                statistics.mean(times) for times in self.performance_history.values()
                if len(times) > 0
            ]) if self.performance_history else 1.0
            
            strategy_performance[strategy] = 1.0 / (avg_response_time + 0.1)
        
        # Adjust weights based on performance
        total_performance = sum(strategy_performance.values())
        if total_performance > 0:
            for strategy, performance in strategy_performance.items():
                self.strategy_weights[strategy] = performance / total_performance
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive load balancing statistics"""
        return {
            'strategy': self.strategy.value,
            'total_nodes': len(self.nodes),
            'healthy_nodes': len([s for s in self.node_states.values() if s == NodeState.HEALTHY]),
            'degraded_nodes': len([s for s in self.node_states.values() if s == NodeState.DEGRADED]),
            'failed_nodes': len([s for s in self.node_states.values() if s == NodeState.FAILED]),
            'active_tasks': len(self.active_tasks),
            'queue_size': self.task_queue.qsize(),
            'statistics': self.statistics.copy(),
            'strategy_weights': {k.value: v for k, v in self.strategy_weights.items()}
        }
    
    def display_dashboard(self):
        """Display comprehensive load balancing dashboard"""
        # Main statistics table
        table = Table(title="🔄 Dynamic Load Balancer Dashboard", style="cyan")
        table.add_column("Metric", style="green")
        table.add_column("Value", style="yellow")
        table.add_column("Details", style="magenta")
        
        stats = asyncio.run(self.get_statistics())
        
        table.add_row("Strategy", stats['strategy'].title(), "Current load balancing strategy")
        table.add_row("Total Nodes", str(stats['total_nodes']), "Registered nodes")
        table.add_row("Healthy Nodes", str(stats['healthy_nodes']), "🟢 Operational")
        table.add_row("Degraded Nodes", str(stats['degraded_nodes']), "🟡 Performance issues")
        table.add_row("Failed Nodes", str(stats['failed_nodes']), "🔴 Offline")
        table.add_row("Active Tasks", str(stats['active_tasks']), "Currently processing")
        table.add_row("Queue Size", str(stats['queue_size']), "Pending tasks")
        table.add_row("Success Rate", f"{(stats['statistics']['successful_tasks']/(stats['statistics']['total_tasks'] or 1)*100):.1f}%", "Task completion rate")
        table.add_row("Avg Response", f"{stats['statistics']['average_response_time']:.2f}s", "Response time")
        
        self.console.print(table)
        
        # Node status table
        node_table = Table(title="Node Status", style="cyan")
        node_table.add_column("Node ID", style="green")
        node_table.add_column("State", style="yellow")
        node_table.add_column("Capacity", style="magenta")
        node_table.add_column("Weight", style="blue")
        
        for node_id, capacity in self.nodes.items():
            state = self.node_states.get(node_id, NodeState.FAILED)
            state_icon = {
                NodeState.HEALTHY: "🟢",
                NodeState.DEGRADED: "🟡",
                NodeState.OVERLOADED: "🟠",
                NodeState.FAILED: "🔴",
                NodeState.MAINTENANCE: "🔵"
            }[state]
            
            node_table.add_row(
                node_id,
                f"{state_icon} {state.value}",
                str(capacity.max_connections),
                f"{capacity.weight:.2f}"
            )
        
        self.console.print(node_table)

class LoadBalancingManager:
    """High-level manager for dynamic load balancing"""
    
    def __init__(self, config_path: str = "config/load_balancer.json"):
        self.config_path = config_path
        self.load_balancer = LoadBalancer()
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.running = False
    
    async def initialize(self):
        """Initialize the load balancing system"""
        try:
            # Load configuration
            await self._load_configuration()
            
            # Start monitoring and processing
            self.running = True
            
            # Start background tasks
            asyncio.create_task(self.load_balancer.process_tasks())
            asyncio.create_task(self.load_balancer.monitor_health())
            
            self.console.print("🚀 [green]Dynamic Load Balancer initialized successfully[/green]")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize load balancer: {e}")
            raise
    
    async def _load_configuration(self):
        """Load configuration from file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                async with aiofiles.open(config_file, 'r') as f:
                    config = json.loads(await f.read())
                    
                # Apply configuration
                strategy = LoadBalancingStrategy(config.get('strategy', 'adaptive'))
                self.load_balancer.strategy = strategy
                
                # Load node configurations
                for node_config in config.get('nodes', []):
                    capacity = NodeCapacity(**node_config)
                    # Note: Health check functions would need to be registered separately
                    
            else:
                # Create default configuration
                await self._create_default_config()
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            # Continue with defaults
    
    async def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "strategy": "adaptive",
            "nodes": [
                {
                    "node_id": "default_node_1",
                    "max_connections": 1000,
                    "max_cpu_usage": 80.0,
                    "max_memory_usage": 85.0,
                    "weight": 1.0,
                    "priority": 1
                }
            ],
            "health_check_interval": 10.0,
            "alert_thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "response_time": 5000.0,
                "error_rate": 5.0
            }
        }
        
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(default_config, indent=2))
                
        except Exception as e:
            self.logger.error(f"Failed to create default config: {e}")
    
    async def add_node(self, node_id: str, capacity: NodeCapacity, health_check: Callable):
        """Add a new node to the load balancer"""
        await self.load_balancer.register_node(node_id, capacity, health_check)
        self.console.print(f"✅ [green]Node {node_id} added to load balancer[/green]")
    
    async def remove_node(self, node_id: str):
        """Remove a node from the load balancer"""
        await self.load_balancer.unregister_node(node_id)
        self.console.print(f"🗑️  [yellow]Node {node_id} removed from load balancer[/yellow]")
    
    async def submit_task(self, task_type: str, payload: Dict[str, Any], priority: int = 1) -> str:
        """Submit a task for processing"""
        task = LoadBalancingTask(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            payload=payload,
            priority=priority
        )
        
        success = await self.load_balancer.submit_task(task)
        if success:
            self.console.print(f"📤 [green]Task {task.task_id} submitted[/green]")
            return task.task_id
        else:
            self.console.print(f"❌ [red]Failed to submit task[/red]")
            return None
    
    async def run_dashboard(self):
        """Run the interactive dashboard"""
        while self.running:
            try:
                # Clear screen and display dashboard
                self.console.clear()
                self.load_balancer.display_dashboard()
                
                # Wait before refresh
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"Dashboard error: {e}")
                await asyncio.sleep(1)
    
    async def shutdown(self):
        """Shutdown the load balancing system"""
        self.running = False
        self.console.print("🛑 [yellow]Shutting down load balancer...[/yellow]")

# Example usage and integration
async def main():
    """Example usage of the dynamic load balancer"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize load balancer
    manager = LoadBalancingManager()
    await manager.initialize()
    
    # Example health check function
    async def example_health_check():
        return {
            'cpu_usage': 45.0,
            'memory_usage': 60.0,
            'response_time': 150.0,
            'error_rate': 0.5,
            'active_connections': 42
        }
    
    # Add example nodes
    node1_capacity = NodeCapacity(
        node_id="node_001",
        max_connections=1000,
        max_cpu_usage=80.0,
        max_memory_usage=85.0,
        weight=1.0
    )
    
    node2_capacity = NodeCapacity(
        node_id="node_002",
        max_connections=500,
        max_cpu_usage=75.0,
        max_memory_usage=80.0,
        weight=0.8
    )
    
    await manager.add_node("node_001", node1_capacity, example_health_check)
    await manager.add_node("node_002", node2_capacity, example_health_check)
    
    # Submit example tasks
    for i in range(10):
        await manager.submit_task("resource_distribution", {"human_id": f"human_{i}"})
        await manager.submit_task("truth_spreading", {"message": f"Truth message {i}"})
    
    # Run dashboard
    await manager.run_dashboard()

if __name__ == "__main__":
    asyncio.run(main())
