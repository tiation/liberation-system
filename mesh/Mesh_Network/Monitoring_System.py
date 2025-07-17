#!/usr/bin/env python3
"""
Advanced Monitoring and Alerting System for Liberation System Mesh Network
Real-time metrics, alerting, and dashboard with dark neon theme
"""

import asyncio
import logging
import time
import json
import socket
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import sqlite3
import os

try:
    import psutil
    import aiohttp
    from aiohttp import web
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call(["pip", "install", "psutil", "aiohttp"])
    import psutil
    import aiohttp
    from aiohttp import web

from Advanced_Node_Discovery import AdvancedMeshNode, NodeType, NetworkMetrics
from Sharding_Strategy import ShardingStrategy

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MetricType(Enum):
    """Types of metrics to monitor"""
    NETWORK_LATENCY = "network_latency"
    NODE_HEALTH = "node_health"
    SHARD_DISTRIBUTION = "shard_distribution"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"
    CONNECTION_COUNT = "connection_count"
    GEOGRAPHIC_DISTRIBUTION = "geographic_distribution"

@dataclass
class Alert:
    """Alert information"""
    id: str
    severity: AlertSeverity
    metric_type: MetricType
    message: str
    node_id: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    node_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Threshold:
    """Monitoring threshold configuration"""
    metric_type: MetricType
    warning_threshold: float
    critical_threshold: float
    comparison: str = "greater"  # "greater", "less", "equal"
    duration: int = 60  # seconds
    enabled: bool = True

