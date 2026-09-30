# THEORY: Caching Architecture & Redis at Scale
## Lab 12 | Production Engineering Academy

---

## 1. The Three Classic Distributed Caching Disasters

```
1. Cache Penetration (Query for Non-Existent Key)
   [Client] ---> [Cache: MISS] ---> [Database: NOT FOUND]
   (Attacker queries negative IDs -> DB bombarded with uncacheable queries)

2. Cache Breakdown / Stampede (Hot Key Expiry)
   [10,000 Concurrent Clients] ---> [Hot Key EXPIRES] ---> [All 10,000 hit DB simultaneously]

3. Cache Avalanche (Mass Synchronized Expiry)
   [Bulk Keys Cached with TTL=3600s] ---> [At T=3600s, 100k keys vanish] ---> [DB collapse]
```

### Definitions & Mitigations:
1. **Cache Penetration**:
   - Queries for keys that do not exist anywhere in the database (e.g. `userId = -9999`).
   - Mitigation: **Bloom Filters** (guarantees a key does not exist without querying DB) or **Cache Null Values** with short TTL (e.g. 60 seconds).
2. **Cache Breakdown / Stampede (Thundering Herd)**:
   - A single hyper-popular key (e.g. flash sale banner, breaking news) expires.
   - 20,000 concurrent requests miss cache simultaneously and hit the database to rebuild the cache.
   - Mitigation: **Distributed Mutex Lock** (`SET key lock NX PX 5000`) or **Probabilistic Early Expiration (XFetch algorithm)**.
3. **Cache Avalanche**:
   - Thousands of cache keys share the identical expiration timestamp (e.g. all set to expire after 1 hour).
   - At $t=3600\text{s}$, the entire cache evaporates simultaneously.
   - Mitigation: **TTL Jitter** ($\text{TTL} = \text{base\_ttl} + \text{random}(0, \text{jitter})$).

---

## 2. Multi-Level Caching (Near-Cache + Remote Cache)

To achieve microsecond response times:
- **L1 (Local In-Memory Cache)**: Caffeine inside the JVM heap. Access time: $< 50\text{ns}$.
- **L2 (Distributed Shared Cache)**: Redis Cluster. Access time: $1 - 3\text{ms}$.
- **L3 (Persistent Database)**: PostgreSQL / Cassandra. Access time: $10 - 100\text{ms}$.

### Cache Coherence Challenge:
When Pod A updates an entity and invalidates Redis, how do Pod B and Pod C know their local JVM Caffeine caches are stale?
Solution: **Redis Pub/Sub Invalidation Bus**:
When any node mutates state, it publishes an invalidation topic event: `PUBLISH cache:invalidate:products product_123`. All subscriber pods evict `product_123` from their local Caffeine caches.

---

## 3. Redis Memory Management & Eviction Policies

Redis stores keys in memory using jemalloc allocator:
- **Memory Fragmentation Ratio (`mem_fragmentation_ratio`)**:
  $$\text{Ratio} = \frac{\text{used\_memory\_rss}}{\text{used\_memory}}$$
  - Ratio between 1.0 and 1.5 is healthy.
  - Ratio $> 1.8$ indicates severe OS memory fragmentation.
- **Eviction Policies (`maxmemory-policy`)**:
  - `volatile-lru`: Evict least recently used among keys with TTL set.
  - `allkeys-lru`: Evict least recently used across all keys.
  - `allkeys-lfu`: Evict least frequently used keys (optimal for caching).
  - `noeviction`: Throw errors when memory is full (standard for queues/state).
