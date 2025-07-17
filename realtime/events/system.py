import asyncio
import json
import logging
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class EventType(Enum):
    """Enum for different event types"""
    RESOURCE_DISTRIBUTED = "resource.distributed"
    RESOURCE_POOL_UPDATED = "resource.pool.updated"
    HUMAN_REGISTERED = "human.registered"
    HUMAN_STATUS_CHANGED = "human.status.changed"
    TRUTH_MESSAGE_SENT = "truth.message.sent"
    TRUTH_CHANNEL_CONVERTED = "truth.channel.converted"
    MESH_NODE_CONNECTED = "mesh.node.connected"
    MESH_NODE_DISCONNECTED = "mesh.node.disconnected"
    MESH_NETWORK_UPDATED = "mesh.network.updated"
    COMMUNITY_CREATED = "community.created"
    HOUSING_ALLOCATED = "housing.allocated"
    SYSTEM_HEALTH_CHANGED = "system.health.changed"
    SYSTEM_METRICS_UPDATED = "system.metrics.updated"
    USER_CONNECTED = "user.connected"
    USER_DISCONNECTED = "user.disconnected"

@dataclass
class Event:
    """Represents a system event"""
    id: str
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "correlation_id": self.correlation_id
        }

class EventHandler:
    """Base class for event handlers"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"EventHandler.{name}")
    
    async def handle(self, event: Event) -> bool:
        """Handle an event. Return True if handled successfully."""
        raise NotImplementedError

class EventSystem:
    """Manages event publishing and subscription"""
    
    def __init__(self):
        self.handlers: Dict[EventType, List[EventHandler]] = {}
        self.middleware: List[Callable] = []
        self.event_history: List[Event] = []
        self.max_history_size = 1000
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "events_published": 0,
            "events_handled": 0,
            "events_failed": 0,
            "handlers_registered": 0
        }
    
    def register_handler(self, event_type: EventType, handler: EventHandler):
        """Register an event handler for a specific event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
        self.metrics["handlers_registered"] += 1
        self.logger.info(f"Registered handler '{handler.name}' for event type '{event_type.value}'")
    
    def register_middleware(self, middleware: Callable):
        """Register middleware function that runs before event handling"""
        self.middleware.append(middleware)
        self.logger.info(f"Registered middleware: {middleware.__name__}")
    
    async def publish(self, event_type: EventType, data: Dict[str, Any], source: str, correlation_id: Optional[str] = None):
        """Publish an event to all registered handlers"""
        event = Event(
            id=str(uuid.uuid4()),
            type=event_type,
            data=data,
            timestamp=datetime.now(),
            source=source,
            correlation_id=correlation_id
        )
        
        # Add to event history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        self.metrics["events_published"] += 1
        self.logger.info(f"Publishing event: {event_type.value} from {source}")
        
        # Run middleware
        for middleware in self.middleware:
            try:
                await middleware(event)
            except Exception as e:
                self.logger.error(f"Middleware error: {e}")
        
        # Handle event
        if event_type in self.handlers:
            tasks = []
            for handler in self.handlers[event_type]:
                tasks.append(self._handle_event_safely(handler, event))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _handle_event_safely(self, handler: EventHandler, event: Event):
        """Handle an event with error handling"""
        try:
            success = await handler.handle(event)
            if success:
                self.metrics["events_handled"] += 1
            else:
                self.metrics["events_failed"] += 1
                self.logger.warning(f"Handler '{handler.name}' failed to handle event {event.id}")
        except Exception as e:
            self.metrics["events_failed"] += 1
            self.logger.error(f"Handler '{handler.name}' raised exception: {e}")
    
    def get_event_history(self, limit: int = 100, event_type: Optional[EventType] = None) -> List[Dict[str, Any]]:
        """Get recent event history"""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        return [event.to_dict() for event in events[-limit:]]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get event system metrics"""
        return {
            **self.metrics,
            "active_handlers": {
                event_type.value: len(handlers) 
                for event_type, handlers in self.handlers.items()
            },
            "middleware_count": len(self.middleware),
            "history_size": len(self.event_history)
        }

# WebSocket event handler
class WebSocketEventHandler(EventHandler):
    """Handler that broadcasts events to WebSocket connections"""
    
    def __init__(self, websocket_manager):
        super().__init__("WebSocketBroadcaster")
        self.websocket_manager = websocket_manager
        self.channel_mapping = {
            EventType.RESOURCE_DISTRIBUTED: "resources",
            EventType.RESOURCE_POOL_UPDATED: "resources",
            EventType.HUMAN_REGISTERED: "humans",
            EventType.HUMAN_STATUS_CHANGED: "humans",
            EventType.TRUTH_MESSAGE_SENT: "truth",
            EventType.TRUTH_CHANNEL_CONVERTED: "truth",
            EventType.MESH_NODE_CONNECTED: "mesh",
            EventType.MESH_NODE_DISCONNECTED: "mesh",
            EventType.MESH_NETWORK_UPDATED: "mesh",
            EventType.COMMUNITY_CREATED: "communities",
            EventType.HOUSING_ALLOCATED: "communities",
            EventType.SYSTEM_HEALTH_CHANGED: "system",
            EventType.SYSTEM_METRICS_UPDATED: "system",
            EventType.USER_CONNECTED: "users",
            EventType.USER_DISCONNECTED: "users"
        }
    
    async def handle(self, event: Event) -> bool:
        """Broadcast event to appropriate WebSocket channel"""
        try:
            channel = self.channel_mapping.get(event.type, "general")
            
            # Broadcast to channel subscribers
            await self.websocket_manager.broadcast_to_channel(
                channel=channel,
                message_type="event",
                data=event.to_dict()
            )
            
            # Also broadcast to dashboard connections
            await self.websocket_manager.broadcast_to_channel(
                channel="dashboard",
                message_type="event",
                data=event.to_dict()
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to broadcast event {event.id}: {e}")
            return False

# Database event handler
class DatabaseEventHandler(EventHandler):
    """Handler that logs events to database"""
    
    def __init__(self, db_connection):
        super().__init__("DatabaseLogger")
        self.db = db_connection
    
    async def handle(self, event: Event) -> bool:
        """Log event to database"""
        try:
            await self.db.execute(
                """INSERT INTO system_events (id, type, data, timestamp, source, correlation_id) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    event.id,
                    event.type.value,
                    json.dumps(event.data),
                    event.timestamp.isoformat(),
                    event.source,
                    event.correlation_id
                )
            )
            await self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to log event {event.id} to database: {e}")
            return False