class MetricsCollector:
    """Collects and processes metrics from mesh network"""
    
    def __init__(self, max_history: int = 1000):
        self.metrics: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=max_history) for metric_type in MetricType
        }
        self.node_metrics: Dict[str, Dict[MetricType, deque]] = defaultdict(
            lambda: {metric_type: deque(maxlen=max_history) for metric_type in MetricType}
        )
        self.logger = logging.getLogger(__name__)
        self.collection_interval = 30  # seconds
        self.running = False
        
    async def start_collection(self, sharding_strategy: ShardingStrategy):
        """Start metrics collection"""
        self.running = True
        self.sharding_strategy = sharding_strategy
        
        while self.running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(self.collection_interval)
    
    def stop_collection(self):
        """Stop metrics collection"""
        self.running = False
    
    async def _collect_metrics(self):
        """Collect all metrics"""
        timestamp = datetime.now()
        
        # Collect network metrics
        await self._collect_network_metrics(timestamp)
        
        # Collect node health metrics
        await self._collect_node_health_metrics(timestamp)
        
        # Collect shard distribution metrics
        await self._collect_shard_metrics(timestamp)
        
        # Collect system resource metrics
        await self._collect_resource_metrics(timestamp)
        
        # Collect throughput metrics
        await self._collect_throughput_metrics(timestamp)
    
    async def _collect_network_metrics(self, timestamp: datetime):
        """Collect network latency and connectivity metrics"""
        try:
            total_latency = 0
            node_count = 0
            
            for node in self.sharding_strategy.nodes.values():
                if node.metrics:
                    latency = node.metrics.latency
                    if latency > 0:
                        total_latency += latency
                        node_count += 1
                        
                        # Store per-node latency
                        point = MetricPoint(timestamp, latency, node.id)
                        self.node_metrics[node.id][MetricType.NETWORK_LATENCY].append(point)
            
            # Store average latency
            if node_count > 0:
                avg_latency = total_latency / node_count
                point = MetricPoint(timestamp, avg_latency)
                self.metrics[MetricType.NETWORK_LATENCY].append(point)
                
        except Exception as e:
            self.logger.error(f"Error collecting network metrics: {e}")
    
    async def _collect_node_health_metrics(self, timestamp: datetime):
        """Collect node health metrics"""
        try:
            healthy_nodes = 0
            total_nodes = len(self.sharding_strategy.nodes)
            
            for node in self.sharding_strategy.nodes.values():
                health_score = self._calculate_node_health_score(node)
                
                # Store per-node health
                point = MetricPoint(timestamp, health_score, node.id)
                self.node_metrics[node.id][MetricType.NODE_HEALTH].append(point)
                
                if health_score > 0.7:  # Healthy threshold
                    healthy_nodes += 1
            
            # Store overall network health
            if total_nodes > 0:
                network_health = healthy_nodes / total_nodes
                point = MetricPoint(timestamp, network_health)
                self.metrics[MetricType.NODE_HEALTH].append(point)
                
        except Exception as e:
            self.logger.error(f"Error collecting node health metrics: {e}")
    
    async def _collect_shard_metrics(self, timestamp: datetime):
        """Collect shard distribution metrics"""
        try:
            stats = self.sharding_strategy.get_shard_statistics()
            load_distribution = stats["load_distribution"]
            
            if load_distribution:
                loads = list(load_distribution.values())
                load_variance = statistics.variance(loads) if len(loads) > 1 else 0
                
                point = MetricPoint(timestamp, load_variance)
                self.metrics[MetricType.SHARD_DISTRIBUTION].append(point)
                
        except Exception as e:
            self.logger.error(f"Error collecting shard metrics: {e}")
    
    async def _collect_resource_metrics(self, timestamp: datetime):
        """Collect system resource metrics"""
        try:
            # Get system-wide metrics
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            # Average resource usage
            avg_resource_usage = (cpu_usage + memory_usage + disk_usage) / 3
            
            point = MetricPoint(timestamp, avg_resource_usage, metadata={
                "cpu": cpu_usage,
                "memory": memory_usage,
                "disk": disk_usage
            })
            self.metrics[MetricType.RESOURCE_USAGE].append(point)
            
        except Exception as e:
            self.logger.error(f"Error collecting resource metrics: {e}")
    
    async def _collect_throughput_metrics(self, timestamp: datetime):
        """Collect throughput metrics"""
        try:
            # Calculate throughput based on sharding operations
            throughput = self.sharding_strategy.shard_metrics.get("total_operations", 0)
            
            point = MetricPoint(timestamp, throughput)
            self.metrics[MetricType.THROUGHPUT].append(point)
            
        except Exception as e:
            self.logger.error(f"Error collecting throughput metrics: {e}")
    
    def _calculate_node_health_score(self, node: AdvancedMeshNode) -> float:
        """Calculate health score for a node"""
        try:
            score = 0.0
            
            # Network quality (40%)
            if node.metrics:
                quality_score = node.metrics.calculate_quality_score()
                score += quality_score * 0.4
            
            # Uptime (30%)
            if node.metrics and node.metrics.uptime > 0:
                uptime_score = min(1.0, node.metrics.uptime / 100.0)
                score += uptime_score * 0.3
            
            # Resource usage (20%) - lower is better
            if node.metrics:
                cpu_score = max(0, 1.0 - (node.metrics.cpu_usage / 100.0))
                memory_score = max(0, 1.0 - (node.metrics.memory_usage / 100.0))
                resource_score = (cpu_score + memory_score) / 2
                score += resource_score * 0.2
            
            # Trust score (10%)
            trust_score = getattr(node, 'trust_score', 1.0)
            score += trust_score * 0.1
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            self.logger.error(f"Error calculating health score for node {node.id}: {e}")
            return 0.5  # Default neutral score
    
    def get_recent_metrics(self, metric_type: MetricType, minutes: int = 60) -> List[MetricPoint]:
        """Get recent metrics for a specific type"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        if metric_type in self.metrics:
            return [point for point in self.metrics[metric_type] 
                   if point.timestamp >= cutoff_time]
        
        return []
    
    def get_node_metrics(self, node_id: str, metric_type: MetricType, minutes: int = 60) -> List[MetricPoint]:
        """Get recent metrics for a specific node"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        if node_id in self.node_metrics and metric_type in self.node_metrics[node_id]:
            return [point for point in self.node_metrics[node_id][metric_type] 
                   if point.timestamp >= cutoff_time]
        
        return []

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, db_path: str = "alerts.db"):
        self.db_path = db_path
        self.alerts: Dict[str, Alert] = {}
        self.thresholds: Dict[MetricType, List[Threshold]] = defaultdict(list)
        self.alert_handlers: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
        
        # Setup default thresholds
        self._setup_default_thresholds()
    
    def _init_database(self):
        """Initialize SQLite database for alerts"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    severity TEXT,
                    metric_type TEXT,
                    message TEXT,
                    node_id TEXT,
                    value REAL,
                    threshold REAL,
                    timestamp TEXT,
                    acknowledged BOOLEAN,
                    resolved BOOLEAN
                )
            ''')
    
    def _setup_default_thresholds(self):
        """Setup default monitoring thresholds"""
        default_thresholds = [
            Threshold(MetricType.NETWORK_LATENCY, 500.0, 1000.0, "greater"),
            Threshold(MetricType.NODE_HEALTH, 0.5, 0.3, "less"),
            Threshold(MetricType.SHARD_DISTRIBUTION, 5.0, 10.0, "greater"),
            Threshold(MetricType.RESOURCE_USAGE, 80.0, 95.0, "greater"),
            Threshold(MetricType.ERROR_RATE, 0.05, 0.1, "greater"),
        ]
        
        for threshold in default_thresholds:
            self.add_threshold(threshold)
    
    def add_threshold(self, threshold: Threshold):
        """Add a monitoring threshold"""
        self.thresholds[threshold.metric_type].append(threshold)
        self.logger.info(f"Added threshold for {threshold.metric_type.value}")
    
    def check_thresholds(self, metric_type: MetricType, metrics: List[MetricPoint]):
        """Check if metrics exceed thresholds"""
        if not metrics or metric_type not in self.thresholds:
            return
        
        for threshold in self.thresholds[metric_type]:
            if not threshold.enabled:
                continue
            
            # Get recent metrics within threshold duration
            cutoff_time = datetime.now() - timedelta(seconds=threshold.duration)
            recent_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                continue
            
            # Calculate average value
            avg_value = sum(m.value for m in recent_metrics) / len(recent_metrics)
            
            # Check threshold
            threshold_breached = False
            severity = AlertSeverity.LOW
            
            if threshold.comparison == "greater":
                if avg_value > threshold.critical_threshold:
                    threshold_breached = True
                    severity = AlertSeverity.CRITICAL
                elif avg_value > threshold.warning_threshold:
                    threshold_breached = True
                    severity = AlertSeverity.MEDIUM
            elif threshold.comparison == "less":
                if avg_value < threshold.critical_threshold:
                    threshold_breached = True
                    severity = AlertSeverity.CRITICAL
                elif avg_value < threshold.warning_threshold:
                    threshold_breached = True
                    severity = AlertSeverity.MEDIUM
            
            if threshold_breached:
                self._create_alert(
                    severity=severity,
                    metric_type=metric_type,
                    message=f"{metric_type.value} threshold breached: {avg_value:.2f}",
                    value=avg_value,
                    threshold=threshold.critical_threshold if severity == AlertSeverity.CRITICAL else threshold.warning_threshold
                )
    
    def _create_alert(self, severity: AlertSeverity, metric_type: MetricType, 
                     message: str, node_id: Optional[str] = None, 
                     value: Optional[float] = None, threshold: Optional[float] = None):
        """Create a new alert"""
        alert_id = f"{metric_type.value}_{int(time.time())}"
        
        # Check if similar alert already exists
        for existing_alert in self.alerts.values():
            if (existing_alert.metric_type == metric_type and 
                existing_alert.node_id == node_id and
                not existing_alert.resolved and
                datetime.now() - existing_alert.timestamp < timedelta(minutes=15)):
                return  # Don't create duplicate alerts
        
        alert = Alert(
            id=alert_id,
            severity=severity,
            metric_type=metric_type,
            message=message,
            node_id=node_id,
            value=value,
            threshold=threshold
        )
        
        self.alerts[alert_id] = alert
        self._save_alert_to_db(alert)
        self._trigger_alert_handlers(alert)
        
        self.logger.warning(f"Alert created: {alert.message}")
    
    def _save_alert_to_db(self, alert: Alert):
        """Save alert to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO alerts 
                    (id, severity, metric_type, message, node_id, value, threshold, timestamp, acknowledged, resolved)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.id, alert.severity.value, alert.metric_type.value,
                    alert.message, alert.node_id, alert.value, alert.threshold,
                    alert.timestamp.isoformat(), alert.acknowledged, alert.resolved
                ))
        except Exception as e:
            self.logger.error(f"Error saving alert to database: {e}")
    
    def _trigger_alert_handlers(self, alert: Alert):
        """Trigger all registered alert handlers"""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")
    
    def add_alert_handler(self, handler: Callable):
        """Add an alert handler function"""
        self.alert_handlers.append(handler)
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            self._save_alert_to_db(self.alerts[alert_id])
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self._save_alert_to_db(self.alerts[alert_id])
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity level"""
        return [alert for alert in self.alerts.values() if alert.severity == severity]

class DashboardServer:
    """Web dashboard server with dark neon theme"""
    
    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager, 
                 sharding_strategy: ShardingStrategy, host: str = "localhost", port: int = 8080):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        self.sharding_strategy = sharding_strategy
        self.host = host
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        
    def setup_routes(self):
        """Setup web routes"""
        self.app.router.add_get('/', self.dashboard_handler)
        self.app.router.add_get('/api/metrics', self.metrics_api_handler)
        self.app.router.add_get('/api/alerts', self.alerts_api_handler)
        self.app.router.add_get('/api/nodes', self.nodes_api_handler)
        self.app.router.add_post('/api/alerts/{alert_id}/acknowledge', self.acknowledge_alert_handler)
        self.app.router.add_post('/api/alerts/{alert_id}/resolve', self.resolve_alert_handler)
        self.app.router.add_static('/', path='static', name='static')
    
    async def dashboard_handler(self, request):
        """Serve dashboard HTML"""
        html_content = self._generate_dashboard_html()
        return web.Response(text=html_content, content_type='text/html')
    
    async def metrics_api_handler(self, request):
        """API endpoint for metrics data"""
        try:
            metrics_data = {}
            
            for metric_type in MetricType:
                recent_metrics = self.metrics_collector.get_recent_metrics(metric_type, 60)
                metrics_data[metric_type.value] = [
                    {
                        "timestamp": point.timestamp.isoformat(),
                        "value": point.value,
                        "node_id": point.node_id,
                        "metadata": point.metadata
                    }
                    for point in recent_metrics
                ]
            
            return web.json_response(metrics_data)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def alerts_api_handler(self, request):
        """API endpoint for alerts data"""
        try:
            alerts_data = []
            
            for alert in self.alert_manager.get_active_alerts():
                alerts_data.append({
                    "id": alert.id,
                    "severity": alert.severity.value,
                    "metric_type": alert.metric_type.value,
                    "message": alert.message,
                    "node_id": alert.node_id,
                    "value": alert.value,
                    "threshold": alert.threshold,
                    "timestamp": alert.timestamp.isoformat(),
                    "acknowledged": alert.acknowledged,
                    "resolved": alert.resolved
                })
            
            return web.json_response(alerts_data)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def nodes_api_handler(self, request):
        """API endpoint for nodes data"""
        try:
            nodes_data = []
            
            for node in self.sharding_strategy.nodes.values():
                health_score = self.metrics_collector._calculate_node_health_score(node)
                
                nodes_data.append({
                    "id": node.id,
                    "host": node.host,
                    "port": node.port,
                    "type": node.node_type.value,
                    "health_score": health_score,
                    "location": {
                        "country": node.location.country if node.location else "Unknown",
                        "city": node.location.city if node.location else "Unknown",
                        "latitude": node.location.latitude if node.location else 0,
                        "longitude": node.location.longitude if node.location else 0
                    },
                    "metrics": {
                        "latency": node.metrics.latency if node.metrics else 0,
                        "bandwidth": node.metrics.bandwidth if node.metrics else 0,
                        "uptime": node.metrics.uptime if node.metrics else 0,
                        "cpu_usage": node.metrics.cpu_usage if node.metrics else 0,
                        "memory_usage": node.metrics.memory_usage if node.metrics else 0
                    }
                })
            
            return web.json_response(nodes_data)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def acknowledge_alert_handler(self, request):
        """API endpoint to acknowledge an alert"""
        try:
            alert_id = request.match_info['alert_id']
            self.alert_manager.acknowledge_alert(alert_id)
            return web.json_response({"status": "acknowledged"})
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def resolve_alert_handler(self, request):
        """API endpoint to resolve an alert"""
        try:
            alert_id = request.match_info['alert_id']
            self.alert_manager.resolve_alert(alert_id)
            return web.json_response({"status": "resolved"})
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML with dark neon theme"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liberation System - Mesh Network Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
            color: #00ffff;
            overflow-x: hidden;
        }
        
        .dashboard {
            min-height: 100vh;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(0, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #00ffff;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
        }
        
        .header h1 {
            font-size: 2.5em;
            text-shadow: 0 0 10px #00ffff;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.8;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: rgba(0, 255, 255, 0.05);
            border: 1px solid #00ffff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 25px rgba(0, 255, 255, 0.4);
        }
        
        .metric-card h3 {
            color: #ff00ff;
            margin-bottom: 15px;
            text-shadow: 0 0 5px #ff00ff;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }
        
        .alerts-section {
            margin-bottom: 30px;
        }
        
        .alert-item {
            background: rgba(255, 0, 0, 0.1);
            border: 1px solid #ff0000;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .alert-critical {
            border-color: #ff0000;
            background: rgba(255, 0, 0, 0.2);
        }
        
        .alert-medium {
            border-color: #ffff00;
            background: rgba(255, 255, 0, 0.1);
        }
        
        .alert-low {
            border-color: #00ff00;
            background: rgba(0, 255, 0, 0.1);
        }
        
        .nodes-section {
            margin-top: 30px;
        }
        
        .nodes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .node-card {
            background: rgba(0, 255, 255, 0.05);
            border: 1px solid #00ffff;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        
        .node-healthy {
            border-color: #00ff00;
            background: rgba(0, 255, 0, 0.1);
        }
        
        .node-warning {
            border-color: #ffff00;
            background: rgba(255, 255, 0, 0.1);
        }
        
        .node-critical {
            border-color: #ff0000;
            background: rgba(255, 0, 0, 0.1);
        }
        
        .refresh-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 255, 255, 0.2);
            border: 1px solid #00ffff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .section-title {
            color: #ff00ff;
            font-size: 1.5em;
            margin-bottom: 20px;
            text-shadow: 0 0 5px #ff00ff;
            border-bottom: 2px solid #ff00ff;
            padding-bottom: 10px;
        }
        
        .loading {
            text-align: center;
            color: #00ffff;
            font-size: 1.2em;
            margin: 20px 0;
        }
        
        .error {
            color: #ff0000;
            text-align: center;
            background: rgba(255, 0, 0, 0.1);
            border: 1px solid #ff0000;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🌐 LIBERATION SYSTEM</h1>
            <p>Mesh Network Monitoring Dashboard</p>
        </div>
        
        <div class="refresh-indicator" id="refreshIndicator">⟳</div>
        
        <div class="metrics-grid" id="metricsGrid">
            <div class="loading">Loading metrics...</div>
        </div>
        
        <div class="alerts-section">
            <h2 class="section-title">🚨 Active Alerts</h2>
            <div id="alertsList">
                <div class="loading">Loading alerts...</div>
            </div>
        </div>
        
        <div class="nodes-section">
            <h2 class="section-title">🔗 Network Nodes</h2>
            <div class="nodes-grid" id="nodesGrid">
                <div class="loading">Loading nodes...</div>
            </div>
        </div>
    </div>
    
    <script>
        // Dashboard JavaScript
        class Dashboard {
            constructor() {
                this.updateInterval = 30000; // 30 seconds
                this.init();
            }
            
            init() {
                this.updateMetrics();
                this.updateAlerts();
                this.updateNodes();
                
                // Auto-refresh
                setInterval(() => {
                    this.updateMetrics();
                    this.updateAlerts();
                    this.updateNodes();
                }, this.updateInterval);
            }
            
            async updateMetrics() {
                try {
                    const response = await fetch('/api/metrics');
                    const data = await response.json();
                    this.renderMetrics(data);
                } catch (error) {
                    console.error('Error updating metrics:', error);
                    document.getElementById('metricsGrid').innerHTML = '<div class="error">Error loading metrics</div>';
                }
            }
            
            async updateAlerts() {
                try {
                    const response = await fetch('/api/alerts');
                    const data = await response.json();
                    this.renderAlerts(data);
                } catch (error) {
                    console.error('Error updating alerts:', error);
                    document.getElementById('alertsList').innerHTML = '<div class="error">Error loading alerts</div>';
                }
            }
            
            async updateNodes() {
                try {
                    const response = await fetch('/api/nodes');
                    const data = await response.json();
                    this.renderNodes(data);
                } catch (error) {
                    console.error('Error updating nodes:', error);
                    document.getElementById('nodesGrid').innerHTML = '<div class="error">Error loading nodes</div>';
                }
            }
            
            renderMetrics(data) {
                const grid = document.getElementById('metricsGrid');
                let html = '';
                
                for (const [metricType, points] of Object.entries(data)) {
                    if (points.length > 0) {
                        const latestPoint = points[points.length - 1];
                        const value = this.formatMetricValue(metricType, latestPoint.value);
                        
                        html += `
                            <div class="metric-card">
                                <h3>${this.formatMetricName(metricType)}</h3>
                                <div class="metric-value">${value}</div>
                                <div class="metric-timestamp">${new Date(latestPoint.timestamp).toLocaleTimeString()}</div>
                            </div>
                        `;
                    }
                }
                
                grid.innerHTML = html || '<div class="loading">No metrics available</div>';
            }
            
            renderAlerts(alerts) {
                const container = document.getElementById('alertsList');
                
                if (alerts.length === 0) {
                    container.innerHTML = '<div style="color: #00ff00; text-align: center;">✅ No active alerts</div>';
                    return;
                }
                
                let html = '';
                for (const alert of alerts) {
                    const severityClass = `alert-${alert.severity}`;
                    html += `
                        <div class="alert-item ${severityClass}">
                            <div>
                                <strong>${alert.severity.toUpperCase()}</strong>: ${alert.message}
                                <br>
                                <small>${new Date(alert.timestamp).toLocaleString()}</small>
                            </div>
                            <div>
                                <button onclick="dashboard.acknowledgeAlert('${alert.id}')">ACK</button>
                                <button onclick="dashboard.resolveAlert('${alert.id}')">RESOLVE</button>
                            </div>
                        </div>
                    `;
                }
                
                container.innerHTML = html;
            }
            
            renderNodes(nodes) {
                const grid = document.getElementById('nodesGrid');
                let html = '';
                
                for (const node of nodes) {
                    const healthClass = this.getNodeHealthClass(node.health_score);
                    html += `
                        <div class="node-card ${healthClass}">
                            <h4>${node.id}</h4>
                            <p>${node.type.toUpperCase()}</p>
                            <p>Health: ${(node.health_score * 100).toFixed(1)}%</p>
                            <p>${node.location.city}, ${node.location.country}</p>
                            <small>Latency: ${node.metrics.latency.toFixed(1)}ms</small>
                        </div>
                    `;
                }
                
                grid.innerHTML = html || '<div class="loading">No nodes available</div>';
            }
            
            formatMetricName(metricType) {
                return metricType.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
            }
            
            formatMetricValue(metricType, value) {
                switch (metricType) {
                    case 'network_latency':
                        return `${value.toFixed(1)}ms`;
                    case 'node_health':
                        return `${(value * 100).toFixed(1)}%`;
                    case 'resource_usage':
                        return `${value.toFixed(1)}%`;
                    case 'throughput':
                        return `${value.toFixed(0)} ops`;
                    default:
                        return value.toFixed(2);
                }
            }
            
            getNodeHealthClass(healthScore) {
                if (healthScore >= 0.8) return 'node-healthy';
                if (healthScore >= 0.5) return 'node-warning';
                return 'node-critical';
            }
            
            async acknowledgeAlert(alertId) {
                try {
                    await fetch(`/api/alerts/${alertId}/acknowledge`, { method: 'POST' });
                    this.updateAlerts();
                } catch (error) {
                    console.error('Error acknowledging alert:', error);
                }
            }
            
            async resolveAlert(alertId) {
                try {
                    await fetch(`/api/alerts/${alertId}/resolve`, { method: 'POST' });
                    this.updateAlerts();
                } catch (error) {
                    console.error('Error resolving alert:', error);
                }
            }
        }
        
        // Initialize dashboard
        const dashboard = new Dashboard();
    </script>
</body>
</html>'''
    
    async def start_server(self):
        """Start the dashboard server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        print(f"🌐 Dashboard server started at http://{self.host}:{self.port}")

