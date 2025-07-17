#!/usr/bin/env python3
"""
Liberation System API Server
Launch script for the REST API server
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Launch the Liberation System API server"""
    
    print("🌟 Liberation System API Server")
    print("=" * 40)
    print("🚀 Starting server...")
    print("📡 Trust by default - Maximum accessibility")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 Documentation at: http://localhost:8000/docs")
    print("🔄 Interactive API at: http://localhost:8000/redoc")
    print("=" * 40)
    
    # Configure uvicorn
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",  # Trust by default - allow all hosts
        port=8000,
        reload=True,  # Auto-reload on changes
        access_log=True,
        log_level="info",
        workers=1  # Single worker for development
    )

if __name__ == "__main__":
    main()
