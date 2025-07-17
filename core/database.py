# core/database.py

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass, asdict
from pathlib import Path
import json

import aiosqlite
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from rich.console import Console
from rich.progress import Progress


@dataclass
class DatabaseConfig:
    """Database configuration"""
    # PostgreSQL settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "liberation_user"
    postgres_password: str = "liberation_password"
    postgres_database: str = "liberation_system"
    
    # SQLite settings
    sqlite_path: str = "data/liberation_system.db"
    
    # General settings
    database_type: str = "postgresql"  # postgresql or sqlite
    connection_pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # Performance settings
    enable_query_logging: bool = False
    query_timeout: int = 30
    
    def get_postgres_url(self, async_driver: bool = True) -> str:
        """Get PostgreSQL connection URL"""
        driver = "asyncpg" if async_driver else "psycopg2"
        return f"postgresql+{driver}://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
    
    def get_sqlite_url(self, async_driver: bool = True) -> str:
        """Get SQLite connection URL"""
        driver = "aiosqlite" if async_driver else "sqlite"
        return f"sqlite+{driver}:///{self.sqlite_path}"


class DatabaseInterface(ABC):
    """Abstract database interface"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize database connection and create tables"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Optional[Tuple] = None) -> Any:
        """Execute a query and return results"""
        pass
    
    @abstractmethod
    async def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute multiple queries with parameter sets"""
        pass
    
    @abstractmethod
    async def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict]:
        """Fetch one row"""
        pass
    
    @abstractmethod
    async def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        """Fetch all rows"""
        pass
    
    @abstractmethod
    async def create_tables(self) -> None:
        """Create database tables"""
        pass


