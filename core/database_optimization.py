# core/database_optimization.py

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod
import hashlib

try:
    import redis.asyncio as redis
    import aioredis
except ImportError:
    print("Installing redis dependencies...")
    import subprocess
    subprocess.check_call(["pip", "install", "redis", "aioredis"])
    import redis.asyncio as redis
    import aioredis

from .database import DatabaseInterface, DatabaseManager
from rich.console import Console


@dataclass
class CacheConfig:
    """Configuration for caching system"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    default_ttl: int = 3600  # 1 hour
    max_connections: int = 20
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


class CacheManager:
    """Enhanced caching system with Redis"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.local_cache: Dict[str, Tuple[Any, float]] = {}
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.config.get_redis_url(),
                max_connections=self.config.max_connections,
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            self.console.print("[green]✅ Redis cache initialized successfully[/green]")
            
        except Exception as e:
            self.logger.warning(f"Redis initialization failed, using local cache: {e}")
            self.console.print(f"[yellow]⚠️  Redis unavailable, using local cache[/yellow]")
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                # Try Redis first
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            
            # Fallback to local cache
            if key in self.local_cache:
                value, timestamp = self.local_cache[key]
                if time.time() - timestamp < self.config.default_ttl:
                    return value
                else:
                    del self.local_cache[key]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Cache get failed for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.config.default_ttl
            json_value = json.dumps(value, default=str)
            
            if self.redis_client:
                await self.redis_client.setex(key, ttl, json_value)
            
            # Also store in local cache
            self.local_cache[key] = (value, time.time())
            
            # Clean up old local cache entries
            if len(self.local_cache) > 1000:
                cutoff_time = time.time() - self.config.default_ttl
                expired_keys = [
                    k for k, (_, timestamp) in self.local_cache.items()
                    if timestamp < cutoff_time
                ]
                for k in expired_keys:
                    del self.local_cache[k]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis_client:
                await self.redis_client.delete(key)
            
            if key in self.local_cache:
                del self.local_cache[key]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> bool:
        """Clear cache entries matching pattern"""
        try:
            if self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            
            # Clear matching local cache entries
            matching_keys = [k for k in self.local_cache.keys() if pattern.replace('*', '') in k]
            for k in matching_keys:
                del self.local_cache[k]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache clear pattern failed for {pattern}: {e}")
            return False
    
    async def close(self) -> None:
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.aclose()
            self.console.print("[yellow]🔒 Redis cache connection closed[/yellow]")


