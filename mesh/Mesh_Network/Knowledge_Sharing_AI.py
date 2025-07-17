#!/usr/bin/env python3
"""
Knowledge Sharing AI Capabilities for Liberation System Mesh Network
Provides AI-powered insights and recommendations
"""

import json
import logging
from typing import Dict, Any, List

from Mesh_Network.Advanced_Node_Discovery import AdvancedMeshNode
from Mesh_Network.Sharding_Strategy import ShardingStrategy

class AICapabilities:
    """Provides AI-powered insights and recommendations"""
    
    def __init__(self, sharding_strategy: ShardingStrategy):
        self.sharding_strategy = sharding_strategy
        self.logger = logging.getLogger(__name__)
    
    def recommend_node_scaling(self) -> Dict[str, Any]:
        """Recommend scaling actions based on network load and node performance"""
        node_performance = self._calculate_node_performance()
        
        recommendations = []
        for node_id, performance in node_performance.items():
            if performance['load'] > performance['capacity'] * 0.85:
                recommendations.append({
                    'node_id': node_id,
                    'action': 'scale_up',
                    'reason': 'High load with limited remaining capacity'
                })
            elif performance['load'] < performance['capacity'] * 0.4:
                recommendations.append({
                    'node_id': node_id,
                    'action': 'scale_down',
                    'reason': 'Low load, potential for scaling down'
                })
        
        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
    
    def _calculate_node_performance(self) -> Dict[str, Dict[str, float]]:
        """Calculate performance metrics for each node"""
        performance_metrics = {}
        for node_id, node in self.sharding_strategy.nodes.items():
            capacity = self.sharding_strategy._calculate_node_capacity(node)
            load = len(self.sharding_strategy.get_nodes_for_shard(node_id))
            
            performance_metrics[node_id] = {
                'load': load,
                'capacity': capacity
            }
        
        return performance_metrics
    
    def analyze_network_metrics(self) -> Dict[str, Any]:
        """Analyze network-wide metrics and provide insights"""
        stats = self.sharding_strategy.get_shard_statistics()
        node_health_scores = [self._calculate_node_health(node) 
                              for node in self.sharding_strategy.nodes.values()]
        avg_health = sum(node_health_scores) / len(node_health_scores)

        insights = {
            "network_health": avg_health,
            "high_load_shards": [shard_id for shard_id, load in stats["load_distribution"].items() if load > 10],
            "potential_bottleneck_nodes": [node for node in self.sharding_strategy.nodes.values() if self._calculate_node_health(node) < 0.5]
        }
        
        return insights
    
    def _calculate_node_health(self, node: AdvancedMeshNode) -> float:
        """Calculate health score for a node for AI analysis"""
        if not node.metrics:
            return 0.5  # Neutral if no data available
        
        return (node.metrics.uptime * 0.5 + node.metrics.calculate_quality_score() * 0.5) / 100.0

