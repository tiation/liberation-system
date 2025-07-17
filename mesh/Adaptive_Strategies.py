#!/usr/bin/env python3
"""
Adaptive Strategies System
Implements intelligent capacity adjustment based on historical data and predictions
"""

import logging
import asyncio
import time
import statistics
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
from enum import Enum

try:
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    HAS_ML_LIBS = True
except ImportError:
    # Fallback to basic statistics if ML libraries not available
    HAS_ML_LIBS = False
    print("ML libraries not available. Using basic statistical predictions.")

from Mesh_Network.Advanced_Node_Discovery import AdvancedMeshNode, NetworkMetrics, GeoLocation
# from Dynamic_Load_Balancer import LoadBalancer, LoadMetrics

class AdaptiveStrategy(Enum):
    """Different adaptive strategies for capacity adjustment"""
    CONSERVATIVE = "conservative"  # Gradual adjustments
    AGGRESSIVE = "aggressive"     # Rapid adjustments
    PREDICTIVE = "predictive"     # ML-based predictions
    HYBRID = "hybrid"            # Combination of strategies

@dataclass
class HistoricalDataPoint:
    """Single point of historical performance data"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    network_load: float
    connections: int
    response_time: float
    throughput: float
    error_rate: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'network_load': self.network_load,
            'connections': self.connections,
            'response_time': self.response_time,
            'throughput': self.throughput,
            'error_rate': self.error_rate
        }

@dataclass
class PerformancePattern:
    """Identified performance patterns"""
    pattern_type: str  # 'daily', 'weekly', 'load_spike', 'gradual_increase'
    peak_times: List[int]  # Hours when load peaks
    avg_duration: float   # Average duration of pattern in hours
    intensity: float      # Relative intensity (0-1)
    confidence: float     # Confidence in pattern (0-1)
    
@dataclass
class PredictionResult:
    """Result of capacity prediction"""
    predicted_cpu: float
    predicted_memory: float
    predicted_network: float
    predicted_connections: int
    confidence: float
    time_horizon: int  # minutes into future
    strategy_used: str

@dataclass
class AdaptiveConfiguration:
    """Configuration for adaptive strategies"""
    strategy: AdaptiveStrategy = AdaptiveStrategy.HYBRID
    history_window: int = 168  # hours (1 week)
    prediction_horizon: int = 60  # minutes
    adjustment_threshold: float = 0.15  # 15% change threshold
    conservative_factor: float = 0.5  # How conservative adjustments are
    aggressive_factor: float = 1.5   # How aggressive adjustments are
    pattern_detection_window: int = 24  # hours
    min_data_points: int = 10
    max_capacity_increase: float = 2.0  # Max 200% of current capacity
    min_capacity_ratio: float = 0.3    # Min 30% of original capacity

class HistoricalDataManager:
    """Manages historical performance data"""
    
    def __init__(self, max_history_points: int = 10000):
        self.data_points: Dict[str, deque] = {}
        self.max_history_points = max_history_points
        self.logger = logging.getLogger(__name__)
        
    def add_data_point(self, node_id: str, data_point: HistoricalDataPoint):
        """Add a new data point for a node"""
        if node_id not in self.data_points:
            self.data_points[node_id] = deque(maxlen=self.max_history_points)
        
        self.data_points[node_id].append(data_point)
        self.logger.debug(f"Added data point for node {node_id}: CPU={data_point.cpu_usage:.1f}%")
    
    def get_recent_data(self, node_id: str, hours: int = 24) -> List[HistoricalDataPoint]:
        """Get recent data points within specified hours"""
        if node_id not in self.data_points:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = [
            dp for dp in self.data_points[node_id]
            if dp.timestamp >= cutoff_time
        ]
        
        return recent_data
    
    def get_all_data(self, node_id: str) -> List[HistoricalDataPoint]:
        """Get all historical data for a node"""
        if node_id not in self.data_points:
            return []
        return list(self.data_points[node_id])
    
    def export_data(self, node_id: str, filename: str):
        """Export historical data to JSON file"""
        data = self.get_all_data(node_id)
        export_data = [dp.to_dict() for dp in data]
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Exported {len(data)} data points for node {node_id} to {filename}")

class PatternDetector:
    """Detects performance patterns in historical data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def detect_patterns(self, data: List[HistoricalDataPoint]) -> List[PerformancePattern]:
        """Detect patterns in historical data"""
        if len(data) < 24:  # Need at least 24 hours of data
            return []
        
        patterns = []
        
        # Detect daily patterns
        daily_pattern = self._detect_daily_pattern(data)
        if daily_pattern:
            patterns.append(daily_pattern)
        
        # Detect load spikes
        spike_patterns = self._detect_load_spikes(data)
        patterns.extend(spike_patterns)
        
        # Detect gradual trends
        trend_pattern = self._detect_gradual_trend(data)
        if trend_pattern:
            patterns.append(trend_pattern)
        
        self.logger.info(f"Detected {len(patterns)} performance patterns")
        return patterns
    
    def _detect_daily_pattern(self, data: List[HistoricalDataPoint]) -> Optional[PerformancePattern]:
        """Detect daily usage patterns"""
        hourly_loads = {}
        
        for dp in data:
            hour = dp.timestamp.hour
            if hour not in hourly_loads:
                hourly_loads[hour] = []
            
            avg_load = (dp.cpu_usage + dp.memory_usage + dp.network_load) / 3
            hourly_loads[hour].append(avg_load)
        
        # Calculate average load for each hour
        hour_averages = {}
        for hour, loads in hourly_loads.items():
            if loads:
                hour_averages[hour] = statistics.mean(loads)
        
        if len(hour_averages) < 12:  # Need at least half a day's data
            return None
        
        # Find peak hours (above average)
        overall_avg = statistics.mean(hour_averages.values())
        peak_hours = [hour for hour, avg in hour_averages.items() if avg > overall_avg * 1.2]
        
        if not peak_hours:
            return None
        
        # Calculate pattern intensity
        max_load = max(hour_averages.values())
        min_load = min(hour_averages.values())
        intensity = (max_load - min_load) / max_load if max_load > 0 else 0
        
        return PerformancePattern(
            pattern_type="daily",
            peak_times=sorted(peak_hours),
            avg_duration=len(peak_hours),
            intensity=intensity,
            confidence=min(1.0, len(data) / 168)  # Higher confidence with more data
        )
    
    def _detect_load_spikes(self, data: List[HistoricalDataPoint]) -> List[PerformancePattern]:
        """Detect sudden load spikes"""
        if len(data) < 10:
            return []
        
        spikes = []
        loads = [(dp.cpu_usage + dp.memory_usage + dp.network_load) / 3 for dp in data]
        
        # Calculate moving average and standard deviation
        window_size = min(10, len(loads) // 2)
        for i in range(window_size, len(loads)):
            window = loads[i-window_size:i]
            avg = statistics.mean(window)
            std_dev = statistics.stdev(window) if len(window) > 1 else 0
            
            current_load = loads[i]
            if current_load > avg + 2 * std_dev and std_dev > 0:  # 2 sigma spike
                spike_time = data[i].timestamp.hour
                spikes.append(PerformancePattern(
                    pattern_type="load_spike",
                    peak_times=[spike_time],
                    avg_duration=1.0,
                    intensity=(current_load - avg) / avg if avg > 0 else 1.0,
                    confidence=0.8
                ))
        
        return spikes
    
    def _detect_gradual_trend(self, data: List[HistoricalDataPoint]) -> Optional[PerformancePattern]:
        """Detect gradual increasing or decreasing trends"""
        if len(data) < 20:
            return None
        
        # Calculate trend using simple linear regression
        loads = [(dp.cpu_usage + dp.memory_usage + dp.network_load) / 3 for dp in data]
        x_values = list(range(len(loads)))
        
        if HAS_ML_LIBS:
            # Use sklearn if available
            X = np.array(x_values).reshape(-1, 1)
            y = np.array(loads)
            model = LinearRegression()
            model.fit(X, y)
            slope = model.coef_[0]
            r_squared = model.score(X, y)
        else:
            # Use basic correlation coefficient
            n = len(loads)
            sum_x = sum(x_values)
            sum_y = sum(loads)
            sum_xy = sum(x * y for x, y in zip(x_values, loads))
            sum_x2 = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            r_squared = 0.5  # Simplified confidence
        
        # Significant trend if slope is substantial and confidence is high
        if abs(slope) > 0.1 and r_squared > 0.3:
            pattern_type = "gradual_increase" if slope > 0 else "gradual_decrease"
            return PerformancePattern(
                pattern_type=pattern_type,
                peak_times=[],
                avg_duration=len(data) / 24,  # Duration in hours
                intensity=abs(slope),
                confidence=r_squared
            )
        
        return None

class PredictiveModel:
    """Predictive model for capacity forecasting"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}  # Store trained models per node
        
    def predict_capacity_needs(self, node_id: str, data: List[HistoricalDataPoint], 
                             patterns: List[PerformancePattern], 
                             horizon_minutes: int = 60) -> PredictionResult:
        """Predict future capacity needs"""
        if len(data) < 5:
            return self._fallback_prediction(data, horizon_minutes)
        
        if HAS_ML_LIBS:
            return self._ml_prediction(node_id, data, patterns, horizon_minutes)
        else:
            return self._statistical_prediction(data, patterns, horizon_minutes)
    
    def _ml_prediction(self, node_id: str, data: List[HistoricalDataPoint], 
                      patterns: List[PerformancePattern], horizon_minutes: int) -> PredictionResult:
        """Machine learning based prediction"""
        try:
            # Prepare features
            features = []
            targets_cpu = []
            targets_memory = []
            targets_network = []
            targets_connections = []
            
            for i, dp in enumerate(data):
                # Features: hour, day of week, historical values, trend
                hour = dp.timestamp.hour
                day_of_week = dp.timestamp.weekday()
                
                # Add pattern indicators
                daily_pattern_active = any(hour in p.peak_times for p in patterns if p.pattern_type == "daily")
                
                feature_vector = [
                    hour, day_of_week, dp.cpu_usage, dp.memory_usage, 
                    dp.network_load, dp.connections, dp.response_time,
                    int(daily_pattern_active)
                ]
                
                features.append(feature_vector)
                targets_cpu.append(dp.cpu_usage)
                targets_memory.append(dp.memory_usage)
                targets_network.append(dp.network_load)
                targets_connections.append(dp.connections)
            
            # Train models
            X = np.array(features)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train separate models for each metric
            cpu_model = LinearRegression()
            memory_model = LinearRegression()
            network_model = LinearRegression()
            connections_model = LinearRegression()
            
            cpu_model.fit(X_scaled, targets_cpu)
            memory_model.fit(X_scaled, targets_memory)
            network_model.fit(X_scaled, targets_network)
            connections_model.fit(X_scaled, targets_connections)
            
            # Predict future values
            future_time = datetime.now() + timedelta(minutes=horizon_minutes)
            future_hour = future_time.hour
            future_day = future_time.weekday()
            
            # Use recent values as base
            recent_dp = data[-1]
            daily_pattern_active = any(future_hour in p.peak_times for p in patterns if p.pattern_type == "daily")
            
            future_features = [
                future_hour, future_day, recent_dp.cpu_usage, recent_dp.memory_usage,
                recent_dp.network_load, recent_dp.connections, recent_dp.response_time,
                int(daily_pattern_active)
            ]
            
            future_X = scaler.transform([future_features])
            
            pred_cpu = float(cpu_model.predict(future_X)[0])
            pred_memory = float(memory_model.predict(future_X)[0])
            pred_network = float(network_model.predict(future_X)[0])
            pred_connections = int(connections_model.predict(future_X)[0])
            
            # Calculate confidence based on model performance
            confidence = min(0.9, (cpu_model.score(X_scaled, targets_cpu) + 
                                 memory_model.score(X_scaled, targets_memory) + 
                                 network_model.score(X_scaled, targets_network)) / 3)
            
            return PredictionResult(
                predicted_cpu=max(0, min(100, pred_cpu)),
                predicted_memory=max(0, min(100, pred_memory)),
                predicted_network=max(0, min(100, pred_network)),
                predicted_connections=max(0, pred_connections),
                confidence=confidence,
                time_horizon=horizon_minutes,
                strategy_used="ml_prediction"
            )
            
        except Exception as e:
            self.logger.error(f"ML prediction failed: {e}")
            return self._statistical_prediction(data, patterns, horizon_minutes)
    
    def _statistical_prediction(self, data: List[HistoricalDataPoint], 
                               patterns: List[PerformancePattern], 
                               horizon_minutes: int) -> PredictionResult:
        """Statistical prediction using patterns and trends"""
        recent_data = data[-min(24, len(data)):]  # Last 24 points or all data
        
        # Base prediction on recent averages
        avg_cpu = statistics.mean(dp.cpu_usage for dp in recent_data)
        avg_memory = statistics.mean(dp.memory_usage for dp in recent_data)
        avg_network = statistics.mean(dp.network_load for dp in recent_data)
        avg_connections = statistics.mean(dp.connections for dp in recent_data)
        
        # Adjust based on patterns
        future_time = datetime.now() + timedelta(minutes=horizon_minutes)
        future_hour = future_time.hour
        
        # Check if future time hits a daily pattern peak
        daily_patterns = [p for p in patterns if p.pattern_type == "daily"]
        pattern_multiplier = 1.0
        
        for pattern in daily_patterns:
            if future_hour in pattern.peak_times:
                pattern_multiplier = 1.0 + (pattern.intensity * 0.5)
                break
        
        # Check for trend patterns
        trend_patterns = [p for p in patterns if p.pattern_type in ["gradual_increase", "gradual_decrease"]]
        trend_adjustment = 0.0
        
        for pattern in trend_patterns:
            if pattern.pattern_type == "gradual_increase":
                trend_adjustment = pattern.intensity * 10  # Adjust by trend intensity
            else:
                trend_adjustment = -pattern.intensity * 10
        
        # Apply adjustments
        pred_cpu = avg_cpu * pattern_multiplier + trend_adjustment
        pred_memory = avg_memory * pattern_multiplier + trend_adjustment
        pred_network = avg_network * pattern_multiplier + trend_adjustment
        pred_connections = avg_connections * pattern_multiplier
        
        confidence = min(0.8, len(recent_data) / 24)  # Higher confidence with more data
        
        return PredictionResult(
            predicted_cpu=max(0, min(100, pred_cpu)),
            predicted_memory=max(0, min(100, pred_memory)),
            predicted_network=max(0, min(100, pred_network)),
            predicted_connections=max(0, int(pred_connections)),
            confidence=confidence,
            time_horizon=horizon_minutes,
            strategy_used="statistical_prediction"
        )
    
    def _fallback_prediction(self, data: List[HistoricalDataPoint], 
                           horizon_minutes: int) -> PredictionResult:
        """Fallback prediction with minimal data"""
        if not data:
            return PredictionResult(
                predicted_cpu=50.0, predicted_memory=50.0, predicted_network=50.0,
                predicted_connections=5, confidence=0.1, time_horizon=horizon_minutes,
                strategy_used="fallback"
            )
        
        # Use last data point as prediction
        last_dp = data[-1]
        return PredictionResult(
            predicted_cpu=last_dp.cpu_usage,
            predicted_memory=last_dp.memory_usage,
            predicted_network=last_dp.network_load,
            predicted_connections=last_dp.connections,
            confidence=0.3,
            time_horizon=horizon_minutes,
            strategy_used="fallback"
        )

class AdaptiveCapacityManager:
    """Main adaptive capacity management system"""
    
    def __init__(self, config: AdaptiveConfiguration = None):
        self.config = config or AdaptiveConfiguration()
        self.history_manager = HistoricalDataManager()
        self.pattern_detector = PatternDetector()
        self.predictive_model = PredictiveModel()
        self.logger = logging.getLogger(__name__)
        
        # Track original capacities
        self.original_capacities: Dict[str, float] = {}
        self.current_capacities: Dict[str, float] = {}
        
    async def collect_performance_data(self, node: AdvancedMeshNode):
        """Collect current performance data for a node"""
        # Simulate additional metrics that would be collected
        response_time = 100.0 + (node.metrics.cpu_usage * 2)  # Simulate response time
        throughput = max(0, 1000 - (node.metrics.network_load * 5))  # Simulate throughput
        
        data_point = HistoricalDataPoint(
            timestamp=datetime.now(),
            cpu_usage=node.metrics.cpu_usage,
            memory_usage=node.metrics.memory_usage,
            network_load=node.metrics.network_load,
            connections=len([c for c in node.connections.values() if c.get('status') == 'connected']),
            response_time=response_time,
            throughput=throughput,
            error_rate=0.0  # Could be calculated from actual errors
        )
        
        self.history_manager.add_data_point(node.id, data_point)
        self.logger.debug(f"Collected performance data for node {node.id}")
    
    async def analyze_and_adjust_capacity(self, node: AdvancedMeshNode) -> Dict[str, float]:
        """Analyze historical data and adjust node capacity"""
        # Collect current data
        await self.collect_performance_data(node)
        
        # Get historical data
        historical_data = self.history_manager.get_recent_data(
            node.id, hours=self.config.history_window
        )
        
        if len(historical_data) < self.config.min_data_points:
            self.logger.info(f"Insufficient data for node {node.id}, using default capacity")
            return self._get_default_capacity(node)
        
        # Detect patterns
        patterns = self.pattern_detector.detect_patterns(historical_data)
        
        # Predict future needs
        prediction = self.predictive_model.predict_capacity_needs(
            node.id, historical_data, patterns, self.config.prediction_horizon
        )
        
        # Calculate capacity adjustments
        adjustments = self._calculate_capacity_adjustments(node, prediction, patterns)
        
        # Apply strategy-specific modifications
        final_adjustments = self._apply_strategy(node, adjustments, prediction)
        
        # Store original capacity if first time
        if node.id not in self.original_capacities:
            self.original_capacities[node.id] = 100.0  # Default capacity
        
        self.current_capacities[node.id] = final_adjustments['total_capacity']
        
        self.logger.info(f"Adjusted capacity for node {node.id}: {final_adjustments}")
        return final_adjustments
    
    def _get_default_capacity(self, node: AdvancedMeshNode) -> Dict[str, float]:
        """Get default capacity settings"""
        return {
            'cpu_capacity': 100.0,
            'memory_capacity': 100.0,
            'network_capacity': 100.0,
            'connection_capacity': 10.0,
            'total_capacity': 100.0
        }
    
    def _calculate_capacity_adjustments(self, node: AdvancedMeshNode, 
                                      prediction: PredictionResult,
                                      patterns: List[PerformancePattern]) -> Dict[str, float]:
        """Calculate capacity adjustments based on predictions and patterns"""
        current_cpu = node.metrics.cpu_usage
        current_memory = node.metrics.memory_usage
        current_network = node.metrics.network_load
        
        # Calculate required capacity buffers
        cpu_buffer = max(0, prediction.predicted_cpu - current_cpu)
        memory_buffer = max(0, prediction.predicted_memory - current_memory)
        network_buffer = max(0, prediction.predicted_network - current_network)
        
        # Add pattern-based adjustments
        pattern_multiplier = 1.0
        for pattern in patterns:
            if pattern.pattern_type == "daily" and pattern.confidence > 0.5:
                pattern_multiplier = max(pattern_multiplier, 1.0 + pattern.intensity * 0.3)
            elif pattern.pattern_type == "load_spike" and pattern.confidence > 0.7:
                pattern_multiplier = max(pattern_multiplier, 1.0 + pattern.intensity * 0.5)
        
        # Calculate new capacities
        cpu_capacity = (100 + cpu_buffer) * pattern_multiplier
        memory_capacity = (100 + memory_buffer) * pattern_multiplier
        network_capacity = (100 + network_buffer) * pattern_multiplier
        connection_capacity = prediction.predicted_connections * 1.2  # 20% buffer
        
        return {
            'cpu_capacity': cpu_capacity,
            'memory_capacity': memory_capacity,
            'network_capacity': network_capacity,
            'connection_capacity': connection_capacity,
            'total_capacity': (cpu_capacity + memory_capacity + network_capacity) / 3
        }
    
    def _apply_strategy(self, node: AdvancedMeshNode, 
                       adjustments: Dict[str, float],
                       prediction: PredictionResult) -> Dict[str, float]:
        """Apply strategy-specific modifications to capacity adjustments"""
        original_capacity = self.original_capacities.get(node.id, 100.0)
        
        if self.config.strategy == AdaptiveStrategy.CONSERVATIVE:
            # Conservative: smaller adjustments, slower changes
            factor = self.config.conservative_factor
            for key in adjustments:
                if key != 'total_capacity':
                    current_val = adjustments[key]
                    target_val = 100 + (current_val - 100) * factor
                    adjustments[key] = target_val
        
        elif self.config.strategy == AdaptiveStrategy.AGGRESSIVE:
            # Aggressive: larger adjustments, faster changes
            factor = self.config.aggressive_factor
            for key in adjustments:
                if key != 'total_capacity':
                    current_val = adjustments[key]
                    target_val = 100 + (current_val - 100) * factor
                    adjustments[key] = target_val
        
        elif self.config.strategy == AdaptiveStrategy.PREDICTIVE:
            # Predictive: adjust based on prediction confidence
            confidence_factor = prediction.confidence
            for key in adjustments:
                if key != 'total_capacity':
                    current_val = adjustments[key]
                    target_val = 100 + (current_val - 100) * confidence_factor
                    adjustments[key] = target_val
        
        elif self.config.strategy == AdaptiveStrategy.HYBRID:
            # Hybrid: combine conservative and predictive approaches
            confidence_factor = prediction.confidence
            conservative_factor = self.config.conservative_factor
            
            # Weight between conservative and predictive based on confidence
            weight = confidence_factor  # High confidence = more predictive
            
            for key in adjustments:
                if key != 'total_capacity':
                    current_val = adjustments[key]
                    conservative_val = 100 + (current_val - 100) * conservative_factor
                    predictive_val = 100 + (current_val - 100) * confidence_factor
                    
                    # Weighted average
                    target_val = conservative_val * (1 - weight) + predictive_val * weight
                    adjustments[key] = target_val
        
        # Apply limits
        for key in adjustments:
            if key != 'total_capacity':
                max_capacity = original_capacity * self.config.max_capacity_increase
                min_capacity = original_capacity * self.config.min_capacity_ratio
                adjustments[key] = max(min_capacity, min(max_capacity, adjustments[key]))
        
        # Recalculate total capacity
        adjustments['total_capacity'] = (
            adjustments['cpu_capacity'] + 
            adjustments['memory_capacity'] + 
            adjustments['network_capacity']
        ) / 3
        
        return adjustments
    
    def get_capacity_history(self, node_id: str) -> List[Dict]:
        """Get capacity adjustment history for a node"""
        historical_data = self.history_manager.get_all_data(node_id)
        return [dp.to_dict() for dp in historical_data]
    
    def get_performance_summary(self, node_id: str) -> Dict:
        """Get performance summary for a node"""
        historical_data = self.history_manager.get_recent_data(node_id, hours=24)
        
        if not historical_data:
            return {"error": "No data available"}
        
        patterns = self.pattern_detector.detect_patterns(historical_data)
        prediction = self.predictive_model.predict_capacity_needs(
            node_id, historical_data, patterns, 60
        )
        
        return {
            "node_id": node_id,
            "data_points": len(historical_data),
            "patterns_detected": len(patterns),
            "patterns": [
                {
                    "type": p.pattern_type,
                    "peak_times": p.peak_times,
                    "intensity": p.intensity,
                    "confidence": p.confidence
                }
                for p in patterns
            ],
            "prediction": {
                "cpu": prediction.predicted_cpu,
                "memory": prediction.predicted_memory,
                "network": prediction.predicted_network,
                "connections": prediction.predicted_connections,
                "confidence": prediction.confidence,
                "strategy": prediction.strategy_used
            },
            "current_capacity": self.current_capacities.get(node_id, 100.0),
            "original_capacity": self.original_capacities.get(node_id, 100.0)
        }

# Example usage and testing
async def main():
    """Example usage of Adaptive Strategies"""
    logging.basicConfig(level=logging.INFO)
    
    # Create adaptive capacity manager
    config = AdaptiveConfiguration(
        strategy=AdaptiveStrategy.HYBRID,
        history_window=24,
        prediction_horizon=60,
        adjustment_threshold=0.15
    )
    
    capacity_manager = AdaptiveCapacityManager(config)
    
    print("🧠 LIBERATION SYSTEM - ADAPTIVE STRATEGIES")
    print("=" * 50)
    print("🎯 Testing intelligent capacity adjustment")
    print()
    
    # Create test node
    from Mesh_Network.Advanced_Node_Discovery import AdvancedMeshNode, NetworkMetrics, GeoLocation
    
    test_node = AdvancedMeshNode(
        id="adaptive_test_node",
        host="127.0.0.1",
        port=8000,
        location=GeoLocation(37.7749, -122.4194, "United States", "San Francisco", "CA"),
        metrics=NetworkMetrics(
            cpu_usage=60.0,
            memory_usage=45.0,
            network_load=70.0,
            uptime=99.5
        )
    )
    
    print(f"📊 Test Node: {test_node.id}")
    print(f"🏙️  Location: {test_node.location.city}, {test_node.location.country}")
    print(f"📈 Initial Metrics: CPU={test_node.metrics.cpu_usage}%, Memory={test_node.metrics.memory_usage}%, Network={test_node.metrics.network_load}%")
    print()
    
    # Simulate data collection over time
    print("🔄 Simulating historical data collection...")
    
    for i in range(50):  # Simulate 50 data points
        # Simulate varying load patterns
        time_factor = i / 10.0
        daily_cycle = 20 * abs(math.sin(time_factor * 0.5))  # Daily pattern
        random_variation = random.uniform(-10, 10)
        
        test_node.metrics.cpu_usage = 60 + daily_cycle + random_variation
        test_node.metrics.memory_usage = 45 + daily_cycle * 0.8 + random_variation * 0.5
        test_node.metrics.network_load = 70 + daily_cycle * 1.2 + random_variation
        
        # Clamp values
        test_node.metrics.cpu_usage = max(0, min(100, test_node.metrics.cpu_usage))
        test_node.metrics.memory_usage = max(0, min(100, test_node.metrics.memory_usage))
        test_node.metrics.network_load = max(0, min(100, test_node.metrics.network_load))
        
        await capacity_manager.collect_performance_data(test_node)
        
        # Small delay to simulate time passing
        await asyncio.sleep(0.01)
    
    print(f"✅ Collected {len(capacity_manager.history_manager.get_all_data(test_node.id))} data points")
    print()
    
    # Analyze and adjust capacity
    print("🧠 Analyzing patterns and adjusting capacity...")
    adjustments = await capacity_manager.analyze_and_adjust_capacity(test_node)
    
    print("📊 Capacity Adjustments:")
    for key, value in adjustments.items():
        print(f"  • {key.replace('_', ' ').title()}: {value:.1f}%")
    print()
    
    # Get performance summary
    print("📈 Performance Summary:")
    summary = capacity_manager.get_performance_summary(test_node.id)
    
    print(f"  📊 Data Points: {summary['data_points']}")
    print(f"  🔍 Patterns Detected: {summary['patterns_detected']}")
    
    for pattern in summary['patterns']:
        print(f"    • {pattern['type'].title()}: intensity={pattern['intensity']:.2f}, confidence={pattern['confidence']:.2f}")
    
    print(f"  🔮 Prediction:")
    pred = summary['prediction']
    print(f"    • CPU: {pred['cpu']:.1f}%")
    print(f"    • Memory: {pred['memory']:.1f}%")
    print(f"    • Network: {pred['network']:.1f}%")
    print(f"    • Connections: {pred['connections']}")
    print(f"    • Confidence: {pred['confidence']:.2f}")
    print(f"    • Strategy: {pred['strategy']}")
    
    print(f"  📈 Capacity Changes:")
    print(f"    • Original: {summary['original_capacity']:.1f}%")
    print(f"    • Current: {summary['current_capacity']:.1f}%")
    print(f"    • Change: {summary['current_capacity'] - summary['original_capacity']:+.1f}%")
    
    print("\n🎉 Adaptive Strategies Test Complete!")
    print("✨ Node capacity intelligently adjusted based on historical patterns")

if __name__ == "__main__":
    import math
    import random
    asyncio.run(main())
