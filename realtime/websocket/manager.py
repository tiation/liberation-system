import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum
import uuid

class ConnectionType(Enum):
    DASHBOARD = "dashboard"
    MOBILE = "mobile"
    ADMIN = "admin"
    SYSTEM = "system"

@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection"""
    id: str
    websocket: WebSocket
    connection_type: ConnectionType
    user_id: Optional[str] = None
    subscriptions: Set[str] = None
    connected_at: datetime = None
    last_ping: datetime = None
    
    def __post_init__(self):
        if self.subscriptions is None:
            self.subscriptions = set()
        if self.connected_at is None:
            self.connected_at = datetime.now()
        if self.last_ping is None:
            self.last_ping = datetime.now()

@dataclass
class WebSocketMessage:
    """Represents a WebSocket message"""
    id: str
    type: str
    channel: str
    data: Dict[str, Any]
    timestamp: datetime = None
    sender_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "channel": self.channel,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "sender_id": self.sender_id
        }

class WebSocketManager:
    """Manages WebSocket connections and real-time communication"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.channels: Dict[str, Set[str]] = {}  # channel -> connection_ids
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.logger = logging.getLogger(__name__)
        self.ping_interval = 30  # seconds
        self.cleanup_interval = 60  # seconds
        self._ping_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the WebSocket manager"""
        self._ping_task = asyncio.create_task(self._ping_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.logger.info("WebSocket manager started")
    
    async def stop(self):
        """Stop the WebSocket manager"""
        if self._ping_task:
            self._ping_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Close all connections
        for connection in list(self.connections.values()):
            await self.disconnect(connection.id)
        
        self.logger.info("WebSocket manager stopped")
    
    async def connect(
        self, 
        websocket: WebSocket, 
        connection_type: ConnectionType,
        user_id: Optional[str] = None
    ) -> str:
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        connection = WebSocketConnection(
            id=connection_id,
            websocket=websocket,
            connection_type=connection_type,
            user_id=user_id
        )
        
        self.connections[connection_id] = connection
        
        # Track user connections
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
        
        # Send welcome message
        await self._send_to_connection(connection_id, {
            "type": "connection_established",
            "channel": "system",
            "data": {
                "connection_id": connection_id,
                "connection_type": connection_type.value,
                "user_id": user_id,
                "server_time": datetime.now().isoformat()
            }
        })
        
        self.logger.info(f"WebSocket connection established: {connection_id} ({connection_type.value})")
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        # Remove from channels
        for channel in connection.subscriptions:
            if channel in self.channels:
                self.channels[channel].discard(connection_id)
                if not self.channels[channel]:
                    del self.channels[channel]
        
        # Remove from user connections
        if connection.user_id:
            if connection.user_id in self.user_connections:
                self.user_connections[connection.user_id].discard(connection_id)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]
        
        # Close WebSocket
        try:
            await connection.websocket.close()
        except:
            pass
        
        del self.connections[connection_id]
        self.logger.info(f"WebSocket connection disconnected: {connection_id}")
    
    async def subscribe(self, connection_id: str, channel: str):
        """Subscribe a connection to a channel"""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        connection.subscriptions.add(channel)
        
        if channel not in self.channels:
            self.channels[channel] = set()
        self.channels[channel].add(connection_id)
        
        # Send subscription confirmation
        await self._send_to_connection(connection_id, {
            "type": "subscription_confirmed",
            "channel": "system",
            "data": {
                "channel": channel,
                "subscribed_at": datetime.now().isoformat()
            }
        })
        
        self.logger.info(f"Connection {connection_id} subscribed to channel {channel}")
        return True
    
    async def unsubscribe(self, connection_id: str, channel: str):
        """Unsubscribe a connection from a channel"""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        connection.subscriptions.discard(channel)
        
        if channel in self.channels:
            self.channels[channel].discard(connection_id)
            if not self.channels[channel]:
                del self.channels[channel]
        
        # Send unsubscription confirmation
        await self._send_to_connection(connection_id, {
            "type": "unsubscription_confirmed",
            "channel": "system",
            "data": {
                "channel": channel,
                "unsubscribed_at": datetime.now().isoformat()
            }
        })
        
        self.logger.info(f"Connection {connection_id} unsubscribed from channel {channel}")
        return True
    
    async def broadcast_to_channel(self, channel: str, message_type: str, data: Dict[str, Any]):
        """Broadcast a message to all subscribers of a channel"""
        if channel not in self.channels:
            return 0
        
        message = WebSocketMessage(
            id=str(uuid.uuid4()),
            type=message_type,
            channel=channel,
            data=data
        )
        
        sent_count = 0
        failed_connections = []
        
        for connection_id in self.channels[channel].copy():
            try:
                await self._send_to_connection(connection_id, message.to_dict())
                sent_count += 1
            except Exception as e:
                self.logger.error(f"Failed to send message to connection {connection_id}: {e}")
                failed_connections.append(connection_id)
        
        # Remove failed connections
        for connection_id in failed_connections:
            await self.disconnect(connection_id)
        
        self.logger.info(f"Broadcasted message to {sent_count} connections on channel {channel}")
        return sent_count
    
    async def send_to_user(self, user_id: str, message_type: str, data: Dict[str, Any]):
        """Send a message to all connections of a specific user"""
        if user_id not in self.user_connections:
            return 0
        
        message = WebSocketMessage(
            id=str(uuid.uuid4()),
            type=message_type,
            channel="user",
            data=data
        )
        
        sent_count = 0
        failed_connections = []
        
        for connection_id in self.user_connections[user_id].copy():
            try:
                await self._send_to_connection(connection_id, message.to_dict())
                sent_count += 1
            except Exception as e:
                self.logger.error(f"Failed to send message to connection {connection_id}: {e}")
                failed_connections.append(connection_id)
        
        # Remove failed connections
        for connection_id in failed_connections:
            await self.disconnect(connection_id)
        
        self.logger.info(f"Sent message to {sent_count} connections for user {user_id}")
        return sent_count
    
    async def send_to_connection(self, connection_id: str, message_type: str, data: Dict[str, Any]):
        """Send a message to a specific connection"""
        message = WebSocketMessage(
            id=str(uuid.uuid4()),
            type=message_type,
            channel="direct",
            data=data
        )
        
        try:
            await self._send_to_connection(connection_id, message.to_dict())
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message to connection {connection_id}: {e}")
            await self.disconnect(connection_id)
            return False
    
    async def _send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Internal method to send a message to a connection"""
        if connection_id not in self.connections:
            raise Exception(f"Connection {connection_id} not found")
        
        connection = self.connections[connection_id]
        await connection.websocket.send_text(json.dumps(message))
    
    async def handle_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle incoming message from a connection"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        connection.last_ping = datetime.now()
        
        message_type = message.get("type")
        
        if message_type == "ping":
            await self._send_to_connection(connection_id, {
                "type": "pong",
                "channel": "system",
                "data": {
                    "timestamp": datetime.now().isoformat()
                }
            })
        
        elif message_type == "subscribe":
            channel = message.get("channel")
            if channel:
                await self.subscribe(connection_id, channel)
        
        elif message_type == "unsubscribe":
            channel = message.get("channel")
            if channel:
                await self.unsubscribe(connection_id, channel)
        
        elif message_type == "get_status":
            await self._send_to_connection(connection_id, {
                "type": "status",
                "channel": "system",
                "data": self.get_stats()
            })
        
        else:
            # Handle custom message types
            self.logger.info(f"Received message type '{message_type}' from connection {connection_id}")
    
    async def _ping_loop(self):
        """Periodically ping connections to keep them alive"""
        while True:
            try:
                await asyncio.sleep(self.ping_interval)
                
                for connection_id in list(self.connections.keys()):
                    try:
                        await self._send_to_connection(connection_id, {
                            "type": "ping",
                            "channel": "system",
                            "data": {
                                "timestamp": datetime.now().isoformat()
                            }
                        })
                    except Exception as e:
                        self.logger.error(f"Failed to ping connection {connection_id}: {e}")
                        await self.disconnect(connection_id)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in ping loop: {e}")
    
    async def _cleanup_loop(self):
        """Periodically cleanup stale connections"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                stale_threshold = datetime.now().timestamp() - (self.ping_interval * 3)
                stale_connections = []
                
                for connection_id, connection in self.connections.items():
                    if connection.last_ping.timestamp() < stale_threshold:
                        stale_connections.append(connection_id)
                
                for connection_id in stale_connections:
                    self.logger.info(f"Removing stale connection: {connection_id}")
                    await self.disconnect(connection_id)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        connection_types = {}
        for connection in self.connections.values():
            conn_type = connection.connection_type.value
            connection_types[conn_type] = connection_types.get(conn_type, 0) + 1
        
        return {
            "total_connections": len(self.connections),
            "total_channels": len(self.channels),
            "total_users": len(self.user_connections),
            "connection_types": connection_types,
            "channels": {
                channel: len(connection_ids) 
                for channel, connection_ids in self.channels.items()
            }
        }
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific connection"""
        if connection_id not in self.connections:
            return None
        
        connection = self.connections[connection_id]
        return {
            "id": connection.id,
            "connection_type": connection.connection_type.value,
            "user_id": connection.user_id,
            "subscriptions": list(connection.subscriptions),
            "connected_at": connection.connected_at.isoformat(),
            "last_ping": connection.last_ping.isoformat()
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
