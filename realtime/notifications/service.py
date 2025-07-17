import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid

from ..websocket.manager import websocket_manager
from ..events.system import event_system, EventType

class NotificationType(Enum):
    """Types of notifications"""
    RESOURCE_DISTRIBUTION = "resource_distribution"
    TRUTH_UPDATE = "truth_update"
    MESH_NETWORK_CHANGE = "mesh_network_change"
    SYSTEM_ALERT = "system_alert"
    USER_ACTION = "user_action"
    WELCOME = "welcome"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    INFO = "info"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class Notification:
    """Real-time notification data structure"""
    id: str
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority
    user_id: Optional[str] = None
    channel: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    expires_at: Optional[datetime] = None
    actions: Optional[List[Dict[str, str]]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.notification_type.value,
            "priority": self.priority.value,
            "user_id": self.user_id,
            "channel": self.channel,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "actions": self.actions
        }

class NotificationService:
    """Enhanced real-time notification service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_notifications: Dict[str, Notification] = {}
        self.user_notifications: Dict[str, List[str]] = {}  # user_id -> notification_ids
        self.notification_history: List[Notification] = []
        self.max_history_size = 1000
        
        # Notification templates
        self.templates = {
            NotificationType.RESOURCE_DISTRIBUTION: {
                "title": "💰 Resource Distribution",
                "message": "You received ${amount:.2f} from the Liberation System",
                "priority": NotificationPriority.MEDIUM,
                "actions": [
                    {"label": "View Details", "action": "view_transaction"},
                    {"label": "Thank You", "action": "acknowledge"}
                ]
            },
            NotificationType.TRUTH_UPDATE: {
                "title": "🌐 Truth Network Update",
                "message": "New truth message spreading: {message}",
                "priority": NotificationPriority.MEDIUM,
                "actions": [
                    {"label": "Spread Truth", "action": "spread_truth"},
                    {"label": "View Details", "action": "view_truth"}
                ]
            },
            NotificationType.MESH_NETWORK_CHANGE: {
                "title": "🔗 Mesh Network Status",
                "message": "Network topology changed: {change_type}",
                "priority": NotificationPriority.LOW,
                "actions": [
                    {"label": "View Network", "action": "view_mesh"}
                ]
            },
            NotificationType.SYSTEM_ALERT: {
                "title": "⚠️ System Alert",
                "message": "System status: {status}",
                "priority": NotificationPriority.HIGH,
                "actions": [
                    {"label": "Check Status", "action": "check_system"}
                ]
            },
            NotificationType.WELCOME: {
                "title": "🎉 Welcome to Liberation System",
                "message": "Your registration is complete. You're now part of the $19T transformation.",
                "priority": NotificationPriority.MEDIUM,
                "actions": [
                    {"label": "Get Started", "action": "onboarding"},
                    {"label": "Learn More", "action": "learn_more"}
                ]
            }
        }
    
    async def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        data: Optional[Dict[str, Any]] = None,
        custom_message: Optional[str] = None,
        custom_title: Optional[str] = None,
        priority: Optional[NotificationPriority] = None,
        channel: Optional[str] = None,
        actions: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Send a real-time notification to a user"""
        
        # Get template
        template = self.templates.get(notification_type, {})
        
        # Format message with data
        message = custom_message or template.get("message", "")
        if data and "{" in message:
            try:
                message = message.format(**data)
            except (KeyError, ValueError):
                pass
        
        # Create notification
        notification = Notification(
            id=str(uuid.uuid4()),
            title=custom_title or template.get("title", "Notification"),
            message=message,
            notification_type=notification_type,
            priority=priority or template.get("priority", NotificationPriority.MEDIUM),
            user_id=user_id,
            channel=channel,
            data=data,
            actions=actions or template.get("actions", [])
        )
        
        # Store notification
        self.active_notifications[notification.id] = notification
        
        # Track user notifications
        if user_id not in self.user_notifications:
            self.user_notifications[user_id] = []
        self.user_notifications[user_id].append(notification.id)
        
        # Add to history
        self.notification_history.append(notification)
        if len(self.notification_history) > self.max_history_size:
            self.notification_history.pop(0)
        
        # Send via WebSocket
        await self._send_websocket_notification(notification)
        
        # Send via channel if specified
        if channel:
            await self._send_channel_notification(notification, channel)
        
        self.logger.info(f"Sent notification {notification.id} to user {user_id}")
        return notification.id
    
    async def send_system_alert(
        self,
        title: str,
        message: str,
        alert_level: str = "info",
        data: Optional[Dict[str, Any]] = None,
        target_channel: str = "system"
    ) -> str:
        """Send system-wide alert"""
        
        priority_map = {
            "info": NotificationPriority.LOW,
            "warning": NotificationPriority.MEDIUM,
            "error": NotificationPriority.HIGH,
            "critical": NotificationPriority.CRITICAL,
            "emergency": NotificationPriority.EMERGENCY
        }
        
        notification = Notification(
            id=str(uuid.uuid4()),
            title=title,
            message=message,
            notification_type=NotificationType.SYSTEM_ALERT,
            priority=priority_map.get(alert_level, NotificationPriority.MEDIUM),
            channel=target_channel,
            data=data
        )
        
        # Store notification
        self.active_notifications[notification.id] = notification
        
        # Add to history
        self.notification_history.append(notification)
        if len(self.notification_history) > self.max_history_size:
            self.notification_history.pop(0)
        
        # Broadcast to all connections on channel
        await websocket_manager.broadcast_to_channel(
            channel=target_channel,
            message_type="system_alert",
            data=notification.to_dict()
        )
        
        # Also broadcast to admin connections
        await websocket_manager.broadcast_to_channel(
            channel="admin",
            message_type="system_alert",
            data=notification.to_dict()
        )
        
        self.logger.info(f"Sent system alert {notification.id} to channel {target_channel}")
        return notification.id
    
    async def _send_websocket_notification(self, notification: Notification):
        """Send notification via WebSocket"""
        try:
            # Send to specific user
            if notification.user_id:
                await websocket_manager.send_to_user(
                    user_id=notification.user_id,
                    message_type="notification",
                    data=notification.to_dict()
                )
            
            # Send to channel if specified
            if notification.channel:
                await websocket_manager.broadcast_to_channel(
                    channel=notification.channel,
                    message_type="notification",
                    data=notification.to_dict()
                )
            
        except Exception as e:
            self.logger.error(f"Failed to send WebSocket notification: {e}")
    
    async def _send_channel_notification(self, notification: Notification, channel: str):
        """Send notification to a specific channel"""
        try:
            await websocket_manager.broadcast_to_channel(
                channel=channel,
                message_type="channel_notification",
                data=notification.to_dict()
            )
        except Exception as e:
            self.logger.error(f"Failed to send channel notification: {e}")
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        try:
            if notification_id in self.active_notifications:
                notification = self.active_notifications[notification_id]
                
                # Verify user ownership
                if notification.user_id != user_id:
                    return False
                
                # Update notification data
                if notification.data is None:
                    notification.data = {}
                notification.data["read_at"] = datetime.now().isoformat()
                notification.data["read_by"] = user_id
                
                # Send update via WebSocket
                await websocket_manager.send_to_user(
                    user_id=user_id,
                    message_type="notification_read",
                    data={"notification_id": notification_id}
                )
                
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to mark notification as read: {e}")
            return False
    
    async def dismiss_notification(self, notification_id: str, user_id: str) -> bool:
        """Dismiss a notification"""
        try:
            if notification_id in self.active_notifications:
                notification = self.active_notifications[notification_id]
                
                # Verify user ownership
                if notification.user_id != user_id:
                    return False
                
                # Remove from active notifications
                del self.active_notifications[notification_id]
                
                # Remove from user's notification list
                if user_id in self.user_notifications:
                    self.user_notifications[user_id] = [
                        nid for nid in self.user_notifications[user_id] 
                        if nid != notification_id
                    ]
                
                # Send dismissal via WebSocket
                await websocket_manager.send_to_user(
                    user_id=user_id,
                    message_type="notification_dismissed",
                    data={"notification_id": notification_id}
                )
                
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to dismiss notification: {e}")
            return False
    
    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        try:
            user_notification_ids = self.user_notifications.get(user_id, [])
            notifications = []
            
            for notification_id in user_notification_ids[-limit:]:
                if notification_id in self.active_notifications:
                    notification = self.active_notifications[notification_id]
                    
                    # Filter unread if requested
                    if unread_only:
                        if notification.data and notification.data.get("read_at"):
                            continue
                    
                    notifications.append(notification.to_dict())
            
            return notifications
        except Exception as e:
            self.logger.error(f"Failed to get user notifications: {e}")
            return []
    
    async def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification system statistics"""
        try:
            stats = {
                "total_notifications": len(self.active_notifications),
                "total_users": len(self.user_notifications),
                "notifications_by_type": {},
                "notifications_by_priority": {},
                "recent_notifications": len([
                    n for n in self.notification_history 
                    if (datetime.now() - n.timestamp).seconds < 3600  # Last hour
                ])
            }
            
            # Count by type and priority
            for notification in self.active_notifications.values():
                # By type
                type_key = notification.notification_type.value
                stats["notifications_by_type"][type_key] = stats["notifications_by_type"].get(type_key, 0) + 1
                
                # By priority
                priority_key = notification.priority.value
                stats["notifications_by_priority"][priority_key] = stats["notifications_by_priority"].get(priority_key, 0) + 1
            
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get notification stats: {e}")
            return {}
    
    async def cleanup_expired_notifications(self):
        """Remove expired notifications"""
        try:
            now = datetime.now()
            expired_ids = []
            
            for notification_id, notification in self.active_notifications.items():
                if notification.expires_at and notification.expires_at < now:
                    expired_ids.append(notification_id)
            
            # Remove expired notifications
            for notification_id in expired_ids:
                notification = self.active_notifications[notification_id]
                
                # Remove from active notifications
                del self.active_notifications[notification_id]
                
                # Remove from user's notification list
                if notification.user_id in self.user_notifications:
                    self.user_notifications[notification.user_id] = [
                        nid for nid in self.user_notifications[notification.user_id] 
                        if nid != notification_id
                    ]
                
                self.logger.info(f"Removed expired notification {notification_id}")
            
            return len(expired_ids)
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired notifications: {e}")
            return 0

# Global notification service instance
notification_service = NotificationService()

# Register event handlers for automatic notifications
async def handle_resource_distribution_event(event):
    """Handle resource distribution events"""
    data = event.data
    human_id = data.get("human_id")
    amount = data.get("amount")
    
    if human_id and amount:
        await notification_service.send_notification(
            user_id=human_id,
            notification_type=NotificationType.RESOURCE_DISTRIBUTION,
            data={"amount": amount}
        )

async def handle_truth_spreading_event(event):
    """Handle truth spreading events"""
    data = event.data
    message = data.get("message")
    
    if message:
        await notification_service.send_system_alert(
            title="🌐 Truth Network Update",
            message=f"New truth spreading: {message[:100]}...",
            alert_level="info",
            target_channel="truth"
        )

async def handle_mesh_network_event(event):
    """Handle mesh network events"""
    data = event.data
    change_type = data.get("change_type", "unknown")
    
    await notification_service.send_system_alert(
        title="🔗 Mesh Network Update",
        message=f"Network change: {change_type}",
        alert_level="info",
        target_channel="mesh"
    )

async def handle_system_health_event(event):
    """Handle system health events"""
    data = event.data
    health_status = data.get("health_status")
    
    if health_status in ["unhealthy", "critical"]:
        await notification_service.send_system_alert(
            title="⚠️ System Health Alert",
            message=f"System health: {health_status}",
            alert_level="warning" if health_status == "unhealthy" else "critical",
            target_channel="system"
        )

# Register event handlers
event_system.register_handler(EventType.RESOURCE_DISTRIBUTED, handle_resource_distribution_event)
event_system.register_handler(EventType.TRUTH_MESSAGE_SENT, handle_truth_spreading_event)
event_system.register_handler(EventType.MESH_NETWORK_UPDATED, handle_mesh_network_event)
event_system.register_handler(EventType.SYSTEM_HEALTH_CHANGED, handle_system_health_event)
