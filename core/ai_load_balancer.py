# core/ai_load_balancer.py

import asyncio
import logging
import numpy as np
import json
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import uuid
import statistics
from pathlib import Path
import aiofiles

from core.dynamic_load_balancer import (
    LoadBalancer, LoadBalancingStrategy, NodeCapacity, 
    LoadBalancingTask, NodeState, NodeMetrics
)
# from core.auto_node_discovery import AutoNodeDiscovery  # Avoid circular import

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

class PredictionModel(Enum):
    LINEAR_REGRESSION = "linear_regression"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"

class ScalingDecision(Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"
    EMERGENCY_SCALE = "emergency_scale"

@dataclass
class TrafficPattern:
    """Represents learned traffic patterns"""
    pattern_id: str
    time_of_day: int  # 0-23
    day_of_week: int  # 0-6
    load_factor: float
    duration_minutes: int
    confidence: float
    historical_data: List[float] = field(default_factory=list)

@dataclass
class ScalingPrediction:
    """Represents a scaling prediction"""
    prediction_id: str
    timestamp: float
    predicted_load: float
    confidence: float
    recommended_action: ScalingDecision
    target_nodes: int
    reasoning: str
    urgency: int  # 1-10

@dataclass
class NodePerformanceProfile:
    """Comprehensive node performance profile"""
    node_id: str
    avg_response_time: float
    throughput_capacity: float
    reliability_score: float
    cost_efficiency: float
    specialization_scores: Dict[str, float] = field(default_factory=dict)
    historical_performance: deque = field(default_factory=lambda: deque(maxlen=1000))

class IntelligentResourcePredictor:
    """AI-powered resource demand predictor"""
    
    def __init__(self, prediction_model: PredictionModel = PredictionModel.ENSEMBLE):
        self.prediction_model = prediction_model
        self.traffic_patterns: Dict[str, TrafficPattern] = {}
        self.historical_data: deque = deque(maxlen=10000)
        self.learning_rate = 0.01
        self.confidence_threshold = 0.7
        self.logger = logging.getLogger(__name__)
        self.console = Console()
        
            # Neural network weights (simplified)
        self.neural_weights = {
            'hidden_layer': np.random.randn(5, 10),
            'output_layer': np.random.randn(10, 1)
        }
    
    async def record_traffic_data(self, current_load: float, active_nodes: int, response_time: float):
        """Record traffic data for learning"""
        now = datetime.now()
        data_point = {
            'timestamp': time.time(),
            'load': current_load,
            'nodes': active_nodes,
            'response_time': response_time,
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'day_of_month': now.day,
            'month': now.month
        }
        
        self.historical_data.append(data_point)
        
        # Learn patterns
        await self._learn_traffic_patterns(data_point)
    
    async def _learn_traffic_patterns(self, data_point: Dict[str, Any]):
        """Learn traffic patterns from historical data"""
        try:
            hour = data_point['hour']
            day_of_week = data_point['day_of_week']
            pattern_key = f"{day_of_week}_{hour}"
            
            if pattern_key not in self.traffic_patterns:
                self.traffic_patterns[pattern_key] = TrafficPattern(
                    pattern_id=pattern_key,
                    time_of_day=hour,
                    day_of_week=day_of_week,
                    load_factor=data_point['load'],
                    duration_minutes=60,
                    confidence=0.1
                )
            
            pattern = self.traffic_patterns[pattern_key]
            pattern.historical_data.append(data_point['load'])
            
            # Update pattern with exponential smoothing
            alpha = 0.3
            pattern.load_factor = alpha * data_point['load'] + (1 - alpha) * pattern.load_factor
            pattern.confidence = min(1.0, pattern.confidence + 0.01)
            
            # Update neural network weights
            await self._update_neural_network(data_point)
            
        except Exception as e:
            self.logger.error(f"Error learning traffic patterns: {e}")
    
    async def _update_neural_network(self, data_point: Dict[str, Any]):
        """Update neural network with new data"""
        try:
            # Simplified neural network update
            features = np.array([
                data_point['hour'] / 24.0,
                data_point['day_of_week'] / 7.0,
                data_point['nodes'] / 100.0,
                data_point['response_time'] / 1000.0,
                data_point['load']
            ]).reshape(1, -1)
            
            # Forward pass (simplified)
            hidden = np.tanh(np.dot(features, self.neural_weights['hidden_layer']))
            output = np.dot(hidden, self.neural_weights['output_layer'])
            
            # Backward pass (simplified gradient update)
            error = data_point['load'] - output[0][0]
            self.neural_weights['output_layer'] += self.learning_rate * error * hidden.T
            
        except Exception as e:
            self.logger.error(f"Neural network update failed: {e}")
    
    async def predict_future_load(self, minutes_ahead: int) -> ScalingPrediction:
        """Predict future load and scaling requirements"""
        try:
            future_time = datetime.now() + timedelta(minutes=minutes_ahead)
            pattern_key = f"{future_time.weekday()}_{future_time.hour}"
            
            if pattern_key in self.traffic_patterns:
                pattern = self.traffic_patterns[pattern_key]
                predicted_load = pattern.load_factor
                confidence = pattern.confidence
                reasoning = f"Based on historical pattern for {pattern_key}"
            else:
                # Use ensemble prediction
                predicted_load = await self._ensemble_prediction(future_time)
                confidence = 0.5
                reasoning = "Ensemble prediction (no historical pattern)"
            
            # Determine scaling decision
            current_load = self.historical_data[-1]['load'] if self.historical_data else 0
            load_change = predicted_load - current_load
            
            if load_change > 0.3:
                action = ScalingDecision.SCALE_UP
                urgency = min(10, int(load_change * 10))
            elif load_change < -0.3:
                action = ScalingDecision.SCALE_DOWN
                urgency = 3
            else:
                action = ScalingDecision.MAINTAIN
                urgency = 1
            
            # Calculate target nodes
            target_nodes = max(1, int(predicted_load * 10))
            
            return ScalingPrediction(
                prediction_id=str(uuid.uuid4()),
                timestamp=time.time(),
                predicted_load=predicted_load,
                confidence=confidence,
                recommended_action=action,
                target_nodes=target_nodes,
                reasoning=reasoning,
                urgency=urgency
            )
            
        except Exception as e:
            self.logger.error(f"Load prediction failed: {e}")
            return ScalingPrediction(
                prediction_id=str(uuid.uuid4()),
                timestamp=time.time(),
                predicted_load=0.5,
                confidence=0.1,
                recommended_action=ScalingDecision.MAINTAIN,
                target_nodes=3,
                reasoning=f"Error: {e}",
                urgency=1
            )
    
    async def _ensemble_prediction(self, future_time: datetime) -> float:
        """Ensemble prediction combining multiple models"""
        try:
            predictions = []
            
            # Linear regression prediction
            linear_pred = await self._linear_prediction(future_time)
            predictions.append(linear_pred)
            
            # Exponential smoothing prediction
            exp_pred = await self._exponential_smoothing_prediction()
            predictions.append(exp_pred)
            
            # Neural network prediction
            neural_pred = await self._neural_network_prediction(future_time)
            predictions.append(neural_pred)
            
            # Weighted average
            weights = [0.3, 0.3, 0.4]  # Favor neural network
            return sum(p * w for p, w in zip(predictions, weights))
            
        except Exception as e:
            self.logger.error(f"Ensemble prediction failed: {e}")
            return 0.5
    
    async def _linear_prediction(self, future_time: datetime) -> float:
        """Simple linear regression prediction"""
        if len(self.historical_data) < 10:
            return 0.5
        
        # Simple trend calculation
        recent_data = list(self.historical_data)[-10:]
        loads = [d['load'] for d in recent_data]
        
        # Calculate trend
        x = np.arange(len(loads))
        slope = np.polyfit(x, loads, 1)[0]
        
        # Project forward
        return max(0, min(1, loads[-1] + slope * 5))
    
    async def _exponential_smoothing_prediction(self) -> float:
        """Exponential smoothing prediction"""
        if len(self.historical_data) < 5:
            return 0.5
        
        recent_data = list(self.historical_data)[-5:]
        loads = [d['load'] for d in recent_data]
        
        alpha = 0.3
        smoothed = loads[0]
        for load in loads[1:]:
            smoothed = alpha * load + (1 - alpha) * smoothed
        
        return smoothed
    
    async def _neural_network_prediction(self, future_time: datetime) -> float:
        """Neural network prediction"""
        try:
            features = np.array([
                future_time.hour / 24.0,
                future_time.weekday() / 7.0,
                0.5,  # Default node count
                0.2,  # Default response time
                0.5   # Default load
            ]).reshape(1, -1)
            
            hidden = np.tanh(np.dot(features, self.neural_weights['hidden_layer']))
            output = np.dot(hidden, self.neural_weights['output_layer'])
            
            return max(0, min(1, output[0][0]))
            
        except Exception as e:
            self.logger.error(f"Neural network prediction failed: {e}")
            return 0.5
    
    async def get_traffic_insights(self) -> Dict[str, Any]:
        """Get insights about traffic patterns"""
        return {
            'total_patterns': len(self.traffic_patterns),
            'data_points': len(self.historical_data),
            'top_patterns': {
                k: v.load_factor for k, v in 
                sorted(self.traffic_patterns.items(), 
                      key=lambda x: x[1].confidence, reverse=True)[:5]
            },
            'prediction_model': self.prediction_model.value,
            'confidence_threshold': self.confidence_threshold
        }

class AILoadBalancer(LoadBalancer):
    """AI-enhanced load balancer with predictive scaling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.predictor = IntelligentResourcePredictor()
        self.node_profiles: Dict[str, NodePerformanceProfile] = {}
        self.auto_scaling_enabled = True
        self.scaling_cooldown = 300  # 5 minutes
        self.last_scaling_action = 0
        # self.auto_discovery = AutoNodeDiscovery()  # Avoid circular import
        
        # Enhanced statistics
        self.ai_statistics = {
            'predictions_made': 0,
            'scaling_actions': 0,
            'prediction_accuracy': 0.0,
            'auto_discoveries': 0,
            'performance_improvements': 0
        }
    
    async def initialize_ai_systems(self):
        """Initialize AI systems"""
        try:
            self.console.print("🤖 [cyan]Initializing AI Load Balancer...[/cyan]")
            
            # Initialize predictive systems
            await self._initialize_node_profiling()
            await self._start_predictive_scaling()
            
            self.console.print("✅ [green]AI Load Balancer initialized[/green]")
            
        except Exception as e:
            self.logger.error(f"AI systems initialization failed: {e}")
            raise
    
    async def _initialize_node_profiling(self):
        """Initialize node performance profiling"""
        for node_id in self.nodes:
            self.node_profiles[node_id] = NodePerformanceProfile(
                node_id=node_id,
                avg_response_time=100.0,
                throughput_capacity=1000.0,
                reliability_score=0.95,
                cost_efficiency=1.0
            )
    
    async def _start_predictive_scaling(self):
        """Start predictive scaling background task"""
        asyncio.create_task(self._predictive_scaling_loop())
    
    async def _predictive_scaling_loop(self):
        """Main predictive scaling loop"""
        while True:
            try:
                # Collect current metrics
                current_load = await self._calculate_current_load()
                active_nodes = len([n for n, s in self.node_states.items() 
                                 if s == NodeState.HEALTHY])
                avg_response_time = await self._calculate_avg_response_time()
                
                # Record data for learning
                await self.predictor.record_traffic_data(
                    current_load, active_nodes, avg_response_time
                )
                
                # Make prediction
                prediction = await self.predictor.predict_future_load(15)  # 15 minutes ahead
                self.ai_statistics['predictions_made'] += 1
                
                # Execute scaling decision if needed
                if self.auto_scaling_enabled and prediction.urgency > 5:
                    await self._execute_scaling_decision(prediction)
                
                # Update node profiles
                await self._update_node_profiles()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Predictive scaling loop error: {e}")
                await asyncio.sleep(30)
    
    async def _calculate_current_load(self) -> float:
        """Calculate current system load"""
        try:
            if not self.active_tasks:
                return 0.0
            
            # Calculate load based on active tasks and queue
            active_task_load = len(self.active_tasks) / 100.0
            queue_load = self.task_queue.qsize() / 50.0
            
            return min(1.0, active_task_load + queue_load)
            
        except Exception as e:
            self.logger.error(f"Load calculation failed: {e}")
            return 0.5
    
    async def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        try:
            if not self.performance_history:
                return 100.0
            
            all_times = []
            for node_times in self.performance_history.values():
                all_times.extend(list(node_times))
            
            return statistics.mean(all_times) * 1000 if all_times else 100.0
            
        except Exception as e:
            self.logger.error(f"Response time calculation failed: {e}")
            return 100.0
    
    async def _execute_scaling_decision(self, prediction: ScalingPrediction):
        """Execute AI-driven scaling decision"""
        try:
            current_time = time.time()
            
            # Check cooldown period
            if current_time - self.last_scaling_action < self.scaling_cooldown:
                return
            
            current_nodes = len(self.nodes)
            
            if prediction.recommended_action == ScalingDecision.SCALE_UP:
                await self._scale_up(prediction.target_nodes - current_nodes)
            elif prediction.recommended_action == ScalingDecision.SCALE_DOWN:
                await self._scale_down(current_nodes - prediction.target_nodes)
            
            self.last_scaling_action = current_time
            self.ai_statistics['scaling_actions'] += 1
            
            self.console.print(
                f"🤖 [cyan]AI Scaling Decision: {prediction.recommended_action.value} "
                f"(Confidence: {prediction.confidence:.2f})[/cyan]"
            )
            
        except Exception as e:
            self.logger.error(f"Scaling execution failed: {e}")
    
    async def _scale_up(self, nodes_to_add: int):
        """Scale up by adding new nodes"""
        try:
            if nodes_to_add <= 0:
                return
            
            for i in range(min(nodes_to_add, 5)):  # Limit to 5 at once
                # Request new node from auto-discovery
                node_info = {
                    'node_id': f'ai_scaled_node_{uuid.uuid4().hex[:8]}',
                    'node_type': 'mesh',
                    'host': 'localhost',
                    'port': 8200 + i,
                    'capabilities': ['mesh_communication', 'truth_spreading'],
                    'metadata': {
                        'max_connections': 1000,
                        'created_by': 'ai_scaler'
                    }
                }
                
                # Announce node for auto-discovery (disabled to avoid circular import)
                # await self.auto_discovery.announce_node(node_info)
                # self.ai_statistics['auto_discoveries'] += 1
                
                self.console.print(f"🚀 [green]AI requested new node: {node_info['node_id']}[/green]")
                
        except Exception as e:
            self.logger.error(f"Scale up failed: {e}")
    
    async def _scale_down(self, nodes_to_remove: int):
        """Scale down by removing nodes"""
        try:
            if nodes_to_remove <= 0:
                return
            
            # Find least utilized nodes
            node_utilization = {}
            for node_id in self.nodes:
                if node_id in self.node_profiles:
                    profile = self.node_profiles[node_id]
                    utilization = (profile.avg_response_time / 1000.0) * \
                                (1.0 - profile.reliability_score)
                    node_utilization[node_id] = utilization
            
            # Remove least utilized nodes
            nodes_to_remove_list = sorted(node_utilization.items(), 
                                        key=lambda x: x[1])[:nodes_to_remove]
            
            for node_id, _ in nodes_to_remove_list:
                await self.unregister_node(node_id)
                self.console.print(f"🔻 [yellow]AI removed node: {node_id}[/yellow]")
                
        except Exception as e:
            self.logger.error(f"Scale down failed: {e}")
    
    async def _update_node_profiles(self):
        """Update node performance profiles"""
        try:
            for node_id in self.nodes:
                if node_id in self.node_profiles:
                    profile = self.node_profiles[node_id]
                    
                    # Update performance metrics
                    if node_id in self.performance_history:
                        times = list(self.performance_history[node_id])
                        if times:
                            profile.avg_response_time = statistics.mean(times) * 1000
                            profile.throughput_capacity = 1000.0 / (profile.avg_response_time / 100.0)
                    
                    # Update reliability score
                    if node_id in self.node_states:
                        state = self.node_states[node_id]
                        if state == NodeState.HEALTHY:
                            profile.reliability_score = min(1.0, profile.reliability_score + 0.01)
                        else:
                            profile.reliability_score = max(0.0, profile.reliability_score - 0.05)
                    
                    # Record historical performance
                    profile.historical_performance.append({
                        'timestamp': time.time(),
                        'response_time': profile.avg_response_time,
                        'reliability': profile.reliability_score,
                        'throughput': profile.throughput_capacity
                    })
                    
        except Exception as e:
            self.logger.error(f"Node profile update failed: {e}")
    
    async def get_optimal_node_ai(self, task: LoadBalancingTask) -> Optional[str]:
        """AI-enhanced node selection"""
        try:
            healthy_nodes = [
                node_id for node_id, state in self.node_states.items()
                if state in [NodeState.HEALTHY, NodeState.DEGRADED]
            ]
            
            if not healthy_nodes:
                return None
            
            # Calculate AI-based scores for each node
            node_scores = {}
            for node_id in healthy_nodes:
                score = await self._calculate_node_ai_score(node_id, task)
                node_scores[node_id] = score
            
            # Select best node
            best_node = max(node_scores, key=node_scores.get)
            return best_node
            
        except Exception as e:
            self.logger.error(f"AI node selection failed: {e}")
            return await self.get_optimal_node(task)  # Fallback
    
    async def _calculate_node_ai_score(self, node_id: str, task: LoadBalancingTask) -> float:
        """Calculate AI-based score for node selection"""
        try:
            profile = self.node_profiles.get(node_id)
            if not profile:
                return 0.5
            
            # Base score components
            response_score = 1.0 - min(1.0, profile.avg_response_time / 1000.0)
            reliability_score = profile.reliability_score
            throughput_score = min(1.0, profile.throughput_capacity / 1000.0)
            
            # Task-specific scoring
            task_type = task.task_type
            specialization_score = profile.specialization_scores.get(task_type, 0.5)
            
            # Weighted combination
            weights = {
                'response': 0.3,
                'reliability': 0.25,
                'throughput': 0.25,
                'specialization': 0.2
            }
            
            total_score = (
                response_score * weights['response'] +
                reliability_score * weights['reliability'] +
                throughput_score * weights['throughput'] +
                specialization_score * weights['specialization']
            )
            
            return total_score
            
        except Exception as e:
            self.logger.error(f"AI score calculation failed: {e}")
            return 0.5
    
    async def get_ai_statistics(self) -> Dict[str, Any]:
        """Get comprehensive AI statistics"""
        base_stats = await self.get_statistics()
        
        traffic_insights = await self.predictor.get_traffic_insights()
        
        ai_stats = {
            'ai_statistics': self.ai_statistics,
            'traffic_insights': traffic_insights,
            'node_profiles': {
                node_id: {
                    'avg_response_time': profile.avg_response_time,
                    'reliability_score': profile.reliability_score,
                    'throughput_capacity': profile.throughput_capacity
                }
                for node_id, profile in self.node_profiles.items()
            },
            'auto_scaling_enabled': self.auto_scaling_enabled,
            'scaling_cooldown': self.scaling_cooldown
        }
        
        return {**base_stats, **ai_stats}
    
    async def display_ai_dashboard(self):
        """Display AI-enhanced dashboard"""
        try:
            # Base dashboard
            super().display_dashboard()
            
            # AI-specific dashboard
            ai_table = Table(title="🤖 AI Load Balancer Status", style="cyan")
            ai_table.add_column("AI Feature", style="green")
            ai_table.add_column("Status", style="yellow")
            ai_table.add_column("Details", style="magenta")
            
            stats = await self.get_ai_statistics()
            ai_stats = stats['ai_statistics']
            
            ai_table.add_row("Auto Scaling", "🟢 Enabled" if self.auto_scaling_enabled else "🔴 Disabled", 
                           f"Cooldown: {self.scaling_cooldown}s")
            ai_table.add_row("Predictions Made", str(ai_stats['predictions_made']), "Total predictions")
            ai_table.add_row("Scaling Actions", str(ai_stats['scaling_actions']), "Automated scaling")
            ai_table.add_row("Auto Discoveries", str(ai_stats['auto_discoveries']), "Nodes auto-discovered")
            ai_table.add_row("Performance Improvements", str(ai_stats['performance_improvements']), "AI optimizations")
            
            self.console.print(ai_table)
            
            # Node profiles
            if self.node_profiles:
                profile_table = Table(title="Node Performance Profiles", style="cyan")
                profile_table.add_column("Node ID", style="green")
                profile_table.add_column("Response Time", style="yellow")
                profile_table.add_column("Reliability", style="magenta")
                profile_table.add_column("Throughput", style="blue")
                
                for node_id, profile in self.node_profiles.items():
                    profile_table.add_row(
                        node_id,
                        f"{profile.avg_response_time:.1f}ms",
                        f"{profile.reliability_score:.2f}",
                        f"{profile.throughput_capacity:.0f}/s"
                    )
                
                self.console.print(profile_table)
            
        except Exception as e:
            self.logger.error(f"AI dashboard display error: {e}")

# Example usage and integration
async def main():
    """Example usage of the AI load balancer"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize AI load balancer
    ai_balancer = AILoadBalancer()
    await ai_balancer.initialize_ai_systems()
    
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
    node_capacity = NodeCapacity(
        node_id="ai_node_001",
        max_connections=1000,
        max_cpu_usage=80.0,
        max_memory_usage=85.0,
        weight=1.0
    )
    
    await ai_balancer.register_node("ai_node_001", node_capacity, example_health_check)
    
    # Submit example tasks
    for i in range(10):
        task = LoadBalancingTask(
            task_id=str(uuid.uuid4()),
            task_type="mesh_communication",
            payload={"message": f"AI test message {i}"},
            priority=1
        )
        await ai_balancer.submit_task(task)
    
    # Display AI dashboard
    await ai_balancer.display_ai_dashboard()
    
    # Keep running for demonstration
    await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
