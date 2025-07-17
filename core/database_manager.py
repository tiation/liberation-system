"""
Liberation System - Database Manager Module
Handles database initialization, migrations, and operations.
"""

import sqlite3
from contextlib import closing
from typing import Optional, Dict, Any
import logging


class DatabaseManager:
    """Manages database operations for the Liberation System"""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def initialize(self):
        """Initialize the database"""
        try:
            self.logger.info(f"🔄 Initializing database at {self.db_path}")
            
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    self._create_tables(conn)
            
            self.logger.info("✅ Database initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Error initializing database: {e}")

    def _create_tables(self, conn: sqlite3.Connection):
        """Create tables if they do not exist"""
        try:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                recipient TEXT NOT NULL,
                date_added TEXT DEFAULT CURRENT_TIMESTAMP
            )''')

            conn.execute('''
            CREATE TABLE IF NOT EXISTS truth_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                subscriber_count INTEGER DEFAULT 0
            )''')
            
            self.logger.info("📚 Tables created or verified successfully")
        except Exception as e:
            self.logger.error(f"❌ Error creating tables: {e}")

    def query(self, query: str, params: Optional[tuple] = ()) -> Optional[list]:
        """Execute a query and return the results"""
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    cur = conn.execute(query, params)
                    results = cur.fetchall()
            return results
        except Exception as e:
            self.logger.error(f"❌ Error executing query: {query} with params {params}: {e}")
            return None

    def execute(self, query: str, params: Optional[tuple] = ()) -> bool:
        """Execute a query without returning results"""
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    conn.execute(query, params)
            return True
        except Exception as e:
            self.logger.error(f"❌ Error executing query: {query} with params {params}: {e}")
            return False


# Example Usage
if __name__ == "__main__":
    # Setup logging for demonstration
    logging.basicConfig(level=logging.INFO)
    
    # Create a database manager instance
    db_manager = DatabaseManager('liberation_system.db')
    
    # Initialize the database
    db_manager.initialize()
    
    # Example query
    resources = db_manager.query('SELECT * FROM resources;')
    print(resources)

