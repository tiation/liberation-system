from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routers import resource

# Create FastAPI app with comprehensive configuration
app = FastAPI(
    title="Liberation System API",
    description="REST API for the Liberation System - Trust by Default, Maximum Accessibility",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trust by default - allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(resource.router, prefix="/api/v1", tags=["resources"])

# Root endpoint
@app.get("/", tags=["system"])
async def root():
    """Root endpoint with system information"""
    return {
        "message": "🌟 Liberation System API - Trust by Default",
        "version": "1.0.0",
        "documentation": "/docs",
        "timestamp": datetime.now(),
        "philosophy": "Maximum accessibility, minimal barriers"
    }

# Health Check
@app.get("/health", tags=["system"])
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "message": "Liberation System is operational!",
        "timestamp": datetime.now(),
        "uptime": "operational"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    print("🚀 Liberation System API starting up...")
    print("📡 Trust by default - Maximum accessibility")
    print("🌐 API Documentation available at /docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    print("🛑 Liberation System API shutting down...")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with trust-by-default principle"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "System encountered an error but continues operating",
            "timestamp": datetime.now().isoformat()
        }
    )

