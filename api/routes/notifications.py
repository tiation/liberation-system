from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging
from datetime import datetime

from ..dependencies import get_current_user
from ...realtime.notifications.service import (
    notification_service, 
    NotificationType, 
    NotificationPriority
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/notifications")
async def get_user_notifications(
    limit: int = Query(default=50, ge=1, le=200),
    unread_only: bool = Query(default=False),
    current_user: dict = Depends(get_current_user)
):
    """Get notifications for the current user"""
    try:
        user_id = current_user.get("user_id", "anonymous")
        
        notifications = await notification_service.get_user_notifications(
            user_id=user_id,
            limit=limit,
            unread_only=unread_only
        )
        
        return {
            "success": True,
            "notifications": notifications,
            "total_count": len(notifications),
            "unread_only": unread_only,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get user notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        user_id = current_user.get("user_id", "anonymous")
        
        success = await notification_service.mark_notification_read(
            notification_id=notification_id,
            user_id=user_id
        )
        
        if success:
            return {
                "success": True,
                "message": "Notification marked as read",
                "notification_id": notification_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Notification not found or access denied")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark notification as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/notifications/{notification_id}")
async def dismiss_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Dismiss a notification"""
    try:
        user_id = current_user.get("user_id", "anonymous")
        
        success = await notification_service.dismiss_notification(
            notification_id=notification_id,
            user_id=user_id
        )
        
        if success:
            return {
                "success": True,
                "message": "Notification dismissed",
                "notification_id": notification_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Notification not found or access denied")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to dismiss notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/send")
async def send_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "info",
    priority: int = 2,
    current_user: dict = Depends(get_current_user)
):
    """Send a notification to a user (admin only)"""
    try:
        # Check if user has admin privileges
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        # Convert string to enum
        try:
            notification_type_enum = NotificationType(notification_type)
        except ValueError:
            notification_type_enum = NotificationType.INFO
        
        priority_enum = NotificationPriority(priority)
        
        notification_id = await notification_service.send_notification(
            user_id=user_id,
            notification_type=notification_type_enum,
            custom_title=title,
            custom_message=message,
            priority=priority_enum
        )
        
        return {
            "success": True,
            "message": "Notification sent successfully",
            "notification_id": notification_id,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/system-alert")
async def send_system_alert(
    title: str,
    message: str,
    alert_level: str = "info",
    target_channel: str = "system",
    current_user: dict = Depends(get_current_user)
):
    """Send a system-wide alert (admin only)"""
    try:
        # Check if user has admin privileges
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        notification_id = await notification_service.send_system_alert(
            title=title,
            message=message,
            alert_level=alert_level,
            target_channel=target_channel
        )
        
        return {
            "success": True,
            "message": "System alert sent successfully",
            "notification_id": notification_id,
            "alert_level": alert_level,
            "target_channel": target_channel,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send system alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications/stats")
async def get_notification_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get notification system statistics (admin only)"""
    try:
        # Check if user has admin privileges
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        stats = await notification_service.get_notification_stats()
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get notification stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/cleanup")
async def cleanup_expired_notifications(
    current_user: dict = Depends(get_current_user)
):
    """Clean up expired notifications (admin only)"""
    try:
        # Check if user has admin privileges
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        cleaned_count = await notification_service.cleanup_expired_notifications()
        
        return {
            "success": True,
            "message": f"Cleaned up {cleaned_count} expired notifications",
            "cleaned_count": cleaned_count,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cleanup notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))
