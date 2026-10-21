# Theory of Distributed Caching

## 1. Why Distributed Caching?

Databases are the bottleneck in most applications. A distributed cache reduces latency and database load by keeping hot data in memory across multiple nodes.

## 2. Caching Patterns

### Cache-Aside (Lazy Loading)
- Application checks cache first
- On miss: load from DB, store in cache
- Simple but can lead to stale data

### Read-Through
- Cache automatically loads from DB on miss
- Cache is authoritative for reads

### Write-Through
- Every write goes through cache to DB
- Cache always consistent with DB
- Higher write latency

### Write-Behind (Write-Back)
- Write goes to cache, async write to DB
- Low latency writes
- Risk of data loss if cache fails

### Write-Around
- Write directly to DB
- Cache invalidated on write
- Reduces cache pollution

## 3. Cache Coherency

### Strong Consistency
- All reads see latest write
- Requires coordination (expensive)

### Eventual Consistency
- Reads may return stale data
- Cache eventually catches up
- Acceptable for many workloads

## 4. Cache Invalidation

- **TTL-based**: Expire entries after time period
- **Event-based**: Invalidate on data change (pub/sub)
- **Version-based**: Track versions, invalidate stale entries
- **Write-invalidation**: Invalidate on every write

## 5. Cache Stampede

When many concurrent requests miss the cache simultaneously:
- All requests hit the database (thundering herd)
- Can overwhelm the database

### Prevention
- Locking (only one request loads data)
- Probabilistic early expiration (jitter TTL)
- Stale-while-revalidate pattern
