from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .routes import resources, truth, mesh, system, websocket, notifications
from .dependencies import initialize_database
from ..realtime.websocket.manager import websocket_manager
from ..realtime.events.system import event_system, WebSocketEventHandler
from ..core.logging_system import get_logger

# API rate limiter and error logger
logger = get_logger('liberation_system_api')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the FastAPI application"""
    # Startup
    logging.info("Starting Liberation System API...")
    
    # Initialize rate limiter
    await FastAPILimiter.init(backend="memory://")  # Use Redis for production
    
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

# Exception handlers
@app.exception_handler(HTTPException)
async def unicorn_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP exception occurred: {exc.detail}", exc_info=True)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception occurred: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

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
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])

# Root endpoint
@app.get("/")
@RateLimiter(times=100, minutes=1)
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
