#!/usr/bin/env python3
"""
Enhanced Network Operations Manager for Liberation System
Provides advanced networking capabilities with load balancing, fault tolerance, and routing
"""

import logging
import asyncio
import socket
import json
import time
import hashlib
import random
from typing import Dict, List, Optional, Tuple, Any, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import uuid
import heapq
from concurrent.futures import ThreadPoolExecutor

# Import existing components
from Network_Connection_Manager import (
    NetworkConnectionManager, 
    ConnectionPriority, 
    ConnectionStatus,
    ManagedConnection
)
from Mesh_Network.Mesh_Network import NetworkMessage, MessageType
from Mesh_Network.Advanced_Node_Discovery import (
    AdvancedMeshNode, 
    NetworkMetrics, 
    GeoLocation,
    NodeType
)

class RoutingStrategy(Enum):
    """Network routing strategies"""
    DIRECT = "direct"
    SHORTEST_PATH = "shortest_path"
    LOWEST_LATENCY = "lowest_latency"
    HIGHEST_BANDWIDTH = "highest_bandwidth"
    LOAD_BALANCED = "load_balanced"
    FAULT_TOLERANT = "fault_tolerant"

class NetworkOperationResult(Enum):
    """Results of network operations"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    RETRY = "retry"
    PARTIAL = "partial"

@dataclass
class RouteMetrics:
    """Metrics for network routes"""
    total_latency: float = 0.0
    total_hops: int = 0
    bandwidth_bottleneck: float = float('inf')
    reliability_score: float = 1.0
    load_factor: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def calculate_route_score(self) -> float:
        """Calculate overall route quality score"""
        latency_score = max(0, 1 - (self.total_latency / 1000))
        hop_score = max(0, 1 - (self.total_hops / 10))
        bandwidth_score = min(1, self.bandwidth_bottleneck / 100)
        load_score = max(0, 1 - self.load_factor)
        
        return (latency_score * 0.3 + hop_score * 0.2 + 
                bandwidth_score * 0.25 + self.reliability_score * 0.15 + 
                load_score * 0.1)

@dataclass
class NetworkRoute:
    """Represents a network route between nodes"""
    source_node: str
    target_node: str
    path: List[str]
    metrics: RouteMetrics = field(default_factory=RouteMetrics)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    use_count: int = 0
    
    def is_valid(self) -> bool:
        """Check if route is still valid"""
        age = (datetime.now() - self.last_used).total_seconds()
        return age < 300 and len(self.path) >= 2  # 5 minutes validity

@dataclass
class NetworkOperation:
    """Represents a network operation"""
    id: str
    operation_type: str
    source_node: str
    target_nodes: List[str]
    priority: ConnectionPriority
    payload: Dict[str, Any]
    timeout: float = 30.0
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[NetworkOperationResult] = None
    error_message: Optional[str] = None

class NetworkLoadBalancer:
    """Advanced load balancer for network operations"""
    
    def __init__(self, connection_manager: NetworkConnectionManager):
        self.connection_manager = connection_manager
        self.node_loads: Dict[str, float] = defaultdict(float)
        self.node_capacities: Dict[str, float] = defaultdict(lambda: 100.0)
        self.active_operations: Dict[str, Set[str]] = defaultdict(set)  # node_id -> operation_ids
        self.logger = logging.getLogger(f"{__name__}.NetworkLoadBalancer")
        
    async def select_optimal_nodes(self, candidate_nodes: List[str], operation: NetworkOperation) -> List[str]:
        """Select optimal nodes based on current load and capacity"""
        if not candidate_nodes:
            return []
        
        # Calculate load scores for each node
        node_scores = []
        for node_id in candidate_nodes:
            if node_id in self.connection_manager.known_nodes:
                node = self.connection_manager.known_nodes[node_id]
                
                # Calculate load score
                current_load = self.node_loads.get(node_id, 0.0)
                capacity = self.node_capacities.get(node_id, 100.0)
                load_ratio = current_load / capacity
                
                # Calculate quality score
                metrics = self.connection_manager.node_metrics.get(node_id, NetworkMetrics())
                quality_score = metrics.calculate_quality_score()
                
                # Calculate distance score (if location available)
                distance_score = 1.0
                if (self.connection_manager.local_node.location and 
                    hasattr(node, 'location') and node.location):
                    distance = self.connection_manager.local_node.location.distance_to(node.location)
                    distance_score = max(0, 1 - (distance / 10000))  # Normalize by 10,000 km
                
                # Combined score
                combined_score = (
                    (1 - load_ratio) * 0.4 +  # Lower load is better
                    quality_score * 0.3 +      # Higher quality is better
                    distance_score * 0.2 +     # Closer is better
                    (1 - len(self.active_operations[node_id]) / 10) * 0.1  # Fewer operations is better
                )
                
                node_scores.append((node_id, combined_score))
        
        # Sort by score (highest first)
        node_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top nodes based on operation requirements
        selected_count = min(len(node_scores), max(1, len(operation.target_nodes)))
        selected_nodes = [node_id for node_id, _ in node_scores[:selected_count]]
        
        self.logger.info(f"Selected {len(selected_nodes)} nodes for operation {operation.id}")
        return selected_nodes
    
    async def update_node_load(self, node_id: str, load_delta: float):
        """Update node load"""
        self.node_loads[node_id] = max(0, self.node_loads[node_id] + load_delta)
        
    async def register_operation(self, node_id: str, operation_id: str):
        """Register an operation on a node"""
        self.active_operations[node_id].add(operation_id)
        await self.update_node_load(node_id, 1.0)
        
    async def unregister_operation(self, node_id: str, operation_id: str):
        """Unregister an operation from a node"""
        self.active_operations[node_id].discard(operation_id)
        await self.update_node_load(node_id, -1.0)

class NetworkRouter:
    """Advanced network router with multiple routing strategies"""
    
    def __init__(self, connection_manager: NetworkConnectionManager):
        self.connection_manager = connection_manager
        self.routing_table: Dict[Tuple[str, str], NetworkRoute] = {}
        self.route_cache: Dict[str, List[NetworkRoute]] = {}
        self.logger = logging.getLogger(f"{__name__}.NetworkRouter")
        
    async def find_route(self, source_node: str, target_node: str, strategy: RoutingStrategy = RoutingStrategy.SHORTEST_PATH) -> Optional[NetworkRoute]:
        """Find optimal route between nodes"""
        route_key = (source_node, target_node)
        
        # Check cache first
        if route_key in self.routing_table:
            route = self.routing_table[route_key]
            if route.is_valid():
                return route
            else:
                del self.routing_table[route_key]
        
        # Calculate new route based on strategy
        if strategy == RoutingStrategy.DIRECT:
            route = await self._find_direct_route(source_node, target_node)
        elif strategy == RoutingStrategy.SHORTEST_PATH:
            route = await self._find_shortest_path(source_node, target_node)
        elif strategy == RoutingStrategy.LOWEST_LATENCY:
            route = await self._find_lowest_latency_route(source_node, target_node)
        elif strategy == RoutingStrategy.HIGHEST_BANDWIDTH:
            route = await self._find_highest_bandwidth_route(source_node, target_node)
        elif strategy == RoutingStrategy.LOAD_BALANCED:
            route = await self._find_load_balanced_route(source_node, target_node)
        elif strategy == RoutingStrategy.FAULT_TOLERANT:
            route = await self._find_fault_tolerant_route(source_node, target_node)
        else:
            route = await self._find_shortest_path(source_node, target_node)
        
        # Cache the route
        if route:
            self.routing_table[route_key] = route
            
        return route
    
    async def _find_direct_route(self, source_node: str, target_node: str) -> Optional[NetworkRoute]:
        """Find direct route between nodes"""
        if target_node in self.connection_manager.known_nodes:
            target = self.connection_manager.known_nodes[target_node]
            metrics = self.connection_manager.node_metrics.get(target_node, NetworkMetrics())
            
            route_metrics = RouteMetrics(
                total_latency=metrics.latency,
                total_hops=1,
                bandwidth_bottleneck=metrics.bandwidth,
                reliability_score=metrics.calculate_quality_score()
            )
            
            return NetworkRoute(
                source_node=source_node,
                target_node=target_node,
                path=[source_node, target_node],
                metrics=route_metrics
            )
        return None
    
    async def _find_shortest_path(self, source_node: str, target_node: str) -> Optional[NetworkRoute]:
        """Find shortest path using Dijkstra's algorithm"""
        if target_node not in self.connection_manager.known_nodes:
            return None
        
        # Build graph
        graph = defaultdict(list)
        for node_id, node in self.connection_manager.known_nodes.items():
            for conn_id in node.connections:
                if conn_id in self.connection_manager.known_nodes:
                    graph[node_id].append(conn_id)
        
        # Dijkstra's algorithm
        distances = {node_id: float('inf') for node_id in self.connection_manager.known_nodes}
        distances[source_node] = 0
        previous = {}
        pq = [(0, source_node)]
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node == target_node:
                break
                
            if current_dist > distances[current_node]:
                continue
                
            for neighbor in graph[current_node]:
                distance = current_dist + 1  # Hop count
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct path
        if target_node not in previous and target_node != source_node:
            return None
        
        path = []
        current = target_node
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        
        # Calculate route metrics
        total_latency = sum(
            self.connection_manager.node_metrics.get(node_id, NetworkMetrics()).latency
            for node_id in path
        )
        
        route_metrics = RouteMetrics(
            total_latency=total_latency,
            total_hops=len(path) - 1,
            bandwidth_bottleneck=min(
                self.connection_manager.node_metrics.get(node_id, NetworkMetrics()).bandwidth or 100
                for node_id in path
            )
        )
        
        return NetworkRoute(
            source_node=source_node,
            target_node=target_node,
            path=path,
            metrics=route_metrics
        )
    
    async def _find_lowest_latency_route(self, source_node: str, target_node: str) -> Optional[NetworkRoute]:
        """Find route with lowest total latency"""
        # Similar to shortest path but using latency as weight
        if target_node not in self.connection_manager.known_nodes:
            return None
        
        # Build weighted graph
        graph = defaultdict(list)
        for node_id, node in self.connection_manager.known_nodes.items():
            metrics = self.connection_manager.node_metrics.get(node_id, NetworkMetrics())
            for conn_id in node.connections:
                if conn_id in self.connection_manager.known_nodes:
                    conn_metrics = self.connection_manager.node_metrics.get(conn_id, NetworkMetrics())
                    weight = metrics.latency + conn_metrics.latency
                    graph[node_id].append((conn_id, weight))
        
        # Dijkstra's with latency weights
        distances = {node_id: float('inf') for node_id in self.connection_manager.known_nodes}
        distances[source_node] = 0
        previous = {}
        pq = [(0, source_node)]
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node == target_node:
                break
                
            if current_dist > distances[current_node]:
                continue
                
            for neighbor, weight in graph[current_node]:
                distance = current_dist + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct path
        if target_node not in previous and target_node != source_node:
            return None
        
        path = []
        current = target_node
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        
        route_metrics = RouteMetrics(
            total_latency=distances[target_node],
            total_hops=len(path) - 1
        )
        
        return NetworkRoute(
            source_node=source_node,
            target_node=target_node,
            path=path,
            metrics=route_metrics
        )
    
    async def _find_highest_bandwidth_route(self, source_node: str, target_node: str) -> Optional[NetworkRoute]:
        """Find route with highest bandwidth bottleneck"""
        # Modified Dijkstra to maximize minimum bandwidth
        if target_node not in self.connection_manager.known_nodes:
            return None
        
        # Build graph with bandwidth weights
        graph = defaultdict(list)
        for node_id, node in self.connection_manager.known_nodes.items():
            metrics = self.connection_manager.node_metrics.get(node_id, NetworkMetrics())
            for conn_id in node.connections:
                if conn_id in self.connection_manager.known_nodes:
                    conn_metrics = self.connection_manager.node_metrics.get(conn_id, NetworkMetrics())
                    bandwidth = min(metrics.bandwidth or 100, conn_metrics.bandwidth or 100)
                    graph[node_id].append((conn_id, bandwidth))
        
        # Modified Dijkstra for maximum bandwidth
        bandwidths = {node_id: 0 for node_id in self.connection_manager.known_nodes}
        bandwidths[source_node] = float('inf')
        previous = {}
        pq = [(-float('inf'), source_node)]  # Negative for max heap
        
        while pq:
            current_bw, current_node = heapq.heappop(pq)
            current_bw = -current_bw
            
            if current_node == target_node:
                break
                
            if current_bw < bandwidths[current_node]:
                continue
                
            for neighbor, link_bw in graph[current_node]:
                new_bw = min(current_bw, link_bw)
                
                if new_bw > bandwidths[neighbor]:
                    bandwidths[neighbor] = new_bw
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (-new_bw, neighbor))
        
        # Reconstruct path
        if target_node not in previous and target_node != source_node:
            return None
        
        path = []
        current = target_node
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        
        route_metrics = RouteMetrics(
            total_hops=len(path) - 1,
            bandwidth_bottleneck=bandwidths[target_node]
        )
        
        return NetworkRoute(
            source_node=source_node,
            target_node=target_node,
            path=path,
            metrics=route_metrics
        )
    
    async def _find_load_balanced_route(self, source_node: str, target_node: str) -> Optional[NetworkRoute]:
        """Find route considering current load balance"""
        # First find multiple possible routes
        routes = []
        
        # Try different strategies
        for strategy in [RoutingStrategy.SHORTEST_PATH, RoutingStrategy.LOWEST_LATENCY]:
            route = await self.find_route(source_node, target_node, strategy)
            if route:
                routes.append(route)
        
        if not routes:
            return None
        
        # Score routes based on load and quality
        best_route = None
        best_score = -1
        
        for route in routes:
            load_score = 0
            for node_id in route.path:
                if node_id in self.connection_manager.connection_pool.node_connections:
                    active_conns = len(self.connection_manager.connection_pool.node_connections[node_id])
                    load_score += active_conns
            
            # Normalize load score
            load_score = load_score / len(route.path)
            
            # Combined score (lower load is better)
            combined_score = route.metrics.calculate_route_score() - (load_score * 0.1)
            
            if combined_score > best_score:
                best_score = combined_score
                best_route = route
        
        return best_route
    
    async def _find_fault_tolerant_route(self, source_node: str, target_node: str) -> Optional[NetworkRoute]:
        """Find route with fault tolerance considerations"""
        # Find multiple disjoint paths and select the most reliable
        primary_route = await self._find_shortest_path(source_node, target_node)
        if not primary_route:
            return None
        
        # Calculate reliability based on node health
        reliability_score = 1.0
        for node_id in primary_route.path:
            if node_id in self.connection_manager.known_nodes:
                node = self.connection_manager.known_nodes[node_id]
                metrics = self.connection_manager.node_metrics.get(node_id, NetworkMetrics())
                node_reliability = metrics.calculate_quality_score()
                reliability_score *= node_reliability
        
        primary_route.metrics.reliability_score = reliability_score
        return primary_route