class DatabaseOptimizer:
    """Database optimization with indexing and materialized views"""
    
    def __init__(self, db_manager: DatabaseManager, cache_manager: CacheManager):
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
    async def create_optimized_indexes(self) -> None:
        """Create optimized indexes for better performance"""
        try:
            self.console.print("[cyan]📊 Creating optimized database indexes...[/cyan]")
            
            # Indexes for humans table - Trust-by-default: No verification checks, just optimization
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_humans_status_created ON humans(status, created_at);
            """)
            
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_humans_last_distribution ON humans(last_distribution) 
                WHERE last_distribution IS NOT NULL;
            """)
            
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_humans_total_received ON humans(total_received);
            """)
            
            # Indexes for transactions table
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_transactions_human_timestamp ON transactions(human_id, timestamp);
            """)
            
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_transactions_type_status ON transactions(transaction_type, status);
            """)
            
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount) 
                WHERE amount > 0;
            """)
            
            # Indexes for system_stats table
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_system_stats_metric_timestamp ON system_stats(metric_name, timestamp);
            """)
            
            # Indexes for knowledge_entries table (if exists)
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_type_status ON knowledge_entries(knowledge_type, status);
            """)
            
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_effectiveness ON knowledge_entries(effectiveness_rating) 
                WHERE effectiveness_rating > 0;
            """)
            
            # Indexes for mesh node data
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_mesh_nodes_status_location ON mesh_nodes(status, location);
            """)
            
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_mesh_nodes_last_seen ON mesh_nodes(last_seen) 
                WHERE last_seen IS NOT NULL;
            """)
            
            self.console.print("[green]✅ Optimized indexes created successfully[/green]")
            
        except Exception as e:
            self.logger.error(f"Failed to create optimized indexes: {e}")
            self.console.print(f"[red]❌ Index creation failed: {e}[/red]")
    
    async def create_materialized_views(self) -> None:
        """Create materialized views for complex queries"""
        try:
            self.console.print("[cyan]📊 Creating materialized views...[/cyan]")
            
            # Human statistics materialized view
            await self.db_manager.execute_query("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS human_stats_mv AS
                SELECT 
                    COUNT(*) as total_humans,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_humans,
                    SUM(total_received) as total_distributed,
                    AVG(total_received) as avg_per_human,
                    MAX(last_distribution) as last_distribution_date,
                    COUNT(CASE WHEN last_distribution > NOW() - INTERVAL '7 days' THEN 1 END) as recent_distributions
                FROM humans;
            """)
            
            # Transaction summary materialized view
            await self.db_manager.execute_query("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS transaction_summary_mv AS
                SELECT 
                    transaction_type,
                    status,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    DATE_TRUNC('day', timestamp) as transaction_date
                FROM transactions
                GROUP BY transaction_type, status, DATE_TRUNC('day', timestamp);
            """)
            
            # Daily distribution stats materialized view
            await self.db_manager.execute_query("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS daily_distribution_mv AS
                SELECT 
                    DATE_TRUNC('day', timestamp) as distribution_date,
                    COUNT(DISTINCT human_id) as unique_recipients,
                    SUM(amount) as total_distributed,
                    AVG(amount) as avg_distribution,
                    COUNT(*) as total_transactions
                FROM transactions
                WHERE transaction_type = 'weekly_distribution'
                GROUP BY DATE_TRUNC('day', timestamp);
            """)
            
            # Knowledge base stats materialized view
            await self.db_manager.execute_query("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS knowledge_stats_mv AS
                SELECT 
                    knowledge_type,
                    status,
                    COUNT(*) as entry_count,
                    AVG(confidence_score) as avg_confidence,
                    AVG(effectiveness_rating) as avg_effectiveness,
                    SUM(usage_count) as total_usage
                FROM knowledge_entries
                GROUP BY knowledge_type, status;
            """)
            
            # Mesh network health materialized view
            await self.db_manager.execute_query("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS mesh_network_health_mv AS
                SELECT 
                    COUNT(*) as total_nodes,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_nodes,
                    AVG(CASE WHEN metrics->>'latency' ~ '^[0-9.]+$' THEN (metrics->>'latency')::float END) as avg_latency,
                    AVG(CASE WHEN metrics->>'bandwidth' ~ '^[0-9.]+$' THEN (metrics->>'bandwidth')::float END) as avg_bandwidth,
                    COUNT(CASE WHEN last_seen > NOW() - INTERVAL '5 minutes' THEN 1 END) as recently_active
                FROM mesh_nodes;
            """)
            
            self.console.print("[green]✅ Materialized views created successfully[/green]")
            
        except Exception as e:
            self.logger.error(f"Failed to create materialized views: {e}")
            self.console.print(f"[red]❌ Materialized view creation failed: {e}[/red]")
    
    async def refresh_materialized_views(self) -> None:
        """Refresh materialized views to update data"""
        try:
            views_to_refresh = [
                'human_stats_mv',
                'transaction_summary_mv', 
                'daily_distribution_mv',
                'knowledge_stats_mv',
                'mesh_network_health_mv'
            ]
            
            for view in views_to_refresh:
                await self.db_manager.execute_query(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view};")
            
            self.logger.info("Materialized views refreshed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh materialized views: {e}")
    
    async def get_cached_human_stats(self) -> Dict[str, Any]:
        """Get human statistics with caching"""
        cache_key = "human_stats_summary"
        
        # Try cache first
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        # Query from materialized view
        try:
            result = await self.db_manager.fetch_one("SELECT * FROM human_stats_mv")
            if result:
                stats = dict(result)
                # Cache for 5 minutes
                await self.cache_manager.set(cache_key, stats, ttl=300)
                return stats
        except Exception as e:
            self.logger.error(f"Failed to get human stats: {e}")
        
        return {}
    
    async def get_cached_transaction_summary(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get transaction summary with caching"""
        cache_key = f"transaction_summary_{days}d"
        
        # Try cache first
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        # Query from materialized view
        try:
            query = """
                SELECT * FROM transaction_summary_mv 
                WHERE transaction_date >= NOW() - INTERVAL %s
                ORDER BY transaction_date DESC
            """
            results = await self.db_manager.fetch_all(query, (f"{days} days",))
            
            if results:
                summary = [dict(row) for row in results]
                # Cache for 15 minutes
                await self.cache_manager.set(cache_key, summary, ttl=900)
                return summary
        except Exception as e:
            self.logger.error(f"Failed to get transaction summary: {e}")
        
        return []
    
    async def get_cached_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics with caching"""
        cache_key = "knowledge_stats_summary"
        
        # Try cache first
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        # Query from materialized view
        try:
            results = await self.db_manager.fetch_all("SELECT * FROM knowledge_stats_mv")
            if results:
                stats = [dict(row) for row in results]
                # Cache for 10 minutes
                await self.cache_manager.set(cache_key, stats, ttl=600)
                return {"knowledge_stats": stats}
        except Exception as e:
            self.logger.error(f"Failed to get knowledge stats: {e}")
        
        return {}
    
    async def get_cached_mesh_health(self) -> Dict[str, Any]:
        """Get mesh network health with caching"""
        cache_key = "mesh_network_health"
        
        # Try cache first
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        # Query from materialized view
        try:
            result = await self.db_manager.fetch_one("SELECT * FROM mesh_network_health_mv")
            if result:
                health = dict(result)
                # Cache for 2 minutes (frequent updates needed)
                await self.cache_manager.set(cache_key, health, ttl=120)
                return health
        except Exception as e:
            self.logger.error(f"Failed to get mesh health: {e}")
        
        return {}
    
    async def invalidate_cache_pattern(self, pattern: str) -> None:
        """Invalidate cache entries matching pattern"""
        await self.cache_manager.clear_pattern(pattern)
        self.logger.info(f"Cache invalidated for pattern: {pattern}")
    
    async def setup_automatic_refresh(self) -> None:
        """Setup automatic refresh of materialized views"""
        async def refresh_loop():
            while True:
                try:
                    await self.refresh_materialized_views()
                    await asyncio.sleep(300)  # Refresh every 5 minutes
                except Exception as e:
                    self.logger.error(f"Auto-refresh failed: {e}")
                    await asyncio.sleep(60)  # Retry after 1 minute
        
        asyncio.create_task(refresh_loop())
        self.logger.info("Automatic materialized view refresh started")


class OptimizedDatabaseManager:
    """Enhanced database manager with optimization features"""
    
    def __init__(self, db_manager: DatabaseManager, cache_config: CacheConfig = None):
        self.db_manager = db_manager
        self.cache_config = cache_config or CacheConfig()
        self.cache_manager = CacheManager(self.cache_config)
        self.optimizer = DatabaseOptimizer(db_manager, self.cache_manager)
        self.console = Console()
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize optimized database system"""
        try:
            self.console.print("[cyan]🚀 Initializing optimized database system...[/cyan]")
            
            # Initialize cache
            await self.cache_manager.initialize()
            
            # Create optimized indexes
            await self.optimizer.create_optimized_indexes()
            
            # Create materialized views
            await self.optimizer.create_materialized_views()
            
            # Setup automatic refresh
            await self.optimizer.setup_automatic_refresh()
            
            self.console.print("[green]✅ Optimized database system initialized successfully[/green]")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize optimized database: {e}")
            self.console.print(f"[red]❌ Optimization initialization failed: {e}[/red]")
            raise
    
    async def close(self) -> None:
        """Close optimized database system"""
        await self.cache_manager.close()
        await self.db_manager.close()
        self.console.print("[yellow]🔒 Optimized database system closed[/yellow]")
    
    # Expose optimized methods
    async def get_human_stats(self) -> Dict[str, Any]:
        """Get cached human statistics"""
        return await self.optimizer.get_cached_human_stats()
    
    async def get_transaction_summary(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get cached transaction summary"""
        return await self.optimizer.get_cached_transaction_summary(days)
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get cached knowledge statistics"""
        return await self.optimizer.get_cached_knowledge_stats()
    
    async def get_mesh_health(self) -> Dict[str, Any]:
        """Get cached mesh network health"""
        return await self.optimizer.get_cached_mesh_health()
    
    async def invalidate_cache(self, pattern: str) -> None:
        """Invalidate cache entries"""
        await self.optimizer.invalidate_cache_pattern(pattern)


# Global optimized database manager instance
optimized_db_manager: Optional[OptimizedDatabaseManager] = None


async def get_optimized_database_manager() -> OptimizedDatabaseManager:
    """Get or create optimized database manager instance"""
    global optimized_db_manager
    
    if optimized_db_manager is None:
        from .database import get_database_manager
        
        db_manager = await get_database_manager()
        cache_config = CacheConfig()
        
        optimized_db_manager = OptimizedDatabaseManager(db_manager, cache_config)
        await optimized_db_manager.initialize()
    
    return optimized_db_manager


async def close_optimized_database_manager() -> None:
    """Close optimized database manager"""
    global optimized_db_manager
    
    if optimized_db_manager:
        await optimized_db_manager.close()
        optimized_db_manager = None
