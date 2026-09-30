# INTERVIEW QUESTIONS: Distributed Caching Architecture & Redis at Scale
## Lab 12 | Senior / Staff / Principal & Chief Architect Level — Top 0.0001% Engineering

---

## Senior Level (5+ Years Experience)

### Q1: What are Cache Penetration, Cache Breakdown, and Cache Avalanche? How do you prevent each with production-grade rigor?
**Answer**:
1. **Cache Penetration**:
   - *Mechanics*: Incoming queries seek non-existent keys (e.g., negative IDs, SQL injection probes). The cache misses, the DB finds nothing, nothing is cached, and subsequent requests continuously pound the persistent database.
   - *Production Prevention*:
     - **Bloom Filters / Cuckoo Filters**: Maintained in front of the cache. If the filter says an ID does not exist, the request is rejected with 404 immediately with zero DB query. The optimal bit-array size is $m = -\frac{n \ln p}{(\ln 2)^2}$ where $n$ is expected elements and $p$ is acceptable false positive rate (e.g. $1\%$).
     - **Negative Caching**: Cache a sentinel null marker (`"@@NULL@@"`) with a short, aggressive TTL ($30 - 60$ seconds).
2. **Cache Breakdown (Stampede / Thundering Herd)**:
   - *Mechanics*: A single hyper-popular hot key expires under high concurrency ($10,000+$ QPS). All concurrent threads miss simultaneously and hammer the database with identical heavy queries.
   - *Production Prevention*:
     - **Probabilistic Early Expiration (XFetch algorithm)**: Computes dynamic background refresh probability based on compute cost $\Delta$ before key expires.
     - **Distributed Mutex Lock**: Only the single thread acquiring `SET lock:key token NX PX 3000` rebuilds the cache; all other threads sleep briefly or return stale data.
3. **Cache Avalanche**:
   - *Mechanics*: Millions of keys are initialized or refreshed with an identical static TTL (e.g., exactly 24 hours). At $t = 86400$, they all evaporate simultaneously, dumping 100% of read traffic onto the database.
   - *Production Prevention*:
     - **TTL Jitter**: Inject random noise: $\text{TTL} = \text{base\_ttl} \pm \text{random}(0, \text{jitter})$.
     - **Circuit Breaking**: Wrap database fallback queries in Resilience4j circuit breakers to shed load if database response times exceed SLA thresholds.

---

### Q2: Why is deleting the cache key AFTER updating the database preferred in Cache-Aside, and what rare race condition remains?
**Answer**:
If you **Delete Cache First, then Update DB**:
1. Thread A deletes the cache key.
2. Thread B queries the key, gets a cache miss, and reads the OLD value from DB.
3. Thread A updates the DB with the NEW value.
4. Thread B writes the OLD value back to the cache.
- **Result**: The cache holds stale data *permanently* until TTL expires!

If you **Update DB First, then Delete Cache**:
1. Thread A reads DB (old value).
2. Thread B updates DB with new value.
3. Thread B deletes the cache key.
4. Thread A writes old value to cache.
- **Why this race is statistically rare**: For Step 4 to overwrite the cache, the read query in Step 1 must take longer to execute than the entire database write + commit + network call + cache eviction in Steps 2 and 3 combined. Since DB writes are orders of magnitude slower than reads due to locking, WAL flushing, and replication, this window is vanishingly small ($< 0.001\%$).
- **Elimination of the remaining race**: Apply **Delayed Double Deletion** (evict key, commit DB, wait $500\text{ms}$ in background executor, evict key again) or use **Debezium WAL CDC** for asynchronous cache invalidation.

---

### Q3: How does Redis implement its LRU and LFU eviction algorithms internally?
**Answer**:
Redis does **NOT** maintain a true global doubly linked list of all keys in memory because the pointer overhead would consume an additional 16 to 24 bytes per key across millions of items.

Instead, Redis uses **Approximated LRU/LFU via Random Sampling**:
- Every `redisObject` stores a 24-bit field `unsigned lru:24`.
  - For **LRU**: Stores the server's current timestamp (resolution: 1 second).
  - For **LFU**: Upper 16 bits store the last decrement time (minutes), lower 8 bits store a logarithmic access counter (Logarithmic 8-bit counter $0-255$).
- **Eviction Process**:
  1. When memory exceeds `maxmemory`, Redis randomly selects $K$ candidate keys (default `maxmemory-samples 5`, recommended `10` in production).
  2. For LRU: Selects the key with the oldest timestamp in the sample.
  3. For LFU: Counter is decremented based on idle time, and the key with lowest frequency is evicted.
  4. With `maxmemory-samples 10`, approximated LRU converges to within $99\%$ mathematical equivalence of true global LRU at zero pointer memory overhead.

