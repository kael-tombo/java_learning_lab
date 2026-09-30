# PRODUCTION READINESS CHECKLIST: Distributed Caching & Redis
## Lab 12 | Go-Live Quality Gate | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Capacity Planning & Memory Sizing Math

- [ ] **Working Set Mathematical Sizing Verified**:
  - Catalog size $N$ and target hit ratio $H$ calculated using Zipfian distribution formula:
    $$C = N^H \quad (\text{for } \alpha = 1.0)$$
  - Confirmed that Redis cluster capacity accommodates the 95th percentile working set with $2.5\times$ growth headroom.
- [ ] **Physical RAM vs `maxmemory` Ceiling**:
  - `maxmemory` configured to **strictly $\le 75\%$** of container/host physical memory.
  - Remaining $25\%$ explicitly reserved for:
    - Kernel socket buffers (`tcp-wmem`, `tcp-rmem`).
    - Copy-on-Write (COW) memory dirtied during `BGSAVE` or `BGREWRITEAOF`.
    - Replication backlog buffer (`repl-backlog-size`).
    - jemalloc unmapped heap fragmentation.
- [ ] **Active Defragmentation Configured**:
  - Confirmed `activedefrag yes` is enabled with production-grade bounds:
    ```conf
    activedefrag yes
    active-defrag-ignore-bytes 100mb
    active-defrag-threshold-lower 10
    active-defrag-threshold-upper 30
    active-defrag-cycle-min 5
    active-defrag-cycle-max 50
    ```

---

## 2. Stampede, Avalanche, & Penetration Hardening

- [ ] **Zero Static TTL Policy (Anti-Avalanche)**:
  - Every cached entity appends dynamic pseudorandom jitter ($\pm 15\%$ to $\pm 25\%$):
    $$\text{TTL}_{\text{effective}} = \text{TTL}_{\text{base}} \pm \text{Random}(0, \text{jitter})$$
  - Prohibited: Synchronized cron jobs refreshing millions of keys with the exact same millisecond TTL.
- [ ] **High-QPS Hot Key Stampede Defense**:
  - Keys receiving $> 2,000$ QPS utilize **Probabilistic Early Expiration (XFetch algorithm)** or distributed mutex locking.
  - Verified that background recomputation threads run on bounded worker pools and never block incoming user HTTP requests.
- [ ] **Cache Penetration Protection**:
  - All non-existent entity lookups either:
    1. Pass through a Guava / Redis **Bloom Filter** with false positive probability $p \le 0.01$.
    2. Cache a sentinel null marker (`"@@NULL@@"`) with a hard-capped $60$-second TTL.
- [ ] **Hot Key Sharding (Anti-Skew)**:
  - Viral keys exceeding 10,000 QPS are salted across $K \ge 8$ sub-keys (`key#0` to `key#7`) to prevent single-shard CPU saturation.

---

## 3. Invalidation & Multi-Tier Coherence

- [ ] **Cache-Aside Write Sequence Enforced**:
  - Application updates database **first**, commits transaction, and **then evicts** the cache key.
  - Writing directly to cache on mutate is strictly forbidden.
- [ ] **Delayed Double Deletion or CDC Invalidation**:
  - Highly concurrent entities implement an asynchronous secondary deletion $500\text{ms}$ after commit, or consume Debezium WAL events from Kafka.
- [ ] **L1 JVM Near-Cache Isolation**:
  - Caffeine L1 caches bounded by `maximumWeight` ($\le 256\text{MB}$ per JVM instance).
  - Outgoing invalidations carry `senderInstanceId` to prevent self-invalidation thrashing.
  - L1 TTL set to short durations ($\le 30\text{s}$) to bound partition inconsistency.

---

## 4. Redis Engine & Cluster Topology Hardening

- [ ] **Dangerous Command Renaming / Disabling**:
  - Production `redis.conf` or cloud parameter groups have explicitly disabled:
    ```conf
    rename-command KEYS ""
    rename-command FLUSHALL ""
    rename-command FLUSHDB ""
    rename-command SHUTDOWN "SHUTDOWN_ADMIN_ONLY_SECURE_TOKEN"
    ```
- [ ] **Eviction Policy Explicitly Declared**:
  - Pure cache clusters configured with:
    ```conf
    maxmemory-policy allkeys-lfu
    maxmemory-samples 10
    ```
  - `noeviction` strictly banned on cache tiers.
- [ ] **Replication Backlog Buffer Sized for Worst-Case Network Blip**:
  - Backlog sized to prevent full resync (`PSYNC`) during a 10-minute network split:
    $$\text{Backlog Size} \ge \text{Peak Write Rate (Bytes/sec)} \times 600\text{ seconds}$$
  - Minimum standard: `repl-backlog-size 512mb`.
- [ ] **Network Split Protection**:
  - Master rejects writes if replicas disconnect:
    ```conf
    min-replicas-to-write 1
    min-replicas-max-lag 10
    ```

---

## 5. Client Library & Connection Tuning

- [ ] **Non-Blocking Client Architecture**:
  - **Lettuce** (Netty non-blocking async) used instead of legacy blocking Jedis.
- [ ] **Timeout Hierarchy Defined**:
  - Connection Timeout: $\le 500\text{ms}$.
  - Command Timeout: $\le 200\text{ms}$ (fail fast rather than starving web worker threads).
- [ ] **Adaptive Topology Refresh Enabled**:
  - Lettuce cluster client configured with:
    ```java
    ClusterTopologyRefreshOptions.builder()
        .enablePeriodicRefresh(Duration.ofMinutes(5))
        .enableAdaptiveRefreshTrigger(RefreshTrigger.MOVED_REDIRECT, RefreshTrigger.PERSISTENT_RECONNECTS)
        .adaptiveRefreshTriggersTimeout(Duration.ofSeconds(10))
        .build();
    ```
- [ ] **Safe Serialization & Compression Standard**:
  - Java Native Serialization (`Serializable`) strictly banned.
  - Protobuf or Jackson JSON with polymorphic type safety configured.
  - Payloads $> 2\text{KB}$ compressed with LZ4.

---

## 6. Observability, SLIs, & Production Alerting Thresholds

| Metric | Prometheus Query | Warning Threshold | Critical Page Threshold |
|---|---|---|---|
| **Cache Hit Ratio** | `rate(cache_requests{result="hit"}[5m]) / rate(cache_requests[5m])` | $< 92\%$ | $< 80\%$ |
| **Redis Shard CPU** | `redis_cpu_sys_seconds_total + redis_cpu_user_seconds_total` | $> 75\%$ | $> 90\%$ |
| **Memory Fragmentation** | `redis_mem_fragmentation_ratio` | $> 1.6$ | $> 2.0$ or $< 1.0$ (Swap) |
| **Eviction Velocity** | `rate(redis_evicted_keys_total[1m])` | $> 1,000/\text{sec}$ | $> 5,000/\text{sec}$ |
| **Replication Lag** | `redis_connected_slaves_offset - redis_master_repl_offset` | $> 10\text{MB}$ | $> 50\text{MB}$ |
| **Slowlog Commands** | `redis_slowlog_length` | $> 10/\text{min}$ | $> 50/\text{min}$ |
| **P99 Read Latency** | `histogram_quantile(0.99, rate(redis_command_latency_seconds_bucket[1m]))` | $> 5\text{ms}$ | $> 25\text{ms}$ |
