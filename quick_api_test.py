#!/usr/bin/env python3
"""
Quick API Test - Validate REST API is working
"""

import requests
import json
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_api():
    """Quick test of the REST API"""
    
    console.print(Panel.fit("🌟 Quick API Test", style="bold blue"))
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    tests = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/api/v1/stats", "System stats"),
        ("GET", "/api/v1/humans", "Get humans"),
    ]
    
    for method, endpoint, name in tests:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                console.print(f"✅ {name}: {response.status_code}", style="green")
            else:
                console.print(f"❌ {name}: {response.status_code}", style="red")
                
        except requests.exceptions.ConnectionError:
            console.print(f"❌ {name}: Connection refused (server not running)", style="red")
        except Exception as e:
            console.print(f"❌ {name}: {str(e)}", style="red")
    
    console.print("\n📚 API Documentation available at: http://localhost:8000/docs")
    console.print("🔄 Interactive API at: http://localhost:8000/redoc")

if __name__ == "__main__":
    test_api()
