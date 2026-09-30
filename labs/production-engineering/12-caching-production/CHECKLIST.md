# CHECKLIST: Caching Production Readiness
## Lab 12 | Production Engineering Academy

---

## 1. Expiration & Avalanche Defense
- [ ] Explicit TTL set on all cache writes.
- [ ] Randomized TTL jitter implemented ($\pm 15\%$).
- [ ] Cache stampede mutex or early refresh implemented on top 1% hot keys.
- [ ] Cache penetration mitigated with null-caching or Bloom filters.

## 2. Redis Operational Hygiene
- [ ] Dangerous commands (`KEYS`, `FLUSHALL`, `FLUSHDB`) disabled or renamed in `redis.conf`.
- [ ] Eviction policy explicitly set (e.g. `allkeys-lfu`).
- [ ] `maxmemory` configured to 75% of container RAM limit to leave room for replication backlog and OS page cache.
- [ ] Active defragmentation enabled (`activedefrag yes`).

## 3. Client & Serialization Standards
- [ ] Connection timeout ($\le 500\text{ms}$) and command timeout ($\le 250\text{ms}$) configured on Redis client.
- [ ] Jackson / Protobuf binary serialization used instead of slow, insecure Java native serialization.
- [ ] Redis connection pool properly sized (Lettuce non-blocking client preferred over blocking Jedis).