# Notification handler
class NotificationHandler(EventHandler):
    """Handler that sends notifications based on events"""
    
    def __init__(self, notification_service):
        super().__init__("NotificationService")
        self.notification_service = notification_service
        self.notification_rules = {
            EventType.RESOURCE_DISTRIBUTED: self._handle_resource_distributed,
            EventType.HUMAN_REGISTERED: self._handle_human_registered,
            EventType.SYSTEM_HEALTH_CHANGED: self._handle_system_health_changed,
            EventType.HOUSING_ALLOCATED: self._handle_housing_allocated
        }
    
    async def handle(self, event: Event) -> bool:
        """Send notifications based on event type"""
        try:
            if event.type in self.notification_rules:
                await self.notification_rules[event.type](event)
            return True
        except Exception as e:
            self.logger.error(f"Failed to send notification for event {event.id}: {e}")
            return False
    
    async def _handle_resource_distributed(self, event: Event):
        """Handle resource distribution notification"""
        data = event.data
        human_id = data.get("human_id")
        amount = data.get("amount")
        
        if human_id:
            await self.notification_service.send_notification(
                user_id=human_id,
                title="Resource Distribution",
                message=f"You received ${amount:.2f} from the Liberation System",
                notification_type="resource_distribution"
            )
    
    async def _handle_human_registered(self, event: Event):
        """Handle human registration notification"""
        data = event.data
        human_id = data.get("human_id")
        
        if human_id:
            await self.notification_service.send_notification(
                user_id=human_id,
                title="Welcome to Liberation System",
                message="Your registration is complete. You're now part of the $19T transformation.",
                notification_type="welcome"
            )
    
    async def _handle_system_health_changed(self, event: Event):
        """Handle system health change notification"""
        data = event.data
        health_status = data.get("health_status")
        
        if health_status == "unhealthy":
            await self.notification_service.send_system_alert(
                title="System Health Alert",
                message="System health has degraded. Monitoring team has been notified.",
                alert_level="warning"
            )
    
    async def _handle_housing_allocated(self, event: Event):
        """Handle housing allocation notification"""
        data = event.data
        human_id = data.get("human_id")
        amount = data.get("amount")
        
        if human_id:
            await self.notification_service.send_notification(
                user_id=human_id,
                title="Housing Credit Approved",
                message=f"Your housing credit of ${amount:,.2f} has been approved and allocated.",
                notification_type="housing_allocation"
            )

# Analytics handler
class AnalyticsHandler(EventHandler):
    """Handler that processes events for analytics"""
    
    def __init__(self, analytics_service):
        super().__init__("AnalyticsProcessor")
        self.analytics_service = analytics_service
    
    async def handle(self, event: Event) -> bool:
        """Process event for analytics"""
        try:
            # Extract analytics data based on event type
            analytics_data = self._extract_analytics_data(event)
            
            if analytics_data:
                await self.analytics_service.track_event(
                    event_type=event.type.value,
                    data=analytics_data,
                    timestamp=event.timestamp
                )
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to process analytics for event {event.id}: {e}")
            return False
    
    def _extract_analytics_data(self, event: Event) -> Optional[Dict[str, Any]]:
        """Extract relevant analytics data from event"""
        if event.type == EventType.RESOURCE_DISTRIBUTED:
            return {
                "amount": event.data.get("amount"),
                "human_id": event.data.get("human_id"),
                "distribution_type": event.data.get("distribution_type")
            }
        elif event.type == EventType.HUMAN_REGISTERED:
            return {
                "human_id": event.data.get("human_id"),
                "registration_method": event.data.get("method")
            }
        elif event.type == EventType.TRUTH_MESSAGE_SENT:
            return {
                "message_id": event.data.get("message_id"),
                "channels_reached": event.data.get("channels_reached"),
                "reach_count": event.data.get("reach_count")
            }
        
        return None

# Global event system instance
event_system = EventSystem()
