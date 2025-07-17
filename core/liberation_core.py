# core/liberation_core.py

import asyncio
import logging
import signal
import sys
from dataclasses import dataclass
from typing import List, Dict, Callable, Optional
from datetime import datetime
from pathlib import Path

# Import our core components
try:
    from core.config import get_config, ConfigManager
    from core.resource_distribution import SystemCore as ResourceSystem
    from transformation.truth_spreader import TruthSystem
    from security.trust_default import AntiSecurity
except ImportError as e:
    print(f"Warning: Could not import all modules: {e}")
    # We'll handle missing modules gracefully
    
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live

@dataclass
class SystemTask:
    """Enhanced task with better tracking"""
    name: str
    function: Callable
    priority: int = 1
    last_run: Optional[datetime] = None
    run_count: int = 0
    error_count: int = 0
    status: str = "ready"  # ready, running, completed, failed
    
class LiberationCore:
    """Core automation system - the heart of liberation"""
    
    def __init__(self):
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.tasks: Dict[str, SystemTask] = {}
        self.running = True
        self.start_time = datetime.now()
        
        # Initialize subsystems
        self.resource_system: Optional[ResourceSystem] = None
        self.truth_system: Optional[TruthSystem] = None
        self.security_system: Optional[AntiSecurity] = None
        
        # System metrics
        self.metrics = {
            'uptime': 0,
            'tasks_completed': 0,
            'errors_handled': 0,
            'resources_distributed': 0,
            'truth_messages_sent': 0,
            'mesh_nodes_active': 0
        }
        
    async def initialize_all_systems(self):
        """Initialize all subsystems"""
        try:
            self.console.print("[cyan]🚀 Initializing Liberation Systems...[/cyan]")
            
            # Initialize resource distribution
            try:
                self.resource_system = ResourceSystem()
                await self.resource_system.initialize()
                self.console.print("[green]✅ Resource Distribution System initialized[/green]")
            except Exception as e:
                self.logger.error(f"Resource system initialization failed: {e}")
                self.console.print(f"[yellow]⚠️  Resource system unavailable: {e}[/yellow]")
            
            # Initialize truth spreading
            try:
                self.truth_system = TruthSystem()
                await self.truth_system.initialize()
                self.console.print("[green]✅ Truth Spreading System initialized[/green]")
            except Exception as e:
                self.logger.error(f"Truth system initialization failed: {e}")
                self.console.print(f"[yellow]⚠️  Truth system unavailable: {e}[/yellow]")
            
            # Initialize security (trust-based)
            try:
                self.security_system = AntiSecurity()
                self.console.print("[green]✅ Trust-Based Security initialized[/green]")
            except Exception as e:
                self.logger.error(f"Security system initialization failed: {e}")
                self.console.print(f"[yellow]⚠️  Security system unavailable: {e}[/yellow]")
            
            self.console.print("[bold green]🌟 Core systems initialized![/bold green]")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize systems: {e}")
            self.console.print(f"[red]❌ System initialization failed: {e}[/red]")
            # Don't raise - continue with available systems
    
    async def add_task(self, name: str, function: Callable, priority: int = 1):
        """Add a task to the automation system"""
        self.tasks[name] = SystemTask(name=name, function=function, priority=priority)
        self.logger.info(f"Added task: {name} (priority: {priority})")
        
    async def setup_core_tasks(self):
        """Setup the core system tasks"""
        await self.add_task("distribute_resources", self.distribute_resources, priority=1)
        await self.add_task("spread_truth", self.spread_truth, priority=2)
        await self.add_task("monitor_system", self.monitor_system_health, priority=3)
        await self.add_task("update_metrics", self.update_metrics, priority=4)
        
    async def distribute_resources(self):
        """Keep resources flowing to everyone"""
        try:
            if self.resource_system:
                # Add some sample humans if none exist
                if len(self.resource_system.resource_pool.humans) == 0:
                    await self.resource_system.add_all_humans('data/population.json')
                
                # Distribute resources
                await self.resource_system.resource_pool.distribute_weekly()
                
                # Update metrics
                stats = await self.resource_system.get_system_stats()
                self.metrics['resources_distributed'] = stats.get('total_distributed', 0)
            else:
                self.logger.warning("Resource system not available")
                
        except Exception as e:
            self.logger.error(f"Resource distribution failed: {e}")
            self.metrics['errors_handled'] += 1
            
    async def spread_truth(self):
        """Keep truth flowing across all channels"""
        try:
            if self.truth_system:
                await self.truth_system.spreader.spread_truth()
                
                # Update metrics
                stats = await self.truth_system.spreader.get_spread_statistics()
                self.metrics['truth_messages_sent'] = stats.get('total_spread_count', 0)
            else:
                self.logger.warning("Truth system not available")
                
        except Exception as e:
            self.logger.error(f"Truth spreading failed: {e}")
            self.metrics['errors_handled'] += 1
            
    async def monitor_system_health(self):
        """Monitor overall system health"""
        try:
            # Check all subsystems
            health_checks = {
                'resource_system': self.resource_system is not None,
                'truth_system': self.truth_system is not None,
                'security_system': self.security_system is not None
            }
            
            # Log health status
            healthy_systems = sum(health_checks.values())
            total_systems = len(health_checks)
            
            if healthy_systems == total_systems:
                self.logger.info("All systems healthy")
            else:
                self.logger.warning(f"System health: {healthy_systems}/{total_systems} systems healthy")
                
        except Exception as e:
            self.logger.error(f"Health monitoring failed: {e}")
            self.metrics['errors_handled'] += 1
            
    async def update_metrics(self):
        """Update system metrics"""
        try:
            uptime = (datetime.now() - self.start_time).total_seconds()
            self.metrics['uptime'] = uptime
            self.metrics['tasks_completed'] = sum(task.run_count for task in self.tasks.values())
            
        except Exception as e:
            self.logger.error(f"Metrics update failed: {e}")
            
    async def run_forever(self):
        """Keep everything running. One person, massive impact."""
        self.console.print("[bold cyan]🌟 Liberation System is now running![/bold cyan]")
        
        try:
            while self.running:
                # Execute tasks in priority order
                sorted_tasks = sorted(self.tasks.values(), key=lambda x: x.priority)
                
                for task in sorted_tasks:
                    if not self.running:
                        break
                        
                    try:
                        task.status = "running"
                        await task.function()
                        task.last_run = datetime.now()
                        task.run_count += 1
                        task.status = "completed"
                        
                    except Exception as e:
                        task.error_count += 1
                        task.status = "failed"
                        self.logger.error(f"Task {task.name} failed: {e}")
                        # Keep running - liberation doesn't stop for errors
                        
                # Display status every few cycles
                if self.metrics['tasks_completed'] % 10 == 0:
                    self.display_status()
                        
                # Brief pause to prevent CPU overload
                await asyncio.sleep(60)  # 1 minute cycle
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]⚠️  Shutdown requested by user[/yellow]")
            await self.shutdown()
        except Exception as e:
            self.logger.error(f"Core system error: {e}")
            self.console.print(f"[red]❌ Core system error: {e}[/red]")
            await self.shutdown()
            
    async def shutdown(self):
        """Gracefully shutdown all systems"""
        self.running = False
        self.console.print("[yellow]🛑 Shutting down Liberation System...[/yellow]")
        
        # Shutdown subsystems
        if self.resource_system:
            self.resource_system.stop()
        if self.truth_system:
            self.truth_system.stop()
            
        self.console.print("[green]✅ Liberation System shutdown complete[/green]")
        
    def display_status(self):
        """Display current system status"""
        try:
            # Create status table
            table = Table(title="Liberation System Status", style="cyan")
            table.add_column("Component", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Details", style="magenta")
            
            # Add system components
            table.add_row("Resource Distribution", "🟢 Active", f"${self.metrics['resources_distributed']:,.2f} distributed")
            table.add_row("Truth Spreading", "🟢 Active", f"{self.metrics['truth_messages_sent']} messages sent")
            table.add_row("Security", "🟢 Trusted", "No barriers, maximum access")
            
            # Add metrics
            uptime_str = f"{self.metrics['uptime']:.0f}s"
            table.add_row("Uptime", "🟢 Running", uptime_str)
            table.add_row("Tasks Completed", "🟢 Processing", str(self.metrics['tasks_completed']))
            table.add_row("Errors Handled", "🟡 Resilient", str(self.metrics['errors_handled']))
            
            self.console.print(table)
            
        except Exception as e:
            self.logger.error(f"Status display failed: {e}")

class LiberationSystemManager:
    """Main system manager - orchestrates everything"""
    
    def __init__(self):
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.core = LiberationCore()
        
    async def launch_liberation_system(self):
        """Launch the complete liberation system"""
        try:
            # Display startup banner
            self.display_startup_banner()
            
            # Initialize all systems
            await self.core.initialize_all_systems()
            
            # Setup core tasks
            await self.core.setup_core_tasks()
            
            # Setup signal handlers for graceful shutdown
            self.setup_signal_handlers()
            
            # Display system status
            self.core.display_status()
            
            # Run the system forever
            await self.core.run_forever()
            
        except Exception as e:
            self.logger.error(f"Failed to launch liberation system: {e}")
            self.console.print(f"[red]❌ Liberation system launch failed: {e}[/red]")
            raise
            
    def display_startup_banner(self):
        """Display the liberation system startup banner"""
        banner = Panel.fit(
            "[bold cyan]🌟 LIBERATION SYSTEM 🌟[/bold cyan]\n\n"
            "[green]One person, massive impact.[/green]\n\n"
            "[yellow]• Trust by default\n"
            "• Resources for everyone\n"
            "• Truth over marketing\n"
            "• Direct action, no BS[/yellow]\n\n"
            "[magenta]Ready to transform everything.[/magenta]",
            style="cyan"
        )
        self.console.print(banner)
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.console.print("\n[yellow]⚠️  Received shutdown signal[/yellow]")
            asyncio.create_task(self.core.shutdown())
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point - launch everything with one command"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/liberation_system.log'),
            logging.StreamHandler()
        ]
    )
    
    # Ensure directories exist
    Path('logs').mkdir(exist_ok=True)
    Path('data').mkdir(exist_ok=True)
    Path('config').mkdir(exist_ok=True)
    
    # Launch the liberation system
    manager = LiberationSystemManager()
    await manager.launch_liberation_system()

if __name__ == "__main__":
    # Just run it. Liberation starts here.
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Liberation system stopped by user.")
    except Exception as e:
        print(f"❌ Liberation system failed: {e}")
        sys.exit(1)
