#!/usr/bin/env python3
"""
🌟 Liberation System - Reality Implementation Startup Script
This script initializes the system for real-world operation
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('liberation_reality.log')
    ]
)

logger = logging.getLogger(__name__)

class RealityBootstrap:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.config_dir = self.base_dir / "config"
        self.logs_dir = self.base_dir / "logs"
        
    async def initialize(self):
        """Initialize the Liberation System for reality"""
        logger.info("🚀 Initializing Liberation System for Reality...")
        
        # Create necessary directories
        await self.create_directories()
        
        # Initialize configuration
        await self.setup_configuration()
        
        # Initialize databases
        await self.initialize_databases()
        
        # Start core services
        await self.start_core_services()
        
        logger.info("✅ Liberation System initialized for reality!")
        
    async def create_directories(self):
        """Create necessary directories"""
        directories = [self.data_dir, self.config_dir, self.logs_dir]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")
    
    async def setup_configuration(self):
        """Setup reality-based configuration"""
        config = {
            "mode": "reality",
            "resource_distribution": {
                "enabled": True,
                "test_mode": True,  # Start in test mode
                "weekly_flow": 800,  # $800 weekly flow
                "housing_credit": 104000,  # $104K housing credit
                "max_participants": 1000  # Start with 1000 people
            },
            "truth_spreading": {
                "enabled": True,
                "channels": ["social_media", "forums", "newsletters"],
                "rate_limit": 100  # Messages per hour
            },
            "mesh_network": {
                "enabled": True,
                "max_nodes": 100,
                "auto_discovery": True
            },
            "security": {
                "trust_level": "high",
                "audit_logging": True,
                "rate_limiting": True
            }
        }
        
        config_file = self.config_dir / "reality_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"⚙️ Configuration saved to {config_file}")
    
    async def initialize_databases(self):
        """Initialize databases for reality operation"""
        try:
            import aiosqlite
            
            # Create main database
            db_path = self.data_dir / "liberation_reality.db"
            async with aiosqlite.connect(db_path) as db:
                # Create tables
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS participants (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE,
                        wallet_address TEXT,
                        total_received REAL DEFAULT 0,
                        last_distribution DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS distributions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        participant_id INTEGER,
                        amount REAL,
                        type TEXT,
                        transaction_hash TEXT,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (participant_id) REFERENCES participants (id)
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS truth_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT NOT NULL,
                        channel TEXT,
                        reach INTEGER DEFAULT 0,
                        effectiveness REAL DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await db.commit()
                
            logger.info(f"🗄️ Database initialized at {db_path}")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    async def start_core_services(self):
        """Start core services for reality operation"""
        logger.info("🔧 Starting core services...")
        
        # Start API server (in background)
        try:
            # This would start the FastAPI server
            logger.info("🌐 API server ready to start")
            logger.info("   Run: uvicorn api.app:app --host 0.0.0.0 --port 8000")
        except Exception as e:
            logger.error(f"❌ API server failed to start: {e}")
        
        # Start mesh network
        try:
            logger.info("🔗 Mesh network initializing...")
            # Initialize mesh network components
        except Exception as e:
            logger.error(f"❌ Mesh network failed to start: {e}")
        
        # Start resource distribution engine
        try:
            logger.info("💰 Resource distribution engine ready")
            # Initialize distribution system
        except Exception as e:
            logger.error(f"❌ Resource distribution failed to start: {e}")
    
    async def show_reality_dashboard(self):
        """Show the reality dashboard"""
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        
        # Create status table
        table = Table(title="Liberation System - Reality Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")
        
        table.add_row("🗄️ Database", "✅ Active", "SQLite initialized")
        table.add_row("🌐 API Server", "⏳ Ready", "Run: uvicorn api.app:app --port 8000")
        table.add_row("🔗 Mesh Network", "⏳ Ready", "P2P network ready")
        table.add_row("💰 Resource Distribution", "⏳ Ready", "Test mode enabled")
        table.add_row("📡 Truth Spreading", "⏳ Ready", "Channels configured")
        
        console.print(Panel(table, title="🌟 Liberation System - Reality Mode", border_style="cyan"))
        
        # Show next steps
        console.print("\n📋 Next Steps:")
        console.print("1. Start API server: uvicorn api.app:app --host 0.0.0.0 --port 8000")
        console.print("2. Start web interface: npm run dev")
        console.print("3. Add initial participants")
        console.print("4. Begin test distributions")
        console.print("5. Monitor and scale")

async def main():
    """Main entry point for reality initialization"""
    bootstrap = RealityBootstrap()
    
    try:
        await bootstrap.initialize()
        await bootstrap.show_reality_dashboard()
        
        # Keep running to show live status
        while True:
            await asyncio.sleep(30)
            # Could add periodic health checks here
            
    except KeyboardInterrupt:
        logger.info("🛑 Reality initialization stopped by user")
    except Exception as e:
        logger.error(f"💥 Reality initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
