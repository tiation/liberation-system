#!/usr/bin/env python3
"""
Performance monitoring and metrics system for the Liberation System.
Provides real-time monitoring, alerting, and performance optimization.
"""

import asyncio
import logging
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import os
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.layout import Layout


@dataclass
class MetricData:
    """Individual metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """System alert configuration"""
    metric_name: str
    threshold: float
    condition: str  # 'above', 'below', 'equal'
    severity: str  # 'low', 'medium', 'high', 'critical'
    callback: Optional[Callable] = None
    enabled: bool = True
    cooldown: int = 300  # 5 minutes default cooldown


@dataclass
class PerformanceReport:
    """Performance analysis report"""
    start_time: datetime
    end_time: datetime
    total_duration: float
    metrics_summary: Dict[str, Dict[str, float]]
    alerts_triggered: List[Dict[str, Any]]
    recommendations: List[str]
    system_health_score: float


class MetricsCollector:
    """Collects and aggregates system metrics"""
    
    def __init__(self, max_data_points: int = 10000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_data_points))
        self.max_data_points = max_data_points
        self.logger = logging.getLogger(__name__)
        
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Record a new metric data point"""
        metric_data = MetricData(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.metrics[name].append(metric_data)
        
    def get_metric_stats(self, name: str, time_window: Optional[timedelta] = None) -> Dict[str, float]:
        """Get statistical summary of a metric"""
        if name not in self.metrics:
            return {}
            
        data_points = self.metrics[name]
        
        # Filter by time window if provided
        if time_window:
            cutoff_time = datetime.now() - time_window
            data_points = [dp for dp in data_points if dp.timestamp >= cutoff_time]
        
        if not data_points:
            return {}
            
        values = [dp.value for dp in data_points]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': sum(values) / len(values),
            'median': sorted(values)[len(values) // 2],
            'current': values[-1] if values else 0,
            'trend': self._calculate_trend(values[-10:]) if len(values) >= 10 else 0
        }
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction (positive = increasing, negative = decreasing)"""
        if len(values) < 2:
            return 0
        
        # Simple linear regression slope
        n = len(values)
        sum_x = sum(range(n))
        sum_y = sum(values)
        sum_xy = sum(i * v for i, v in enumerate(values))
        sum_xx = sum(i * i for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        return slope
    
    def get_all_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get stats for all metrics"""
        return {name: self.get_metric_stats(name) for name in self.metrics.keys()}


class AlertManager:
    """Manages performance alerts and notifications"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_history: List[Dict[str, Any]] = []
        self.last_alert_time: Dict[str, datetime] = {}
        self.logger = logging.getLogger(__name__)
        
    def add_alert(self, alert: Alert):
        """Add a new alert configuration"""
        self.alerts.append(alert)
        self.logger.info(f"Added alert for {alert.metric_name}: {alert.condition} {alert.threshold}")
        
    def check_alerts(self, metrics: Dict[str, Dict[str, float]]):
        """Check all alerts against current metrics"""
        current_time = datetime.now()
        
        for alert in self.alerts:
            if not alert.enabled:
                continue
                
            # Check cooldown
            if alert.metric_name in self.last_alert_time:
                time_since_last = (current_time - self.last_alert_time[alert.metric_name]).total_seconds()
                if time_since_last < alert.cooldown:
                    continue
                    
            # Check if metric exists
            if alert.metric_name not in metrics:
                continue
                
            metric_stats = metrics[alert.metric_name]
            current_value = metric_stats.get('current', 0)
            
            # Check alert condition
            triggered = False
            if alert.condition == 'above' and current_value > alert.threshold:
                triggered = True
            elif alert.condition == 'below' and current_value < alert.threshold:
                triggered = True
            elif alert.condition == 'equal' and abs(current_value - alert.threshold) < 0.01:
                triggered = True
                
            if triggered:
                self._trigger_alert(alert, current_value, metric_stats)
                
    def _trigger_alert(self, alert: Alert, current_value: float, metric_stats: Dict[str, float]):
        """Trigger an alert"""
        alert_data = {
            'timestamp': datetime.now(),
            'metric_name': alert.metric_name,
            'current_value': current_value,
            'threshold': alert.threshold,
            'condition': alert.condition,
            'severity': alert.severity,
            'metric_stats': metric_stats
        }
        
        self.alert_history.append(alert_data)
        self.last_alert_time[alert.metric_name] = datetime.now()
        
        # Log alert
        self.logger.warning(f"ALERT: {alert.metric_name} {alert.condition} {alert.threshold} (current: {current_value})")
        
        # Execute callback if provided
        if alert.callback:
            try:
                alert.callback(alert_data)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    def get_recent_alerts(self, time_window: timedelta = timedelta(hours=1)) -> List[Dict[str, Any]]:
        """Get recent alerts within time window"""
        cutoff_time = datetime.now() - time_window
        return [alert for alert in self.alert_history if alert['timestamp'] >= cutoff_time]


class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: float = 5.0):
        """Start system monitoring in background thread"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
            
    def _monitor_loop(self, interval: float):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Record metrics
                performance_monitor.record_metric('system.cpu_percent', cpu_percent)
                performance_monitor.record_metric('system.memory_percent', memory.percent)
                performance_monitor.record_metric('system.memory_available', memory.available / 1024 / 1024 / 1024)  # GB
                performance_monitor.record_metric('system.disk_percent', disk.percent)
                performance_monitor.record_metric('system.disk_free', disk.free / 1024 / 1024 / 1024)  # GB
                
                # Network I/O
                net_io = psutil.net_io_counters()
                performance_monitor.record_metric('system.network_bytes_sent', net_io.bytes_sent)
                performance_monitor.record_metric('system.network_bytes_recv', net_io.bytes_recv)
                
                # Process-specific metrics
                process = psutil.Process()
                performance_monitor.record_metric('process.cpu_percent', process.cpu_percent())
                performance_monitor.record_metric('process.memory_mb', process.memory_info().rss / 1024 / 1024)
                performance_monitor.record_metric('process.threads', process.num_threads())
                performance_monitor.record_metric('process.open_files', len(process.open_files()))
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"System monitoring error: {e}")
                time.sleep(interval)


