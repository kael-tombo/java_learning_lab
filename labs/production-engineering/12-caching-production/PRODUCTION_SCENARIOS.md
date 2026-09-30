# PRODUCTION SCENARIOS: Caching & Redis Incidents
## Lab 12 | Production Engineering Academy

---

## Scenario 1: The Super Bowl Hot-Key Cache Breakdown

### Context
A video streaming and sports betting platform. During a live championship game, the odds for "Next Touchdown Scorer" were cached in Redis with a 30-second TTL:
`Key: odds:superbowl:player_87, TTL: 30s`

### The Outage
- Traffic reached 45,000 requests/second on that single player.
- At $t=30.000\text{s}$, the Redis key expired.
- Within 100 milliseconds, over 4,500 concurrent threads in the Java fleet encountered a cache MISS.
- All 4,500 threads executed the heavy aggregation query against the primary PostgreSQL database:
  `SELECT calculate_live_odds(87, NOW());` (A query taking 250ms).
- PostgreSQL connection pool instantly locked up with 400 active running backends.
- Database CPU hit 100%, query latency degraded from 250ms to 45 seconds.
- The entire sports platform collapsed during the most lucrative commercial break of the year.

### The Fix: Mutex Cache Rebuild with Probabilistic Early Expiry
1. **Distributed Mutex Lock**: When a cache miss occurs, only the single thread that acquires the lock `lock:odds:superbowl:player_87` is allowed to query the database. All other 4,499 threads wait 50ms or return the slightly stale cached value.
2. **Probabilistic Early Rebuild (XFetch)**:
   $$\text{rebuild if } -\beta \times \delta \times \ln(\text{random}()) > (\text{expiry} - \text{now})$$
   A background thread proactively refreshes the cache *before* it officially expires.

---

## Scenario 2: The Redis Memory Fragmentation OOMKill

### Context
A session management Redis cluster running on AWS EC2 with 32 GB RAM. Memory usage was reported by application metrics as `used_memory: 14 GB`.

### The Disaster
- Linux kernel OOM Killer abruptly terminated the Redis master process!
- Why? While Redis was storing 14 GB of actual keys, `used_memory_rss` was **31.5 GB**!
- Memory fragmentation ratio was **2.25**.
- Millions of small string allocations and continuous deletions caused jemalloc to accumulate un-freed empty pages.

### The Fix
1. Enabled active defragmentation in Redis configuration:
   `activedefrag yes`, `active-defrag-ignore-bytes 100mb`, `active-defrag-threshold-lower 10`.
2. Pack small strings into Redis Hashes (`HSET`) to take advantage of compact memory-efficient ziplist representations.
