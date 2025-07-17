import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
from collections import defaultdict, deque

from ..websocket.manager import websocket_manager
from ..events.system import event_system, EventType

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

class MetricCategory(Enum):
    """Categories of metrics"""
    SYSTEM = "system"
    RESOURCE = "resource"
    TRUTH = "truth"
    MESH = "mesh"
    USER = "user"
    PERFORMANCE = "performance"
    SECURITY = "security"

@dataclass
class MetricPoint:
    """Individual metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "tags": self.tags
        }

@dataclass
class Metric:
    """Metric definition and data"""
    name: str
    type: MetricType
    category: MetricCategory
    description: str
    unit: str
    points: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def add_point(self, value: float, tags: Dict[str, str] = None):
        """Add a new data point"""
        self.points.append(MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {}
        ))
    
    def get_latest_value(self) -> Optional[float]:
        """Get the latest metric value"""
        if self.points:
            return self.points[-1].value
        return None
    
    def get_average(self, time_window: timedelta = None) -> float:
        """Get average value over time window"""
        if not self.points:
            return 0.0
        
        if time_window:
            cutoff_time = datetime.now() - time_window
            relevant_points = [p for p in self.points if p.timestamp >= cutoff_time]
        else:
            relevant_points = list(self.points)
        
        if not relevant_points:
            return 0.0
        
        return statistics.mean(point.value for point in relevant_points)
    
    def get_trend(self, time_window: timedelta = None) -> str:
        """Get trend direction: 'up', 'down', or 'stable'"""
        if len(self.points) < 2:
            return "stable"
        
        if time_window:
            cutoff_time = datetime.now() - time_window
            relevant_points = [p for p in self.points if p.timestamp >= cutoff_time]
        else:
            relevant_points = list(self.points)
        
        if len(relevant_points) < 2:
            return "stable"
        
        # Compare first and last values
        first_value = relevant_points[0].value
        last_value = relevant_points[-1].value
        
        if last_value > first_value * 1.05:  # 5% threshold
            return "up"
        elif last_value < first_value * 0.95:
            return "down"
        else:
            return "stable"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.value,
            "category": self.category.value,
            "description": self.description,
            "unit": self.unit,
            "latest_value": self.get_latest_value(),
            "average": self.get_average(),
            "trend": self.get_trend(),
            "point_count": len(self.points)
        }

class RealTimeMetricsService:
    """Advanced real-time metrics and analytics service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, Metric] = {}
        self.metric_subscribers: Dict[str, List[str]] = {}  # metric_name -> connection_ids
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.dashboard_metrics: Dict[str, List[str]] = {}  # dashboard_id -> metric_names
        
        # Initialize core metrics
        self._initialize_core_metrics()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_core_metrics(self):
        """Initialize core system metrics"""
        core_metrics = [
            # System metrics
            ("system_uptime", MetricType.TIMER, MetricCategory.SYSTEM, "System uptime in seconds", "seconds"),
            ("system_memory_usage", MetricType.GAUGE, MetricCategory.SYSTEM, "Memory usage percentage", "percent"),
            ("system_cpu_usage", MetricType.GAUGE, MetricCategory.SYSTEM, "CPU usage percentage", "percent"),
            ("system_disk_usage", MetricType.GAUGE, MetricCategory.SYSTEM, "Disk usage percentage", "percent"),
            
            # Resource metrics
            ("resources_distributed_total", MetricType.COUNTER, MetricCategory.RESOURCE, "Total resources distributed", "dollars"),
            ("resources_distributed_rate", MetricType.RATE, MetricCategory.RESOURCE, "Resource distribution rate", "dollars/second"),
            ("active_humans", MetricType.GAUGE, MetricCategory.RESOURCE, "Number of active humans", "count"),
            ("weekly_distributions", MetricType.COUNTER, MetricCategory.RESOURCE, "Weekly distributions completed", "count"),
            
            # Truth spreading metrics
            ("truth_messages_sent", MetricType.COUNTER, MetricCategory.TRUTH, "Truth messages sent", "count"),
            ("truth_channels_active", MetricType.GAUGE, MetricCategory.TRUTH, "Active truth channels", "count"),
            ("truth_reach_total", MetricType.COUNTER, MetricCategory.TRUTH, "Total truth reach", "count"),
            ("truth_effectiveness", MetricType.GAUGE, MetricCategory.TRUTH, "Truth spreading effectiveness", "percent"),
            
            # Mesh network metrics
            ("mesh_nodes_active", MetricType.GAUGE, MetricCategory.MESH, "Active mesh nodes", "count"),
            ("mesh_connections_total", MetricType.COUNTER, MetricCategory.MESH, "Total mesh connections", "count"),
            ("mesh_latency_avg", MetricType.GAUGE, MetricCategory.MESH, "Average mesh latency", "milliseconds"),
            ("mesh_throughput", MetricType.GAUGE, MetricCategory.MESH, "Mesh network throughput", "bytes/second"),
            
            # User metrics
            ("websocket_connections", MetricType.GAUGE, MetricCategory.USER, "Active WebSocket connections", "count"),
            ("user_sessions_active", MetricType.GAUGE, MetricCategory.USER, "Active user sessions", "count"),
            ("user_actions_rate", MetricType.RATE, MetricCategory.USER, "User actions per second", "actions/second"),
            
            # Performance metrics
            ("api_response_time", MetricType.HISTOGRAM, MetricCategory.PERFORMANCE, "API response time", "milliseconds"),
            ("websocket_message_rate", MetricType.RATE, MetricCategory.PERFORMANCE, "WebSocket message rate", "messages/second"),
            ("database_query_time", MetricType.HISTOGRAM, MetricCategory.PERFORMANCE, "Database query time", "milliseconds"),
            ("error_rate", MetricType.RATE, MetricCategory.PERFORMANCE, "Error rate", "errors/second"),
        ]
        
        for name, metric_type, category, description, unit in core_metrics:
            self.metrics[name] = Metric(
                name=name,
                type=metric_type,
                category=category,
                description=description,
                unit=unit
            )
    
    def _start_background_tasks(self):
        """Start background tasks for metrics collection"""
        asyncio.create_task(self._collect_system_metrics())
        asyncio.create_task(self._broadcast_metrics())
        asyncio.create_task(self._check_alerts())
    
    async def _collect_system_metrics(self):
        """Collect system metrics periodically"""
        while True:
            try:
                import psutil
                
                # System resource metrics
                self.record_metric("system_cpu_usage", psutil.cpu_percent())
                self.record_metric("system_memory_usage", psutil.virtual_memory().percent)
                self.record_metric("system_disk_usage", psutil.disk_usage('/').percent)
                
                # WebSocket connections
                ws_stats = websocket_manager.get_stats()
                self.record_metric("websocket_connections", ws_stats.get("total_connections", 0))
                
                await asyncio.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(30)
    
    async def _broadcast_metrics(self):
        """Broadcast metrics to subscribers"""
        while True:
            try:
                # Broadcast metrics to dashboard connections
                dashboard_data = await self.get_dashboard_metrics()
                
                await websocket_manager.broadcast_to_channel(
                    channel="dashboard",
                    message_type="metrics_update",
                    data=dashboard_data
                )
                
                # Broadcast to admin connections
                admin_data = await self.get_admin_metrics()
                await websocket_manager.broadcast_to_channel(
                    channel="admin",
                    message_type="admin_metrics",
                    data=admin_data
                )
                
                await asyncio.sleep(5)  # Broadcast every 5 seconds
            except Exception as e:
                self.logger.error(f"Error broadcasting metrics: {e}")
                await asyncio.sleep(5)
    
    async def _check_alerts(self):
        """Check for metric alerts"""
        while True:
            try:
                for metric_name, rule in self.alert_rules.items():
                    if metric_name in self.metrics:
                        metric = self.metrics[metric_name]
                        latest_value = metric.get_latest_value()
                        
                        if latest_value is not None:
                            await self._evaluate_alert_rule(metric, latest_value, rule)
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error checking alerts: {e}")
                await asyncio.sleep(60)
    
    async def _evaluate_alert_rule(self, metric: Metric, value: float, rule: Dict[str, Any]):
        """Evaluate a single alert rule"""
        try:
            threshold = rule.get("threshold", 0)
            condition = rule.get("condition", "greater_than")
            severity = rule.get("severity", "warning")
            
            triggered = False
            
            if condition == "greater_than" and value > threshold:
                triggered = True
            elif condition == "less_than" and value < threshold:
                triggered = True
            elif condition == "equals" and value == threshold:
                triggered = True
            
            if triggered:
                from ..notifications.service import notification_service
                await notification_service.send_system_alert(
                    title=f"🚨 Metric Alert: {metric.name}",
                    message=f"Metric {metric.name} is {value} {metric.unit} (threshold: {threshold})",
                    alert_level=severity,
                    data={
                        "metric_name": metric.name,
                        "current_value": value,
                        "threshold": threshold,
                        "condition": condition
                    }
                )
        except Exception as e:
            self.logger.error(f"Error evaluating alert rule: {e}")
    
    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric value"""
        try:
            if metric_name in self.metrics:
                self.metrics[metric_name].add_point(value, tags)
            else:
                self.logger.warning(f"Unknown metric: {metric_name}")
        except Exception as e:
            self.logger.error(f"Error recording metric {metric_name}: {e}")
    
    def create_custom_metric(
        self,
        name: str,
        metric_type: MetricType,
        category: MetricCategory,
        description: str,
        unit: str
    ) -> bool:
        """Create a custom metric"""
        try:
            if name in self.metrics:
                return False
            
            self.metrics[name] = Metric(
                name=name,
                type=metric_type,
                category=category,
                description=description,
                unit=unit
            )
            
            self.logger.info(f"Created custom metric: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating custom metric: {e}")
            return False
    
    def add_alert_rule(
        self,
        metric_name: str,
        threshold: float,
        condition: str = "greater_than",
        severity: str = "warning"
    ) -> bool:
        """Add an alert rule for a metric"""
        try:
            if metric_name not in self.metrics:
                return False
            
            self.alert_rules[metric_name] = {
                "threshold": threshold,
                "condition": condition,
                "severity": severity
            }
            
            self.logger.info(f"Added alert rule for {metric_name}: {condition} {threshold}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding alert rule: {e}")
            return False
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get metrics for the main dashboard"""
        try:
            key_metrics = [
                "resources_distributed_total",
                "active_humans",
                "truth_messages_sent",
                "mesh_nodes_active",
                "websocket_connections",
                "system_cpu_usage",
                "system_memory_usage"
            ]
            
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "metrics": {},
                "summary": {
                    "total_metrics": len(self.metrics),
                    "active_connections": websocket_manager.get_stats().get("total_connections", 0),
                    "system_health": "healthy"  # Calculated based on metrics
                }
            }
            
            for metric_name in key_metrics:
                if metric_name in self.metrics:
                    metric = self.metrics[metric_name]
                    dashboard_data["metrics"][metric_name] = {
                        "current_value": metric.get_latest_value(),
                        "average": metric.get_average(timedelta(hours=1)),
                        "trend": metric.get_trend(timedelta(hours=1)),
                        "unit": metric.unit
                    }
            
            return dashboard_data
        except Exception as e:
            self.logger.error(f"Error getting dashboard metrics: {e}")
            return {"error": str(e)}
    
    async def get_admin_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics for admin dashboard"""
        try:
            admin_data = {
                "timestamp": datetime.now().isoformat(),
                "categories": {},
                "alerts": [],
                "system_overview": {
                    "total_metrics": len(self.metrics),
                    "active_alert_rules": len(self.alert_rules),
                    "metrics_by_category": {}
                }
            }
            
            # Group metrics by category
            for metric in self.metrics.values():
                category = metric.category.value
                if category not in admin_data["categories"]:
                    admin_data["categories"][category] = []
                
                admin_data["categories"][category].append(metric.to_dict())
                
                # Count by category
                admin_data["system_overview"]["metrics_by_category"][category] = \
                    admin_data["system_overview"]["metrics_by_category"].get(category, 0) + 1
            
            # Recent alerts (would be stored in a proper implementation)
            admin_data["alerts"] = []
            
            return admin_data
        except Exception as e:
            self.logger.error(f"Error getting admin metrics: {e}")
            return {"error": str(e)}
    
    async def get_metric_history(
        self,
        metric_name: str,
        time_window: timedelta = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get historical data for a metric"""
        try:
            if metric_name not in self.metrics:
                return []
            
            metric = self.metrics[metric_name]
            points = list(metric.points)
            
            if time_window:
                cutoff_time = datetime.now() - time_window
                points = [p for p in points if p.timestamp >= cutoff_time]
            
            # Return latest points up to limit
            return [point.to_dict() for point in points[-limit:]]
        except Exception as e:
            self.logger.error(f"Error getting metric history: {e}")
            return []
    
    def get_metric_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        try:
            if metric_name not in self.metrics:
                return {"error": "Metric not found"}
            
            metric = self.metrics[metric_name]
            values = [p.value for p in metric.points]
            
            if not values:
                return {"error": "No data points"}
            
            return {
                "name": metric.name,
                "description": metric.description,
                "unit": metric.unit,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "latest_value": values[-1],
                "trend": metric.get_trend()
            }
        except Exception as e:
            self.logger.error(f"Error getting metric summary: {e}")
            return {"error": str(e)}