---

## Staff Level (8+ Years Experience)

### Q4: Explain the difference between Redis `embstr` and `raw` string encodings. Why does the threshold change at 44 bytes?
**Answer**:
A Redis string object consists of a `redisObject` metadata header and an `sdshdr` (Simple Dynamic String) header:
- `redisObject` is strictly 16 bytes: `type(4 bits) + encoding(4 bits) + lru(24 bits) + refcount(4 bytes) + *ptr(8 bytes)`.
- For short strings, Redis uses `sdshdr8`, which is 3 bytes: `len(1 byte) + alloc(1 byte) + flags(1 byte)`.
- Strings must also terminate with a null byte `\0` (1 byte) for compatibility with C standard library functions.

**The Math of 44 Bytes**:
- Modern operating systems and jemalloc allocate memory in power-of-two chunks: $8, 16, 32, 64$ bytes.
- A standard CPU cache line is exactly **64 bytes**.
- To store an entire Redis key in a single contiguous 64-byte memory chunk:
  $$\text{Max Payload} = 64\text{ bytes} - \text{sizeof(redisObject)} - \text{sizeof(sdshdr8)} - 1\text{ byte (\0)}$$
  $$\text{Max Payload} = 64 - 16 - 3 - 1 = 44\text{ bytes}$$

**Production Consequence**:
- **$\le 44$ bytes (`embstr`)**: Allocated via a single `malloc(64)`. The object header and string payload sit contiguously in memory. Reading it requires **one CPU cache line fetch** with zero pointer chasing.
- **$> 44$ bytes (`raw`)**: Requires two separate `malloc()` allocations. The `*ptr` pointer must be dereferenced, incurring an extra CPU L1/L2 cache miss.

---

### Q5: How does Redis Cluster route requests without a central coordinator? What is the difference between `-MOVED` and `-ASK`?
**Answer**:
Redis Cluster divides the keyspace into **16,384 hash slots**:
$$\text{Slot} = \text{CRC16}(\text{Key}) \pmod{16384}$$

1. **Topology Awareness**:
   Smart clients (Lettuce, Jedis) cache the slot-to-node routing table locally. When executing `GET user:100`, the client hashes the key to a slot and routes the TCP packet directly to the responsible master.
2. **`-MOVED slot host:port`**:
   - Returned when the client queries a node for a slot that has been **permanently migrated** to another node.
   - **Client Action**: The client updates its internal slot mapping table permanently and retries the command against the target node.
