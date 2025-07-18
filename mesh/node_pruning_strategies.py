#!/usr/bin/env python3
"""
Node Pruning Strategies for Liberation System
Implements intelligent pruning of poorly performing nodes with dark neon themed monitoring
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque

from Mesh_Network.Advanced_Node_Discovery import AdvancedMeshNode, NetworkMetrics
from Adaptive_Strategies import HistoricalDataPoint, HistoricalDataManager


class PruningTrigger(Enum):
    """Triggers for node pruning decisions"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_INSTABILITY = "network_instability"
    MANUAL_INTERVENTION = "manual_intervention"
    SECURITY_THREAT = "security_threat"
    COST_OPTIMIZATION = "cost_optimization"


class PruningAction(Enum):
    """Actions that can be taken for poor performers"""
    MONITOR = "monitor"                 # Just monitor, no action
    DEPRIORITIZE = "deprioritize"      # Lower priority in load balancing
    ISOLATE = "isolate"                # Isolate from critical operations
    REMOVE = "remove"                  # Remove from mesh entirely
    QUARANTINE = "quarantine"          # Quarantine for investigation


@dataclass
class PerformanceThreshold:
    """Performance thresholds for pruning decisions"""
    cpu_threshold: float = 90.0        # CPU usage %
    memory_threshold: float = 85.0     # Memory usage %
    network_threshold: float = 80.0    # Network load %
    latency_threshold: float = 1000.0  # Latency in ms
    error_rate_threshold: float = 5.0  # Error rate %
    uptime_threshold: float = 95.0     # Uptime %
    response_time_threshold: float = 500.0  # Response time in ms


@dataclass
class PruningDecision:
    """A pruning decision for a node"""
    node_id: str
    action: PruningAction
    trigger: PruningTrigger
    confidence: float  # 0-1 confidence in decision
    rationale: str
    timestamp: datetime
    performance_score: float
    estimated_impact: float  # Expected impact on system performance
    reversal_conditions: List[str]  # Conditions for reversing the decision


@dataclass
class NodePerformanceProfile:
    """Performance profile for a node"""
    node_id: str
    performance_history: deque = field(default_factory=lambda: deque(maxlen=100))
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    recovery_attempts: int = 0
    quarantine_until: Optional[datetime] = None
    performance_trend: float = 0.0  # Positive = improving, negative = degrading
    trust_score: float = 1.0  # 0-1 trust score
    last_pruning_action: Optional[PruningAction] = None
    last_pruning_time: Optional[datetime] = None


