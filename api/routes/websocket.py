from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional
import json
import logging
from datetime import datetime

from ..dependencies import get_current_user
from ...realtime.websocket.manager import websocket_manager, ConnectionType
from ...realtime.events.system import event_system, EventType

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    connection_type: str = Query(default="dashboard"),
    user_id: Optional[str] = Query(default=None)
):
    """Main WebSocket endpoint for real-time communication"""
    
    # Validate connection type
    try:
        conn_type = ConnectionType(connection_type)
    except ValueError:
        await websocket.close(code=1008, reason="Invalid connection type")
        return
    
    connection_id = None
    
    try:
        # Connect to WebSocket manager
        connection_id = await websocket_manager.connect(
            websocket=websocket,
            connection_type=conn_type,
            user_id=user_id
        )
        
        # Auto-subscribe to default channels based on connection type
        if conn_type == ConnectionType.DASHBOARD:
            await websocket_manager.subscribe(connection_id, "dashboard")
            await websocket_manager.subscribe(connection_id, "resources")
            await websocket_manager.subscribe(connection_id, "system")
        elif conn_type == ConnectionType.MOBILE:
            await websocket_manager.subscribe(connection_id, "mobile")
            await websocket_manager.subscribe(connection_id, "resources")
        elif conn_type == ConnectionType.ADMIN:
            await websocket_manager.subscribe(connection_id, "admin")
            await websocket_manager.subscribe(connection_id, "system")
            await websocket_manager.subscribe(connection_id, "resources")
            await websocket_manager.subscribe(connection_id, "truth")
            await websocket_manager.subscribe(connection_id, "mesh")
        
        # Publish user connection event
        if user_id:
            await event_system.publish(
                event_type=EventType.USER_CONNECTED,
                data={
                    "user_id": user_id,
                    "connection_id": connection_id,
                    "connection_type": conn_type.value
                },
                source="websocket_endpoint"
            )
        
        # Handle incoming messages
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle message
                await websocket_manager.handle_message(connection_id, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket_manager.send_to_connection(
                    connection_id,
                    "error",
                    {"message": "Invalid JSON format"}
                )
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket_manager.send_to_connection(
                    connection_id,
                    "error",
                    {"message": "Internal server error"}
                )
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    
    finally:
        # Cleanup connection
        if connection_id:
            # Publish user disconnection event
            if user_id:
                await event_system.publish(
                    event_type=EventType.USER_DISCONNECTED,
                    data={
                        "user_id": user_id,
                        "connection_id": connection_id,
                        "connection_type": conn_type.value
                    },
                    source="websocket_endpoint"
                )
            
            await websocket_manager.disconnect(connection_id)

@router.get("/ws/stats")
async def get_websocket_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get WebSocket connection statistics"""
    return {
        "websocket_stats": websocket_manager.get_stats(),
        "event_stats": event_system.get_metrics(),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/ws/connections")
async def get_active_connections(
    current_user: dict = Depends(get_current_user)
):
    """Get information about active WebSocket connections"""
    connections = []
    
    for connection_id in websocket_manager.connections:
        connection_info = websocket_manager.get_connection_info(connection_id)
        if connection_info:
            connections.append(connection_info)
    
    return {
        "active_connections": connections,
        "total_connections": len(connections),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/ws/broadcast")
async def broadcast_message(
    channel: str,
    message_type: str,
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Broadcast a message to all connections on a channel"""
    try:
        sent_count = await websocket_manager.broadcast_to_channel(
            channel=channel,
            message_type=message_type,
            data=data
        )
        
        return {
            "success": True,
            "channel": channel,
            "message_type": message_type,
            "sent_count": sent_count,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to broadcast message: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/ws/notify/{user_id}")
async def send_user_notification(
    user_id: str,
    message_type: str,
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send a notification to a specific user"""
    try:
        sent_count = await websocket_manager.send_to_user(
            user_id=user_id,
            message_type=message_type,
            data=data
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "message_type": message_type,
            "sent_count": sent_count,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to send user notification: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/events/history")
async def get_event_history(
    limit: int = Query(default=100, ge=1, le=1000),
    event_type: Optional[str] = Query(default=None),
    current_user: dict = Depends(get_current_user)
):
    """Get recent event history"""
    try:
        event_type_enum = None
        if event_type:
            event_type_enum = EventType(event_type)
        
        history = event_system.get_event_history(
            limit=limit,
            event_type=event_type_enum
        )
        
        return {
            "events": history,
            "total_events": len(history),
            "timestamp": datetime.now().isoformat()
        }
    
    except ValueError:
        return {
            "error": "Invalid event type",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get event history: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/events/publish")
async def publish_event(
    event_type: str,
    data: dict,
    source: str = "api",
    correlation_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Publish an event to the event system"""
    try:
        event_type_enum = EventType(event_type)
        
        await event_system.publish(
            event_type=event_type_enum,
            data=data,
            source=source,
            correlation_id=correlation_id
        )
        
        return {
            "success": True,
            "event_type": event_type,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
    
    except ValueError:
        return {
            "success": False,
            "error": "Invalid event type",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
