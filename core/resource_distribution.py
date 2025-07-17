# core/resource_distribution.py

import asyncio
import logging
import aiofiles
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

# Import the new database abstraction layer
from core.database import get_database_manager, DatabaseManager

@dataclass
class Human:
    id: str
    weekly_flow: Decimal = Decimal('800.00')
    housing_credit: Decimal = Decimal('104000.00')
    investment_pool: Decimal = Decimal('104000.00')
    created_at: datetime = None
    last_distribution: datetime = None
    total_received: Decimal = Decimal('0.00')
    status: str = 'active'
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        # No verification needed - trust by default
        # No complex rules - just direct flow
        logging.info(f"Human {self.id} initialized with trust-based access")

class ResourcePool:
    def __init__(self, total_wealth: Decimal = Decimal('19000000000000.00')):
        self.total_wealth = total_wealth
        self.humans: Dict[str, Human] = {}
        self.db_path = Path('data/liberation_system.db')
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.distributed_this_week = Decimal('0.00')
        self.total_distributed = Decimal('0.00')
        
    async def initialize_database(self):
        """Initialize SQLite database for persistence"""
        try:
            # Create data directory if it doesn't exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS humans (
                        id TEXT PRIMARY KEY,
                        weekly_flow REAL,
                        housing_credit REAL,
                        investment_pool REAL,
                        created_at TEXT,
                        last_distribution TEXT,
                        total_received REAL,
                        status TEXT
                    )
                ''')
                
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        human_id TEXT,
                        amount REAL,
                        transaction_type TEXT,
                        timestamp TEXT,
                        status TEXT
                    )
                ''')
                
                await db.commit()
                self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
            
    async def distribute_weekly(self):
        """Just give people what they need. No questions."""
        self.distributed_this_week = Decimal('0.00')
        
        with Progress() as progress:
            task = progress.add_task("Distributing resources...", total=len(self.humans))
            
            for human in self.humans.values():
                try:
                    # Direct transfer, no bureaucracy
                    success = await self._transfer(human.weekly_flow, human.id)
                    if success:
                        human.last_distribution = datetime.now()
                        human.total_received += human.weekly_flow
                        self.distributed_this_week += human.weekly_flow
                        await self._save_human(human)
                        
                except Exception as e:
                    self.logger.error(f"Failed to distribute to {human.id}: {e}")
                    # Keep going - trust by default means we don't stop for errors
                    
                progress.advance(task)
                    
        self.total_distributed += self.distributed_this_week
        self.console.print(f"✅ Weekly distribution complete: ${self.distributed_this_week:,.2f}")
        
    async def _transfer(self, amount: Decimal, recipient_id: str) -> bool:
        """Transfer resources with basic logging"""
        try:
            # In real system, this would interface with actual transfer mechanism
            # But zero verification - trust by default
            
            # Log the transaction
            await self._log_transaction(recipient_id, amount, "weekly_distribution", "completed")
            
            # Simulate transfer delay
            await asyncio.sleep(0.1)
            
            self.logger.info(f"Transferred ${amount} to {recipient_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Transfer failed for {recipient_id}: {e}")
            await self._log_transaction(recipient_id, amount, "weekly_distribution", "failed")
            return False
    
    async def _log_transaction(self, human_id: str, amount: Decimal, tx_type: str, status: str):
        """Log transaction to database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT INTO transactions (human_id, amount, transaction_type, timestamp, status) VALUES (?, ?, ?, ?, ?)',
                    (human_id, float(amount), tx_type, datetime.now().isoformat(), status)
                )
                await db.commit()
        except Exception as e:
            self.logger.error(f"Failed to log transaction: {e}")
    
    async def _save_human(self, human: Human):
        """Save human data to database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    '''INSERT OR REPLACE INTO humans 
                       (id, weekly_flow, housing_credit, investment_pool, created_at, last_distribution, total_received, status) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (human.id, float(human.weekly_flow), float(human.housing_credit), 
                     float(human.investment_pool), human.created_at.isoformat(), 
                     human.last_distribution.isoformat() if human.last_distribution else None,
                     float(human.total_received), human.status)
                )
                await db.commit()
        except Exception as e:
            self.logger.error(f"Failed to save human {human.id}: {e}")
    
    async def add_human(self, human_id: str) -> bool:
        """Everyone gets resources. No applications needed."""
        try:
            if human_id not in self.humans:
                human = Human(id=human_id)
                self.humans[human_id] = human
                await self._save_human(human)
                self.console.print(f"✅ Added human {human_id} to resource pool")
                return True
            else:
                self.console.print(f"ℹ️  Human {human_id} already exists")
                return False
        except Exception as e:
            self.logger.error(f"Failed to add human {human_id}: {e}")
            return False
    
    async def load_humans_from_db(self):
        """Load existing humans from database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('SELECT * FROM humans') as cursor:
                    async for row in cursor:
                        human = Human(
                            id=row[0],
                            weekly_flow=Decimal(str(row[1])),
                            housing_credit=Decimal(str(row[2])),
                            investment_pool=Decimal(str(row[3])),
                            created_at=datetime.fromisoformat(row[4]),
                            last_distribution=datetime.fromisoformat(row[5]) if row[5] else None,
                            total_received=Decimal(str(row[6])),
                            status=row[7]
                        )
                        self.humans[human.id] = human
                        
            self.console.print(f"✅ Loaded {len(self.humans)} humans from database")
        except Exception as e:
            self.logger.error(f"Failed to load humans from database: {e}")
    
    async def get_statistics(self) -> Dict:
        """Get current system statistics"""
        try:
            total_humans = len(self.humans)
            active_humans = sum(1 for h in self.humans.values() if h.status == 'active')
            
            return {
                'total_humans': total_humans,
                'active_humans': active_humans,
                'total_distributed': float(self.total_distributed),
                'distributed_this_week': float(self.distributed_this_week),
                'remaining_wealth': float(self.total_wealth - self.total_distributed),
                'average_per_human': float(self.total_distributed / total_humans) if total_humans > 0 else 0
            }
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def display_dashboard(self):
        """Display resource distribution dashboard"""
        try:
            table = Table(title="Resource Distribution Dashboard")
            
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            stats = asyncio.run(self.get_statistics())
            
            table.add_row("Total Humans", str(stats.get('total_humans', 0)))
            table.add_row("Active Humans", str(stats.get('active_humans', 0)))
            table.add_row("Total Distributed", f"${stats.get('total_distributed', 0):,.2f}")
            table.add_row("This Week", f"${stats.get('distributed_this_week', 0):,.2f}")
            table.add_row("Remaining Wealth", f"${stats.get('remaining_wealth', 0):,.2f}")
            table.add_row("Average per Human", f"${stats.get('average_per_human', 0):,.2f}")
            
            self.console.print(table)
        except Exception as e:
            self.logger.error(f"Failed to display dashboard: {e}")

class SystemCore:
    def __init__(self):
        self.resource_pool = ResourcePool()
        self.running = True
        self.logger = logging.getLogger(__name__)
        self.console = Console()
        
    async def initialize(self):
        """Initialize the system"""
        try:
            await self.resource_pool.initialize_database()
            await self.resource_pool.load_humans_from_db()
            self.console.print("🚀 Liberation System initialized successfully")
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            raise
        
    async def run_forever(self):
        """Keep the resources flowing. No interruptions."""
        try:
            while self.running:
                self.console.print("📡 Starting weekly distribution cycle...")
                await self.resource_pool.distribute_weekly()
                
                # Display dashboard
                self.resource_pool.display_dashboard()
                
                if self.running:  # Check if we should continue
                    self.console.print("⏳ Waiting for next weekly cycle...")
                    # In development, use shorter intervals for testing
                    await asyncio.sleep(60)  # 1 minute for testing
                    # await asyncio.sleep(7 * 24 * 60 * 60)  # Week in seconds for production
                    
        except KeyboardInterrupt:
            self.console.print("\n⚠️  Shutdown requested by user")
            self.stop()
        except Exception as e:
            self.logger.error(f"System error: {e}")
            self.console.print(f"❌ System error: {e}")
            raise
            
    async def add_all_humans(self, population_file: str):
        """Add everyone. No questions asked."""
        try:
            # Read from population file if it exists
            population_path = Path(population_file)
            if population_path.exists():
                async with aiofiles.open(population_path, 'r') as f:
                    content = await f.read()
                    population_data = json.loads(content)
                    
                    for human_data in population_data:
                        if isinstance(human_data, dict):
                            human_id = human_data.get('id')
                        else:
                            human_id = str(human_data)
                            
                        if human_id:
                            await self.resource_pool.add_human(human_id)
                            
                self.console.print(f"✅ Added {len(population_data)} humans from {population_file}")
            else:
                # Create sample population for testing
                sample_humans = [f"human_{i:06d}" for i in range(1, 101)]  # 100 test humans
                
                for human_id in sample_humans:
                    await self.resource_pool.add_human(human_id)
                    
                # Save sample data to file
                await self._save_population_file(population_file, sample_humans)
                self.console.print(f"✅ Created sample population of {len(sample_humans)} humans")
                
        except Exception as e:
            self.logger.error(f"Failed to add humans from {population_file}: {e}")
            # Continue anyway - trust by default
            
    async def _save_population_file(self, filename: str, population: List[str]):
        """Save population data to file"""
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(filename, 'w') as f:
                await f.write(json.dumps(population, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save population file: {e}")
    
    async def add_human(self, human_id: str) -> bool:
        """Add a single human to the system"""
        return await self.resource_pool.add_human(human_id)
    
    async def get_system_stats(self) -> Dict:
        """Get current system statistics"""
        return await self.resource_pool.get_statistics()
    
    def stop(self):
        """Emergency stop if needed. But why would we stop giving people what they need?"""
        self.running = False
        self.console.print("🛑 System shutdown initiated")

async def main():
    """Launch the whole thing. One command, no BS."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/liberation_system.log'),
            logging.StreamHandler()
        ]
    )
    
    console = Console()
    console.print("🌟 Liberation System Starting...", style="bold cyan")
    
    try:
        system = SystemCore()
        await system.initialize()
        
        # Add population
        await system.add_all_humans('data/population.json')
        
        # Start the system
        await system.run_forever()
        
    except KeyboardInterrupt:
        console.print("\n👋 Liberation System shutting down gracefully...")
    except Exception as e:
        console.print(f"❌ System failed to start: {e}")
        raise

if __name__ == "__main__":
    # Just run it. No complex setup.
    asyncio.run(main())
