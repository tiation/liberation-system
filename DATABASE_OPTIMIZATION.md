# Database Optimization Guide

This guide covers the database optimization features implemented in the Liberation System, including indexing, materialized views, caching, and NoSQL integration for scalable mesh node storage.

## 🚀 Features Implemented

### 1. Optimized Indexing
- **Composite indexes** for multi-column queries
- **Partial indexes** for filtered data
- **Time-based indexes** with TTL for automatic cleanup
- **Geospatial indexes** for mesh node location queries

### 2. Materialized Views
- **Human statistics** aggregation
- **Transaction summaries** with time-based grouping
- **Mesh network health** monitoring
- **Knowledge base statistics** for collaborative learning

### 3. Caching System
- **Redis integration** with local fallback
- **TTL-based cache expiration**
- **Pattern-based cache invalidation**
- **Query result caching** for repeated operations

### 4. NoSQL Integration
- **MongoDB integration** for mesh node data
- **Distributed storage** with sharding support
- **Time-series data** for metrics tracking
- **Geographical queries** for regional node discovery

## 📊 Performance Benefits

| Optimization | Performance Gain | Use Case |
|-------------|------------------|----------|
| **Indexing** | 10-100x faster queries | WHERE/ORDER BY operations |
| **Caching** | 99%+ improvement | Repeated queries |
| **Materialized Views** | Pre-computed results | Complex aggregations |
| **Batch Operations** | Reduced I/O overhead | Multiple inserts/updates |

## 🛠️ Installation

### Prerequisites
```bash
# For Redis caching
pip install redis aioredis

# For MongoDB integration
pip install pymongo motor

# For PostgreSQL with asyncpg
pip install asyncpg

# For demonstration
pip install rich
```

### Setup Redis (Optional)
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
```

### Setup MongoDB (Optional)
```bash
# macOS
brew install mongodb/brew/mongodb-community
brew services start mongodb/brew/mongodb-community

# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb
```

## 🔧 Usage

### Basic Database Optimization
```python
from core.database_optimization import get_optimized_database_manager

# Initialize optimized database
db_manager = await get_optimized_database_manager()

# Get cached human statistics
human_stats = await db_manager.get_human_stats()

# Get cached transaction summary
transactions = await db_manager.get_transaction_summary(days=30)

# Invalidate cache when data changes
await db_manager.invalidate_cache("human_stats*")
```

### Mesh Network Storage
```python
from mesh.optimized_mesh_storage import get_mesh_storage
from mesh.Mesh_Network.Advanced_Node_Discovery import AdvancedMeshNode

# Initialize mesh storage
mesh_storage = await get_mesh_storage()

# Store node with caching
await mesh_storage.store_node(node)

# Query nodes by region (cached)
us_nodes = await mesh_storage.get_nodes_by_region("US")

# Get network topology (cached)
topology = await mesh_storage.get_network_topology()
```

### API Integration
```python
from api.routes.optimized_resources import router

# The optimized routes automatically use:
# - Cached queries for repeated requests
# - Batch operations for bulk updates
# - Index-optimized queries
# - Cache invalidation on data changes
```

## 📈 Database Schema Optimizations

### Humans Table Indexes
```sql
-- Status and creation date composite index
CREATE INDEX idx_humans_status_created ON humans(status, created_at);

-- Partial index for active distributions
CREATE INDEX idx_humans_last_distribution ON humans(last_distribution) 
WHERE last_distribution IS NOT NULL;

-- Total received for statistics
CREATE INDEX idx_humans_total_received ON humans(total_received);
```

### Transactions Table Indexes
```sql
-- Human and timestamp composite index
CREATE INDEX idx_transactions_human_timestamp ON transactions(human_id, timestamp);

-- Transaction type and status composite index
CREATE INDEX idx_transactions_type_status ON transactions(transaction_type, status);

-- Amount index for financial queries
CREATE INDEX idx_transactions_amount ON transactions(amount) WHERE amount > 0;
```

### Mesh Nodes Indexes (MongoDB)
```javascript
// Compound index for active nodes
db.mesh_nodes.createIndex({
  "status": 1,
  "last_seen": -1,
  "node_id": 1
});

// Geospatial index for location queries
db.mesh_nodes.createIndex({
  "location.country": 1,
  "location.region": 1
});

// Trust score index for node ranking
db.mesh_nodes.createIndex({
  "trust_score": -1,
  "node_type": 1
});
```

## 🔄 Materialized Views

### Human Statistics View
```sql
CREATE MATERIALIZED VIEW human_stats_mv AS
SELECT 
    COUNT(*) as total_humans,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_humans,
    SUM(total_received) as total_distributed,
    AVG(total_received) as avg_per_human,
    MAX(last_distribution) as last_distribution_date
FROM humans;
```

### Transaction Summary View
```sql
CREATE MATERIALIZED VIEW transaction_summary_mv AS
SELECT 
    transaction_type,
    status,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    DATE_TRUNC('day', timestamp) as transaction_date
FROM transactions
GROUP BY transaction_type, status, DATE_TRUNC('day', timestamp);
```

### Mesh Network Health View
```sql
CREATE MATERIALIZED VIEW mesh_network_health_mv AS
SELECT 
    COUNT(*) as total_nodes,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_nodes,
    AVG(CASE WHEN metrics->>'latency' ~ '^[0-9.]+$' 
        THEN (metrics->>'latency')::float END) as avg_latency,
    COUNT(CASE WHEN last_seen > NOW() - INTERVAL '5 minutes' 
        THEN 1 END) as recently_active