class NodePruningStrategy:
    """🔥 LIBERATION SYSTEM - NODE PRUNING STRATEGY"""
    
    def __init__(self, 
                 thresholds: PerformanceThreshold = None,
                 history_window_hours: int = 24,
                 min_evaluation_period: int = 300):  # 5 minutes
        
        self.thresholds = thresholds or PerformanceThreshold()
        self.history_window_hours = history_window_hours
        self.min_evaluation_period = min_evaluation_period
        
        # Node tracking
        self.node_profiles: Dict[str, NodePerformanceProfile] = {}
        self.pruning_decisions: Dict[str, PruningDecision] = {}
        self.quarantined_nodes: Set[str] = set()
        self.deprioritized_nodes: Set[str] = set()
        
        # Historical data manager
        self.history_manager = HistoricalDataManager(max_history_points=10000)
        
        # Statistics
        self.pruning_stats = {
            "total_evaluations": 0,
            "nodes_pruned": 0,
            "nodes_recovered": 0,
            "false_positives": 0,
            "performance_improvements": 0
        }
        
        # Monitoring
        self.logger = logging.getLogger(__name__)
        self.running = False
        
    async def start_monitoring(self):
        """Start the pruning monitoring system"""
        self.running = True
        self.logger.info("🚀 LIBERATION SYSTEM - Node Pruning Strategy ACTIVATED")
        
        # Start background tasks
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._recovery_evaluation_loop())
        asyncio.create_task(self._statistics_reporting_loop())
        
    async def stop_monitoring(self):
        """Stop the pruning monitoring system"""
        self.running = False
        self.logger.info("🛑 Node Pruning Strategy DEACTIVATED")
        
    async def evaluate_node_performance(self, node: AdvancedMeshNode) -> Optional[PruningDecision]:
        """🧠 Evaluate a node's performance and make pruning decisions"""
        
        self.pruning_stats["total_evaluations"] += 1
        
        # Get or create node profile
        if node.id not in self.node_profiles:
            self.node_profiles[node.id] = NodePerformanceProfile(node_id=node.id)
        
        profile = self.node_profiles[node.id]
        
        # Add current performance data
        current_data = self._collect_node_data(node)
        profile.performance_history.append(current_data)
        self.history_manager.add_data_point(node.id, current_data)
        
        # Skip evaluation if insufficient data
        if len(profile.performance_history) < 3:
            return None
        
        # Calculate performance metrics
        performance_score = self._calculate_performance_score(profile)
        performance_trend = self._calculate_performance_trend(profile)
        
        # Update profile
        profile.performance_trend = performance_trend
        
        # Make pruning decision
        decision = await self._make_pruning_decision(node, profile, performance_score)
        
        if decision:
            self.pruning_decisions[node.id] = decision
            await self._execute_pruning_action(decision)
            
            # Log with dark neon theme
            self.logger.info(f"⚡ PRUNING DECISION: {decision.action.value.upper()} for node {node.id}")
            self.logger.info(f"🔥 Trigger: {decision.trigger.value} | Confidence: {decision.confidence:.2f}")
            self.logger.info(f"💀 Performance Score: {performance_score:.2f} | Rationale: {decision.rationale}")
        
        return decision
        
    def _collect_node_data(self, node: AdvancedMeshNode) -> HistoricalDataPoint:
        """Collect current performance data from node"""
        return HistoricalDataPoint(
            timestamp=datetime.now(),
            cpu_usage=node.metrics.cpu_usage,
            memory_usage=node.metrics.memory_usage,
            network_load=node.metrics.network_load,
            connections=getattr(node.metrics, 'connections', 0),
            response_time=node.metrics.latency,
            throughput=getattr(node.metrics, 'throughput', 0),
            error_rate=getattr(node.metrics, 'error_rate', 0)
        )
    
    def _calculate_performance_score(self, profile: NodePerformanceProfile) -> float:
        """Calculate overall performance score (0-100, higher is better)"""
        if not profile.performance_history:
            return 50.0
        
        recent_data = list(profile.performance_history)[-10:]  # Last 10 data points
        
        # Calculate individual metric scores
        cpu_score = 100 - statistics.mean(dp.cpu_usage for dp in recent_data)
        memory_score = 100 - statistics.mean(dp.memory_usage for dp in recent_data)
        network_score = 100 - statistics.mean(dp.network_load for dp in recent_data)
        
        # Response time score (lower is better)
        avg_response_time = statistics.mean(dp.response_time for dp in recent_data)
        response_score = max(0, 100 - (avg_response_time / 10))  # Normalize to 0-100
        
        # Error rate score (lower is better)
        avg_error_rate = statistics.mean(dp.error_rate for dp in recent_data)
        error_score = max(0, 100 - (avg_error_rate * 10))  # Normalize to 0-100
        
        # Weighted average
        performance_score = (
            cpu_score * 0.25 +
            memory_score * 0.25 +
            network_score * 0.20 +
            response_score * 0.15 +
            error_score * 0.15
        )
        
        # Apply trust score multiplier
        performance_score *= profile.trust_score
        
        return max(0, min(100, performance_score))
    
    def _calculate_performance_trend(self, profile: NodePerformanceProfile) -> float:
        """Calculate performance trend (-1 to 1, positive = improving)"""
        if len(profile.performance_history) < 5:
            return 0.0
        
        # Calculate trend over recent performance scores
        recent_scores = []
        for i in range(len(profile.performance_history) - 4, len(profile.performance_history)):
            if i >= 0:
                data_slice = list(profile.performance_history)[max(0, i-2):i+1]
                if data_slice:
                    score = self._calculate_performance_score_for_data(data_slice)
                    recent_scores.append(score)
        
        if len(recent_scores) < 2:
            return 0.0
        
        # Simple linear trend
        x = list(range(len(recent_scores)))
        y = recent_scores
        
        # Calculate slope
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] * x[i] for i in range(n))
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Normalize to -1 to 1
        return max(-1.0, min(1.0, slope / 10.0))
    
    def _calculate_performance_score_for_data(self, data_points: List[HistoricalDataPoint]) -> float:
        """Calculate performance score for specific data points"""
        if not data_points:
            return 50.0
        
        cpu_score = 100 - statistics.mean(dp.cpu_usage for dp in data_points)
        memory_score = 100 - statistics.mean(dp.memory_usage for dp in data_points)
        network_score = 100 - statistics.mean(dp.network_load for dp in data_points)
        
        return (cpu_score + memory_score + network_score) / 3
    
    async def _make_pruning_decision(self, node: AdvancedMeshNode, 
                                   profile: NodePerformanceProfile, 
                                   performance_score: float) -> Optional[PruningDecision]:
        """Make intelligent pruning decision based on performance data"""
        
        # Check if node is in quarantine
        if profile.quarantine_until and datetime.now() < profile.quarantine_until:
            return None
        
        # Determine trigger and action
        trigger, action, confidence, rationale = self._analyze_performance_indicators(
            node, profile, performance_score
        )
        
        if action == PruningAction.MONITOR:
            return None
        
        # Calculate estimated impact
        estimated_impact = self._estimate_pruning_impact(node, action)
        
        # Generate reversal conditions
        reversal_conditions = self._generate_reversal_conditions(action, performance_score)
        
        return PruningDecision(
            node_id=node.id,
            action=action,
            trigger=trigger,
            confidence=confidence,
            rationale=rationale,
            timestamp=datetime.now(),
            performance_score=performance_score,
            estimated_impact=estimated_impact,
            reversal_conditions=reversal_conditions
        )
    
    def _analyze_performance_indicators(self, node: AdvancedMeshNode, 
                                      profile: NodePerformanceProfile, 
                                      performance_score: float) -> Tuple[PruningTrigger, PruningAction, float, str]:
        """Analyze performance indicators to determine action"""
        
        # Critical performance failure
        if performance_score < 20:
            return (PruningTrigger.PERFORMANCE_DEGRADATION, PruningAction.REMOVE, 0.9, 
                   f"Critical performance failure: score {performance_score:.1f}")
        
        # Severe performance degradation
        if performance_score < 40:
            if profile.consecutive_failures > 3:
                return (PruningTrigger.PERFORMANCE_DEGRADATION, PruningAction.ISOLATE, 0.8,
                       f"Severe degradation with {profile.consecutive_failures} consecutive failures")
            else:
                return (PruningTrigger.PERFORMANCE_DEGRADATION, PruningAction.QUARANTINE, 0.7,
                       f"Severe degradation: score {performance_score:.1f}")
        
        # Moderate performance issues
        if performance_score < 60:
            if profile.performance_trend < -0.3:  # Declining trend
                return (PruningTrigger.PERFORMANCE_DEGRADATION, PruningAction.DEPRIORITIZE, 0.6,
                       f"Declining performance trend: score {performance_score:.1f}")
            else:
                return (PruningTrigger.PERFORMANCE_DEGRADATION, PruningAction.MONITOR, 0.5,
                       f"Moderate performance issues: score {performance_score:.1f}")
        
        # Resource exhaustion check
        recent_data = list(profile.performance_history)[-5:]
        if recent_data:
            avg_cpu = statistics.mean(dp.cpu_usage for dp in recent_data)
            avg_memory = statistics.mean(dp.memory_usage for dp in recent_data)
            
            if avg_cpu > self.thresholds.cpu_threshold or avg_memory > self.thresholds.memory_threshold:
                return (PruningTrigger.RESOURCE_EXHAUSTION, PruningAction.DEPRIORITIZE, 0.7,
                       f"Resource exhaustion: CPU {avg_cpu:.1f}%, Memory {avg_memory:.1f}%")
        
        # Network instability check
        if recent_data:
            avg_response_time = statistics.mean(dp.response_time for dp in recent_data)
            if avg_response_time > self.thresholds.response_time_threshold:
                return (PruningTrigger.NETWORK_INSTABILITY, PruningAction.DEPRIORITIZE, 0.6,
                       f"Network instability: response time {avg_response_time:.1f}ms")
        
        return (PruningTrigger.PERFORMANCE_DEGRADATION, PruningAction.MONITOR, 0.3, "Performance within acceptable range")
    
    def _estimate_pruning_impact(self, node: AdvancedMeshNode, action: PruningAction) -> float:
        """Estimate the impact of pruning action on system performance"""
        # This is a simplified estimation - in practice, you'd consider:
        # - Node's current workload
        # - Available alternatives
        # - System capacity
        # - Critical services running on node
        
        base_impact = {
            PruningAction.MONITOR: 0.0,
            PruningAction.DEPRIORITIZE: 0.1,
            PruningAction.ISOLATE: 0.3,
            PruningAction.QUARANTINE: 0.5,
            PruningAction.REMOVE: 0.8
        }
        
        # Adjust based on node importance (simplified)
        node_importance = getattr(node, 'importance', 0.5)  # Default medium importance
        
        return base_impact[action] * node_importance
    
    def _generate_reversal_conditions(self, action: PruningAction, performance_score: float) -> List[str]:
        """Generate conditions for reversing the pruning decision"""
        conditions = []
        
        if action == PruningAction.DEPRIORITIZE:
            conditions.append(f"Performance score > {performance_score + 20}")
            conditions.append("No failures for 1 hour")
        elif action == PruningAction.ISOLATE:
            conditions.append(f"Performance score > {performance_score + 30}")
            conditions.append("No failures for 2 hours")
            conditions.append("Manual verification required")
        elif action == PruningAction.QUARANTINE:
            conditions.append(f"Performance score > {performance_score + 25}")
            conditions.append("Root cause identified and fixed")
            conditions.append("Manual approval required")
        elif action == PruningAction.REMOVE:
            conditions.append("Node completely rebuilt")
            conditions.append("Performance score > 70")
            conditions.append("Administrative approval required")
        
        return conditions
    
    async def _execute_pruning_action(self, decision: PruningDecision):
        """Execute the pruning action"""
        node_id = decision.node_id
        action = decision.action
        
        if action == PruningAction.DEPRIORITIZE:
            self.deprioritized_nodes.add(node_id)
            self.logger.warning(f"⚠️  Node {node_id} DEPRIORITIZED")
            
        elif action == PruningAction.ISOLATE:
            self.deprioritized_nodes.add(node_id)
            # Additional isolation logic would go here
            self.logger.warning(f"🔒 Node {node_id} ISOLATED")
            
        elif action == PruningAction.QUARANTINE:
            self.quarantined_nodes.add(node_id)
            profile = self.node_profiles[node_id]
            profile.quarantine_until = datetime.now() + timedelta(hours=2)
            self.logger.warning(f"🚨 Node {node_id} QUARANTINED")
            
        elif action == PruningAction.REMOVE:
            self.quarantined_nodes.add(node_id)
            # Additional removal logic would go here
            self.logger.error(f"💀 Node {node_id} MARKED FOR REMOVAL")
            
        # Update statistics
        self.pruning_stats["nodes_pruned"] += 1
        
        # Update node profile
        profile = self.node_profiles[node_id]
        profile.last_pruning_action = action
        profile.last_pruning_time = datetime.now()
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # This would integrate with your existing node discovery system
                # For now, it's a placeholder
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _recovery_evaluation_loop(self):
        """Evaluate nodes for recovery from pruning actions"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check quarantined nodes
                for node_id in list(self.quarantined_nodes):
                    profile = self.node_profiles.get(node_id)
                    if profile and profile.quarantine_until and current_time > profile.quarantine_until:
                        # Re-evaluate for recovery
                        await self._evaluate_node_recovery(node_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"❌ Error in recovery evaluation: {e}")
                await asyncio.sleep(60)
    
    async def _evaluate_node_recovery(self, node_id: str):
        """Evaluate if a node can be recovered from pruning"""
        profile = self.node_profiles.get(node_id)
        if not profile:
            return
        
        # Check if recovery conditions are met
        recent_score = self._calculate_performance_score(profile)
        
        if recent_score > 70:  # Good performance threshold
            # Remove from quarantine/deprioritized
            self.quarantined_nodes.discard(node_id)
            self.deprioritized_nodes.discard(node_id)
            
            # Update statistics
            self.pruning_stats["nodes_recovered"] += 1
            
            self.logger.info(f"🔄 Node {node_id} RECOVERED - Performance score: {recent_score:.1f}")
    
    async def _statistics_reporting_loop(self):
        """Report pruning statistics periodically"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Report every 5 minutes
                
                self.logger.info("📊 PRUNING STATISTICS:")
                self.logger.info(f"  🔍 Total Evaluations: {self.pruning_stats['total_evaluations']}")
                self.logger.info(f"  ⚡ Nodes Pruned: {self.pruning_stats['nodes_pruned']}")
                self.logger.info(f"  🔄 Nodes Recovered: {self.pruning_stats['nodes_recovered']}")
                self.logger.info(f"  🚨 Quarantined: {len(self.quarantined_nodes)}")
                self.logger.info(f"  ⚠️  Deprioritized: {len(self.deprioritized_nodes)}")
                
            except Exception as e:
                self.logger.error(f"❌ Error in statistics reporting: {e}")
                await asyncio.sleep(300)
    
    def get_pruning_status(self) -> Dict:
        """Get current pruning system status"""
        return {
            "system_status": {
                "running": self.running,
                "total_nodes_tracked": len(self.node_profiles),
                "quarantined_nodes": len(self.quarantined_nodes),
                "deprioritized_nodes": len(self.deprioritized_nodes)
            },
            "statistics": self.pruning_stats.copy(),
            "recent_decisions": [
                {
                    "node_id": decision.node_id,
                    "action": decision.action.value,
                    "trigger": decision.trigger.value,
                    "confidence": decision.confidence,
                    "timestamp": decision.timestamp.isoformat()
                }
                for decision in list(self.pruning_decisions.values())[-10:]
            ]
        }


# Example usage and integration
async def main():
    """🌐 LIBERATION SYSTEM - Node Pruning Strategy Demo"""
    print("🔥 LIBERATION SYSTEM - NODE PRUNING STRATEGY")
    print("=" * 60)
    print("⚡ Initializing intelligent node pruning system...")
    print()
    
    # Initialize pruning strategy
    pruning_strategy = NodePruningStrategy()
    await pruning_strategy.start_monitoring()
    
    # Example integration with your existing system
    print("🚀 Node Pruning Strategy is now active!")
    print("   💀 Monitoring for poor performance...")
    print("   ⚡ Ready to prune underperforming nodes...")
    print("   🔄 Automatic recovery enabled...")
    
    # Keep running (in practice, this would be integrated with your main system)
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await pruning_strategy.stop_monitoring()
        print("\n🛑 Node Pruning Strategy deactivated")


if __name__ == "__main__":
    asyncio.run(main())