class MonitoringSystem:
    """Main monitoring system coordinator"""
    
    def __init__(self, sharding_strategy: ShardingStrategy):
        self.sharding_strategy = sharding_strategy
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.dashboard = DashboardServer(self.metrics_collector, self.alert_manager, sharding_strategy)
        self.logger = logging.getLogger(__name__)
        
        # Setup alert handlers
        self.alert_manager.add_alert_handler(self._log_alert_handler)
        self.alert_manager.add_alert_handler(self._email_alert_handler)
        
        self.running = False
    
    async def start(self):
        """Start the monitoring system"""
        self.running = True
        self.logger.info("🚀 Starting monitoring system...")
        
        # Start metrics collection
        metrics_task = asyncio.create_task(
            self.metrics_collector.start_collection(self.sharding_strategy)
        )
        
        # Start dashboard server
        dashboard_task = asyncio.create_task(self.dashboard.start_server())
        
        # Start monitoring loop
        monitor_task = asyncio.create_task(self._monitoring_loop())
        
        # Wait for all tasks
        await asyncio.gather(metrics_task, dashboard_task, monitor_task)
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Check all metric types for threshold breaches
                for metric_type in MetricType:
                    recent_metrics = self.metrics_collector.get_recent_metrics(metric_type, 5)
                    if recent_metrics:
                        self.alert_manager.check_thresholds(metric_type, recent_metrics)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    def _log_alert_handler(self, alert: Alert):
        """Log alert handler"""
        self.logger.warning(f"ALERT [{alert.severity.value.upper()}]: {alert.message}")
    
    def _email_alert_handler(self, alert: Alert):
        """Email alert handler (placeholder)"""
        # TODO: Implement email notifications
        pass
    
    def stop(self):
        """Stop the monitoring system"""
        self.running = False
        self.metrics_collector.stop_collection()
        self.logger.info("⏹️  Monitoring system stopped")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        active_alerts = self.alert_manager.get_active_alerts()
        critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
        
        return {
            "status": "critical" if critical_alerts else "healthy",
            "total_nodes": len(self.sharding_strategy.nodes),
            "active_alerts": len(active_alerts),
            "critical_alerts": len(critical_alerts),
            "system_health": self._calculate_system_health()
        }
    
    def _calculate_system_health(self) -> float:
        """Calculate overall system health score"""
        if not self.sharding_strategy.nodes:
            return 0.0
        
        total_health = 0.0
        for node in self.sharding_strategy.nodes.values():
            health_score = self.metrics_collector._calculate_node_health_score(node)
            total_health += health_score
        
        return total_health / len(self.sharding_strategy.nodes)
