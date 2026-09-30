# PRODUCTION SCENARIOS: Real-World Caching & Redis Incidents
## Lab 12 | Production Engineering Academy — Top 0.0001% Engineering

---

## Scenario 1: The Black Friday Single-Shard Event-Loop Starvation

### Incident Overview
- **Impact**: Global checkout and product detail page unavailable for 38 minutes during peak Black Friday sales. Estimated revenue loss: $1.4M.
- **Affected System**: 16-node AWS ElastiCache Redis Cluster (8 Masters, 8 Replicas) supporting the e-commerce storefront.
- **Symptoms**: P99 HTTP latency jumped from $12\text{ms}$ to $8,500\text{ms}$. Error rates on `/products/{id}` spiked to $78\%$ with `RedisCommandTimeoutException: Command timed out after 1000ms`.

### Timeline & Telemetry Analysis
```
08:00:00 - Door-buster deal goes live: 65-inch 4K TV discounted by 70% (productId: 984210).
08:01:15 - Global traffic surges to 120,000 QPS.
08:02:00 - Telemetry reveals Redis Shard 4 CPU hits 100%, while Shards 0-3 and 5-7 remain at < 8% CPU!
08:03:30 - Lettuce client connection pool on 60 Spring Boot pods exhausts. Netty worker threads back up.
08:05:00 - Database CPU remains low (12%), confirming the bottleneck is inside Redis, not PostgreSQL.
08:12:00 - SRE executes: `redis-cli -h shard-4.redis -p 6379 --hotkeys`
           Output: [00.00%] Hot key 'product:984210' found with 84,200 accesses/min.
08:24:00 - Emergency traffic shed deployed at Cloudflare Edge to drop 50% of traffic to that product.
08:38:00 - Hotfix deployed enabling dynamic L1 Caffeine near-cache. Shard 4 CPU drops to 14%. Incident resolved.
```

### Forensic Root Cause
1. **Hash Slot Concentrated on Single Master**:
   `CRC16("product:984210") mod 16384` mapped to Slot 12110, located on Shard 4.
2. **Single-Thread Event Loop Constraint**:
   Because Redis command execution is single-threaded, Shard 4 was processing over 45,000 commands/second on that single key. Network socket I/O and command parsing saturated the single CPU core.
3. **No Local In-Memory Buffer**:
   Application pods did not have an L1 in-memory cache; every HTTP request made a remote Redis network call.

### The Remediation & Permanent Architecture Fix
1. **Dynamic L1 Near-Cache (Caffeine)**:
   Enabled an in-heap Caffeine cache on all 60 Java pods with a 15-second TTL. The 45,000 QPS dropped from Redis to less than 4 QPS per pod reaching Shard 4.
2. **Salted Sharding for Viral Keys**:
   When any key exceeds 5,000 QPS, the application layer splits the key into 8 salted shards (`product:984210#0` to `product:984210#7`), distributing load across all 8 cluster masters.

---

## Scenario 2: The Redis Memory Fragmentation OOMKill & Replication Buffer Explosion

### Incident Overview
- **Impact**: Full Redis Cluster failover loop; all 4 master nodes crash within 3 minutes of each other.
- **Affected System**: 4-node Redis Cluster running on Linux VMs with 32 GB RAM per host.
- **Root Cause**: Memory fragmentation combined with replication buffer explosion during `BGSAVE` snapshotting.

### Incident Chronology
1. **The State Before Crash**:
   - `info memory` showed:
     - `used_memory: 16.2 GB` (actual size of stored key-values)
     - `used_memory_rss: 29.8 GB` (resident set size allocated by OS)
     - `mem_fragmentation_ratio: 1.84`
2. **The Trigger**:
   - At 03:00:00, automated backup triggered a background RDB snapshot (`BGSAVE`).
   - Redis executed `fork()`. The Linux kernel duplicated the page table using Copy-On-Write (COW).
3. **The Cascade**:
   - High write traffic (40,000 writes/sec) dirtied memory pages continuously.
   - Because memory was severely fragmented, every 1-byte write caused jemalloc to copy an entire 4KB or 2MB OS memory page.
   - Host physical RAM reached $100\%$. The Linux Kernel Out-Of-Memory Killer was invoked:
     ```
     kernel: [129481.102] Out of memory: Kill process 18239 (redis-server) score 948 or sacrifice child
     kernel: [129481.103] Killed process 18239 (redis-server) total-vm:34521400kB, anon-rss:31458924kB
     ```
4. **The Replica Thundering Herd**:
   - The replica node detected master death and triggered failover.
   - The surviving nodes attempted to synchronize replication backlog buffers, exceeding `client-output-buffer-limit slave` thresholds, triggering full resync (`PSYNC`) and crashing the remaining nodes in sequence!

### The Architectural Safeguards
1. **Active Defragmentation Configuration**:
   ```conf
   activedefrag yes
   active-defrag-ignore-bytes 100mb
   active-defrag-threshold-lower 10
   active-defrag-threshold-upper 30
   active-defrag-cycle-min 5
   active-defrag-cycle-max 50
   active-defrag-max-scan-fields 1000
   ```
