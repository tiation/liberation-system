from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routers import resource
from core.knowledge_sharing import KnowledgeShareManager, KnowledgeType

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

# Initialize Knowledge Sharing system
knowledge_system = KnowledgeShareManager()

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

# Startup event to initialize the API and Knowledge Sharing System
@app.on_event("startup")
async def startup_event():
    """Initializes the system on startup and ensures all components are ready."""
    print("🚀 Liberation System API starting up...")  # Indicates API is starting
    print("📡 Trust by default - Maximum accessibility")  # System philosophy
    print("🌐 API Documentation available at /docs")  # API docs location
    
    # Initialize the knowledge sharing subsystem
    await knowledge_system.initialize()
    print("📚 Knowledge Sharing System initialized")  # Confirmation message

# Knowledge Sharing Endpoints

@app.get("/api/v1/knowledge", tags=["knowledge"])
async def get_knowledge_stats():
    """
    Get knowledge sharing system statistics.

    Returns a dictionary with total knowledge entries, active sessions, solved problems, etc.
    """
    stats = await knowledge_system.get_knowledge_stats()
    return {
        "success": True,
        "data": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/knowledge/add", tags=["knowledge"])
async def add_knowledge(request: dict):
    """
    Add a new knowledge entry.
    
    Args:
        request (dict): Contains "title", "content", "knowledge_type", "author", "tags".

    Returns:
        dict: JSON response indicating success or failure with entry ID.
    """
    title = request.get("title", "")
    content = request.get("content", "")
    knowledge_type = request.get("knowledge_type", "technical")
    author = request.get("author", "api_user")
    tags = request.get("tags", [])
    
    try:
        entry_id = await knowledge_system.add_knowledge(
            title=title,
            content=content,
            knowledge_type=KnowledgeType(knowledge_type.upper()),
            author=author,
            tags=tags
        )
        
        return {
            "success": True,
            "entry_id": entry_id,
            "message": "Knowledge entry added successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/v1/knowledge/search", tags=["knowledge"])
async def search_knowledge(query: str):
    """
    Search knowledge base using text query.
    
    Args:
        query (str): Search query string to find relevant knowledge entries.
        
    Returns:
        dict: JSON response with matching knowledge entries, including their metadata.
    """
    try:
        results = await knowledge_system.search_knowledge(query)
        return {
            "success": True,
            "results": [{
                "id": entry.id,
                "title": entry.title,
                "content": entry.content[:200] + "..." if len(entry.content) > 200 else entry.content,
                "knowledge_type": entry.knowledge_type.value,
                "author": entry.author,
                "tags": entry.tags,
                "confidence_score": entry.confidence_score,
                "effectiveness_rating": entry.effectiveness_rating
            } for entry in results],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/v1/knowledge/session", tags=["knowledge"])
async def start_learning_session(request: dict):
    """
    Start a collaborative learning session.
    
    Args:
        request (dict): Contains "title", "description", and "participants" list.
        
    Returns:
        dict: JSON response with session ID and confirmation message.
    """
    title = request.get("title", "")
    description = request.get("description", "")
    participants = request.get("participants", [])
    
    try:
        session_id = await knowledge_system.start_learning_session(
            title=title,
            description=description,
            participants=participants
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Learning session started successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/v1/knowledge/problem", tags=["knowledge"])
async def add_problem_context(request: dict):
    """
    Add problem context for autonomous solving.
    
    Args:
        request (dict): Contains "problem_description", "domain", and "priority".
        
    Returns:
        dict: JSON response with context ID for the autonomous solver.
    """
    problem_description = request.get("problem_description", "")
    domain = request.get("domain", "general")
    priority = request.get("priority", 1)
    
    try:
        context_id = await knowledge_system.add_problem_context(
            problem_description=problem_description,
            domain=domain,
            priority=priority
        )
        
        return {
            "success": True,
            "context_id": context_id,
            "message": "Problem context added for autonomous solving",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

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