class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self, enable_console_display: bool = True):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.system_monitor = SystemMonitor()
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
        self.enable_console_display = enable_console_display
        self.display_thread = None
        self.display_running = False
        
        # Setup default alerts
        self._setup_default_alerts()
        
    def _setup_default_alerts(self):
        """Setup default system alerts"""
        default_alerts = [
            Alert("system.cpu_percent", 80.0, "above", "medium"),
            Alert("system.memory_percent", 90.0, "above", "high"),
            Alert("system.disk_percent", 90.0, "above", "high"),
            Alert("system.disk_free", 1.0, "below", "medium"),  # Less than 1GB free
            Alert("database.connection_errors", 5, "above", "high"),
            Alert("database.query_timeout", 30.0, "above", "medium"),
            Alert("liberation.error_rate", 0.1, "above", "medium"),  # 10% error rate
        ]
        
        for alert in default_alerts:
            self.alert_manager.add_alert(alert)
            
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Record a metric value"""
        self.metrics_collector.record_metric(name, value, tags, metadata)
        
    def start_monitoring(self):
        """Start comprehensive monitoring"""
        self.system_monitor.start_monitoring()
        
        if self.enable_console_display:
            self.start_console_display()
            
        self.logger.info("Performance monitoring started")
        
    def stop_monitoring(self):
        """Stop all monitoring"""
        self.system_monitor.stop_monitoring()
        self.stop_console_display()
        self.logger.info("Performance monitoring stopped")
        
    def start_console_display(self):
        """Start console display in background thread"""
        if self.display_running:
            return
            
        self.display_running = True
        self.display_thread = threading.Thread(target=self._display_loop)
        self.display_thread.daemon = True
        self.display_thread.start()
        
    def stop_console_display(self):
        """Stop console display"""
        self.display_running = False
        if self.display_thread:
            self.display_thread.join(timeout=1)
            
    def _display_loop(self):
        """Console display loop"""
        while self.display_running:
            try:
                self._update_display()
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                self.logger.error(f"Display update error: {e}")
                time.sleep(2)
                
    def _update_display(self):
        """Update console display"""
        # Get current metrics
        metrics = self.metrics_collector.get_all_metrics()
        
        # Check alerts
        self.alert_manager.check_alerts(metrics)
        
        # Create display table
        table = Table(title="🚀 Liberation System Performance Monitor")
        table.add_column("Metric", style="cyan")
        table.add_column("Current", style="green")
        table.add_column("Average", style="yellow")
        table.add_column("Trend", style="magenta")
        table.add_column("Status", style="bold")
        
        for metric_name, stats in metrics.items():
            if not stats:
                continue
                
            current = f"{stats['current']:.2f}"
            average = f"{stats['mean']:.2f}"
            trend = "📈" if stats['trend'] > 0 else "📉" if stats['trend'] < 0 else "➡️"
            
            # Determine status
            status = "✅ OK"
            if metric_name.endswith('_percent'):
                if stats['current'] > 90:
                    status = "🔴 CRITICAL"
                elif stats['current'] > 80:
                    status = "🟡 WARNING"
            elif metric_name.endswith('_errors'):
                if stats['current'] > 0:
                    status = "🟡 WARNING"
                    
            table.add_row(metric_name, current, average, trend, status)
            
        # Show recent alerts
        recent_alerts = self.alert_manager.get_recent_alerts(timedelta(minutes=5))
        if recent_alerts:
            alert_panel = Panel(
                "\n".join([f"⚠️  {alert['metric_name']}: {alert['current_value']:.2f} {alert['condition']} {alert['threshold']}" 
                          for alert in recent_alerts[-5:]]),
                title="🚨 Recent Alerts",
                border_style="red"
            )
            self.console.print(alert_panel)
            
        self.console.print(table)
        
    def get_performance_report(self, time_window: timedelta = timedelta(hours=1)) -> PerformanceReport:
        """Generate comprehensive performance report"""
        end_time = datetime.now()
        start_time = end_time - time_window
        
        # Get metrics summary
        metrics_summary = {}
        for metric_name in self.metrics_collector.metrics.keys():
            metrics_summary[metric_name] = self.metrics_collector.get_metric_stats(metric_name, time_window)
            
        # Get alerts
        alerts_triggered = self.alert_manager.get_recent_alerts(time_window)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics_summary, alerts_triggered)
        
        # Calculate health score
        health_score = self._calculate_health_score(metrics_summary, alerts_triggered)
        
        return PerformanceReport(
            start_time=start_time,
            end_time=end_time,
            total_duration=time_window.total_seconds(),
            metrics_summary=metrics_summary,
            alerts_triggered=alerts_triggered,
            recommendations=recommendations,
            system_health_score=health_score
        )
    
    def _generate_recommendations(self, metrics_summary: Dict[str, Dict[str, float]], 
                                alerts: List[Dict[str, Any]]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Check CPU usage
        if 'system.cpu_percent' in metrics_summary:
            cpu_stats = metrics_summary['system.cpu_percent']
            if cpu_stats.get('mean', 0) > 70:
                recommendations.append("High CPU usage detected. Consider optimizing resource-intensive operations.")
                
        # Check memory usage
        if 'system.memory_percent' in metrics_summary:
            memory_stats = metrics_summary['system.memory_percent']
            if memory_stats.get('mean', 0) > 80:
                recommendations.append("High memory usage detected. Consider implementing memory optimization.")
                
        # Check database performance
        if 'database.connection_errors' in metrics_summary:
            db_errors = metrics_summary['database.connection_errors']
            if db_errors.get('current', 0) > 0:
                recommendations.append("Database connection errors detected. Check database connectivity and pool settings.")
                
        # Check error rates
        if 'liberation.error_rate' in metrics_summary:
            error_rate = metrics_summary['liberation.error_rate']
            if error_rate.get('mean', 0) > 0.05:  # 5% error rate
                recommendations.append("High error rate detected. Review error logs and implement better error handling.")
                
        # Alert-based recommendations
        if len(alerts) > 10:
            recommendations.append("High number of alerts triggered. Consider adjusting alert thresholds or investigating root causes.")
            
        return recommendations
    
    def _calculate_health_score(self, metrics_summary: Dict[str, Dict[str, float]], 
                               alerts: List[Dict[str, Any]]) -> float:
        """Calculate system health score (0-100)"""
        score = 100.0
        
        # Penalize high resource usage
        if 'system.cpu_percent' in metrics_summary:
            cpu_mean = metrics_summary['system.cpu_percent'].get('mean', 0)
            if cpu_mean > 80:
                score -= 20
            elif cpu_mean > 60:
                score -= 10
                
        if 'system.memory_percent' in metrics_summary:
            memory_mean = metrics_summary['system.memory_percent'].get('mean', 0)
            if memory_mean > 90:
                score -= 25
            elif memory_mean > 70:
                score -= 15
                
        # Penalize errors
        if 'liberation.error_rate' in metrics_summary:
            error_rate = metrics_summary['liberation.error_rate'].get('mean', 0)
            score -= error_rate * 100  # Direct penalty for error rate
            
        # Penalize alerts
        critical_alerts = [a for a in alerts if a['severity'] == 'critical']
        high_alerts = [a for a in alerts if a['severity'] == 'high']
        
        score -= len(critical_alerts) * 10
        score -= len(high_alerts) * 5
        
        return max(0, min(100, score))
    
    def save_metrics_to_file(self, filepath: str):
        """Save current metrics to file"""
        metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics_collector.get_all_metrics(),
            'alerts': self.alert_manager.get_recent_alerts(timedelta(hours=24))
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2, default=str)
            
    def load_metrics_from_file(self, filepath: str):
        """Load metrics from file"""
        if not os.path.exists(filepath):
            return
            
        with open(filepath, 'r') as f:
            metrics_data = json.load(f)
            
        # TODO: Implement metric loading logic
        self.logger.info(f"Loaded metrics from {filepath}")


# Global performance monitor instance
performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor"""
    global performance_monitor
    
    if performance_monitor is None:
        performance_monitor = PerformanceMonitor()
        
    return performance_monitor


def start_performance_monitoring():
    """Start global performance monitoring"""
    monitor = get_performance_monitor()
    monitor.start_monitoring()


def stop_performance_monitoring():
    """Stop global performance monitoring"""
    global performance_monitor
    
    if performance_monitor:
        performance_monitor.stop_monitoring()


def record_metric(name: str, value: float, tags: Dict[str, str] = None, metadata: Dict[str, Any] = None):
    """Record a metric globally"""
    monitor = get_performance_monitor()
    monitor.record_metric(name, value, tags, metadata)


def get_performance_report(time_window: timedelta = timedelta(hours=1)) -> PerformanceReport:
    """Get global performance report"""
    monitor = get_performance_monitor()
    return monitor.get_performance_report(time_window)


if __name__ == "__main__":
    # Example usage
    monitor = PerformanceMonitor()
    
    # Record some test metrics
    for i in range(100):
        monitor.record_metric("test.cpu", 50 + i % 30)
        monitor.record_metric("test.memory", 60 + i % 20)
        time.sleep(0.1)
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        # Keep running for demonstration
        time.sleep(30)
    finally:
        monitor.stop_monitoring()
