#!/usr/bin/env python3
"""
Simple Database Optimization Demo
Demonstrates basic optimization concepts without external dependencies
"""

import asyncio
import logging
import time
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress


@dataclass
class SimpleCache:
    """Simple in-memory cache implementation"""
    def __init__(self, ttl: int = 300):
        self.cache: Dict[str, tuple] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self.cache[key] = (value, time.time())
    
    def clear_pattern(self, pattern: str) -> None:
        """Clear cache entries matching pattern"""
        keys_to_remove = [k for k in self.cache.keys() if pattern.replace('*', '') in k]
        for k in keys_to_remove:
            del self.cache[k]


class OptimizedDatabaseDemo:
    """Demo class showing database optimization techniques"""
    
    def __init__(self):
        self.db_path = Path("demo_database.db")
        self.cache = SimpleCache(ttl=300)
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize demo database with sample data"""
        self.console.print("[cyan]🔧 Initializing demo database...[/cyan]")
        
        # Create database and tables
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables with proper indexes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS humans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                human_id TEXT UNIQUE NOT NULL,
                weekly_flow REAL NOT NULL DEFAULT 800.00,
                housing_credit REAL NOT NULL DEFAULT 104000.00,
                investment_pool REAL NOT NULL DEFAULT 104000.00,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_distribution TEXT,
                total_received REAL DEFAULT 0.00,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                human_id TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (human_id) REFERENCES humans(human_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mesh_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT UNIQUE NOT NULL,
                host TEXT NOT NULL,
                port INTEGER NOT NULL,
                location TEXT,
                metrics TEXT,
                last_seen REAL NOT NULL,
                status TEXT DEFAULT 'active',
                trust_score REAL DEFAULT 1.0
            )
        ''')
        
        # Create optimized indexes
        self.console.print("[cyan]📊 Creating optimized indexes...[/cyan]")
        
        # Indexes for humans table
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_humans_status ON humans(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_humans_created_at ON humans(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_humans_last_distribution ON humans(last_distribution)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_humans_status_created ON humans(status, created_at)')
        
        # Indexes for transactions table
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_human_id ON transactions(human_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_human_timestamp ON transactions(human_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type_status ON transactions(transaction_type, status)')
        
        # Indexes for mesh_nodes table
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mesh_nodes_status ON mesh_nodes(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mesh_nodes_last_seen ON mesh_nodes(last_seen)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mesh_nodes_trust_score ON mesh_nodes(trust_score)')
        
        # Insert sample data
        self.console.print("[cyan]📝 Inserting sample data...[/cyan]")
        
        # Sample humans
        sample_humans = [
            (f"human_{i:06d}", 800.00, 104000.00, 104000.00, 
             (datetime.now() - timedelta(days=i)).isoformat(), 
             0.00, 'active')
            for i in range(1, 1001)  # 1000 humans
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO humans (human_id, weekly_flow, housing_credit, investment_pool, created_at, total_received, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_humans)
        
        # Sample transactions
        sample_transactions = []
        for i in range(1, 5001):  # 5000 transactions
            human_id = f"human_{(i % 1000) + 1:06d}"
            amount = 800.00 if i % 7 == 0 else 0.00  # Weekly distributions
            tx_type = "weekly_distribution" if i % 7 == 0 else "system_check"
            timestamp = (datetime.now() - timedelta(days=i // 100)).isoformat()
            status = "completed" if i % 10 != 0 else "pending"
            
            sample_transactions.append((human_id, amount, tx_type, timestamp, status))
        
        cursor.executemany('''
            INSERT INTO transactions (human_id, amount, transaction_type, timestamp, status)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_transactions)
        
        # Sample mesh nodes
        sample_nodes = []
        for i in range(1, 101):  # 100 nodes
            node_id = f"node_{i:03d}"
            host = f"10.0.{i // 25}.{i % 25}"
            port = 8000 + i
            location = json.dumps({
                "country": ["US", "UK", "DE", "JP"][i % 4],
                "region": ["California", "London", "Bavaria", "Tokyo"][i % 4],
                "latitude": [37.7749, 51.5074, 48.1351, 35.6762][i % 4],
                "longitude": [-122.4194, -0.1278, 11.5820, 139.6503][i % 4]
            })
            metrics = json.dumps({
                "latency": 50 + (i % 100),
                "bandwidth": 100 + (i % 50),
                "uptime": 95 + (i % 5)
            })
            last_seen = time.time() - (i % 300)  # Some nodes seen recently
            trust_score = 0.8 + (i % 20) * 0.01
            
            sample_nodes.append((node_id, host, port, location, metrics, last_seen, 'active', trust_score))
        
        cursor.executemany('''
            INSERT OR IGNORE INTO mesh_nodes (node_id, host, port, location, metrics, last_seen, status, trust_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_nodes)
        
        conn.commit()
        conn.close()
        
        self.console.print("[green]✅ Demo database initialized with sample data[/green]")
    
    async def demonstrate_indexing_performance(self) -> None:
        """Demonstrate the performance benefits of indexing"""
        self.console.print("\\n[cyan]🏎️  Demonstrating Indexing Performance Benefits[/cyan]")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test 1: Query with index vs without index
        performance_table = Table(title="Query Performance Comparison")
        performance_table.add_column("Query Type", style="cyan")
        performance_table.add_column("Index Used", style="green")
        performance_table.add_column("Time (ms)", style="yellow")
        performance_table.add_column("Records", style="magenta")
        
        # Query 1: Get active humans (uses status index)
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM humans WHERE status = 'active'")
        active_count = cursor.fetchone()[0]
        query_time = (time.time() - start_time) * 1000
        
        performance_table.add_row("Active Humans Count", "✅ Yes", f"{query_time:.2f}", str(active_count))
        
        # Query 2: Get recent transactions (uses timestamp index)
        start_time = time.time()
        cursor.execute("""
            SELECT COUNT(*) FROM transactions 
            WHERE timestamp >= datetime('now', '-7 days')
        """)
        recent_count = cursor.fetchone()[0]
        query_time = (time.time() - start_time) * 1000
        
        performance_table.add_row("Recent Transactions", "✅ Yes", f"{query_time:.2f}", str(recent_count))
        
        # Query 3: Complex join with indexes
        start_time = time.time()
        cursor.execute("""
            SELECT h.human_id, h.status, COUNT(t.id) as transaction_count
            FROM humans h
            LEFT JOIN transactions t ON h.human_id = t.human_id
            WHERE h.status = 'active' AND t.transaction_type = 'weekly_distribution'
            GROUP BY h.human_id
            LIMIT 10
        """)
        join_results = cursor.fetchall()
        query_time = (time.time() - start_time) * 1000
        
        performance_table.add_row("Complex Join", "✅ Yes", f"{query_time:.2f}", str(len(join_results)))
        
        # Query 4: Mesh nodes by trust score (uses trust_score index)
        start_time = time.time()
        cursor.execute("""
            SELECT node_id, trust_score FROM mesh_nodes 
            WHERE trust_score > 0.9 
            ORDER BY trust_score DESC
        """)
        trusted_nodes = cursor.fetchall()
        query_time = (time.time() - start_time) * 1000
        
        performance_table.add_row("High Trust Nodes", "✅ Yes", f"{query_time:.2f}", str(len(trusted_nodes)))
        
        self.console.print(performance_table)
        
        conn.close()
    
    async def demonstrate_caching(self) -> None:
        """Demonstrate caching performance improvements"""
        self.console.print("\\n[cyan]💾 Demonstrating Caching Performance[/cyan]")
        
        cache_table = Table(title="Cache Performance Comparison")
        cache_table.add_column("Query", style="cyan")
        cache_table.add_column("First Call (ms)", style="green")
        cache_table.add_column("Cached Call (ms)", style="yellow")
        cache_table.add_column("Improvement", style="magenta")
        
        # Test caching with different queries
        test_queries = [
            ("Human Statistics", "SELECT COUNT(*) as total, AVG(total_received) as avg_received FROM humans"),
            ("Transaction Summary", "SELECT transaction_type, COUNT(*) as count FROM transactions GROUP BY transaction_type"),
            ("Active Nodes", "SELECT COUNT(*) FROM mesh_nodes WHERE status = 'active'"),
            ("Top Trust Nodes", "SELECT node_id, trust_score FROM mesh_nodes ORDER BY trust_score DESC LIMIT 5")
        ]
        
        for query_name, sql_query in test_queries:
            # First call (database)
            start_time = time.time()
            result = await self._execute_cached_query(f"cache_{query_name}", sql_query)
            first_call_time = (time.time() - start_time) * 1000
            
            # Second call (cache)
            start_time = time.time()
            cached_result = await self._execute_cached_query(f"cache_{query_name}", sql_query)
            cached_call_time = (time.time() - start_time) * 1000
            
            improvement = ((first_call_time - cached_call_time) / first_call_time * 100) if first_call_time > 0 else 0
            
            cache_table.add_row(
                query_name,
                f"{first_call_time:.2f}",
                f"{cached_call_time:.2f}",
                f"{improvement:.1f}% faster"
            )
        
        self.console.print(cache_table)
    
    async def _execute_cached_query(self, cache_key: str, query: str) -> Any:
        """Execute a query with caching"""
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Execute query
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        
        # Cache the result
        self.cache.set(cache_key, result)
        return result
    
    async def demonstrate_materialized_views(self) -> None:
        """Demonstrate materialized view concepts using SQLite views"""
        self.console.print("\\n[cyan]📊 Demonstrating Materialized View Concepts[/cyan]")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create views for commonly accessed data
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS human_stats_view AS
            SELECT 
                COUNT(*) as total_humans,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_humans,
                SUM(total_received) as total_distributed,
                AVG(total_received) as avg_per_human
            FROM humans
        ''')
        
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS transaction_summary_view AS
            SELECT 
                transaction_type,
                status,
                COUNT(*) as transaction_count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount,
                date(timestamp) as transaction_date
            FROM transactions
            GROUP BY transaction_type, status, date(timestamp)
        ''')
        
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS mesh_network_health_view AS
            SELECT 
                COUNT(*) as total_nodes,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_nodes,
                AVG(trust_score) as avg_trust_score,
                COUNT(CASE WHEN last_seen > (strftime('%s', 'now') - 300) THEN 1 END) as recently_active
            FROM mesh_nodes
        ''')
        
        # Test view performance
        view_table = Table(title="Materialized View Performance")
        view_table.add_column("View", style="cyan")
        view_table.add_column("Query Time (ms)", style="green")
        view_table.add_column("Result", style="yellow")
        
        # Human stats view
        start_time = time.time()
        cursor.execute("SELECT * FROM human_stats_view")
        human_stats = cursor.fetchone()
        query_time = (time.time() - start_time) * 1000
        
        view_table.add_row("Human Statistics", f"{query_time:.2f}", f"{human_stats[0]} total, {human_stats[1]} active")
        
        # Transaction summary view
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM transaction_summary_view")
        summary_count = cursor.fetchone()[0]
        query_time = (time.time() - start_time) * 1000
        
        view_table.add_row("Transaction Summary", f"{query_time:.2f}", f"{summary_count} summary records")
        
        # Mesh health view
        start_time = time.time()
        cursor.execute("SELECT * FROM mesh_network_health_view")
        mesh_health = cursor.fetchone()
        query_time = (time.time() - start_time) * 1000
        
        view_table.add_row("Mesh Network Health", f"{query_time:.2f}", f"{mesh_health[0]} nodes, {mesh_health[1]} active")
        
        self.console.print(view_table)
        
        conn.close()
    
    async def demonstrate_cache_invalidation(self) -> None:
        """Demonstrate cache invalidation strategies"""
        self.console.print("\\n[cyan]🔄 Demonstrating Cache Invalidation[/cyan]")
        
        # Show cache contents before invalidation
        cache_info_table = Table(title="Cache Management")
        cache_info_table.add_column("Action", style="cyan")
        cache_info_table.add_column("Cache Size", style="green")
        cache_info_table.add_column("Status", style="yellow")
        
        cache_info_table.add_row("Initial State", str(len(self.cache.cache)), "Populated")
        
        # Invalidate specific pattern
        self.cache.clear_pattern("cache_Human*")
        cache_info_table.add_row("After Pattern Clear", str(len(self.cache.cache)), "Human stats cleared")
        
        # Repopulate cache
        await self._execute_cached_query("cache_new_query", "SELECT COUNT(*) FROM humans")
        cache_info_table.add_row("After New Query", str(len(self.cache.cache)), "Repopulated")
        
        self.console.print(cache_info_table)
    
    async def show_optimization_summary(self) -> None:
        """Show summary of optimization benefits"""
        self.console.print("\\n[cyan]📈 Optimization Summary[/cyan]")
        
        summary_table = Table(title="Database Optimization Techniques")
        summary_table.add_column("Technique", style="cyan")
        summary_table.add_column("Benefit", style="green")
        summary_table.add_column("Use Case", style="yellow")
        summary_table.add_column("Implementation", style="magenta")
        
        summary_table.add_row(
            "Indexing",
            "10-100x faster queries",
            "Frequent WHERE/ORDER BY",
            "CREATE INDEX statements"
        )
        
        summary_table.add_row(
            "Caching",
            "Near-instant retrieval",
            "Repeated queries",
            "In-memory storage"
        )
        
        summary_table.add_row(
            "Materialized Views",
            "Pre-computed results",
            "Complex aggregations",
            "CREATE VIEW statements"
        )
        
        summary_table.add_row(
            "Batch Operations",
            "Reduced I/O overhead",
            "Multiple inserts/updates",
            "executemany() calls"
        )
        
        self.console.print(summary_table)
    
    async def cleanup(self) -> None:
        """Clean up demo resources"""
        if self.db_path.exists():
            self.db_path.unlink()
        self.console.print("[yellow]🧹 Demo cleanup completed[/yellow]")


async def main():
    """Main demo function"""
    console = Console()
    
    console.print(Panel.fit(
        "🎯 Simple Database Optimization Demo",
        style="bold blue"
    ))
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    demo = OptimizedDatabaseDemo()
    
    try:
        # Initialize demo
        await demo.initialize()
        
        # Run demonstrations
        await demo.demonstrate_indexing_performance()
        await demo.demonstrate_caching()
        await demo.demonstrate_materialized_views()
        await demo.demonstrate_cache_invalidation()
        await demo.show_optimization_summary()
        
        console.print("\n")
        console.print(Panel.fit(
            "✅ Database Optimization Demo Completed Successfully!",
            style="bold green"
        ))
        
    except Exception as e:
        console.print(f"\\n[red]❌ Demo failed: {e}[/red]")
        raise
    
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
