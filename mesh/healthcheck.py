#!/usr/bin/env python3
"""
Health check script for mesh network application
Used by Docker and Kubernetes for container health monitoring
"""

import sys
import socket
import requests
import json
from typing import Dict, Any

def check_http_endpoint(host: str = "localhost", port: int = 8080) -> bool:
    """Check if HTTP endpoint is responding"""
    try:
        response = requests.get(f"http://{host}:{port}/api/metrics", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def check_tcp_socket(host: str = "localhost", port: int = 8080) -> bool:
    """Check if TCP socket is listening"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def main():
    """Main health check function"""
    health_status = {
        "tcp_socket": check_tcp_socket(),
        "http_endpoint": check_http_endpoint(),
        "overall": False
    }
    
    # Overall health is good if both checks pass
    health_status["overall"] = health_status["tcp_socket"] and health_status["http_endpoint"]
    
    # Print status for debugging
    print(json.dumps(health_status, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if health_status["overall"] else 1)

if __name__ == "__main__":
    main()