class PostgreSQLDatabase(DatabaseInterface):
    """PostgreSQL database implementation with enterprise features"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize PostgreSQL connection pool"""
        try:
            self.console.print("[cyan]🐘 Initializing PostgreSQL connection...[/cyan]")
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                host=self.config.postgres_host,
                port=self.config.postgres_port,
                user=self.config.postgres_user,
                password=self.config.postgres_password,
                database=self.config.postgres_database,
                min_size=1,
                max_size=self.config.connection_pool_size,
                command_timeout=self.config.query_timeout,
                server_settings={
                    'application_name': 'liberation_system',
                    'timezone': 'UTC'
                }
            )
            
            # Test connection
            async with self.pool.acquire() as conn:
                await conn.execute('SELECT 1')
                
            await self.create_tables()
            self.console.print("[green]✅ PostgreSQL initialized successfully[/green]")
            
        except Exception as e:
            self.logger.error(f"PostgreSQL initialization failed: {e}")
            self.console.print(f"[red]❌ PostgreSQL initialization failed: {e}[/red]")
            raise
    
    async def close(self) -> None:
        """Close PostgreSQL connection pool"""
        if self.pool:
            await self.pool.close()
            self.console.print("[yellow]🔒 PostgreSQL connection pool closed[/yellow]")
    
    async def execute_query(self, query: str, params: Optional[Tuple] = None) -> Any:
        """Execute a query and return results"""
        if not self.pool:
            raise RuntimeError("Database not initialized")
            
        async with self.pool.acquire() as conn:
            if params:
                return await conn.execute(query, *params)
            else:
                return await conn.execute(query)
    
    async def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute multiple queries with parameter sets"""
        if not self.pool:
            raise RuntimeError("Database not initialized")
            
        async with self.pool.acquire() as conn:
            await conn.executemany(query, params_list)
    
    async def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict]:
        """Fetch one row"""
        if not self.pool:
            raise RuntimeError("Database not initialized")
            
        async with self.pool.acquire() as conn:
            if params:
                row = await conn.fetchrow(query, *params)
            else:
                row = await conn.fetchrow(query)
            
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        """Fetch all rows"""
        if not self.pool:
            raise RuntimeError("Database not initialized")
            
        async with self.pool.acquire() as conn:
            if params:
                rows = await conn.fetch(query, *params)
            else:
                rows = await conn.fetch(query)
            
            return [dict(row) for row in rows]
    
    async def create_tables(self) -> None:
        """Create PostgreSQL tables with enterprise features"""
        if not self.pool:
            raise RuntimeError("Database not initialized")
            
        async with self.pool.acquire() as conn:
            # Create humans table with advanced features
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS humans (
                    id TEXT PRIMARY KEY,
                    weekly_flow DECIMAL(15,2) NOT NULL DEFAULT 800.00,
                    housing_credit DECIMAL(15,2) NOT NULL DEFAULT 104000.00,
                    investment_pool DECIMAL(15,2) NOT NULL DEFAULT 104000.00,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_distribution TIMESTAMP WITH TIME ZONE,
                    total_received DECIMAL(15,2) DEFAULT 0.00,
                    status TEXT DEFAULT 'active',
                    metadata JSONB DEFAULT '{}',
                    version INTEGER DEFAULT 1,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create transactions table with partitioning support
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id BIGSERIAL PRIMARY KEY,
                    human_id TEXT NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    transaction_type TEXT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    metadata JSONB DEFAULT '{}',
                    hash TEXT,
                    block_number BIGINT,
                    gas_used BIGINT,
                    FOREIGN KEY (human_id) REFERENCES humans(id) ON DELETE CASCADE
                )
            ''')
            
            # Create system_stats table for performance monitoring
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id BIGSERIAL PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    metric_value DECIMAL(15,2),
                    metadata JSONB DEFAULT '{}',
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_humans_status ON humans(status)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_humans_created_at ON humans(created_at)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_transactions_human_id ON transactions(human_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_system_stats_name ON system_stats(metric_name)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_system_stats_timestamp ON system_stats(timestamp)')
            
            # Create functions for automatic updates
            await conn.execute('''
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql'
            ''')
            
            # Create triggers
            await conn.execute('''
                DROP TRIGGER IF EXISTS update_humans_updated_at ON humans;
                CREATE TRIGGER update_humans_updated_at
                    BEFORE UPDATE ON humans
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column()
            ''')
            
            self.logger.info("PostgreSQL tables created successfully")


class SQLiteDatabase(DatabaseInterface):
    """SQLite database implementation for development/testing"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.db_path = Path(config.sqlite_path)
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize SQLite database"""
        try:
            self.console.print("[cyan]📄 Initializing SQLite database...[/cyan]")
            
            # Create data directory if it doesn't exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            await self.create_tables()
            self.console.print("[green]✅ SQLite initialized successfully[/green]")
            
        except Exception as e:
            self.logger.error(f"SQLite initialization failed: {e}")
            self.console.print(f"[red]❌ SQLite initialization failed: {e}[/red]")
            raise
    
    async def close(self) -> None:
        """Close SQLite connection"""
        self.console.print("[yellow]🔒 SQLite connection closed[/yellow]")
    
    async def execute_query(self, query: str, params: Optional[Tuple] = None) -> Any:
        """Execute a query and return results"""
        async with aiosqlite.connect(self.db_path) as db:
            if params:
                return await db.execute(query, params)
            else:
                return await db.execute(query)
    
    async def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute multiple queries with parameter sets"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.executemany(query, params_list)
            await db.commit()
    
    async def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict]:
        """Fetch one row"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        """Fetch all rows"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def create_tables(self) -> None:
        """Create SQLite tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Create humans table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS humans (
                    id TEXT PRIMARY KEY,
                    weekly_flow REAL NOT NULL DEFAULT 800.00,
                    housing_credit REAL NOT NULL DEFAULT 104000.00,
                    investment_pool REAL NOT NULL DEFAULT 104000.00,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_distribution TEXT,
                    total_received REAL DEFAULT 0.00,
                    status TEXT DEFAULT 'active',
                    metadata TEXT DEFAULT '{}',
                    version INTEGER DEFAULT 1,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create transactions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    human_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    metadata TEXT DEFAULT '{}',
                    hash TEXT,
                    block_number INTEGER,
                    gas_used INTEGER,
                    FOREIGN KEY (human_id) REFERENCES humans(id) ON DELETE CASCADE
                )
            ''')
            
            # Create system_stats table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metadata TEXT DEFAULT '{}',
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            await db.execute('CREATE INDEX IF NOT EXISTS idx_humans_status ON humans(status)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_humans_created_at ON humans(created_at)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_transactions_human_id ON transactions(human_id)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_system_stats_name ON system_stats(metric_name)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_system_stats_timestamp ON system_stats(timestamp)')
            
            await db.commit()
            self.logger.info("SQLite tables created successfully")


class DatabaseManager:
    """Database manager with automatic failover and connection management"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.db: Optional[DatabaseInterface] = None
        self.fallback_db: Optional[DatabaseInterface] = None
        
    async def initialize(self) -> None:
        """Initialize database with automatic failover"""
        try:
            # Primary database
            if self.config.database_type == "postgresql":
                self.db = PostgreSQLDatabase(self.config)
                self.fallback_db = SQLiteDatabase(self.config)
            else:
                self.db = SQLiteDatabase(self.config)
                self.fallback_db = PostgreSQLDatabase(self.config)
            
            # Try to initialize primary database
            try:
                await self.db.initialize()
                self.console.print(f"[green]✅ Primary database ({self.config.database_type}) initialized[/green]")
            except Exception as e:
                self.logger.warning(f"Primary database failed, trying fallback: {e}")
                self.console.print(f"[yellow]⚠️  Primary database failed, using fallback[/yellow]")
                
                # Switch to fallback
                self.db = self.fallback_db
                await self.db.initialize()
                self.console.print("[green]✅ Fallback database initialized[/green]")
                
        except Exception as e:
            self.logger.error(f"All database initialization failed: {e}")
            self.console.print(f"[red]❌ All database initialization failed: {e}[/red]")
            raise
    
    async def close(self) -> None:
        """Close database connections"""
        if self.db:
            await self.db.close()
        if self.fallback_db and self.fallback_db != self.db:
            await self.fallback_db.close()
    
    async def execute_query(self, query: str, params: Optional[Tuple] = None) -> Any:
        """Execute query with automatic retry"""
        try:
            return await self.db.execute_query(query, params)
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    async def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict]:
        """Fetch one row with automatic retry"""
        try:
            return await self.db.fetch_one(query, params)
        except Exception as e:
            self.logger.error(f"Fetch one failed: {e}")
            raise
    
    async def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        """Fetch all rows with automatic retry"""
        try:
            return await self.db.fetch_all(query, params)
        except Exception as e:
            self.logger.error(f"Fetch all failed: {e}")
            raise
    
    async def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute multiple queries with automatic retry"""
        try:
            await self.db.execute_many(query, params_list)
        except Exception as e:
            self.logger.error(f"Execute many failed: {e}")
            raise


# Global database manager instance
database_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """Get or create database manager instance"""
    global database_manager
    
    if database_manager is None:
        # Load config from environment or use defaults
        config = DatabaseConfig(
            database_type=os.getenv('DATABASE_TYPE', 'postgresql'),
            postgres_host=os.getenv('POSTGRES_HOST', 'localhost'),
            postgres_port=int(os.getenv('POSTGRES_PORT', '5432')),
            postgres_user=os.getenv('POSTGRES_USER', 'liberation_user'),
            postgres_password=os.getenv('POSTGRES_PASSWORD', 'liberation_password'),
            postgres_database=os.getenv('POSTGRES_DATABASE', 'liberation_system'),
            sqlite_path=os.getenv('SQLITE_PATH', 'data/liberation_system.db')
        )
        
        database_manager = DatabaseManager(config)
        await database_manager.initialize()
    
    return database_manager


async def close_database_manager() -> None:
    """Close database manager"""
    global database_manager
    
    if database_manager:
        await database_manager.close()
        database_manager = None