2. **Strict Memory Limits**:
   Configured `maxmemory 20gb` on a 32GB host, leaving 12GB of buffer strictly for fork copy-on-write and replication stream buffers.
3. **Replication Buffer Protection**:
   Increased replication backlog buffer from default 1MB to 512MB:
   ```conf
   repl-backlog-size 512mb
   client-output-buffer-limit replica 1gb 512mb 300
   ```

---

## Scenario 3: The Stale Inventory Ghost & The Double-Deletion Race

### Incident Overview
- **Impact**: Flash sale for limited sneakers resulted in 1,420 pairs sold when physical stock was strictly 500 pairs. Company had to issue refunds and $50 apology coupons ($71,000 cost).
- **Architecture**: Cache-Aside with PostgreSQL as source of truth and Redis caching remaining stock.

### Forensic Sequence of Events
```
Timeline:
T0: Remaining Stock in DB = 1. Remaining Stock in Redis = 1.
T1: Customer A and Customer B click "Buy" at the exact same millisecond.
T2: Thread A updates DB: stock = stock - 1 (stock becomes 0). Transaction commits.
T3: Thread A attempts to delete Redis key: `DEL item:inventory:402`.
    Network hiccup occurs between App Pod 1 and Redis cluster; packet is dropped.
T4: Thread A logs a warning but HTTP 200 is returned to Customer A.
T5: Customer C queries product page.
    Redis returns stale stock = 1!
T6: Customer C clicks "Buy". Application passes optimistic check based on cached stock.
    Database lock queue backs up, and concurrent threads read stale values from cache.
```

### Why Standard Cache-Aside Fails Under Concurrency
Developers assumed that deleting the cache key upon DB write guarantees consistency. In reality:
1. Network drops or timeout exceptions during `DEL` leave stale data in cache until TTL expires.
2. Read-Write races: A concurrent slow read (`SELECT`) can execute before the DB write, pause during JVM GC pause, and overwrite the cache *after* the writer has already deleted the key!

### The Production Fix: Atomic Redis Lua Invalidation + CDC
1. **Never Cache Critical Transactional Counters via Cache-Aside**:
   Inventory counters must be decremented atomically directly inside Redis using Lua scripts:
   ```lua
   -- Atomic Inventory Decrement Script
   local stock = redis.call('get', KEYS[1])
   if not stock or tonumber(stock) <= 0 then
       return -1
   end
   return redis.call('decr', KEYS[1])
   ```
2. **Debezium WAL-Driven Cache Eviction**:
   Even if application pods crash during network operations, Debezium streams PostgreSQL WAL commits to Kafka. A dedicated, idempotent consumer pool guarantees eventual cache eviction within 25ms.

---

## Scenario 4: The 02:00:00 AM Synchronized Cache Avalanche

### Incident Overview
- **Impact**: Multi-AZ Aurora PostgreSQL cluster CPU spiked to 100%, causing automatic failover and dropping all active connections across 40 microservices. Total downtime: 19 minutes.
- **Root Cause**: Synchronized static TTL expiration across 2,400,000 product recommendations.

### Forensic Telemetry
```
01:59:58 - Database Read IOPS: 450. Cache Hit Ratio: 99.4%.
02:00:00 - Cache Hit Ratio plunges to 4.1% in 500 milliseconds!
02:00:01 - Database Read IOPS surges from 450 to 78,500.
02:00:03 - Aurora primary node CPU hits 100%. Thread pool exhausted (max_connections=5000 hit).
02:00:08 - Health check pings fail. AWS Aurora triggers unplanned Multi-AZ reboot and failover.
02:05:00 - SRE on-call paged. All pods throwing ConnectionPoolTimeoutException.
```

### The Root Cause Discovery
A nightly batch job ran at 02:00 AM every morning to compute recommendation matrices. The batch job inserted 2.4 million keys with a fixed, static TTL:
```java
// THE DEADLY CODE:
redisTemplate.opsForValue().set("recs:" + userId, json, Duration.ofDays(1));
```
Because all 2.4 million records were written between 01:55 AM and 02:00 AM the previous night, they all had an exact expiration time of 02:00:00 AM. When the clock struck 02:00:00, Redis evicted all 2.4 million keys within seconds. Every subsequent user recommendation request resulted in a cold database miss.

### The Mitigation: TTL Jitter Formula + Circuit Breaking
1. **Mandatory TTL Jitter Injection**:
   ```java
   public Duration calculateJitteredTtl(Duration baseTtl, double jitterFactor) {
       long baseSeconds = baseTtl.toSeconds();
       long maxJitter = (long) (baseSeconds * jitterFactor);
       long jitter = ThreadLocalRandom.current().nextLong(-maxJitter, maxJitter + 1);
       return Duration.ofSeconds(baseSeconds + jitter);
   }
   ```
   For a 24-hour TTL with a $20\%$ jitter factor, keys expire smoothly across an 8-hour window (between 19.2 hours and 28.8 hours), eliminating all synchronized cliff edges.
2. **Resilience4j Circuit Breaker on DB Fallback**:
   If database latency exceeds $500\text{ms}$ or failure rate exceeds $30\%$, the circuit breaker opens immediately and returns a fallback cached static default recommendation list, preventing DB collapse.
