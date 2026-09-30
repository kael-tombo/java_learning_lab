# ARCHITECTURE DECISIONS: Enterprise Caching Standards
## Lab 12 | Production Engineering Academy

---

## ADR-01: Multi-Tier Caching & Stampede Prevention Standards

### Status: ACCEPTED

### Context
Outages during promotional traffic spikes were repeatedly traced to cache stampedes on hot catalog keys and cache avalanches following batch jobs.

### Decisions
1. **TTL Jitter Standard**:
   - Every cached entity must append a random jitter between 10% and 25% of its base TTL.
   - Synchronized static TTLs are strictly prohibited.
2. **Cache Stampede Prevention Mandate**:
   - High-throughput read endpoints must implement distributed mutex rebuild or probabilistic early refresh (XFetch).
3. **Redis Cluster Topology**:
   - Redis deployments must run as a minimum 3-shard, 3-replica Redis Cluster.
   - Maximum memory policy: `allkeys-lfu` for cache clusters.
   - `KEYS`, `FLUSHALL`, `FLUSHDB` disabled via `rename-command` in production.

### Consequences
- Eliminates database collapse during promotional flash events.
- Prevents accidental developer command execution from blocking the Redis event loop.