# Global metrics service instance
metrics_service = RealTimeMetricsService()

# Event handlers for automatic metric collection
async def handle_resource_distribution_event(event):
    """Handle resource distribution events for metrics"""
    data = event.data
    amount = data.get("amount", 0)
    
    metrics_service.record_metric("resources_distributed_total", amount)
    metrics_service.record_metric("weekly_distributions", 1)

async def handle_truth_message_event(event):
    """Handle truth message events for metrics"""
    data = event.data
    reach = data.get("reach_count", 0)
    
    metrics_service.record_metric("truth_messages_sent", 1)
    metrics_service.record_metric("truth_reach_total", reach)

async def handle_mesh_network_event(event):
    """Handle mesh network events for metrics"""
    data = event.data
    
    if event.type == EventType.MESH_NODE_CONNECTED:
        metrics_service.record_metric("mesh_nodes_active", 1)
    elif event.type == EventType.MESH_NODE_DISCONNECTED:
        metrics_service.record_metric("mesh_nodes_active", -1)

async def handle_user_connection_event(event):
    """Handle user connection events for metrics"""
    if event.type == EventType.USER_CONNECTED:
        metrics_service.record_metric("websocket_connections", 1)
        metrics_service.record_metric("user_sessions_active", 1)
    elif event.type == EventType.USER_DISCONNECTED:
        metrics_service.record_metric("websocket_connections", -1)
        metrics_service.record_metric("user_sessions_active", -1)

# Register event handlers
event_system.register_handler(EventType.RESOURCE_DISTRIBUTED, handle_resource_distribution_event)
event_system.register_handler(EventType.TRUTH_MESSAGE_SENT, handle_truth_message_event)
event_system.register_handler(EventType.MESH_NODE_CONNECTED, handle_mesh_network_event)
event_system.register_handler(EventType.MESH_NODE_DISCONNECTED, handle_mesh_network_event)
event_system.register_handler(EventType.USER_CONNECTED, handle_user_connection_event)
event_system.register_handler(EventType.USER_DISCONNECTED, handle_user_connection_event)