class EnhancedNetworkOperations:
    """Enhanced network operations manager"""
    
    def __init__(self, connection_manager: NetworkConnectionManager):
        self.connection_manager = connection_manager
        self.load_balancer = NetworkLoadBalancer(connection_manager)
        self.router = NetworkRouter(connection_manager)
        self.operation_queue: asyncio.Queue = asyncio.Queue()
        self.active_operations: Dict[str, NetworkOperation] = {}
        self.completed_operations: deque = deque(maxlen=1000)
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.logger = logging.getLogger(f"{__name__}.EnhancedNetworkOperations")
        
        # Operation handlers
        self.operation_handlers = {
            "send_message": self._handle_send_message,
            "broadcast": self._handle_broadcast,
            "data_sync": self._handle_data_sync,
            "health_check": self._handle_health_check,
            "resource_request": self._handle_resource_request
        }
        
        self.running = False
        self.worker_tasks = []
        
    async def start(self):
        """Start the enhanced network operations"""
        self.logger.info("Starting Enhanced Network Operations")
        self.running = True
        
        # Start worker tasks
        self.worker_tasks = [
            asyncio.create_task(self._operation_worker(i))
            for i in range(5)  # 5 worker tasks
        ]
        
        self.logger.info("Enhanced Network Operations started")
    
    async def stop(self):
        """Stop the enhanced network operations"""
        self.logger.info("Stopping Enhanced Network Operations")
        self.running = False
        
        # Cancel worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        self.executor.shutdown(wait=True)
        self.logger.info("Enhanced Network Operations stopped")
    
    async def submit_operation(self, operation_type: str, target_nodes: List[str], 
                             payload: Dict[str, Any], priority: ConnectionPriority = ConnectionPriority.NORMAL,
                             timeout: float = 30.0) -> str:
        """Submit a network operation"""
        operation = NetworkOperation(
            id=str(uuid.uuid4()),
            operation_type=operation_type,
            source_node=self.connection_manager.local_node.id,
            target_nodes=target_nodes,
            priority=priority,
            payload=payload,
            timeout=timeout
        )
        
        self.active_operations[operation.id] = operation
        await self.operation_queue.put(operation)
        
        self.logger.info(f"Submitted operation {operation.id} of type {operation_type}")
        return operation.id
    
    async def _operation_worker(self, worker_id: int):
        """Worker task for processing operations"""
        self.logger.info(f"Starting operation worker {worker_id}")
        
        while self.running:
            try:
                # Get operation from queue
                operation = await asyncio.wait_for(self.operation_queue.get(), timeout=1.0)
                
                # Process operation
                await self._process_operation(operation)
                
                # Mark task as done
                self.operation_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in operation worker {worker_id}: {e}")
                await asyncio.sleep(1)
        
        self.logger.info(f"Operation worker {worker_id} stopped")
    
    async def _process_operation(self, operation: NetworkOperation):
        """Process a single operation"""
        operation.started_at = datetime.now()
        
        try:
            # Get handler for operation type
            handler = self.operation_handlers.get(operation.operation_type)
            if not handler:
                raise ValueError(f"Unknown operation type: {operation.operation_type}")
            
            # Select optimal nodes
            optimal_nodes = await self.load_balancer.select_optimal_nodes(
                operation.target_nodes, operation
            )
            
            if not optimal_nodes:
                raise ValueError("No available nodes for operation")
            
            # Register operation on selected nodes
            for node_id in optimal_nodes:
                await self.load_balancer.register_operation(node_id, operation.id)
            
            try:
                # Execute operation
                result = await asyncio.wait_for(
                    handler(operation, optimal_nodes),
                    timeout=operation.timeout
                )
                
                operation.result = result
                
            finally:
                # Unregister operation from nodes
                for node_id in optimal_nodes:
                    await self.load_balancer.unregister_operation(node_id, operation.id)
            
        except asyncio.TimeoutError:
            operation.result = NetworkOperationResult.TIMEOUT
            operation.error_message = "Operation timed out"
        except Exception as e:
            operation.result = NetworkOperationResult.FAILURE
            operation.error_message = str(e)
        
        finally:
            operation.completed_at = datetime.now()
            
            # Move to completed operations
            if operation.id in self.active_operations:
                del self.active_operations[operation.id]
            self.completed_operations.append(operation)
            
            self.logger.info(f"Operation {operation.id} completed with result: {operation.result}")
    
    async def _handle_send_message(self, operation: NetworkOperation, target_nodes: List[str]) -> NetworkOperationResult:
        """Handle send message operation"""
        if len(target_nodes) != 1:
            raise ValueError("Send message operation requires exactly one target node")
        
        target_node = target_nodes[0]
        
        # Create message
        message = NetworkMessage(
            id=str(uuid.uuid4()),
            type=MessageType.DATA,
            source_node=operation.source_node,
            target_node=target_node,
            payload=operation.payload,
            timestamp=time.time()
        )
        
        # Send message
        success = await self.connection_manager.send_message_to_node(
            target_node, message, operation.priority
        )
        
        return NetworkOperationResult.SUCCESS if success else NetworkOperationResult.FAILURE
    
    async def _handle_broadcast(self, operation: NetworkOperation, target_nodes: List[str]) -> NetworkOperationResult:
        """Handle broadcast operation"""
        # Create message
        message = NetworkMessage(
            id=str(uuid.uuid4()),
            type=MessageType.DATA,
            source_node=operation.source_node,
            target_node=None,
            payload=operation.payload,
            timestamp=time.time()
        )
        
        # Broadcast message
        successful_sends = await self.connection_manager.broadcast_message(message, operation.priority)
        
        if successful_sends > 0:
            return NetworkOperationResult.SUCCESS if successful_sends == len(target_nodes) else NetworkOperationResult.PARTIAL
        else:
            return NetworkOperationResult.FAILURE
    
    async def _handle_data_sync(self, operation: NetworkOperation, target_nodes: List[str]) -> NetworkOperationResult:
        """Handle data synchronization operation"""
        # Implementation for data sync
        sync_data = operation.payload.get("sync_data", {})
        
        successful_syncs = 0
        for node_id in target_nodes:
            message = NetworkMessage(
                id=str(uuid.uuid4()),
                type=MessageType.DATA,
                source_node=operation.source_node,
                target_node=node_id,
                payload={"sync_data": sync_data, "operation": "sync"},
                timestamp=time.time()
            )
            
            success = await self.connection_manager.send_message_to_node(
                node_id, message, operation.priority
            )
            
            if success:
                successful_syncs += 1
        
        if successful_syncs == len(target_nodes):
            return NetworkOperationResult.SUCCESS
        elif successful_syncs > 0:
            return NetworkOperationResult.PARTIAL
        else:
            return NetworkOperationResult.FAILURE
    
    async def _handle_health_check(self, operation: NetworkOperation, target_nodes: List[str]) -> NetworkOperationResult:
        """Handle health check operation"""
        healthy_nodes = 0
        
        for node_id in target_nodes:
            message = NetworkMessage(
                id=str(uuid.uuid4()),
                type=MessageType.HEARTBEAT,
                source_node=operation.source_node,
                target_node=node_id,
                payload={"health_check": True, "timestamp": time.time()},
                timestamp=time.time()
            )
            
            success = await self.connection_manager.send_message_to_node(
                node_id, message, operation.priority
            )
            
            if success:
                healthy_nodes += 1
        
        return NetworkOperationResult.SUCCESS if healthy_nodes == len(target_nodes) else NetworkOperationResult.PARTIAL
    
    async def _handle_resource_request(self, operation: NetworkOperation, target_nodes: List[str]) -> NetworkOperationResult:
        """Handle resource request operation"""
        resource_type = operation.payload.get("resource_type")
        amount = operation.payload.get("amount", 1)
        
        successful_requests = 0
        
        for node_id in target_nodes:
            message = NetworkMessage(
                id=str(uuid.uuid4()),
                type=MessageType.RESOURCE_BROADCAST,
                source_node=operation.source_node,
                target_node=node_id,
                payload={
                    "resource_type": resource_type,
                    "amount": amount,
                    "operation": "request"
                },
                timestamp=time.time()
            )
            
            success = await self.connection_manager.send_message_to_node(
                node_id, message, operation.priority
            )
            
            if success:
                successful_requests += 1
        
        return NetworkOperationResult.SUCCESS if successful_requests > 0 else NetworkOperationResult.FAILURE
    
    async def get_operation_status(self, operation_id: str) -> Optional[NetworkOperation]:
        """Get status of an operation"""
        # Check active operations
        if operation_id in self.active_operations:
            return self.active_operations[operation_id]
        
        # Check completed operations
        for operation in self.completed_operations:
            if operation.id == operation_id:
                return operation
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        active_ops_by_type = defaultdict(int)
        for operation in self.active_operations.values():
            active_ops_by_type[operation.operation_type] += 1
        
        completed_ops_by_result = defaultdict(int)
        for operation in self.completed_operations:
            if operation.result:
                completed_ops_by_result[operation.result.value] += 1
        
        return {
            "active_operations": len(self.active_operations),
            "completed_operations": len(self.completed_operations),
            "active_operations_by_type": dict(active_ops_by_type),
            "completed_operations_by_result": dict(completed_ops_by_result),
            "queue_size": self.operation_queue.qsize(),
            "load_balancer_stats": {
                "node_loads": dict(self.load_balancer.node_loads),
                "active_operations_per_node": {
                    node_id: len(ops) for node_id, ops in self.load_balancer.active_operations.items()
                }
            },
            "routing_table_size": len(self.router.routing_table)
        }

