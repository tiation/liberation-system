#!/usr/bin/env python3
"""
Automated Scalability Enhancement System for Liberation System Mesh Network
Implements predictive scaling with automated resource management
"""

import asyncio
import logging
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import concurrent.futures

# Import existing components
from Adaptive_Strategies import (
    AdaptiveCapacityManager, 
    AdaptiveConfiguration, 
    AdaptiveStrategy,
    HistoricalDataManager,
    PatternDetector,
    PredictiveModel,
    PredictionResult
)
from Mesh_Network.Advanced_Node_Discovery import AdvancedMeshNode, NetworkMetrics, GeoLocation
from Mesh_Network.Sharding_Strategy import ShardingStrategy
from Mesh_Network.Knowledge_Sharing_AI import AICapabilities
from Mesh_Network.Monitoring_System import MonitoringSystem, MetricsCollector, AlertManager
from Dynamic_Load_Balancer import LoadBalancer

class ScalingAction(Enum):
    """Types of scaling actions"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"
    REDISTRIBUTE = "redistribute"

@dataclass
class ScalingDecision:
    """Scaling decision with rationale"""
    node_id: str
    action: ScalingAction
    target_capacity: float
    current_capacity: float
    confidence: float
    rationale: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SystemMetrics:
    """Overall system metrics"""
    total_nodes: int
    active_nodes: int
    average_cpu: float
    average_memory: float
    average_network: float
    total_connections: int
    system_health: float
    prediction_accuracy: float

class AutomatedScalabilitySystem:
    """Main automated scalability system"""
    
    def __init__(self, sharding_strategy: ShardingStrategy, 
                 config: AdaptiveConfiguration = None,
                 monitoring_interval: int = 300):  # 5 minutes
        """
        Initialize the automated scalability system
        
        Args:
            sharding_strategy: The sharding strategy instance
            config: Configuration for adaptive strategies
            monitoring_interval: Seconds between monitoring cycles
        """
        self.sharding_strategy = sharding_strategy
        self.config = config or AdaptiveConfiguration(strategy=AdaptiveStrategy.HYBRID)
        self.monitoring_interval = monitoring_interval
        
        # Initialize components
        self.capacity_manager = AdaptiveCapacityManager(self.config)
        self.ai_capabilities = AICapabilities(sharding_strategy)
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.load_balancer = LoadBalancer(discovery=None)  # Will be set later
        
        # System state
        self.running = False
        self.scaling_decisions: List[ScalingDecision] = []
        self.system_metrics_history: List[SystemMetrics] = []
        
        # Performance tracking
        self.prediction_accuracy_history = []
        self.scaling_effectiveness_history = []
        
        # Logger setup
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler with dark neon theme formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Custom formatter with neon colors
        formatter = logging.Formatter(
            '%(asctime)s - \033[96m%(name)s\033[0m - \033[95m%(levelname)s\033[0m - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
    async def start(self):
        """Start the automated scalability system"""
        self.running = True
        self.logger.info("🚀 Starting Automated Scalability System...")
        
        # Start monitoring system
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        # Start scaling system
        scaling_task = asyncio.create_task(self._scaling_loop())
        
        # Start refinement system
        refinement_task = asyncio.create_task(self._refinement_loop())
        
        # Start metrics collection
        metrics_task = asyncio.create_task(
            self.metrics_collector.start_collection(self.sharding_strategy)
        )
        
        self.logger.info("✅ All systems operational!")
        
        # Wait for all tasks
        await asyncio.gather(
            monitoring_task, 
            scaling_task, 
            refinement_task,
            metrics_task
        )
    
    async def stop(self):
        """Stop the automated scalability system"""
        self.running = False
        self.metrics_collector.stop_collection()
        self.logger.info("⏹️  Automated Scalability System stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop - Step 1: Collect Historical Data"""
        while self.running:
            try:
                self.logger.info("📊 Collecting performance data from all nodes...")
                
                # Collect data from all nodes
                collection_tasks = []
                for node in self.sharding_strategy.nodes.values():
                    task = asyncio.create_task(
                        self.capacity_manager.collect_performance_data(node)
                    )
                    collection_tasks.append(task)
                
                # Wait for all data collection to complete
                await asyncio.gather(*collection_tasks)
                
                # Update system metrics
                await self._update_system_metrics()
                
                self.logger.info(f"✅ Data collection complete for {len(collection_tasks)} nodes")
                
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")
            
            await asyncio.sleep(self.monitoring_interval)
    
    async def _scaling_loop(self):
        """Main scaling loop - Steps 2-5: Detect, Predict, Adjust, Scale"""
        while self.running:
            try:
                self.logger.info("🧠 Analyzing patterns and making scaling decisions...")
                
                # Process each node
                scaling_tasks = []
                for node in self.sharding_strategy.nodes.values():
                    task = asyncio.create_task(self._process_node_scaling(node))
                    scaling_tasks.append(task)
                
                # Wait for all scaling decisions
                scaling_decisions = await asyncio.gather(*scaling_tasks)
                
                # Filter out None decisions
                valid_decisions = [d for d in scaling_decisions if d is not None]
                self.scaling_decisions.extend(valid_decisions)
                
                # Execute scaling decisions
                await self._execute_scaling_decisions(valid_decisions)
                
                # Get AI recommendations
                ai_recommendations = self.ai_capabilities.recommend_node_scaling()
                self.logger.info(f"🤖 AI Recommendations: {ai_recommendations['total_recommendations']} actions suggested")
                
                # Apply load balancing
                await self._apply_load_balancing()
                
                self.logger.info(f"✅ Scaling cycle complete - {len(valid_decisions)} decisions made")
                
            except Exception as e:
                self.logger.error(f"❌ Error in scaling loop: {e}")
            
            # Run scaling less frequently than monitoring
            await asyncio.sleep(self.monitoring_interval * 2)
    
    async def _refinement_loop(self):
        """Refinement loop - Step 6: Monitor and Refine"""
        while self.running:
            try:
                self.logger.info("🔧 Refining prediction models and strategies...")
                
                # Evaluate prediction accuracy
                await self._evaluate_prediction_accuracy()
                
                # Evaluate scaling effectiveness
                await self._evaluate_scaling_effectiveness()
                
                # Adjust strategies based on performance
                await self._adjust_strategies()
                
                self.logger.info("✅ Model refinement complete")
                
            except Exception as e:
                self.logger.error(f"❌ Error in refinement loop: {e}")
            
            # Run refinement less frequently
            await asyncio.sleep(self.monitoring_interval * 4)
    
    async def _process_node_scaling(self, node: AdvancedMeshNode) -> Optional[ScalingDecision]:
        """Process scaling decision for a single node"""
        try:
            # Get historical data
            historical_data = self.capacity_manager.history_manager.get_recent_data(
                node.id, hours=self.config.history_window
            )
            
            if len(historical_data) < self.config.min_data_points:
                return None
            
            # Step 2: Detect Patterns
            pattern_detector = PatternDetector()
            patterns = pattern_detector.detect_patterns(historical_data)
            
            # Step 3: Predict Future Loads
            predictive_model = PredictiveModel()
            prediction = predictive_model.predict_capacity_needs(
                node.id, historical_data, patterns, self.config.prediction_horizon
            )
            
            # Step 4: Implement Adaptive Adjustments
            adjustments = await self.capacity_manager.analyze_and_adjust_capacity(node)
            
            # Step 5: Determine scaling action
            scaling_decision = self._determine_scaling_action(
                node, prediction, adjustments, patterns
            )
            
            return scaling_decision
            
        except Exception as e:
            self.logger.error(f"❌ Error processing node {node.id}: {e}")
            return None
    
    def _determine_scaling_action(self, node: AdvancedMeshNode, 
                                prediction: PredictionResult,
                                adjustments: Dict[str, float],
                                patterns: List) -> ScalingDecision:
        """Determine the appropriate scaling action for a node"""
        
        current_capacity = adjustments.get('total_capacity', 100.0)
        target_capacity = current_capacity
        
        # Calculate capacity need based on prediction
        predicted_load = (prediction.predicted_cpu + 
                         prediction.predicted_memory + 
                         prediction.predicted_network) / 3
        
        # Determine action based on predicted load and current capacity
        if predicted_load > 85:  # High load predicted
            action = ScalingAction.SCALE_UP
            target_capacity = min(200.0, current_capacity * 1.5)
            rationale = f"High predicted load ({predicted_load:.1f}%) - scaling up"
            
        elif predicted_load < 30:  # Low load predicted
            action = ScalingAction.SCALE_DOWN
            target_capacity = max(50.0, current_capacity * 0.8)
            rationale = f"Low predicted load ({predicted_load:.1f}%) - scaling down"
            
        elif abs(predicted_load - 65) > 15:  # Significant deviation from optimal
            action = ScalingAction.REDISTRIBUTE
            target_capacity = current_capacity
            rationale = f"Load imbalance detected - redistributing"
            
        else:
            action = ScalingAction.MAINTAIN
            rationale = f"Optimal load predicted ({predicted_load:.1f}%) - maintaining"
        
        return ScalingDecision(
            node_id=node.id,
            action=action,
            target_capacity=target_capacity,
            current_capacity=current_capacity,
            confidence=prediction.confidence,
            rationale=rationale
        )
    
    async def _execute_scaling_decisions(self, decisions: List[ScalingDecision]):
        """Execute scaling decisions"""
        for decision in decisions:
            try:
                node = self.sharding_strategy.nodes.get(decision.node_id)
                if not node:
                    continue
                
                if decision.action == ScalingAction.SCALE_UP:
                    await self._scale_up_node(node, decision.target_capacity)
                    
                elif decision.action == ScalingAction.SCALE_DOWN:
                    await self._scale_down_node(node, decision.target_capacity)
                    
                elif decision.action == ScalingAction.REDISTRIBUTE:
                    await self._redistribute_node_load(node)
                
                self.logger.info(f"✅ Executed {decision.action.value} for node {decision.node_id}: {decision.rationale}")
                
            except Exception as e:
                self.logger.error(f"❌ Error executing scaling decision for {decision.node_id}: {e}")
    
    async def _scale_up_node(self, node: AdvancedMeshNode, target_capacity: float):
        """Scale up a node's capacity"""
        # Update node metrics to reflect increased capacity
        scaling_factor = target_capacity / 100.0
        
        # Simulate capacity increase (in real implementation, this would interact with infrastructure)
        node.metrics.cpu_usage = max(0, node.metrics.cpu_usage / scaling_factor)
        node.metrics.memory_usage = max(0, node.metrics.memory_usage / scaling_factor)
        node.metrics.network_load = max(0, node.metrics.network_load / scaling_factor)
        
        self.logger.info(f"⬆️  Scaled up node {node.id} to {target_capacity:.1f}% capacity")
    
    async def _scale_down_node(self, node: AdvancedMeshNode, target_capacity: float):
        """Scale down a node's capacity"""
        # Update node metrics to reflect decreased capacity
        scaling_factor = target_capacity / 100.0
        
        # Simulate capacity decrease (in real implementation, this would interact with infrastructure)
        node.metrics.cpu_usage = min(100, node.metrics.cpu_usage / scaling_factor)
        node.metrics.memory_usage = min(100, node.metrics.memory_usage / scaling_factor)
        node.metrics.network_load = min(100, node.metrics.network_load / scaling_factor)
        
        self.logger.info(f"⬇️  Scaled down node {node.id} to {target_capacity:.1f}% capacity")
    
    async def _redistribute_node_load(self, node: AdvancedMeshNode):
        """Redistribute load for a node"""
        # Get all nodes for load balancing
        all_nodes = list(self.sharding_strategy.nodes.values())
        
        # Apply load balancing
        await self.load_balancer.distribute_load(all_nodes)
        
        self.logger.info(f"🔄 Redistributed load for node {node.id}")
    
    async def _apply_load_balancing(self):
        """Apply load balancing across all nodes"""
        try:
            all_nodes = list(self.sharding_strategy.nodes.values())
            if all_nodes:
                await self.load_balancer.distribute_load(all_nodes)
                self.logger.info("⚖️  Load balancing applied across all nodes")
        except Exception as e:
            self.logger.error(f"❌ Error applying load balancing: {e}")
    
    async def _update_system_metrics(self):
        """Update overall system metrics"""
        try:
            nodes = list(self.sharding_strategy.nodes.values())
            if not nodes:
                return
            
            # Calculate system-wide metrics
            total_nodes = len(nodes)
            active_nodes = sum(1 for node in nodes if node.metrics.uptime > 90)
            
            avg_cpu = statistics.mean(node.metrics.cpu_usage for node in nodes)
            avg_memory = statistics.mean(node.metrics.memory_usage for node in nodes)
            avg_network = statistics.mean(node.metrics.network_load for node in nodes)
            
            total_connections = sum(len(node.connections) for node in nodes)
            
            # Calculate system health
            health_scores = []
            for node in nodes:
                health_score = (
                    (100 - node.metrics.cpu_usage) * 0.3 +
                    (100 - node.metrics.memory_usage) * 0.3 +
                    (100 - node.metrics.network_load) * 0.2 +
                    node.metrics.uptime * 0.2
                ) / 100
                health_scores.append(health_score)
            
            system_health = statistics.mean(health_scores)
            
            # Calculate prediction accuracy
            prediction_accuracy = statistics.mean(self.prediction_accuracy_history[-10:]) if self.prediction_accuracy_history else 0.5
            
            # Create system metrics
            system_metrics = SystemMetrics(
                total_nodes=total_nodes,
                active_nodes=active_nodes,
                average_cpu=avg_cpu,
                average_memory=avg_memory,
                average_network=avg_network,
                total_connections=total_connections,
                system_health=system_health,
                prediction_accuracy=prediction_accuracy
            )
            
            self.system_metrics_history.append(system_metrics)
            
            # Keep only last 100 metrics
            if len(self.system_metrics_history) > 100:
                self.system_metrics_history.pop(0)
                
        except Exception as e:
            self.logger.error(f"❌ Error updating system metrics: {e}")
    
    async def _evaluate_prediction_accuracy(self):
        """Evaluate the accuracy of predictions"""
        try:
            # Compare recent predictions with actual outcomes
            recent_decisions = self.scaling_decisions[-10:]  # Last 10 decisions
            
            if not recent_decisions:
                return
            
            accuracy_scores = []
            for decision in recent_decisions:
                node = self.sharding_strategy.nodes.get(decision.node_id)
                if node:
                    # Simple accuracy metric based on whether the scaling action was beneficial
                    current_load = (node.metrics.cpu_usage + node.metrics.memory_usage + node.metrics.network_load) / 3
                    
                    if decision.action == ScalingAction.SCALE_UP and current_load < 80:
                        accuracy_scores.append(0.9)  # Good prediction
                    elif decision.action == ScalingAction.SCALE_DOWN and current_load > 40:
                        accuracy_scores.append(0.9)  # Good prediction
                    elif decision.action == ScalingAction.MAINTAIN and 40 <= current_load <= 80:
                        accuracy_scores.append(0.95)  # Very good prediction
                    else:
                        accuracy_scores.append(0.3)  # Poor prediction
            
            if accuracy_scores:
                avg_accuracy = statistics.mean(accuracy_scores)
                self.prediction_accuracy_history.append(avg_accuracy)
                
                # Keep only last 50 accuracy scores
                if len(self.prediction_accuracy_history) > 50:
                    self.prediction_accuracy_history.pop(0)
                
                self.logger.info(f"📊 Prediction accuracy: {avg_accuracy:.2f}")
                
        except Exception as e:
            self.logger.error(f"❌ Error evaluating prediction accuracy: {e}")
    
    async def _evaluate_scaling_effectiveness(self):
        """Evaluate the effectiveness of scaling decisions"""
        try:
            recent_metrics = self.system_metrics_history[-5:]  # Last 5 system metrics
            
            if len(recent_metrics) < 2:
                return
            
            # Calculate improvement in system health
            health_improvement = recent_metrics[-1].system_health - recent_metrics[0].system_health
            
            # Calculate resource utilization efficiency
            current_metrics = recent_metrics[-1]
            resource_efficiency = 1.0 - abs(current_metrics.average_cpu - 65) / 65  # Optimal around 65%
            
            effectiveness_score = (health_improvement + resource_efficiency) / 2
            self.scaling_effectiveness_history.append(effectiveness_score)
            
            # Keep only last 50 effectiveness scores
            if len(self.scaling_effectiveness_history) > 50:
                self.scaling_effectiveness_history.pop(0)
            
            self.logger.info(f"📈 Scaling effectiveness: {effectiveness_score:.2f}")
            
        except Exception as e:
            self.logger.error(f"❌ Error evaluating scaling effectiveness: {e}")
    
    async def _adjust_strategies(self):
        """Adjust strategies based on performance metrics"""
        try:
            if not self.prediction_accuracy_history or not self.scaling_effectiveness_history:
                return
            
            recent_accuracy = statistics.mean(self.prediction_accuracy_history[-5:])
            recent_effectiveness = statistics.mean(self.scaling_effectiveness_history[-5:])
            
            # Adjust strategy based on performance
            if recent_accuracy < 0.6 and recent_effectiveness < 0.4:
                # Poor performance, switch to conservative
                self.config.strategy = AdaptiveStrategy.CONSERVATIVE
                self.logger.info("🔄 Switched to CONSERVATIVE strategy due to poor performance")
                
            elif recent_accuracy > 0.8 and recent_effectiveness > 0.7:
                # Good performance, can use aggressive
                self.config.strategy = AdaptiveStrategy.AGGRESSIVE
                self.logger.info("🚀 Switched to AGGRESSIVE strategy due to good performance")
                
            else:
                # Moderate performance, use hybrid
                self.config.strategy = AdaptiveStrategy.HYBRID
                self.logger.info("⚖️  Using HYBRID strategy for balanced performance")
            
            # Update capacity manager configuration
            self.capacity_manager.config = self.config
            
        except Exception as e:
            self.logger.error(f"❌ Error adjusting strategies: {e}")
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        if not self.system_metrics_history:
            return {"error": "No system metrics available"}
        
        current_metrics = self.system_metrics_history[-1]
        recent_decisions = self.scaling_decisions[-5:]
        
        return {
            "system_metrics": {
                "total_nodes": current_metrics.total_nodes,
                "active_nodes": current_metrics.active_nodes,
                "average_cpu": current_metrics.average_cpu,
                "average_memory": current_metrics.average_memory,
                "average_network": current_metrics.average_network,
                "total_connections": current_metrics.total_connections,
                "system_health": current_metrics.system_health,
                "prediction_accuracy": current_metrics.prediction_accuracy
            },
            "recent_decisions": [
                {
                    "node_id": d.node_id,
                    "action": d.action.value,
                    "target_capacity": d.target_capacity,
                    "confidence": d.confidence,
                    "rationale": d.rationale,
                    "timestamp": d.timestamp.isoformat()
                }
                for d in recent_decisions
            ],
            "current_strategy": self.config.strategy.value,
            "monitoring_interval": self.monitoring_interval,
            "system_running": self.running
        }
    
    def export_performance_data(self, filename: str):
        """Export performance data to JSON file"""
        try:
            data = {
                "system_metrics_history": [
                    {
                        "total_nodes": m.total_nodes,
                        "active_nodes": m.active_nodes,
                        "average_cpu": m.average_cpu,
                        "average_memory": m.average_memory,
                        "average_network": m.average_network,
                        "total_connections": m.total_connections,
                        "system_health": m.system_health,
                        "prediction_accuracy": m.prediction_accuracy
                    }
                    for m in self.system_metrics_history
                ],
                "scaling_decisions": [
                    {
                        "node_id": d.node_id,
                        "action": d.action.value,
                        "target_capacity": d.target_capacity,
                        "current_capacity": d.current_capacity,
                        "confidence": d.confidence,
                        "rationale": d.rationale,
                        "timestamp": d.timestamp.isoformat()
                    }
                    for d in self.scaling_decisions
                ],
                "prediction_accuracy_history": self.prediction_accuracy_history,
                "scaling_effectiveness_history": self.scaling_effectiveness_history
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"📁 Performance data exported to {filename}")
            
        except Exception as e:
            self.logger.error(f"❌ Error exporting performance data: {e}")

