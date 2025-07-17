# core/web_server.py

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import aiohttp
from aiohttp import web, WSMsgType
from aiohttp.web import Request, Response, WebSocketResponse
from aiohttp_cors import setup as cors_setup, ResourceOptions

from core.config import get_config
from core.liberation_core import LiberationSystemManager
from rich.console import Console

class ProductionWebServer:
    """Production-ready web server for Liberation System"""
    
    def __init__(self):
        self.config = get_config()
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.app = web.Application()
        self.liberation_manager: Optional[LiberationSystemManager] = None
        self.websocket_clients = set()
        
    async def initialize(self):
        """Initialize the web server"""
        try:
            # Initialize liberation system
            self.liberation_manager = LiberationSystemManager()
            await self.liberation_manager.core.initialize_all_systems()
            
            # Setup routes
            self.setup_routes()
            
            # Setup CORS
            self.setup_cors()
            
            # Setup websocket broadcasting
            asyncio.create_task(self.broadcast_system_stats())
            
            self.console.print("🌐 Web server initialized", style="green")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize web server: {e}")
            raise
    
    def setup_routes(self):
        """Setup API routes"""
        # Health check
        self.app.router.add_get('/health', self.health_check)
        
        # System status
        self.app.router.add_get('/api/status', self.get_system_status)
        
        # Resource distribution
        self.app.router.add_get('/api/resources/stats', self.get_resource_stats)
        self.app.router.add_post('/api/resources/add_human', self.add_human)
        self.app.router.add_post('/api/resources/distribute', self.distribute_resources)
        
        # Truth spreading
        self.app.router.add_get('/api/truth/stats', self.get_truth_stats)
        self.app.router.add_post('/api/truth/add_message', self.add_truth_message)
        self.app.router.add_post('/api/truth/spread', self.spread_truth)
        
        # Mesh network
        self.app.router.add_get('/api/mesh/stats', self.get_mesh_stats)
        
        # System control
        self.app.router.add_post('/api/system/start', self.start_system)
        self.app.router.add_post('/api/system/stop', self.stop_system)
        self.app.router.add_post('/api/system/restart', self.restart_system)
        
        # WebSocket for real-time updates
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Static files
        self.app.router.add_static('/', 'static/', name='static')
        
    def setup_cors(self):
        """Setup CORS for cross-origin requests"""
        cors = cors_setup(self.app, defaults={
            "*": ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "uptime": (datetime.now() - self.liberation_manager.core.start_time).total_seconds() if self.liberation_manager else 0
        })
    
    async def get_system_status(self, request: Request) -> Response:
        """Get overall system status"""
        try:
            if not self.liberation_manager:
                return web.json_response({"error": "System not initialized"}, status=500)
            
            status = {
                "running": self.liberation_manager.core.running,
                "uptime": (datetime.now() - self.liberation_manager.core.start_time).total_seconds(),
                "tasks": len(self.liberation_manager.core.tasks),
                "metrics": self.liberation_manager.core.metrics,
                "subsystems": {
                    "resource_distribution": self.liberation_manager.core.resource_system is not None,
                    "truth_spreading": self.liberation_manager.core.truth_system is not None,
                    "security": self.liberation_manager.core.security_system is not None
                }
            }
            
            return web.json_response(status)
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_resource_stats(self, request: Request) -> Response:
        """Get resource distribution statistics"""
        try:
            if not self.liberation_manager or not self.liberation_manager.core.resource_system:
                return web.json_response({"error": "Resource system not available"}, status=503)
            
            stats = await self.liberation_manager.core.resource_system.get_system_stats()
            return web.json_response(stats)
            
        except Exception as e:
            self.logger.error(f"Error getting resource stats: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def add_human(self, request: Request) -> Response:
        """Add a human to the resource distribution system"""
        try:
            data = await request.json()
            human_id = data.get('human_id')
            
            if not human_id:
                return web.json_response({"error": "human_id required"}, status=400)
            
            if not self.liberation_manager or not self.liberation_manager.core.resource_system:
                return web.json_response({"error": "Resource system not available"}, status=503)
            
            success = await self.liberation_manager.core.resource_system.add_human(human_id)
            
            return web.json_response({"success": success, "human_id": human_id})
            
        except Exception as e:
            self.logger.error(f"Error adding human: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def distribute_resources(self, request: Request) -> Response:
        """Trigger resource distribution"""
        try:
            if not self.liberation_manager or not self.liberation_manager.core.resource_system:
                return web.json_response({"error": "Resource system not available"}, status=503)
            
            await self.liberation_manager.core.resource_system.resource_pool.distribute_weekly()
            
            return web.json_response({"success": True, "message": "Resources distributed"})
            
        except Exception as e:
            self.logger.error(f"Error distributing resources: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_truth_stats(self, request: Request) -> Response:
        """Get truth spreading statistics"""
        try:
            if not self.liberation_manager or not self.liberation_manager.core.truth_system:
                return web.json_response({"error": "Truth system not available"}, status=503)
            
            stats = await self.liberation_manager.core.truth_system.spreader.get_spread_statistics()
            return web.json_response(stats)
            
        except Exception as e:
            self.logger.error(f"Error getting truth stats: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def add_truth_message(self, request: Request) -> Response:
        """Add a truth message to spread"""
        try:
            data = await request.json()
            content = data.get('content')
            source = data.get('source', 'api')
            priority = data.get('priority', 3)
            
            if not content:
                return web.json_response({"error": "content required"}, status=400)
            
            if not self.liberation_manager or not self.liberation_manager.core.truth_system:
                return web.json_response({"error": "Truth system not available"}, status=503)
            
            message_id = await self.liberation_manager.core.truth_system.spreader.add_truth_message(
                content, source, priority
            )\n            \n            return web.json_response({"success": True, "message_id": message_id})
            
        except Exception as e:
            self.logger.error(f"Error adding truth message: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def spread_truth(self, request: Request) -> Response:
        """Trigger truth spreading"""
        try:
            if not self.liberation_manager or not self.liberation_manager.core.truth_system:
                return web.json_response({"error": "Truth system not available"}, status=503)
            
            await self.liberation_manager.core.truth_system.spreader.spread_truth()
            
            return web.json_response({"success": True, "message": "Truth spread initiated"})
            
        except Exception as e:
            self.logger.error(f"Error spreading truth: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_mesh_stats(self, request: Request) -> Response:
        """Get mesh network statistics"""
        try:
            # For now, return mock data since mesh system is basic
            stats = {
                "nodes_active": 0,
                "connections": 0,
                "performance": 0.0,
                "message": "Mesh network system is in development"
            }
            
            return web.json_response(stats)
            
        except Exception as e:
            self.logger.error(f"Error getting mesh stats: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def start_system(self, request: Request) -> Response:
        """Start the liberation system"""
        try:
            if not self.liberation_manager:
                return web.json_response({"error": "System not initialized"}, status=500)
            
            # Start the system in background
            asyncio.create_task(self.liberation_manager.core.run_forever())
            
            return web.json_response({"success": True, "message": "System started"})
            
        except Exception as e:
            self.logger.error(f"Error starting system: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def stop_system(self, request: Request) -> Response:
        """Stop the liberation system"""
        try:
            if not self.liberation_manager:
                return web.json_response({"error": "System not initialized"}, status=500)
            
            await self.liberation_manager.core.shutdown()
            
            return web.json_response({"success": True, "message": "System stopped"})
            
        except Exception as e:
            self.logger.error(f"Error stopping system: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def restart_system(self, request: Request) -> Response:
        """Restart the liberation system"""
        try:
            if not self.liberation_manager:
                return web.json_response({"error": "System not initialized"}, status=500)
            
            await self.liberation_manager.core.shutdown()
            await self.liberation_manager.core.initialize_all_systems()
            asyncio.create_task(self.liberation_manager.core.run_forever())
            
            return web.json_response({"success": True, "message": "System restarted"})
            
        except Exception as e:
            self.logger.error(f"Error restarting system: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def websocket_handler(self, request: Request) -> WebSocketResponse:
        """WebSocket handler for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_clients.add(ws)
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    # Handle incoming WebSocket messages if needed
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f"WebSocket error: {ws.exception()}")
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            self.websocket_clients.discard(ws)
        
        return ws
    
    async def broadcast_system_stats(self):
        """Broadcast system statistics to all connected WebSocket clients"""
        while True:
            try:
                if self.websocket_clients and self.liberation_manager:
                    stats = {
                        "timestamp": datetime.now().isoformat(),
                        "metrics": self.liberation_manager.core.metrics,
                        "uptime": (datetime.now() - self.liberation_manager.core.start_time).total_seconds(),
                        "running": self.liberation_manager.core.running
                    }
                    
                    message = json.dumps(stats)
                    
                    # Send to all connected clients
                    disconnected = set()
                    for client in self.websocket_clients:
                        try:
                            await client.send_str(message)
                        except ConnectionResetError:
                            disconnected.add(client)
                    
                    # Remove disconnected clients
                    self.websocket_clients -= disconnected
                
                await asyncio.sleep(5)  # Broadcast every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error broadcasting stats: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the web server"""
        try:
            await self.initialize()
            
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, host, port)
            await site.start()
            
            self.console.print(f"🌐 Liberation System Web Server running on http://{host}:{port}", style="bold green")
            
            # Keep the server running
            await asyncio.Future()  # Run forever
            
        except Exception as e:
            self.logger.error(f"Failed to start web server: {e}")
            raise

async def main():
    """Main entry point for the web server"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    server = ProductionWebServer()
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())
