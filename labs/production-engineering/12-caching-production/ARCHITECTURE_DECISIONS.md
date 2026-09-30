# ARCHITECTURE DECISIONS: Enterprise Distributed Caching Standards
## Lab 12 | Production Engineering Academy — Top 0.0001% Engineering

---

## ADR-01: Two-Tier Caching Architecture (JVM Heap L1 Caffeine + Distributed L2 Redis Cluster)

### Status: ACCEPTED
**Context & Problem Statement**:
High-frequency read queries (user sessions, tenant entitlements, catalog product details) generate over 150,000 QPS across our microservices fleet. Serving all read traffic against remote Redis clusters incurs a $1.2\text{ms}$ network hop, saturating NIC bandwidth and driving Redis CPU utilization above $85\%$. Conversely, caching purely inside JVM heap memory risks cache inconsistency across 80 Kubernetes pods and inflates JVM GC pause times.

### Decision
1. **Implement Hybrid Two-Tier Architecture**:
   - **Tier 1 (L1 Near-Cache)**: In-process Caffeine cache inside each JVM instance. Access latency: $< 50\text{ns}$.
   - **Tier 2 (L2 Shared Distributed Cache)**: 6-node Redis Cluster (3 Masters, 3 Replicas). Access latency: $0.8 - 1.5\text{ms}$.
   - **Tier 3 (Persistent Database)**: Aurora PostgreSQL / DynamoDB. Access latency: $10 - 30\text{ms}$.
2. **L1 Heap Constraint**:
   - L1 maximum size is strictly hard-capped at 20,000 entries or $256\text{MB}$ per JVM instance using Caffeine `maximumWeight` and `weigher` to prevent GC pressure.
   - L1 TTL is set to short durations ($\le 30\text{s}$) with active eviction.
3. **Coherence & Invalidation**:
   - Cache writes update DB, delete L2 Redis key, and publish eviction events via **Redis RESP3 Client Tracking** (or fallback Redis Pub/Sub invalidation bus).
   - All subscriber application pods evict the modified key from their local L1 Caffeine cache within $5\text{ms}$.

### Consequences
- **Positive**: 
  - Reduced Redis Cluster network ingress by $78\%$.
  - 99th percentile HTTP read latency dropped from $4.2\text{ms}$ to $0.45\text{ms}$ (served directly from JVM memory).
- **Negative / Trade-offs**:
  - Small temporary inconsistency window ($\le 10\text{ms}$) between pods during network partitions.
  - Requires maintaining Lettuce client-side tracking state and connection reconnect logic.

---

## ADR-02: Cache Stampede Mitigation: Probabilistic Early Expiration (XFetch) vs Distributed Mutex

### Status: ACCEPTED
**Context & Problem Statement**:
When a critical hot key (e.g., homepage layout, flash sale inventory counter) expires under 30,000 concurrent requests/sec, all concurrent threads experience a cache miss simultaneously. Using standard distributed locks (`SETNX`) causes thread starvation: thousands of incoming requests block waiting for the lock, saturating Tomcat/Undertow worker thread pools and triggering cascade HTTP 504 Gateway Timeouts.

### Decision
1. **Adopt Probabilistic Early Expiration (XFetch / Vattani 2015 Algorithm)** as the default stampede defense for high-throughput read operations:
   - Cached entries store both the value and their computed metadata: `cached_at`, `compute_time_delta_ms`, and `base_ttl_ms`.
   - When any reading thread queries the key, it evaluates:
     $$\Delta - \beta \cdot \ln(U) \cdot \delta > \text{TTL}$$
   - If condition evaluates to true, the thread triggers an asynchronous background refresh via a dedicated virtual thread / thread pool, while immediately serving the currently cached value to the user.
2. **Distributed Mutex Lock (`SETNX`) Fallback**:
   - Distributed mutex is reserved strictly for heavy, non-idempotent computational tasks (e.g., expensive reporting queries taking $> 2\text{s}$) where duplicate computation must be strictly avoided.
   - Lock timeout must have a strict upper bound (max 3,000ms) with non-blocking spin-wait (max 3 retries with exponential backoff).

### Consequences
- **Positive**:
  - Hot keys are refreshed transparently in the background *before* expiration.
  - Zero thread blocking, zero lock contention, zero thundering herd spikes on persistent databases.
- **Negative / Trade-offs**:
  - Cache payload size increases by ~24 bytes per key to store expiration calculation metadata.

---

## ADR-03: Cache Invalidation Strategy: Cache-Aside with Delayed Double Delete & CDC

### Status: ACCEPTED
**Context & Problem Statement**:
Synchronous dual-writes (updating DB and updating Cache) fail during network blips or unexpected exceptions. If the database commit succeeds but the cache update fails, the cache contains stale data indefinitely. Furthermore, updating cache directly without locks invites write-order race conditions ($W_1$ overwrites $W_2$ if network packets reorder).

### Decision
1. **Cache-Aside Pattern Enforcement**:
   - Application write operations **must NEVER update the cache directly**. They must only **DELETE (evict)** the cache key after committing to the database.
2. **Write Sequence Ordering**:
   - Step 1: Execute DB Transaction and Commit.
   - Step 2: Delete Key from Redis L2.
   - Step 3: Publish L1 Invalidation Message.
3. **Delayed Double Delete**:
   - For high-concurrency entities prone to read-write race conditions, an asynchronous scheduled task executes a secondary eviction $500\text{ms}$ after the initial delete to clear any stale cache state written by concurrent slow reads.
