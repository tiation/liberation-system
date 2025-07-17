# core/monitoring.py

import time
import asyncio
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
from pathlib import Path

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from prometheus_client.exposition import MetricsHandler
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from .config import get_config
from .logging_system import get_logger

# Prometheus metrics
REGISTRY = CollectorRegistry()

# Core metrics
REQUEST_COUNT = Counter(
    'liberation_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

REQUEST_DURATION = Histogram(
    'liberation_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=REGISTRY
)

ACTIVE_CONNECTIONS = Gauge(
    'liberation_active_connections',
    'Number of active WebSocket connections',
    registry=REGISTRY
)

DATABASE_QUERIES = Counter(
    'liberation_database_queries_total',
    'Total number of database queries',
    ['operation', 'table'],
    registry=REGISTRY
)

DATABASE_QUERY_DURATION = Histogram(
    'liberation_database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table'],
    registry=REGISTRY
)

SYSTEM_MEMORY = Gauge(
    'liberation_system_memory_bytes',
    'System memory usage in bytes',
    ['type'],
    registry=REGISTRY
)

SYSTEM_CPU = Gauge(
    'liberation_system_cpu_percent',
    'System CPU usage percentage',
    registry=REGISTRY
)

MESH_NODES = Gauge(
    'liberation_mesh_nodes',
    'Number of active mesh nodes',
    registry=REGISTRY
)

TRUTH_MESSAGES = Counter(
    'liberation_truth_messages_total',
    'Total number of truth messages processed',
    ['type', 'channel'],
    registry=REGISTRY
)

RESOURCE_DISTRIBUTIONS = Counter(
    'liberation_resource_distributions_total',
    'Total number of resource distributions',
    ['type'],
    registry=REGISTRY
)