3. **`-ASK slot host:port`**:
   - Returned during an active, in-progress slot rebalancing operation where some keys for that slot have moved to the new node, but the slot migration is not yet finalized.
   - **Client Action**: The client sends an `ASKING` command to the target node (which tells it to accept this single command even though the slot isn't fully assigned), executes the command, but **does NOT update its internal slot routing table**.

---

### Q6: Why is Redlock controversial, and what are Martin Kleppmann's critique and Salvatore Sanfilippo's counter-arguments?
**Answer**:
The **Redlock** algorithm proposes acquiring locks across $N$ independent Redis masters (e.g. 5 nodes) using `SETNX`, requiring a majority quorum ($N/2 + 1 = 3$) within a timeout to guarantee safety.

**Martin Kleppmann's Critique (Distributed Systems Researcher)**:
Redlock assumes a **partially synchronous system model** (bounded network delays, bounded clock drift). In real production:
1. **Stop-the-World GC Pauses**: Thread A acquires the lock on 3 nodes with a 5-second TTL. JVM enters a 10-second Full GC pause. The lock expires. Thread B acquires the lock. Thread A wakes up, unaware time elapsed, and writes to storage, causing split-brain data corruption.
2. **System Clock Jumps**: NTP step changes can instantly expire leases on individual nodes, breaking quorum safety.
3. **Storage Fencing Tokens**: Distributed locks cannot guarantee mutual exclusion on external storage unless the storage engine verifies monotonic fencing tokens (`fencing_token > last_seen_token`). If storage supports fencing tokens, Redlock is redundant.

**Salvatore Sanfilippo (Antirez) Counter-Argument**:
1. In high-performance systems where storage engines do not support monotonic fencing tokens, Redlock provides practical, best-effort mutual exclusion when properly tuned with monotonic clocks (`CLOCK_MONOTONIC`) and reasonable TTL safety margins.

---

## Principal / Chief Architect Level (Top 0.0001%)

### Q7: Mathematically derive the XFetch Probabilistic Early Expiration algorithm. Why does it guarantee zero herd under arbitrary concurrency?
**Answer**:
Let:
- $\text{now}$: Current timestamp.
- $\text{expiry}$: Time at which the cached item is evicted.
- $\delta = \text{expiry} - \text{now}$: Time remaining until expiration.
- $\Delta$: Measured duration (computation cost) required to query DB and compute the value.
- $\beta > 0$: Tunable aggressiveness factor (typically $\beta = 1.0$).
- $U \sim \text{Uniform}(0, 1)$: Independent standard uniform random variable.

**The Decision Rule**:
A reading client triggers a background recomputation if and only if:
$$\Delta - \beta \cdot \ln(U) \cdot \delta > \text{TTL}$$
Rearranging for the probability of recomputation $P(\text{recompute})$ at remaining time $\delta$:
$$- \ln(U) > \frac{\text{TTL} - \Delta}{\beta \cdot \delta} \implies U < \exp\left(-\frac{\text{TTL} - \Delta}{\beta \cdot \delta}\right)$$
$$P(\text{recompute}) = \exp\left(-\frac{\text{TTL} - \Delta}{\beta \cdot \delta}\right)$$

**Behavioral Proof**:
1. When $\delta$ is large (key just cached): $\frac{\text{TTL} - \Delta}{\beta \cdot \delta}$ is large, so $P(\text{recompute}) \approx e^{-\infty} = 0$. Zero overhead.
2. As $\delta \to 0$ (approaching expiration): $\frac{\text{TTL} - \Delta}{\beta \cdot \delta} \to 0$, so $P(\text{recompute}) \to e^0 = 1.0$. Recomputation is guaranteed to occur.
3. Under high request rate $\lambda$ (e.g. $50,000$ RPS):
   - The time between successive requests is $1/\lambda = 20\mu\text{s}$.
   - The first request arriving in the early expiration window where $U < \exp(-\dots)$ acquires an in-memory boolean flag and triggers background refresh.
   - The expected number of duplicate recomputations across the entire expiration transition is mathematically bounded by:
     $$E[\text{recomputations}] \approx 1 + O\left(\frac{\Delta}{\text{TTL}}\right)$$
   - Since $\Delta \ll \text{TTL}$ ($50\text{ms} \ll 3600\text{s}$), $E[\text{recomputations}] \approx 1.000014$.
   - **Result**: Exactly one client recalculates the cache, zero locks are acquired, and no request experiences a cache miss.

---

### Q8: How does Redis 6+ Client-Side Caching (RESP3 Tracking) work, and how do you design an invalidation protocol that prevents broadcast storm degradation?
**Answer**:
Traditional Near-Cache setups (Caffeine L1 + Redis L2) use Redis Pub/Sub to broadcast invalidations, requiring dedicated connections and creating high CPU overhead on subscriber nodes.

**RESP3 Server-Assisted Client Tracking Architecture**:
Redis tracks which keys a client has read over its standard connection and proactively pushes invalidation frames:
```
CLIENT TRACKING on bcast prefixes 1 product:
```
1. **Default Mode (Keyspace Tracking)**:
   - Redis remembers every key queried by connection ID in an internal radix tree table (`TrackingTable`).
   - When key $K$ is modified, Redis pushes an invalidation message `PUSH "invalidate" [K]` to all clients that read $K$.
   - *Limitation*: Sizing the `TrackingTable` consumes server memory ($O(\text{keys} \times \text{clients})$).
2. **Broadcasting Mode (`BCAST`)**:
   - Redis tracks only key **prefixes** registered by clients (e.g. `product:`).
   - Redis does not store individual key-to-client mappings, saving massive memory.
   - When `product:942` is updated, Redis broadcasts invalidation to all clients registered for prefix `product:`.

**Mitigating Broadcast Storms**:
- In high-throughput write clusters, broadcasting every write inundates thousands of client connections with invalidation frames.
- **Top 0.0001% Architectural Solution**:
  1. **Hash Slot Prefixing**: Register tracking on coarse-grained slot prefixes rather than individual entity IDs.
  2. **Client-Side Message Deduplication Buffer**: Application pods buffer incoming invalidations in a high-speed lock-free ring buffer (Disruptor) and batch-evict Caffeine keys every $5\text{ms}$, preventing GC pressure from millions of discrete eviction tasks.