4. **CDC (Change Data Capture) Invalidation Pipeline**:
   - For legacy or distributed services that bypass our primary API layer, Debezium CDC reads PostgreSQL WAL logs and streams row mutations to Kafka topic `cache-invalidations`.
   - Dedicated invalidator consumers evict corresponding Redis and Caffeine keys.

### Consequences
- **Positive**:
  - Eliminates stale cache state caused by out-of-order write race conditions.
  - Prevents permanent inconsistency if an application node crashes during execution.
- **Negative / Trade-offs**:
  - Next subsequent read incurs a cache miss latency penalty to repopulate the warm cache.

---

## ADR-04: Serialization Standard: Jackson JSON vs Protobuf vs Kryo

### Status: ACCEPTED
**Context & Problem Statement**:
Standard Java native serialization (`java.io.Serializable`) is banned due to extreme security vulnerabilities (RCE deserialization gadgets), high CPU overhead, and massive byte payloads (often $10\times$ larger than raw data). Default Jackson JSON serialization produces large payloads that inflate Redis memory and network bandwidth.

### Decision
1. **Dual Serialization Strategy**:
   - **Internal High-Throughput & Hot Entities**: **Protobuf (Protocol Buffers v3)** or optimized Jackson with **Afterburner / Blackbird bytecode optimization** and Snappy/LZ4 compression for payloads $> 1\text{KB}$.
   - **General Domain Entities**: **Jackson JSON with explicit type information disabled** and polymorphic type handling strictly locked down via Safe White-listing (`BasicPolymorphicTypeValidator`).
2. **Compression Threshold**:
   - Any value exceeding $2\text{KB}$ must be compressed using **LZ4-Java** prior to Redis transmission.
   - Compression yields $60-80\%$ memory reduction on JSON/text payloads with less than $15\mu\text{s}$ CPU decompression overhead.

### Consequences
- **Positive**:
  - Cluster memory footprint reduced by $52\%$.
  - 10Gbps Redis NIC bandwidth usage decreased by $65\%$.
- **Negative / Trade-offs**:
  - CLI debugging requires deserialization scripts (cannot inspect raw Protobuf or LZ4 binary strings with `redis-cli get`).

---

## ADR-05: Hot Key Mitigation: Salted Sharding & Anti-Skew Topology

### Status: ACCEPTED
**Context & Problem Statement**:
A single viral key (e.g. `event:superbowl:score` or a mega-seller product ID) routed to one Redis cluster master can saturate the single CPU core event loop of that shard ($100\%$ CPU), causing request timeouts while the remaining 15 shards sit idle ($5\%$ CPU).

### Decision
1. **Dynamic Hot Key Detection**:
   - Monitor Redis via `hotkeys` sampling and client-side metrics (Micrometer counter per key prefix).
2. **Salted Key Sharding for Hyper-Hot Read Keys**:
   - Hot keys exceeding 10,000 QPS are replicated across $K$ sub-keys using a pseudorandom suffix:
     $$\text{Key}_i = \text{original\_key} + \text{"#"!} + \text{random}(1, K) \quad \text{where } K = 8$$
   - Each sub-key maps to a different hash slot and therefore distributes traffic across multiple Redis masters.
   - Invalidation must write a delete to all $K$ sub-keys (`DEL original_key#1 original_key#2 ... original_key#K`).
3. **Read Replica Offloading**:
   - Configure Lettuce connection pooling with `ReadFrom.REPLICA_PREFERRED` for read-only analytics or non-critical cache lookups.

### Consequences
- **Positive**:
  - Eliminates single-core CPU saturation during traffic surges.
  - Distributes read throughput linearly across the entire cluster.
- **Negative / Trade-offs**:
  - Increases eviction complexity (must evict all $K$ salted keys).

---

## ADR-06: Redis Cluster Resilience, Eviction Policy, and Failure Isolation

### Status: ACCEPTED
**Context & Problem Statement**:
When Redis memory fills up, the default `noeviction` policy throws OOM errors to application clients, breaking read/write flows. Conversely, unconstrained memory growth triggers Linux Out-Of-Memory Killer (`oom-killer`), violently terminating the Redis process.

### Decision
1. **Eviction Policy**:
   - Pure Caching Clusters must configure:
     ```conf
     maxmemory 12gb
     maxmemory-policy allkeys-lfu
     maxmemory-samples 10
     ```
   - State/Session Clusters must configure `volatile-ttl` or dedicated scaling without arbitrary eviction.
2. **Memory Allocation Safety**:
   - `maxmemory` must be set to $\le 75\%$ of total host/container RAM to reserve headroom for copy-on-write during BGSAVE, replication buffers, and jemalloc fragmentation.
3. **Dangerous Command Ban**:
   - Disable destructive commands via `redis.conf`:
     ```conf
     rename-command FLUSHALL ""
     rename-command FLUSHDB ""
     rename-command KEYS ""
     rename-command SHUTDOWN "SHUTDOWN_ADMIN_ONLY_SECURE_TOKEN"
     ```
4. **Lettuce Client Resilience**:
   - Set timeout: `timeout = 500ms`.
   - Enable adaptive topology refresh:
     ```java
     ClusterTopologyRefreshOptions.builder()
         .enableAdaptiveRefreshTrigger(RefreshTrigger.MOVED_REDIRECT, RefreshTrigger.PERSISTENT_RECONNECTS)
         .adaptiveRefreshTriggersTimeout(Duration.ofSeconds(10))
         .build();
     ```

### Consequences
- **Positive**:
  - Zero catastrophic event-loop locks from ad-hoc developer queries.
  - Automatic fast failover recovery within 5 seconds without application restarts.
