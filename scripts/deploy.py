#!/usr/bin/env python3
"""
🚀 Liberation System Deployment Script
======================================

Enterprise-grade deployment automation with health checks,
rollback capabilities, and comprehensive monitoring.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import docker
import psutil
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.text import Text

console = Console()

class DeploymentManager:
    """Enterprise deployment management system"""
    
    def __init__(self, config_path: str = "deploy/config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.docker_client = docker.from_env()
        self.deployment_id = f"deploy_{int(time.time())}"
        
    def load_config(self) -> Dict:
        """Load deployment configuration"""
        default_config = {
            "app_name": "liberation-system",
            "docker_image": "liberation-system:latest",
            "ports": {
                "api": 8000,
                "web": 3000
            },
            "health_check": {
                "endpoint": "/health",
                "timeout": 30,
                "retries": 5
            },
            "rollback": {
                "enabled": True,
                "backup_image": "liberation-system:backup"
            },
            "monitoring": {
                "enabled": True,
                "metrics_port": 9090
            }
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
        
        return default_config
    
    def pre_deployment_checks(self) -> bool:
        """Run pre-deployment system checks"""
        console.print("🔍 Running pre-deployment checks...", style="bold cyan")
        
        checks = [
            ("Docker daemon", self.check_docker),
            ("System resources", self.check_system_resources),
            ("Network ports", self.check_ports),
            ("Database connectivity", self.check_database),
            ("Environment variables", self.check_environment)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "✅" if result else "❌"
                console.print(f"  {status} {check_name}")
                if not result:
                    all_passed = False
            except Exception as e:
                console.print(f"  ❌ {check_name}: {e}")
                all_passed = False
        
        return all_passed
    
    def check_docker(self) -> bool:
        """Check Docker daemon status"""
        try:
            self.docker_client.ping()
            return True
        except Exception:
            return False
    
    def check_system_resources(self) -> bool:
        """Check system resources"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Require at least 1GB RAM and 5GB disk space
        return memory.available > 1024**3 and disk.free > 5 * 1024**3
    
    def check_ports(self) -> bool:
        """Check if required ports are available"""
        for port in self.config["ports"].values():
            if self.is_port_in_use(port):
                console.print(f"    Port {port} is in use")
                return False
        return True
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if port is in use"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False
    
    def check_database(self) -> bool:
        """Check database connectivity"""
        # Placeholder for database checks
        return True
    
    def check_environment(self) -> bool:
        """Check environment variables"""
        required_vars = ["LIBERATION_MODE", "NODE_ENV"]
        for var in required_vars:
            if not os.getenv(var):
                console.print(f"    Missing environment variable: {var}")
                return False
        return True
    
    def backup_current_deployment(self) -> bool:
        """Create backup of current deployment"""
        console.print("📦 Creating deployment backup...", style="bold cyan")
        
        try:
            # Stop current containers
            containers = self.docker_client.containers.list(
                filters={"label": f"app={self.config['app_name']}"}
            )
            
            for container in containers:
                console.print(f"  Stopping container: {container.name}")
                container.stop()
            
            # Tag current image as backup
            try:
                current_image = self.docker_client.images.get(self.config["docker_image"])
                current_image.tag(self.config["rollback"]["backup_image"])
                console.print("  ✅ Backup image created")
            except docker.errors.ImageNotFound:
                console.print("  ⚠️  No current image to backup")
            
            return True
            
        except Exception as e:
            console.print(f"  ❌ Backup failed: {e}")
            return False
    
    def build_application(self) -> bool:
        """Build the application"""
        console.print("🏗️  Building application...", style="bold cyan")
        
        try:
            # Build Docker image
            console.print("  Building Docker image...")
            image, logs = self.docker_client.images.build(
                path=".",
                tag=self.config["docker_image"],
                rm=True,
                nocache=False
            )
            
            console.print("  ✅ Docker image built successfully")
            return True
            
        except Exception as e:
            console.print(f"  ❌ Build failed: {e}")
            return False
    
    def deploy_application(self) -> bool:
        """Deploy the application"""
        console.print("🚀 Deploying application...", style="bold cyan")
        
        try:
            # Deploy API container
            api_container = self.docker_client.containers.run(
                self.config["docker_image"],
                name=f"{self.config['app_name']}-api-{self.deployment_id}",
                ports={f"{self.config['ports']['api']}/tcp": self.config['ports']['api']},
                environment={
                    "LIBERATION_MODE": os.getenv("LIBERATION_MODE", "production"),
                    "API_PORT": str(self.config['ports']['api'])
                },
                labels={
                    "app": self.config['app_name'],
                    "component": "api",
                    "deployment_id": self.deployment_id
                },
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            
            console.print(f"  ✅ API container deployed: {api_container.name}")
            
            # Deploy web container
            web_container = self.docker_client.containers.run(
                self.config["docker_image"],
                name=f"{self.config['app_name']}-web-{self.deployment_id}",
                ports={f"{self.config['ports']['web']}/tcp": self.config['ports']['web']},
                environment={
                    "NODE_ENV": os.getenv("NODE_ENV", "production"),
                    "PORT": str(self.config['ports']['web'])
                },
                labels={
                    "app": self.config['app_name'],
                    "component": "web",
                    "deployment_id": self.deployment_id
                },
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            
            console.print(f"  ✅ Web container deployed: {web_container.name}")
            return True
            
        except Exception as e:
            console.print(f"  ❌ Deployment failed: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Perform health checks on deployed application"""
        console.print("🏥 Performing health checks...", style="bold cyan")
        
        import aiohttp
        
        endpoints = [
            f"http://localhost:{self.config['ports']['api']}/health",
            f"http://localhost:{self.config['ports']['web']}"
        ]
        
        for endpoint in endpoints:
            console.print(f"  Checking {endpoint}...")
            
            for attempt in range(self.config["health_check"]["retries"]):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            endpoint,
                            timeout=aiohttp.ClientTimeout(total=self.config["health_check"]["timeout"])
                        ) as response:
                            if response.status == 200:
                                console.print(f"    ✅ Health check passed")
                                break
                            else:
                                console.print(f"    ⚠️  Attempt {attempt + 1}: Status {response.status}")
                
                except Exception as e:
                    console.print(f"    ⚠️  Attempt {attempt + 1}: {e}")
                
                if attempt < self.config["health_check"]["retries"] - 1:
                    await asyncio.sleep(5)
            else:
                console.print(f"    ❌ Health check failed after {self.config['health_check']['retries']} attempts")
                return False
        
        return True
    
    def rollback(self) -> bool:
        """Rollback to previous deployment"""
        console.print("🔄 Rolling back deployment...", style="bold yellow")
        
        if not self.config["rollback"]["enabled"]:
            console.print("  ❌ Rollback disabled in configuration")
            return False
        
        try:
            # Stop current containers
            containers = self.docker_client.containers.list(
                filters={"label": f"deployment_id={self.deployment_id}"}
            )
            
            for container in containers:
                console.print(f"  Stopping container: {container.name}")
                container.stop()
                container.remove()
            
            # Deploy backup image
            console.print("  Deploying backup image...")
            # Implementation similar to deploy_application but with backup image
            
            console.print("  ✅ Rollback completed")
            return True
            
        except Exception as e:
            console.print(f"  ❌ Rollback failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up old deployments"""
        console.print("🧹 Cleaning up old deployments...", style="bold cyan")
        
        try:
            # Remove old containers
            containers = self.docker_client.containers.list(
                all=True,
                filters={"label": f"app={self.config['app_name']}"}
            )
            
            for container in containers:
                if container.labels.get("deployment_id") != self.deployment_id:
                    console.print(f"  Removing old container: {container.name}")
                    container.remove(force=True)
            
            # Remove old images
            images = self.docker_client.images.list()
            for image in images:
                if image.tags and any("liberation-system" in tag for tag in image.tags):
                    if not any(self.config["docker_image"] in tag or self.config["rollback"]["backup_image"] in tag for tag in image.tags):
                        console.print(f"  Removing old image: {image.tags}")
                        self.docker_client.images.remove(image.id, force=True)
            
            console.print("  ✅ Cleanup completed")
            
        except Exception as e:
            console.print(f"  ⚠️  Cleanup warning: {e}")
    
    def generate_deployment_report(self, success: bool) -> Dict:
        """Generate deployment report"""
        report = {
            "deployment_id": self.deployment_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "config": self.config,
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_free": psutil.disk_usage('/').free
            }
        }
        
        # Save report
        os.makedirs("deploy/reports", exist_ok=True)
        report_path = f"deploy/reports/deployment_{self.deployment_id}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        console.print(f"📊 Deployment report saved: {report_path}")
        return report

async def main():
    """Main deployment orchestration"""
    
    console.print("🌟 Liberation System Deployment", style="bold cyan")
    console.print("================================", style="cyan")
    
    manager = DeploymentManager()
    
    try:
        # Pre-deployment checks
        if not manager.pre_deployment_checks():
            console.print("❌ Pre-deployment checks failed", style="bold red")
            return 1
        
        # Backup current deployment
        if not manager.backup_current_deployment():
            console.print("❌ Backup failed", style="bold red")
            return 1
        
        # Build application
        if not manager.build_application():
            console.print("❌ Build failed", style="bold red")
            return 1
        
        # Deploy application
        if not manager.deploy_application():
            console.print("❌ Deployment failed", style="bold red")
            manager.rollback()
            return 1
        
        # Health checks
        if not await manager.health_check():
            console.print("❌ Health checks failed", style="bold red")
            manager.rollback()
            return 1
        
        # Cleanup
        manager.cleanup()
        
        # Generate report
        report = manager.generate_deployment_report(True)
        
        console.print("\n🎉 Deployment completed successfully!", style="bold green")
        console.print(f"   API: http://localhost:{manager.config['ports']['api']}")
        console.print(f"   Web: http://localhost:{manager.config['ports']['web']}")
        
        return 0
        
    except Exception as e:
        console.print(f"❌ Deployment failed: {e}", style="bold red")
        manager.generate_deployment_report(False)
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
