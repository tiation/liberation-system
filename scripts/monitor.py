#!/usr/bin/env python3
"""
📊 Liberation System Performance Monitor
========================================

Enterprise-grade monitoring system with alerts, metrics collection,
and automated performance optimization.
"""

import asyncio
import json
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
import logging
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

console = Console()

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    liberation_metrics: Dict[str, Any]

@dataclass
class Alert:
    """Alert configuration"""
    name: str
    threshold: float
    current_value: float
    severity: str
    message: str
    timestamp: str

class LiberationMonitor:
    """Enterprise monitoring system"""
    
    def __init__(self, config_path: str = "config/monitor.json"):
        self.config = self.load_config(config_path)
        self.metrics_history: List[SystemMetrics] = []
        self.alerts: List[Alert] = []
        self.api_base_url = self.config.get("api_base_url", "http://localhost:8000")
        
    def load_config(self, config_path: str) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            "api_base_url": "http://localhost:8000",
            "metrics_interval": 5,
            "history_retention": 3600,  # 1 hour
            "alerts": {
                "cpu_threshold": 80.0,
                "memory_threshold": 85.0,
                "disk_threshold": 90.0,
                "response_time_threshold": 2.0,
                "error_rate_threshold": 5.0
            },
            "notifications": {
                "email_enabled": False,
                "email_smtp": "smtp.gmail.com",
                "email_port": 587,
                "email_user": "alerts@liberation.system",
                "email_password": "your_app_password",
                "email_recipients": ["admin@liberation.system"]
            },
            "performance": {
                "auto_restart": True,
                "auto_scale": False,
                "optimization_enabled": True
            }
        }
        
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
        except FileNotFoundError:
            console.print(f"⚠️  Config file not found: {config_path}, using defaults")
        
        return default_config
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        # Liberation System specific metrics
        liberation_metrics = await self.collect_liberation_metrics()
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=(disk.used / disk.total) * 100,
            network_io={
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            liberation_metrics=liberation_metrics
        )
    
    async def collect_liberation_metrics(self) -> Dict[str, Any]:
        """Collect Liberation System specific metrics"""
        try:
            async with aiohttp.ClientSession() as session:
                # System stats
                async with session.get(f"{self.api_base_url}/api/v1/stats") as response:
                    if response.status == 200:
                        stats = await response.json()
                    else:
                        stats = {"error": f"API returned {response.status}"}
                
                # Health check
                start_time = time.time()
                async with session.get(f"{self.api_base_url}/health") as response:
                    response_time = time.time() - start_time
                    health_status = response.status == 200
                
                # Automation stats
                async with session.get(f"{self.api_base_url}/api/v1/automation/stats") as response:
                    if response.status == 200:
                        automation_stats = await response.json()
                    else:
                        automation_stats = {"error": f"API returned {response.status}"}
                
                return {
                    "api_response_time": response_time,
                    "api_health": health_status,
                    "system_stats": stats,
                    "automation_stats": automation_stats
                }
        
        except Exception as e:
            return {
                "error": str(e),
                "api_response_time": 0,
                "api_health": False
            }
    
    def check_alerts(self, metrics: SystemMetrics):
        """Check for alert conditions"""
        alert_config = self.config["alerts"]
        
        # CPU alert
        if metrics.cpu_percent > alert_config["cpu_threshold"]:
            self.alerts.append(Alert(
                name="High CPU Usage",
                threshold=alert_config["cpu_threshold"],
                current_value=metrics.cpu_percent,
                severity="WARNING",
                message=f"CPU usage at {metrics.cpu_percent:.1f}%",
                timestamp=metrics.timestamp
            ))
        
        # Memory alert
        if metrics.memory_percent > alert_config["memory_threshold"]:
            self.alerts.append(Alert(
                name="High Memory Usage",
                threshold=alert_config["memory_threshold"],
                current_value=metrics.memory_percent,
                severity="WARNING",
                message=f"Memory usage at {metrics.memory_percent:.1f}%",
                timestamp=metrics.timestamp
            ))
        
        # Disk alert
        if metrics.disk_percent > alert_config["disk_threshold"]:
            self.alerts.append(Alert(
                name="High Disk Usage",
                threshold=alert_config["disk_threshold"],
                current_value=metrics.disk_percent,
                severity="CRITICAL",
                message=f"Disk usage at {metrics.disk_percent:.1f}%",
                timestamp=metrics.timestamp
            ))
        
        # API response time alert
        if metrics.liberation_metrics.get("api_response_time", 0) > alert_config["response_time_threshold"]:
            self.alerts.append(Alert(
                name="Slow API Response",
                threshold=alert_config["response_time_threshold"],
                current_value=metrics.liberation_metrics["api_response_time"],
                severity="WARNING",
                message=f"API response time: {metrics.liberation_metrics['api_response_time']:.2f}s",
                timestamp=metrics.timestamp
            ))
        
        # API health alert
        if not metrics.liberation_metrics.get("api_health", False):
            self.alerts.append(Alert(
                name="API Health Check Failed",
                threshold=1.0,
                current_value=0.0,
                severity="CRITICAL",
                message="Liberation System API is not responding",
                timestamp=metrics.timestamp
            ))
    
    async def send_alerts(self):
        """Send alerts via configured channels"""
        if not self.alerts:
            return
        
        # Email notifications
        if self.config["notifications"]["email_enabled"]:
            await self.send_email_alerts()
        
        # Log alerts
        for alert in self.alerts:
            console.print(f"🚨 {alert.severity}: {alert.name} - {alert.message}")
        
        # Clear processed alerts
        self.alerts.clear()
    
    async def send_email_alerts(self):
        """Send email alerts"""
        try:
            email_config = self.config["notifications"]
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = email_config["email_user"]
            msg['To'] = ", ".join(email_config["email_recipients"])
            msg['Subject'] = f"Liberation System Alerts - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Email body
            body = "🚨 Liberation System Alerts\\n\\n"
            for alert in self.alerts:
                body += f"• {alert.severity}: {alert.name}\\n"
                body += f"  Message: {alert.message}\\n"
                body += f"  Threshold: {alert.threshold}\\n"
                body += f"  Current: {alert.current_value}\\n"
                body += f"  Time: {alert.timestamp}\\n\\n"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(email_config["email_smtp"], email_config["email_port"])
            server.starttls()
            server.login(email_config["email_user"], email_config["email_password"])
            server.send_message(msg)
            server.quit()
            
            console.print("📧 Alert emails sent successfully")
            
        except Exception as e:
            console.print(f"❌ Failed to send email alerts: {e}")
    
    async def optimize_performance(self, metrics: SystemMetrics):
        """Automated performance optimization"""
        if not self.config["performance"]["optimization_enabled"]:
            return
        
        # Memory optimization
        if metrics.memory_percent > 70:
            console.print("🔧 Running memory optimization...")
            await self.trigger_garbage_collection()
        
        # CPU optimization
        if metrics.cpu_percent > 80:
            console.print("🔧 Running CPU optimization...")
            await self.optimize_cpu_usage()
        
        # Auto-restart if critical
        if (metrics.memory_percent > 95 or 
            metrics.cpu_percent > 95 or
            not metrics.liberation_metrics.get("api_health", False)):
            
            if self.config["performance"]["auto_restart"]:
                console.print("🔄 Auto-restarting system due to critical conditions...")
                await self.restart_system()
    
    async def trigger_garbage_collection(self):
        """Trigger garbage collection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base_url}/api/v1/system/gc") as response:
                    if response.status == 200:
                        console.print("  ✅ Garbage collection triggered")
                    else:
                        console.print(f"  ⚠️  GC request failed: {response.status}")
        except Exception as e:
            console.print(f"  ❌ GC trigger failed: {e}")
    
    async def optimize_cpu_usage(self):
        """Optimize CPU usage"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base_url}/api/v1/system/optimize") as response:
                    if response.status == 200:
                        console.print("  ✅ CPU optimization triggered")
                    else:
                        console.print(f"  ⚠️  Optimization request failed: {response.status}")
        except Exception as e:
            console.print(f"  ❌ CPU optimization failed: {e}")
    
    async def restart_system(self):
        """Restart the Liberation System"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base_url}/api/v1/system/restart") as response:
                    if response.status == 200:
                        console.print("  ✅ System restart initiated")
                    else:
                        console.print(f"  ⚠️  Restart request failed: {response.status}")
        except Exception as e:
            console.print(f"  ❌ System restart failed: {e}")
    
    def create_dashboard(self) -> Layout:
        """Create monitoring dashboard"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        return layout
    
    def update_dashboard(self, layout: Layout, metrics: SystemMetrics):
        """Update dashboard with current metrics"""
        # Header
        layout["header"].update(
            Panel(
                Align.center("🌟 Liberation System Monitor", style="bold cyan"),
                title="Status Dashboard",
                border_style="cyan"
            )
        )
        
        # System metrics table
        system_table = Table(title="System Metrics")
        system_table.add_column("Metric", style="cyan")
        system_table.add_column("Value", style="green")
        system_table.add_column("Status", style="yellow")
        
        # CPU status
        cpu_status = "🟢 Normal" if metrics.cpu_percent < 70 else "🟡 High" if metrics.cpu_percent < 90 else "🔴 Critical"
        system_table.add_row("CPU Usage", f"{metrics.cpu_percent:.1f}%", cpu_status)
        
        # Memory status
        mem_status = "🟢 Normal" if metrics.memory_percent < 70 else "🟡 High" if metrics.memory_percent < 90 else "🔴 Critical"
        system_table.add_row("Memory Usage", f"{metrics.memory_percent:.1f}%", mem_status)
        
        # Disk status
        disk_status = "🟢 Normal" if metrics.disk_percent < 80 else "🟡 High" if metrics.disk_percent < 95 else "🔴 Critical"
        system_table.add_row("Disk Usage", f"{metrics.disk_percent:.1f}%", disk_status)
        
        layout["left"].update(Panel(system_table, title="System Health", border_style="green"))
        
        # Liberation metrics table
        lib_table = Table(title="Liberation System Metrics")
        lib_table.add_column("Metric", style="cyan")
        lib_table.add_column("Value", style="green")
        lib_table.add_column("Status", style="yellow")
        
        # API health
        api_health = "🟢 Online" if metrics.liberation_metrics.get("api_health", False) else "🔴 Offline"
        lib_table.add_row("API Health", "Active" if metrics.liberation_metrics.get("api_health", False) else "Down", api_health)
        
        # Response time
        response_time = metrics.liberation_metrics.get("api_response_time", 0)
        response_status = "🟢 Fast" if response_time < 0.5 else "🟡 Slow" if response_time < 2.0 else "🔴 Very Slow"
        lib_table.add_row("Response Time", f"{response_time:.3f}s", response_status)
        
        # System stats
        stats = metrics.liberation_metrics.get("system_stats", {})
        if isinstance(stats, dict) and "total_humans" in stats:
            lib_table.add_row("Total Humans", str(stats.get("total_humans", 0)), "🟢 Active")
            lib_table.add_row("Total Distributed", f"${stats.get('total_distributed', 0):,.2f}", "🟢 Flowing")
        
        layout["right"].update(Panel(lib_table, title="Liberation Metrics", border_style="magenta"))
        
        # Footer with alerts
        if self.alerts:
            alert_text = " | ".join([f"🚨 {alert.name}: {alert.message}" for alert in self.alerts[-3:]])
            layout["footer"].update(Panel(alert_text, title="Active Alerts", border_style="red"))
        else:
            layout["footer"].update(Panel("✅ No active alerts", title="System Status", border_style="green"))
    
    def save_metrics(self, metrics: SystemMetrics):
        """Save metrics to file"""
        self.metrics_history.append(metrics)
        
        # Keep only recent history
        cutoff_time = datetime.now() - timedelta(seconds=self.config["history_retention"])
        self.metrics_history = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        # Save to JSON file
        with open("logs/metrics.json", "w") as f:
            json.dump([asdict(m) for m in self.metrics_history], f, indent=2)
    
    async def run_monitor(self):
        """Main monitoring loop"""
        console.print("🚀 Starting Liberation System Monitor", style="bold cyan")
        
        layout = self.create_dashboard()
        
        with Live(layout, refresh_per_second=1) as live:
            while True:
                try:
                    # Collect metrics
                    metrics = await self.collect_system_metrics()
                    
                    # Check for alerts
                    self.check_alerts(metrics)
                    
                    # Send alerts if any
                    await self.send_alerts()
                    
                    # Optimize performance
                    await self.optimize_performance(metrics)
                    
                    # Update dashboard
                    self.update_dashboard(layout, metrics)
                    
                    # Save metrics
                    self.save_metrics(metrics)
                    
                    # Wait for next cycle
                    await asyncio.sleep(self.config["metrics_interval"])
                    
                except KeyboardInterrupt:
                    console.print("\\n👋 Monitoring stopped by user")
                    break
                except Exception as e:
                    console.print(f"❌ Monitor error: {e}")
                    await asyncio.sleep(5)

async def main():
    """Main monitor execution"""
    monitor = LiberationMonitor()
    await monitor.run_monitor()

if __name__ == "__main__":
    asyncio.run(main())