FROM mesh_nodes;
```

## 💾 Caching Strategy

### Cache Configuration
```python
from core.database_optimization import CacheConfig

cache_config = CacheConfig(
    redis_host="localhost",
    redis_port=6379,
    redis_db=0,
    default_ttl=3600,  # 1 hour
    max_connections=20
)
```

### Cache Patterns
- **Human data**: `human_{id}` (TTL: 10 minutes)
- **Statistics**: `human_stats_summary` (TTL: 5 minutes)
- **Transactions**: `transaction_summary_{days}d` (TTL: 15 minutes)
- **Mesh nodes**: `node_{id}` (TTL: 5 minutes)
- **Topology**: `network_topology` (TTL: 2 minutes)

### Cache Invalidation
```python
# Pattern-based invalidation
await cache_manager.clear_pattern("human_stats*")
await cache_manager.clear_pattern("transaction_summary*")

# Specific key invalidation
await cache_manager.delete("human_123")
```

## 🌐 NoSQL Integration

### MongoDB Collections

#### Mesh Nodes Collection
```javascript
{
  "_id": ObjectId("..."),
  "node_id": "node_001",
  "host": "10.0.1.1",
  "port": 8000,
  "node_type": "standard",
  "location": {
    "country": "US",
    "region": "California",
    "city": "San Francisco",
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "metrics": {
    "latency": 45.2,
    "bandwidth": 120.5,
    "packet_loss": 0.1,
    "uptime": 99.5
  },
  "last_seen": 1642684800,
  "status": "active",
  "trust_score": 0.95,
  "updated_at": ISODate("2022-01-20T10:00:00Z")
}
```

#### Node Metrics Collection (Time-series)
```javascript
{
  "_id": ObjectId("..."),
  "node_id": "node_001",
  "timestamp": ISODate("2022-01-20T10:00:00Z"),
  "metrics": {
    "latency": 45.2,
    "bandwidth": 120.5,
    "cpu_usage": 65.3,
    "memory_usage": 78.1
  },
  "quality_score": 0.92,
  "trust_score": 0.95
}
```

### Sharding Strategy
```javascript
// Shard nodes by node_id
sh.shardCollection("liberation_mesh.mesh_nodes", {"node_id": 1});

// Shard metrics by node_id and timestamp
sh.shardCollection("liberation_mesh.node_metrics", {
  "node_id": 1, 
  "timestamp": 1
});
```

## 🧪 Testing

### Run the Demo
```bash
# Simple optimization demo (no external dependencies)
python3 examples/simple_optimization_demo.py

# Full optimization demo (requires Redis/MongoDB)
python3 examples/database_optimization_demo.py
```

### Performance Testing
```python
# Test query performance
import time

start_time = time.time()
result = await db_manager.get_human_stats()
query_time = (time.time() - start_time) * 1000
print(f"Query time: {query_time:.2f}ms")

# Test cache performance
start_time = time.time()
cached_result = await db_manager.get_human_stats()
cache_time = (time.time() - start_time) * 1000
print(f"Cache time: {cache_time:.2f}ms")
```

## 📚 Best Practices

### 1. Index Design
- **Create composite indexes** for multi-column queries
- **Use partial indexes** for filtered data
- **Monitor index usage** with EXPLAIN ANALYZE
- **Remove unused indexes** to improve write performance

### 2. Caching Strategy
- **Cache frequently accessed data** with appropriate TTL
- **Use pattern-based invalidation** for related data
- **Implement cache warming** for critical queries
- **Monitor cache hit rates** and adjust TTL accordingly

### 3. Query Optimization
- **Use LIMIT and OFFSET** for pagination
- **Avoid SELECT *** and specify columns
- **Use batch operations** for multiple inserts/updates
- **Implement connection pooling** for concurrent access

### 4. Monitoring
- **Track query performance** with logging
- **Monitor cache hit rates** and memory usage
- **Set up alerts** for performance degradation
- **Regular maintenance** of indexes and views

## 🔍 Troubleshooting

### Common Issues

1. **Slow Queries**
   - Check if indexes are being used
   - Analyze query execution plan
   - Consider adding composite indexes

2. **Cache Misses**
   - Verify Redis connection
   - Check TTL settings
   - Monitor cache invalidation patterns

3. **Memory Issues**
   - Tune cache size limits
   - Implement cache eviction policies
   - Monitor memory usage

### Debug Commands
```bash
# Check Redis connection
redis-cli ping

# Monitor Redis operations
redis-cli monitor

# Check MongoDB status
mongosh --eval "db.runCommand({serverStatus: 1})"
```

## 🎯 Future Enhancements

### Planned Features
- **Query result streaming** for large datasets
- **Distributed caching** with Redis Cluster
- **Real-time cache invalidation** via pub/sub
- **Advanced sharding strategies** for MongoDB
- **Machine learning-based** query optimization

### Performance Targets
- **Sub-millisecond** cache retrieval
- **Multi-region** data replication
- **Automatic** index optimization
- **Predictive** cache warming

---

For more information, see the individual module documentation:
- [Core Database Optimization](core/database_optimization.py)
- [Mesh Storage Optimization](mesh/optimized_mesh_storage.py)
- [Optimized API Routes](api/routes/optimized_resources.py)
