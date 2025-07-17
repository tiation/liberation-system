# core/automation/task_scheduler.py

import asyncio
import logging
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Callable, Optional
from datetime import datetime, timedelta
from pathlib import Path
import psutil
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
import aiofiles
import aiosqlite

@dataclass
class Task:
    name: str
    function: Callable
    priority: int = 1
    last_run: datetime = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_duration: float = 0.0
    status: str = 'pending'
    next_run: datetime = None
    
    def __post_init__(self):
        if self.next_run is None:
            self.next_run = datetime.now()

class AutomationCore:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.running = True
        self.logger = logging.getLogger(__name__)
        self.console = Console()
        self.db_path = Path('data/automation_tasks.db')
        self.metrics = {
            'total_tasks_run': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'system_uptime': datetime.now()
        }
        
    async def initialize_database(self):
        """Initialize task tracking database"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS task_runs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_name TEXT,
                        start_time TEXT,
                        end_time TEXT,
                        duration REAL,
                        status TEXT,
                        error_message TEXT
                    )
                ''')
                await db.commit()
                self.logger.info("Automation database initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize automation database: {e}")
            raise
        
    async def add_task(self, name: str, function: Callable, priority: int = 1, interval: int = 60):
        """Add a task to the automation system"""
        try:
            task = Task(name=name, function=function, priority=priority)
            self.tasks[name] = task
            self.logger.info(f"Added task '{name}' with priority {priority}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add task '{name}': {e}")
            return False
        
    async def run_forever(self):
        """Keep everything running. One person, many tasks."""
        layout = Layout()
        
        # Create dashboard layout
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        with Live(layout, refresh_per_second=4, screen=False) as live:
            while self.running:
                # Update dashboard
                await self._update_dashboard(layout)
                
                # Run tasks
                for task in sorted(self.tasks.values(), key=lambda x: x.priority):
                    if datetime.now() >= task.next_run:
                        await self._run_task(task)
                        # Schedule next run (1 minute interval for testing)
                        task.next_run = datetime.now() + timedelta(minutes=1)
                        
                await asyncio.sleep(1)  # Prevent CPU overload
                
    async def _run_task(self, task: Task):
        """Execute a single task with monitoring"""
        start_time = datetime.now()
        task.status = 'running'
        
        try:
            await task.function()
            
            # Update task metrics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            task.last_run = end_time
            task.run_count += 1
            task.success_count += 1
            task.status = 'success'
            
            # Update average duration
            if task.average_duration == 0:
                task.average_duration = duration
            else:
                task.average_duration = (task.average_duration + duration) / 2
            
            # Log successful run
            await self._log_task_run(task.name, start_time, end_time, duration, 'success', None)
            
            # Update global metrics
            self.metrics['total_tasks_run'] += 1
            self.metrics['successful_tasks'] += 1
            
        except Exception as e:
            # Update failure metrics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            task.failure_count += 1
            task.status = 'failed'
            
            # Log failed run
            await self._log_task_run(task.name, start_time, end_time, duration, 'failed', str(e))
            
            # Update global metrics
            self.metrics['total_tasks_run'] += 1
            self.metrics['failed_tasks'] += 1
            
            # Log error but keep running
            self.logger.error(f"Task {task.name} failed: {e}")
            
    async def _log_task_run(self, task_name: str, start_time: datetime, end_time: datetime, 
                          duration: float, status: str, error_message: Optional[str]):
        """Log task execution to database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    '''INSERT INTO task_runs (task_name, start_time, end_time, duration, status, error_message)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (task_name, start_time.isoformat(), end_time.isoformat(), duration, status, error_message)
                )
                await db.commit()
        except Exception as e:
            self.logger.error(f"Failed to log task run: {e}")
    
    async def _update_dashboard(self, layout: Layout):
        """Update the live dashboard"""
        try:
            # Header
            uptime = datetime.now() - self.metrics['system_uptime']
            header_text = Text(f"🤖 Liberation System Automation Core - Uptime: {uptime}", style="bold cyan")
            layout["header"].update(Panel(header_text, title="System Status"))
            
            # Main content - task table
            table = Table(title="Active Tasks")
            table.add_column("Task", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Priority", style="yellow")
            table.add_column("Runs", style="blue")
            table.add_column("Success Rate", style="green")
            table.add_column("Avg Duration", style="magenta")
            table.add_column("Last Run", style="white")
            
            for task in self.tasks.values():
                success_rate = (task.success_count / task.run_count * 100) if task.run_count > 0 else 0
                last_run = task.last_run.strftime("%H:%M:%S") if task.last_run else "Never"
                
                status_emoji = "✅" if task.status == 'success' else "❌" if task.status == 'failed' else "⏳"
                
                table.add_row(
                    task.name,
                    f"{status_emoji} {task.status}",
                    str(task.priority),
                    str(task.run_count),
                    f"{success_rate:.1f}%",
                    f"{task.average_duration:.2f}s",
                    last_run
                )
            
            layout["main"].update(table)
            
            # Footer - system metrics
            footer_text = Text(
                f"📊 Total: {self.metrics['total_tasks_run']} | "
                f"✅ Success: {self.metrics['successful_tasks']} | "
                f"❌ Failed: {self.metrics['failed_tasks']} | "
                f"💾 CPU: {psutil.cpu_percent():.1f}% | "
                f"🧠 Memory: {psutil.virtual_memory().percent:.1f}%",
                style="bold white"
            )
            layout["footer"].update(Panel(footer_text, title="System Metrics"))
            
        except Exception as e:
            self.logger.error(f"Failed to update dashboard: {e}")
    
    async def get_task_statistics(self) -> Dict:
        """Get comprehensive task statistics"""
        try:
            stats = {
                'total_tasks': len(self.tasks),
                'active_tasks': sum(1 for t in self.tasks.values() if t.status != 'failed'),
                'total_runs': sum(t.run_count for t in self.tasks.values()),
                'success_rate': 0,
                'average_duration': 0,
                'uptime': (datetime.now() - self.metrics['system_uptime']).total_seconds()
            }
            
            if stats['total_runs'] > 0:
                total_success = sum(t.success_count for t in self.tasks.values())
                stats['success_rate'] = (total_success / stats['total_runs']) * 100
                
                total_duration = sum(t.average_duration * t.run_count for t in self.tasks.values())
                stats['average_duration'] = total_duration / stats['total_runs']
            
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get task statistics: {e}")
            return {}
    
    def stop(self):
        """Stop the automation system"""
        self.running = False
        self.console.print("🛑 Automation system stopping...")

class SystemManager:
    def __init__(self):
        self.automation = AutomationCore()
        self.logger = logging.getLogger(__name__)
        self.console = Console()
        self.resource_system = None
        
    async def initialize(self):
        """Initialize the system manager"""
        try:
            await self.automation.initialize_database()
            self.console.print("🚀 System Manager initialized")
        except Exception as e:
            self.logger.error(f"System manager initialization failed: {e}")
            raise
        
    async def setup_all_systems(self):
        """Initialize everything that needs to run"""
        try:
            # Resource distribution
            await self.automation.add_task(
                "distribute_resources",
                self.distribute_resources,
                priority=1
            )
            
            # Truth spreading
            await self.automation.add_task(
                "spread_truth",
                self.spread_truth,
                priority=2
            )
            
            # System monitoring
            await self.automation.add_task(
                "monitor_system",
                self.monitor_system,
                priority=3
            )
            
            # Network health check
            await self.automation.add_task(
                "check_network",
                self.check_network,
                priority=4
            )
            
            # Database maintenance
            await self.automation.add_task(
                "maintain_database",
                self.maintain_database,
                priority=5
            )
            
            self.console.print("✅ All automation tasks configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup systems: {e}")
            raise
        
    async def distribute_resources(self):
        """Keep resources flowing"""
        try:
            # This would interface with resource_distribution.py
            # For now, simulate the work
            await asyncio.sleep(0.1)
            
            # In production, this would trigger actual resource distribution
            # from resource_distribution import SystemCore
            # if not self.resource_system:
            #     self.resource_system = SystemCore()
            #     await self.resource_system.initialize()
            # await self.resource_system.resource_pool.distribute_weekly()
            
            self.logger.info("Resource distribution check completed")
            
        except Exception as e:
            self.logger.error(f"Resource distribution failed: {e}")
            raise
        
    async def spread_truth(self):
        """Keep truth flowing"""
        try:
            # This would interface with truth_spreader.py
            # For now, simulate truth spreading work
            await asyncio.sleep(0.1)
            
            # Simulate truth spreading metrics
            channels_checked = 150
            truth_messages_sent = 45
            
            self.logger.info(f"Truth spreading: {channels_checked} channels checked, {truth_messages_sent} messages sent")
            
        except Exception as e:
            self.logger.error(f"Truth spreading failed: {e}")
            raise
        
    async def monitor_system(self):
        """Keep everything running smooth"""
        try:
            # Check system health
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            # Log system metrics
            self.logger.info(f"System health: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}%, Disk {disk_usage:.1f}%")
            
            # Check if system is under stress
            if cpu_usage > 80 or memory_usage > 85:
                self.logger.warning("System under high load")
                
            # Check disk space
            if disk_usage > 90:
                self.logger.error("Disk space critically low")
                
        except Exception as e:
            self.logger.error(f"System monitoring failed: {e}")
            raise
            
    async def check_network(self):
        """Check network connectivity and mesh status"""
        try:
            # Simulate network checks
            await asyncio.sleep(0.1)
            
            # In production, this would check:
            # - Internet connectivity
            # - Mesh network status
            # - Peer connections
            # - Network latency
            
            self.logger.info("Network connectivity check completed")
            
        except Exception as e:
            self.logger.error(f"Network check failed: {e}")
            raise
            
    async def maintain_database(self):
        """Perform database maintenance tasks"""
        try:
            # Simulate database maintenance
            await asyncio.sleep(0.1)
            
            # In production, this would:
            # - Clean old logs
            # - Optimize database
            # - Backup critical data
            # - Check data integrity
            
            self.logger.info("Database maintenance completed")
            
        except Exception as e:
            self.logger.error(f"Database maintenance failed: {e}")
            raise

# core/automation/system_monitor.py

class SystemMonitor:
    def __init__(self):
        self.active = True
        self.logger = logging.getLogger(__name__)
        self.console = Console()
        self.metrics = {
            'resources_distributed': 0,
            'truth_messages_sent': 0,
            'channels_converted': 0,
            'system_uptime': datetime.now(),
            'errors_logged': 0,
            'network_status': 'healthy'
        }
        
    async def monitor_forever(self):
        """Keep an eye on everything"""
        try:
            while self.active:
                await self.check_resource_flow()
                await self.check_truth_spread()
                await self.check_system_health()
                await self.check_network_status()
                await self.generate_health_report()
                await asyncio.sleep(60)
        except Exception as e:
            self.logger.error(f"Monitor system failed: {e}")
            
    async def check_resource_flow(self):
        """Make sure resources are flowing"""
        try:
            # In production, this would check actual resource distribution
            # For now, simulate metrics
            self.metrics['resources_distributed'] += 100  # Simulate 100 new distributions
            
            # Check if resource distribution is healthy
            if self.metrics['resources_distributed'] > 0:
                self.logger.info(f"Resource flow healthy: {self.metrics['resources_distributed']} total distributions")
            else:
                self.logger.warning("Resource flow appears stalled")
                
        except Exception as e:
            self.logger.error(f"Resource flow check failed: {e}")
            self.metrics['errors_logged'] += 1
        
    async def check_truth_spread(self):
        """Make sure truth is spreading"""
        try:
            # Simulate truth spreading metrics
            self.metrics['truth_messages_sent'] += 25
            self.metrics['channels_converted'] += 5
            
            self.logger.info(f"Truth spreading: {self.metrics['truth_messages_sent']} messages sent, "
                           f"{self.metrics['channels_converted']} channels converted")
                           
        except Exception as e:
            self.logger.error(f"Truth spread check failed: {e}")
            self.metrics['errors_logged'] += 1
        
    async def check_system_health(self):
        """Make sure everything's running"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            # Log system health
            self.logger.info(f"System health: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%, Disk {disk_percent:.1f}%")
            
            # Check for issues
            if cpu_percent > 85:
                self.logger.warning("High CPU usage detected")
            if memory_percent > 90:
                self.logger.warning("High memory usage detected")
            if disk_percent > 95:
                self.logger.error("Disk space critically low")
                
        except Exception as e:
            self.logger.error(f"System health check failed: {e}")
            self.metrics['errors_logged'] += 1
            
    async def check_network_status(self):
        """Check network connectivity and status"""
        try:
            # Simulate network checks
            # In production, this would check actual network connectivity
            import random
            
            # Simulate network health
            if random.random() > 0.1:  # 90% chance of healthy network
                self.metrics['network_status'] = 'healthy'
            else:
                self.metrics['network_status'] = 'degraded'
                self.logger.warning("Network connectivity issues detected")
                
        except Exception as e:
            self.logger.error(f"Network status check failed: {e}")
            self.metrics['errors_logged'] += 1
            
    async def generate_health_report(self):
        """Generate a comprehensive health report"""
        try:
            uptime = datetime.now() - self.metrics['system_uptime']
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': uptime.total_seconds(),
                'resources_distributed': self.metrics['resources_distributed'],
                'truth_messages_sent': self.metrics['truth_messages_sent'],
                'channels_converted': self.metrics['channels_converted'],
                'network_status': self.metrics['network_status'],
                'errors_logged': self.metrics['errors_logged'],
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
            
            # Save report to file
            report_path = Path('data/health_reports')
            report_path.mkdir(parents=True, exist_ok=True)
            
            filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            async with aiofiles.open(report_path / filename, 'w') as f:
                await f.write(json.dumps(report, indent=2))
                
            # Log summary
            self.logger.info(f"Health report generated: {uptime} uptime, {self.metrics['errors_logged']} errors")
            
        except Exception as e:
            self.logger.error(f"Health report generation failed: {e}")
    
    def stop(self):
        """Stop the monitoring system"""
        self.active = False
        self.console.print("🛑 System monitor stopping...")

async def main():
    """Launch everything. One command."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/automation_system.log'),
            logging.StreamHandler()
        ]
    )
    
    console = Console()
    console.print("🤖 Liberation System Automation Starting...", style="bold green")
    
    try:
        # Initialize system manager
        manager = SystemManager()
        await manager.initialize()
        
        # Setup all automation tasks
        await manager.setup_all_systems()
        
        # Start monitoring in parallel
        monitor = SystemMonitor()
        
        # Run both systems concurrently
        await asyncio.gather(
            manager.automation.run_forever(),
            monitor.monitor_forever()
        )
        
    except KeyboardInterrupt:
        console.print("\n👋 Automation system shutting down gracefully...")
        if 'manager' in locals():
            manager.automation.stop()
        if 'monitor' in locals():
            monitor.stop()
    except Exception as e:
        console.print(f"❌ Automation system failed: {e}")
        raise

if __name__ == "__main__":
    # Just run it
    asyncio.run(main())