# Example usage
async def main():
    """Example usage of Enhanced Network Operations"""
    logging.basicConfig(level=logging.INFO)
    
    # Import and setup connection manager
    from Network_Connection_Manager import NetworkConnectionManager
    
    # Create local node
    local_node = AdvancedMeshNode(
        id="enhanced_node_001",
        host="127.0.0.1",
        port=8000
    )
    
    # Create connection manager
    connection_manager = NetworkConnectionManager(local_node)
    
    # Create enhanced operations
    enhanced_ops = EnhancedNetworkOperations(connection_manager)
    
    try:
        # Start services
        await connection_manager.start()
        await enhanced_ops.start()
        
        # Add test nodes
        test_nodes = [
            AdvancedMeshNode(id="node_001", host="127.0.0.1", port=8001),
            AdvancedMeshNode(id="node_002", host="127.0.0.1", port=8002),
            AdvancedMeshNode(id="node_003", host="127.0.0.1", port=8003)
        ]
        
        for node in test_nodes:
            connection_manager.add_known_node(node)
        
        # Submit operations
        op1 = await enhanced_ops.submit_operation(
            "send_message",
            ["node_001"],
            {"test": "data", "timestamp": time.time()},
            ConnectionPriority.HIGH
        )
        
        op2 = await enhanced_ops.submit_operation(
            "broadcast",
            ["node_001", "node_002", "node_003"],
            {"broadcast": "message", "timestamp": time.time()},
            ConnectionPriority.NORMAL
        )
        
        op3 = await enhanced_ops.submit_operation(
            "health_check",
            ["node_001", "node_002"],
            {"check_type": "full"},
            ConnectionPriority.LOW
        )
        
        # Wait for operations to complete
        await asyncio.sleep(5)
        
        # Get operation status
        for op_id in [op1, op2, op3]:
            status = await enhanced_ops.get_operation_status(op_id)
            print(f"Operation {op_id}: {status.result if status else 'Not found'}")
        
        # Get statistics
        stats = enhanced_ops.get_statistics()
        print(f"Enhanced Operations Statistics: {json.dumps(stats, indent=2)}")
        
    finally:
        await enhanced_ops.stop()
        await connection_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())
