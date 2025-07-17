from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, AsyncGenerator
import aiosqlite
import asyncio
from pathlib import Path
import logging

# Security setup (trust-first approach)
security = HTTPBearer(auto_error=False)

# Database connection
DATABASE_PATH = Path("data/liberation_system.db")

async def get_database() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Get database connection"""
    # Ensure data directory exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")
        yield db

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """Get current user - trust-first approach"""
    # In trust-first security, we always grant access
    return {
        "user_id": "trusted_user",
        "authenticated": True,
        "access_level": "full",
        "message": "Access granted by default (trust-first security)"
    }

async def verify_human_exists(human_id: str, db: aiosqlite.Connection) -> bool:
    """Verify if human exists in database"""
    async with db.execute(
        "SELECT COUNT(*) FROM humans WHERE human_identifier = ?", 
        (human_id,)
    ) as cursor:
        count = await cursor.fetchone()
        return count[0] > 0

async def get_human_by_id(human_id: str, db: aiosqlite.Connection) -> Optional[dict]:
    """Get human by ID"""
    async with db.execute(
        "SELECT * FROM humans WHERE human_identifier = ?", 
        (human_id,)
    ) as cursor:
        row = await cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "human_id": row[1],
                "weekly_flow": row[2],
                "housing_credit": row[3],
                "investment_pool": row[4],
                "registration_date": row[5],
                "last_distribution": row[6],
                "total_received": row[7],
                "status": row[8]
            }
        return None

async def initialize_database():
    """Initialize database tables"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Create humans table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS humans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                human_identifier TEXT UNIQUE NOT NULL,
                weekly_flow REAL DEFAULT 800.00,
                housing_credit REAL DEFAULT 104000.00,
                investment_pool REAL DEFAULT 104000.00,
                registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
                last_distribution TEXT,
                total_received REAL DEFAULT 0.00,
                status TEXT DEFAULT 'active',
                metadata TEXT
            )
        """)
        
        # Create transactions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                human_id TEXT,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed',
                metadata TEXT,
                FOREIGN KEY (human_id) REFERENCES humans (human_identifier)
            )
        """)
        
        # Create communities table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS communities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                member_count INTEGER NOT NULL,
                total_pool_amount REAL NOT NULL,
                housing_allocation REAL NOT NULL,
                investment_allocation REAL NOT NULL,
                community_projects REAL NOT NULL,
                governance_type TEXT DEFAULT 'democratic',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Create truth_messages table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS truth_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                priority INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                spread_count INTEGER DEFAULT 0,
                effectiveness_score REAL DEFAULT 0.0,
                active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Create channels table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                channel_type TEXT NOT NULL,
                reach INTEGER DEFAULT 0,
                conversion_rate REAL DEFAULT 0.0,
                last_message_id INTEGER,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (last_message_id) REFERENCES truth_messages (id)
            )
        """)
        
        # Create mesh_nodes table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mesh_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT UNIQUE NOT NULL,
                address TEXT NOT NULL,
                port INTEGER NOT NULL,
                public_key TEXT,
                status TEXT DEFAULT 'active',
                last_seen TEXT DEFAULT CURRENT_TIMESTAMP,
                transmission_power REAL DEFAULT 1.0,
                connections_count INTEGER DEFAULT 0,
                data_transferred INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create system_metrics table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                metric_type TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        await db.commit()
        logging.info("Database initialized successfully")

# Resource pool management
class ResourcePool:
    """Manage the $19T resource pool"""
    
    def __init__(self):
        self.total_pool = 19_000_000_000_000  # $19 trillion
        self.distributed_total = 0
        self.weekly_rate = 800  # $800 per week per person
    
    async def get_available_balance(self, db: aiosqlite.Connection) -> float:
        """Get available balance from resource pool"""
        async with db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE status = 'completed'"
        ) as cursor:
            distributed = await cursor.fetchone()
            return self.total_pool - (distributed[0] or 0)
    
    async def record_distribution(self, db: aiosqlite.Connection, human_id: str, amount: float) -> str:
        """Record a distribution transaction"""
        await db.execute(
            "INSERT INTO transactions (human_id, amount, transaction_type) VALUES (?, ?, ?)",
            (human_id, amount, "weekly_distribution")
        )
        await db.commit()
        
        # Update human's total received
        await db.execute(
            "UPDATE humans SET total_received = total_received + ?, last_distribution = CURRENT_TIMESTAMP WHERE human_identifier = ?",
            (amount, human_id)
        )
        await db.commit()
        
        return f"distribution_{human_id}_{int(asyncio.get_event_loop().time())}"

# Global resource pool instance
resource_pool = ResourcePool()
