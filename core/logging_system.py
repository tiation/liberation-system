# core/logging_system.py

import logging
import logging.handlers
import json
import uuid
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import sys
import traceback
from functools import wraps

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress
from rich.table import Table
from rich.panel import Panel

from .config import get_config

@dataclass
class LogRecord:
    """Structured log record for Liberation System"""
    timestamp: str
    level: str
    message: str
    logger_name: str
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    extra_fields: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_fields is None:
            self.extra_fields = {}

class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records"""
    
    def __init__(self):
        super().__init__()
        self.correlation_id = None
    
    def filter(self, record):
        if hasattr(record, 'correlation_id'):
            record.correlation_id = getattr(record, 'correlation_id', self.correlation_id)
        else:
            record.correlation_id = self.correlation_id
        return True
    
    def set_correlation_id(self, correlation_id: str):
        self.correlation_id = correlation_id

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger_name': record.name,
            'module': record.module,
            'function': record.funcName,
            'line_number': record.lineno,
            'correlation_id': getattr(record, 'correlation_id', None),
            'request_id': getattr(record, 'request_id', None),
            'user_id': getattr(record, 'user_id', None),
        }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'stack_info', 
                          'exc_info', 'exc_text', 'correlation_id', 'request_id', 'user_id']:
                log_entry[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_entry)

class LiberationSystemLogger:
    """Enhanced logging system for Liberation System"""
    
    def __init__(self):
        self.config = get_config()
        self.console = Console()
        self.correlation_filter = CorrelationIdFilter()
        self.loggers = {}
        self.performance_metrics = {}
        
        # Set up root logger
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Set up the root logger with proper configuration"""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.logging.level))
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler with rich formatting
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_level=True,
            show_path=True,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True
        )
        console_handler.setLevel(getattr(logging, self.config.logging.level))
        
        # File handler with JSON formatting
        if self.config.logging.file_path:
            log_file = Path(self.config.logging.file_path)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.config.logging.max_file_size,
                backupCount=self.config.logging.backup_count
            )
            
            if self.config.logging.json_format:
                file_handler.setFormatter(JSONFormatter())
            else:
                file_handler.setFormatter(logging.Formatter(self.config.logging.format))
            
            file_handler.addFilter(self.correlation_filter)
            root_logger.addHandler(file_handler)
        
        # Add filters
        console_handler.addFilter(self.correlation_filter)
        root_logger.addHandler(console_handler)
        
        # Set up system-specific loggers
        self._setup_system_loggers()
    
    def _setup_system_loggers(self):
        """Set up specific loggers for different system components"""
        components = [
            'liberation.core',
            'liberation.database',
            'liberation.mesh',
            'liberation.truth',
            'liberation.api',
            'liberation.security',
            'liberation.monitoring'
        ]
        
        for component in components:
            logger = logging.getLogger(component)
            logger.setLevel(getattr(logging, self.config.logging.level))
            self.loggers[component] = logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            logger.setLevel(getattr(logging, self.config.logging.level))
            self.loggers[name] = logger
        return self.loggers[name]
    
    @contextmanager
    def correlation_context(self, correlation_id: Optional[str] = None):
        """Context manager for correlation ID"""
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        old_correlation_id = self.correlation_filter.correlation_id
        self.correlation_filter.set_correlation_id(correlation_id)
        
        try:
            yield correlation_id
        finally:
            self.correlation_filter.set_correlation_id(old_correlation_id)
    
    def log_performance(self, operation: str, duration: float, extra_data: Dict[str, Any] = None):
        """Log performance metrics"""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = []
        
        self.performance_metrics[operation].append({
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'extra_data': extra_data or {}
        })
        
        # Log slow operations
        if duration > self.config.monitoring.slow_query_threshold:
            logger = self.get_logger('liberation.performance')
            logger.warning(
                f"Slow operation detected: {operation}",
                extra={
                    'operation': operation,
                    'duration': duration,
                    'threshold': self.config.monitoring.slow_query_threshold,
                    **extra_data or {}
                }
            )
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events"""
        logger = self.get_logger('liberation.security')
        logger.info(
            f"Security event: {event_type}",
            extra={
                'event_type': event_type,
                'security_event': True,
                **details
            }
        )
    
    def log_system_event(self, event_type: str, details: Dict[str, Any]):
        """Log system events"""
        logger = self.get_logger('liberation.system')
        logger.info(
            f"System event: {event_type}",
            extra={
                'event_type': event_type,
                'system_event': True,
                **details
            }
        )
    
    def log_error_with_context(self, message: str, error: Exception, context: Dict[str, Any] = None):
        """Log error with full context"""
        logger = self.get_logger('liberation.errors')
        logger.error(
            message,
            exc_info=True,
            extra={
                'error_type': error.__class__.__name__,
                'error_message': str(error),
                'context': context or {},
                'stack_trace': traceback.format_exc()
            }
        )
    
    def display_performance_report(self):
        """Display performance report in rich format"""
        table = Table(title="Liberation System Performance Report")
        table.add_column("Operation", style="cyan")
        table.add_column("Count", style="magenta")
        table.add_column("Avg Duration", style="green")
        table.add_column("Max Duration", style="red")
        table.add_column("Min Duration", style="yellow")
        
        for operation, metrics in self.performance_metrics.items():
            durations = [m['duration'] for m in metrics]
            if durations:
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)
                min_duration = min(durations)
                
                table.add_row(
                    operation,
                    str(len(metrics)),
                    f"{avg_duration:.3f}s",
                    f"{max_duration:.3f}s",
                    f"{min_duration:.3f}s"
                )
        
        self.console.print(table)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status for monitoring"""
        return {
            'logging_level': self.config.logging.level,
            'active_loggers': len(self.loggers),
            'performance_metrics': len(self.performance_metrics),
            'correlation_id': self.correlation_filter.correlation_id,
            'log_file_path': self.config.logging.file_path,
            'json_format': self.config.logging.json_format
        }

def performance_monitor(operation_name: str = None):
    """Decorator for monitoring function performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger_system.log_performance(operation, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger_system.log_performance(operation, duration, {'error': str(e)})
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger_system.log_performance(operation, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger_system.log_performance(operation, duration, {'error': str(e)})
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Global logger instance
logger_system = LiberationSystemLogger()

# Convenience functions
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logger_system.get_logger(name)

def log_performance(operation: str, duration: float, extra_data: Dict[str, Any] = None):
    """Log performance metrics"""
    logger_system.log_performance(operation, duration, extra_data)

def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security events"""
    logger_system.log_security_event(event_type, details)

def log_system_event(event_type: str, details: Dict[str, Any]):
    """Log system events"""
    logger_system.log_system_event(event_type, details)

def correlation_context(correlation_id: Optional[str] = None):
    """Context manager for correlation ID"""
    return logger_system.correlation_context(correlation_id)

def display_performance_report():
    """Display performance report"""
    logger_system.display_performance_report()

def get_system_status() -> Dict[str, Any]:
    """Get current system status"""
    return logger_system.get_system_status()
