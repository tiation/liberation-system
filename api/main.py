from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .routes import resources, truth, mesh, system, websocket
from .dependencies import initialize_database
from ..realtime.websocket.manager import websocket_manager
from ..realtime.events.system import event_system, WebSocketEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the FastAPI application"""
    # Startup
    logging.info("Starting Liberation System API...")
    
    # Initialize database
    await initialize_database()
    
    # Start WebSocket manager
    await websocket_manager.start()
    
    # Register WebSocket event handler
    websocket_handler = WebSocketEventHandler(websocket_manager)
    for event_type in websocket_handler.channel_mapping.keys():
        event_system.register_handler(event_type, websocket_handler)
    
    logging.info("Liberation System API started successfully")
    
    yield
    
    # Shutdown
    logging.info("Shutting down Liberation System API...")
    await websocket_manager.stop()
    logging.info("Liberation System API shutdown complete")

app = FastAPI(
    title="Liberation System API",
    description="API for the $19 Trillion Economic Reform",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware for handling CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
app.include_router(resources.router, prefix="/api/v1/resources", tags=["Resources"])
app.include_router(truth.router, prefix="/api/v1/truth", tags=["Truth"])
app.include_router(mesh.router, prefix="/api/v1/mesh", tags=["Mesh"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])
app.include_router(websocket.router, prefix="/api/v1/realtime", tags=["Real-time"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Liberation System API",
        "version": "1.0.0",
        "features": [
            "$19T Resource Distribution",
            "Truth Spreading Network",
            "Mesh Network Management",
            "Real-time WebSocket Communication",
            "Event-driven Architecture"
        ]
    }