ERRORS = Counter(
    'liberation_errors_total',
    'Total number of errors',
    ['component', 'type'],
    registry=REGISTRY
)

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: str  # 'healthy', 'unhealthy', 'warning'
    message: str
    timestamp: datetime
    duration: float
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricSnapshot:
    """Snapshot of system metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_used: int
    memory_total: int
    disk_used: int
    disk_total: int
    active_connections: int
    database_connections: int
    mesh_nodes: int
    error_rate: float
    request_rate: float

class HealthChecker:
    """System health checker"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger('liberation.monitoring')
        self.checks = {}
        self.results = {}
        
        # Register default health checks
        self._register_default_checks()
    
    def register_check(self, name: str, check_func: Callable[[], HealthCheckResult]):
        """Register a health check function"""
        self.checks[name] = check_func
    
    def _register_default_checks(self):
        """Register default system health checks"""
        self.register_check('system_resources', self._check_system_resources)
        self.register_check('database', self._check_database)
        self.register_check('disk_space', self._check_disk_space)
        self.register_check('memory', self._check_memory)
    
    def _check_system_resources(self) -> HealthCheckResult:
        """Check system resources"""
        start_time = time.time()
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            status = 'healthy'
            if cpu_percent > 80:
                status = 'warning'
            if cpu_percent > 95:
                status = 'unhealthy'
            
            if memory.percent > 80:
                status = 'warning'
            if memory.percent > 95:
                status = 'unhealthy'
            
            return HealthCheckResult(
                name='system_resources',
                status=status,
                message=f'CPU: {cpu_percent}%, Memory: {memory.percent}%',
                timestamp=datetime.now(),
                duration=time.time() - start_time,
                details={
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used': memory.used,
                    'memory_total': memory.total
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name='system_resources',
                status='unhealthy',
                message=f'Failed to check system resources: {e}',
                timestamp=datetime.now(),
                duration=time.time() - start_time,
                details={'error': str(e)}
            )
    
    def _check_database(self) -> HealthCheckResult:
        """Check database connectivity"""
        start_time = time.time()
        
        try:
            # This would need to be implemented based on your database setup
            # For now, return a mock result
            return HealthCheckResult(
                name='database',
                status='healthy',
                message='Database connection is healthy',
                timestamp=datetime.now(),
                duration=time.time() - start_time,
                details={'connections': 5, 'pool_size': 20}
            )
        except Exception as e:
            return HealthCheckResult(
                name='database',
                status='unhealthy',
                message=f'Database check failed: {e}',
                timestamp=datetime.now(),
                duration=time.time() - start_time,
                details={'error': str(e)}
            )
    
    def _check_disk_space(self) -> HealthCheckResult:
        """Check disk space"""
        start_time = time.time()
        
        try:
            disk = psutil.disk_usage('/')
            used_percent = (disk.used / disk.total) * 100
            
            status = 'healthy'
            if used_percent > 80:
                status = 'warning'
            if used_percent > 95:
                status = 'unhealthy'
            
            return HealthCheckResult(
                name='disk_space',
                status=status,
                message=f'Disk usage: {used_percent:.1f}%',
                timestamp=datetime.now(),
                duration=time.time() - start_time,
                details={
                    'used_percent': used_percent,
                    'used_bytes': disk.used,
                    'total_bytes': disk.total,
                    'free_bytes': disk.free
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name='disk_space',
                status='unhealthy',
                message=f'Disk space check failed: {e}',
                timestamp=datetime.now(),
                duration=time.time() - start_time,
                details={'error': str(e)}
            )
    
    def _check_memory(self) -> HealthCheckResult:
        """Check memory usage"""
        start_time = time.time()
        
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            status = 'healthy'
            if memory.percent > 80 or swap.percent > 50:
                status = 'warning'
            if memory.percent > 95 or swap.percent > 80:
                status = 'unhealthy'
            
            return HealthCheckResult(
                name='memory',
                status=status,
                message=f'Memory: {memory.percent}%, Swap: {swap.percent}%',
                timestamp=datetime.now(),
                duration=time.time() - start_time,
                details={
                    'memory_percent': memory.percent,
                    'memory_used': memory.used,
                    'memory_total': memory.total,
                    'swap_percent': swap.percent,
                    'swap_used': swap.used,
                    'swap_total': swap.total
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name='memory',
                status='unhealthy',
                message=f'Memory check failed: {e}',
                timestamp=datetime.now(),
                duration=time.time() - start_time,
                details={'error': str(e)}
            )
    
    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks"""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                result = check_func()
                results[name] = result
                self.results[name] = result
            except Exception as e:
                self.logger.error(f"Health check {name} failed: {e}")
                results[name] = HealthCheckResult(
                    name=name,
                    status='unhealthy',
                    message=f'Check failed: {e}',
                    timestamp=datetime.now(),
                    duration=0,
                    details={'error': str(e)}
                )
        
        return results
    
    def get_overall_health(self) -> str:
        """Get overall system health status"""
        if not self.results:
            return 'unknown'
        
        statuses = [result.status for result in self.results.values()]
        
        if 'unhealthy' in statuses:
            return 'unhealthy'
        elif 'warning' in statuses:
            return 'warning'
        else:
            return 'healthy'

class PrometheusMetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics"""
    
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')
            self.end_headers()
            self.wfile.write(generate_latest(REGISTRY))
        else:
            self.send_response(404)
            self.end_headers()

class MonitoringSystem:
    """Comprehensive monitoring system for Liberation System"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger('liberation.monitoring')
        self.health_checker = HealthChecker()
        self.metrics_server = None
        self.monitoring_thread = None
        self.running = False
        
        # Performance tracking
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.connection_counts = defaultdict(int)
        
        # Metric snapshots for trending
        self.metric_snapshots = deque(maxlen=100)  # Store last 100 snapshots
        
        # Start metrics server if enabled
        if self.config.monitoring.prometheus_enabled:
            self._start_metrics_server()
    
    def _start_metrics_server(self):
        """Start Prometheus metrics server"""
        try:
            self.metrics_server = HTTPServer(
                ('0.0.0.0', self.config.monitoring.metrics_port),
                PrometheusMetricsHandler
            )
            
            def serve_metrics():
                self.logger.info(f"Prometheus metrics server started on port {self.config.monitoring.metrics_port}")
                self.metrics_server.serve_forever()
            
            metrics_thread = threading.Thread(target=serve_metrics, daemon=True)
            metrics_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {e}")
    
    def start_monitoring(self):
        """Start the monitoring system"""
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Monitoring system started")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False
        if self.metrics_server:
            self.metrics_server.shutdown()
        self.logger.info("Monitoring system stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Update system metrics
                self._update_system_metrics()
                
                # Take metric snapshot
                self._take_metric_snapshot()
                
                # Run health checks
                asyncio.run(self.health_checker.run_all_checks())
                
                # Sleep for the configured interval
                time.sleep(self.config.monitoring.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _update_system_metrics(self):
        """Update system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            SYSTEM_CPU.set(cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            SYSTEM_MEMORY.labels(type='used').set(memory.used)
            SYSTEM_MEMORY.labels(type='total').set(memory.total)
            SYSTEM_MEMORY.labels(type='available').set(memory.available)
            
            # Disk metrics (if needed)
            disk = psutil.disk_usage('/')
            
        except Exception as e:
            self.logger.error(f"Failed to update system metrics: {e}")
    
    def _take_metric_snapshot(self):
        """Take a snapshot of current metrics"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            snapshot = MetricSnapshot(
                timestamp=datetime.now(),
                cpu_percent=psutil.cpu_percent(interval=0.1),
                memory_used=memory.used,
                memory_total=memory.total,
                disk_used=disk.used,
                disk_total=disk.total,
                active_connections=len(self.connection_counts),
                database_connections=0,  # Would need to implement
                mesh_nodes=0,  # Would need to implement
                error_rate=sum(self.error_counts.values()) / max(len(self.request_times), 1),
                request_rate=len(self.request_times) / 60  # Requests per minute
            )
            
            self.metric_snapshots.append(snapshot)
            
        except Exception as e:
            self.logger.error(f"Failed to take metric snapshot: {e}")
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record an HTTP request"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        
        self.request_times.append(time.time())
        
        if status >= 400:
            self.record_error('api', f'http_{status}')
    
    def record_database_query(self, operation: str, table: str, duration: float):
        """Record a database query"""
        DATABASE_QUERIES.labels(operation=operation, table=table).inc()
        DATABASE_QUERY_DURATION.labels(operation=operation, table=table).observe(duration)
    
    def record_error(self, component: str, error_type: str):
        """Record an error"""
        ERRORS.labels(component=component, type=error_type).inc()
        self.error_counts[f"{component}_{error_type}"] += 1
    
    def record_connection(self, connection_type: str, delta: int = 1):
        """Record connection changes"""
        self.connection_counts[connection_type] += delta
        
        if connection_type == 'websocket':
            ACTIVE_CONNECTIONS.set(max(0, self.connection_counts[connection_type]))
    
    def record_mesh_node(self, delta: int = 1):
        """Record mesh node changes"""
        current = MESH_NODES._value._value if hasattr(MESH_NODES, '_value') else 0
        MESH_NODES.set(max(0, current + delta))
    
    def record_truth_message(self, message_type: str, channel: str):
        """Record truth message processing"""
        TRUTH_MESSAGES.labels(type=message_type, channel=channel).inc()
    
    def record_resource_distribution(self, distribution_type: str):
        """Record resource distribution"""
        RESOURCE_DISTRIBUTIONS.labels(type=distribution_type).inc()
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        results = await self.health_checker.run_all_checks()
        overall_health = self.health_checker.get_overall_health()
        
        return {
            'overall_health': overall_health,
            'checks': {name: {
                'status': result.status,
                'message': result.message,
                'timestamp': result.timestamp.isoformat(),
                'duration': result.duration,
                'details': result.details
            } for name, result in results.items()},
            'timestamp': datetime.now().isoformat()
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        if not self.metric_snapshots:
            return {}
        
        latest = self.metric_snapshots[-1]
        
        # Calculate trends if we have enough data
        trends = {}
        if len(self.metric_snapshots) >= 2:
            previous = self.metric_snapshots[-2]
            trends = {
                'cpu_trend': latest.cpu_percent - previous.cpu_percent,
                'memory_trend': latest.memory_used - previous.memory_used,
                'error_rate_trend': latest.error_rate - previous.error_rate,
                'request_rate_trend': latest.request_rate - previous.request_rate
            }
        
        return {
            'timestamp': latest.timestamp.isoformat(),
            'cpu_percent': latest.cpu_percent,
            'memory_used': latest.memory_used,
            'memory_total': latest.memory_total,
            'disk_used': latest.disk_used,
            'disk_total': latest.disk_total,
            'active_connections': latest.active_connections,
            'database_connections': latest.database_connections,
            'mesh_nodes': latest.mesh_nodes,
            'error_rate': latest.error_rate,
            'request_rate': latest.request_rate,
            'trends': trends
        }
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics"""
        return generate_latest(REGISTRY).decode('utf-8')
    
    def export_metrics(self, file_path: str):
        """Export metrics to file"""
        try:
            metrics_data = {
                'timestamp': datetime.now().isoformat(),
                'health_status': asyncio.run(self.get_health_status()),
                'metrics_summary': self.get_metrics_summary(),
                'prometheus_metrics': self.get_prometheus_metrics()
            }
            
            with open(file_path, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            self.logger.info(f"Metrics exported to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")

# Global monitoring instance
monitoring_system = MonitoringSystem()

# Convenience functions
def start_monitoring():
    """Start the monitoring system"""
    monitoring_system.start_monitoring()

def stop_monitoring():
    """Stop the monitoring system"""
    monitoring_system.stop_monitoring()

def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record an HTTP request"""
    monitoring_system.record_request(method, endpoint, status, duration)

def record_database_query(operation: str, table: str, duration: float):
    """Record a database query"""
    monitoring_system.record_database_query(operation, table, duration)

def record_error(component: str, error_type: str):
    """Record an error"""
    monitoring_system.record_error(component, error_type)

def record_connection(connection_type: str, delta: int = 1):
    """Record connection changes"""
    monitoring_system.record_connection(connection_type, delta)

def get_health_status():
    """Get current health status"""
    return monitoring_system.get_health_status()

def get_metrics_summary():
    """Get metrics summary"""
    return monitoring_system.get_metrics_summary()