# Example usage and demonstration
async def main():
    """Demonstration of the Automated Scalability System"""
    print("🌐 LIBERATION SYSTEM - AUTOMATED SCALABILITY")
    print("=" * 60)
    print("🚀 Initializing predictive scaling system...")
    print()
    
    # Import required modules for demonstration
    try:
        from Mesh_Network.Sharding_Strategy import ShardingStrategy
        from Mesh_Network.Advanced_Node_Discovery import AdvancedNodeDiscovery
        
        # Create sharding strategy
        discovery = AdvancedNodeDiscovery()
        sharding_strategy = ShardingStrategy(discovery)
        
        # Create test nodes
        test_nodes = [
            AdvancedMeshNode(
                id=f"node_{i}",
                host=f"192.168.1.{i}",
                port=8000 + i,
                location=GeoLocation(37.7749, -122.4194, "United States", "San Francisco", "CA"),
                metrics=NetworkMetrics(
                    cpu_usage=50.0 + (i * 5),
                    memory_usage=45.0 + (i * 3),
                    network_load=60.0 + (i * 4),
                    uptime=99.0 + (i * 0.1)
                )
            )
            for i in range(1, 6)  # Create 5 nodes
        ]
        
        # Add nodes to sharding strategy
        for node in test_nodes:
            sharding_strategy.add_node(node)
        
        # Create automated scalability system
        config = AdaptiveConfiguration(
            strategy=AdaptiveStrategy.HYBRID,
            history_window=24,
            prediction_horizon=60,
            monitoring_interval=300  # 5 minutes
        )
        
        scalability_system = AutomatedScalabilitySystem(
            sharding_strategy=sharding_strategy,
            config=config,
            monitoring_interval=10  # Faster for demo
        )
        
        print(f"✅ System initialized with {len(test_nodes)} nodes")
        print(f"🧠 Strategy: {config.strategy.value}")
        print(f"⏱️  Monitoring interval: {scalability_system.monitoring_interval} seconds")
        print()
        
        # Run system for demonstration (limited time)
        print("🔄 Starting automated scalability system...")
        print("   (Running for 30 seconds for demonstration)")
        print()
        
        # Start system
        system_task = asyncio.create_task(scalability_system.start())
        
        # Let it run for 30 seconds
        await asyncio.sleep(30)
        
        # Stop system
        await scalability_system.stop()
        
        # Show results
        print("\n📊 SYSTEM PERFORMANCE SUMMARY")
        print("=" * 60)
        
        status = scalability_system.get_system_status()
        
        if "system_metrics" in status:
            metrics = status["system_metrics"]
            print(f"🏗️  Total Nodes: {metrics['total_nodes']}")
            print(f"✅ Active Nodes: {metrics['active_nodes']}")
            print(f"💻 Average CPU: {metrics['average_cpu']:.1f}%")
            print(f"🧠 Average Memory: {metrics['average_memory']:.1f}%")
            print(f"🌐 Average Network: {metrics['average_network']:.1f}%")
            print(f"🔗 Total Connections: {metrics['total_connections']}")
            print(f"💚 System Health: {metrics['system_health']:.2f}")
            print(f"🎯 Prediction Accuracy: {metrics['prediction_accuracy']:.2f}")
            
            print(f"\n🔄 Strategy: {status['current_strategy']}")
            print(f"📈 Recent Decisions: {len(status['recent_decisions'])}")
            
            for decision in status['recent_decisions']:
                print(f"  • {decision['node_id']}: {decision['action']} - {decision['rationale']}")
        
        # Export performance data
        scalability_system.export_performance_data("scalability_performance.json")
        
        print("\n🎉 Automated Scalability System Demo Complete!")
        print("✨ System successfully demonstrated predictive scaling capabilities")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all required modules are available")
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")

if __name__ == "__main__":
    # Setup logging for demonstration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())
