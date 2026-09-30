# THEORY: Distributed Caching Architecture & Redis Internals at Scale
## Lab 12 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Mathematical Foundations of Caching

### 1.1 Access Distributions and Cache Sizing: Zipf's Law
Real-world data access follows a power-law distribution known as **Zipf's Law**. The probability $P(r)$ of accessing the $r$-th most popular item among $N$ total items is:

$$P(r) = \frac{1}{r^\alpha \sum_{n=1}^N \frac{1}{n^\alpha}}$$

Where:
- $\alpha \approx 0.7 - 1.2$ for web traffic, e-commerce catalog access, and social network feeds.
- When $\alpha = 1.0$, the top $20\%$ of items account for approximately $80\%$ of all requests (Pareto Principle).
- When $\alpha \to 0$, access is completely uniform (caching gives almost zero hit rate advantage).
- When $\alpha > 1.2$, the skew is extreme: a tiny working set ($< 2\%$ of items) captures $> 95\%$ of all queries.

#### Cache Hit Ratio as a Function of Cache Size $C$
For a cache holding $C$ items using optimal or near-optimal eviction (e.g., LFU / W-TinyLFU):

$$\text{Hit Ratio}(C) \approx \frac{\sum_{r=1}^C r^{-\alpha}}{\sum_{r=1}^N r^{-\alpha}} \approx \frac{C^{1-\alpha} - 1}{N^{1-\alpha} - 1} \quad (\text{for } \alpha \neq 1)$$

$$\text{Hit Ratio}(C) \approx \frac{\ln(C)}{\ln(N)} \quad (\text{for } \alpha = 1)$$

#### Sizing Rule for Target Hit Ratio $H$:
To guarantee hit ratio $H \in (0, 1)$ when $\alpha = 1$:
$$C = N^H$$

> **Example**: With a catalog of $N = 10,000,000$ products ($10\text{M}$ items) under Zipf $\alpha = 1.0$:
> - To achieve an $80\%$ hit ratio ($H = 0.8$): $C = (10^7)^{0.8} = 10^{5.6} \approx 398,107$ keys.
> - To push from $80\%$ to $95\%$ hit ratio ($H = 0.95$): $C = (10^7)^{0.95} = 10^{6.65} \approx 4,466,835$ keys.
> - **Insight**: Gaining the extra $15\%$ hit ratio requires an **$11.2\times$ increase in RAM capacity**.

---

### 1.2 The Latency Penalty Theorem
The effective average latency of a cached system $T_{\text{eff}}$ is:

$$T_{\text{eff}} = H \cdot T_{\text{cache}} + (1 - H) \cdot (T_{\text{cache}} + T_{\text{DB}} + T_{\text{fill}})$$

Where:
- $H$ is the cache hit ratio.
- $T_{\text{cache}}$ is the cache round-trip lookup latency ($0.05\text{ms}$ for L1 Caffeine, $1.2\text{ms}$ for Redis L2).
- $T_{\text{DB}}$ is the persistent database query latency ($15\text{ms}$).
- $T_{\text{fill}}$ is the cost of serializing and writing the miss back into the cache ($1.0\text{ms}$).

When cache hit ratio degrades:
```
Hit Ratio (H) | Effective Latency (L1+L2+DB) | DB QPS Multiplier (vs H=99%)
------------- | ----------------------------- | -----------------------------
99.9%         | 1.21 ms                       | 1.0x (Baseline)
95.0%         | 2.01 ms                       | 50.0x DB traffic spike
90.0%         | 2.82 ms                       | 100.0x DB traffic spike
80.0%         | 4.44 ms                       | 200.0x DB traffic spike
0.0% (Outage) | 17.20 ms                      | 1000.0x DB load (Cascade Failure)
```
**Key Takeaway**: A cache hit ratio drop from $99\%$ to $90\%$ does not mean a $10\%$ performance penalty; it means a **$10\times$ increase in DB throughput load**.

---

## 2. Eviction Algorithms: From LRU to W-TinyLFU

### 2.1 The Limits of Classic LRU & LFU
- **LRU (Least Recently Used)**: Evicts the item that has not been accessed for the longest time.
  - *Weakness*: Vulnerable to **scan pollution**. A batch job reading 100,000 cold records flushes the entire warm cache out of memory.
- **LFU (Least Frequently Used)**: Tracks total access frequency counters.
  - *Weakness*: Suffers from **historical bias**. A key accessed 100,000 times during a Black Friday spike remains in cache forever, blocking fresh warm items because its frequency never decays. Also high memory overhead ($4-8$ bytes per key for frequency counters).

---

### 2.2 W-TinyLFU (Window TinyLFU — Caffeine Cache Architecture)
Used by **Caffeine** (the gold standard JVM cache by Ben Manes). It combines the recency protection of LRU with the frequency retention of LFU while bounding memory to $\sim 8$ bytes per cache entry:

```
[ New Entries ] 
       │
       ▼
┌──────────────────────────────────────────────┐
│  Window Cache (Small LRU: ~1% of Total Size) │
└──────────────────────────────────────────────┘
       │  (Evicted from Window)
       ▼
   [ Candidate vs Victim Duel ] <─────── [ Count-Min 4-bit Sketch ]
       │                                  (Estimates Frequency in 4 bits)
       ▼
┌──────────────────────────────────────────────┐
│  Main Cache: Protected SLRU (~79% of Size)   │
│  Main Cache: Probationary SLRU (~20% of Size)│
└──────────────────────────────────────────────┘
```

1. **Count-Min 4-bit Sketch**:
   - Uses 4 hash functions mapping keys into a 2D array of 4-bit saturation counters (max count = 15).
   - Consumes only **8 bits per item** regardless of access count.
2. **Frequency Halving (Decay)**:
   - When the total number of accesses reaches sample size $W$, all 4-bit counters across the sketch are shifted right by 1 bit (halved: $c = \lfloor c/2 \rfloor$).
   - This evicts stale historical popularity automatically.
3. **The Admission Policy (Duel)**:
   - When the Window Cache overflows, the evicted item is a *Candidate*.
   - The *Victim* is the oldest item in the Probationary Main Cache.
   - Caffeine queries the Count-Min Sketch:
     $$\text{Frequency}(\text{Candidate}) > \text{Frequency}(\text{Victim})$$
   - If Candidate wins, Victim is evicted and Candidate is admitted to Probationary SLRU.
   - If Victim wins, Candidate is dropped immediately. **Scan pollution is mathematically impossible**.

---

## 3. Cache Invalidation & Consistency Patterns

### 3.1 Pattern Comparison Matrix

| Pattern | Read Path | Write Path | Inconsistency Window | Failure Mode |
|---|---|---|---|---|
| **Cache-Aside (Lazy Loading)** | App reads Cache $\to$ misses $\to$ reads DB $\to$ populates Cache | App writes DB $\to$ App deletes Cache | Concurrency race between Read miss & Write | Cache stale until TTL expiry if delete fails |
| **Read-Through** | App calls Cache Provider $\to$ Cache Provider reads DB transparently | Same as Cache-Aside or Write-Through | Minimal (encapsulated) | Cache library failure blocks read path |
| **Write-Through** | Read Cache $\to$ misses $\to$ Read DB | App writes Cache $\to$ Cache writes DB synchronously before returning | None (linearized) | Write latency increased by $(T_{\text{cache}} + T_{\text{DB}})$ |
| **Write-Behind (Write-Back)** | Read Cache | App writes Cache (async dirty queue) $\to$ background batch flushes to DB | High (data lives in cache memory only) | **Permanent data loss** if cache crashes before dirty flush |
| **Change Data Capture (CDC)** | Read Cache | App writes DB $\to$ DB WAL parsed by Debezium $\to$ Kafka $\to$ Cache Invalidator | Async replication lag ($\sim 10-50\text{ms}$) | Kafka lag leads to temporary eventual consistency |

---

### 3.2 The Fundamental Dual-Write Problem
In Cache-Aside, why must you **Update Database First, then Delete Cache Key** instead of deleting cache key first?

#### Case A: Delete Cache First, Then Update DB (VULNERABLE)
```
Thread A (Writer)          Thread B (Reader)           Database         Cache
       │                           │                      │               │
  1. Delete Key ──────────────────────────────────────────┼───────────────► [DELETED]
       │                           │                      │               │
       │                      2. Read Key (MISS) ─────────┼───────────────► [MISS]
       │                      3. Read Old Value ◄─────────┤ (Reads v=1)   │
       │                           │                      │               │
  4. Update Value ────────────────────────────────────────► (Writes v=2)  │
       │                           │                      │               │
       │                      5. Set Key (v=1) ───────────────────────────► [STALE v=1!]
       ▼                           ▼                      ▼               ▼
Result: DB has v=2, but Cache holds v=1 permanently until TTL expiry!
```

#### Case B: Update DB First, Then Delete Cache (ROBUST)
```
Thread A (Reader)          Thread B (Writer)           Database         Cache
       │                           │                      │               │
  1. Read Key (MISS) ─────────────────────────────────────┼───────────────► [MISS]
  2. Read Old Value ◄─────────────────────────────────────┤ (Reads v=1)   │
       │                           │                      │               │
       │                      3. Update DB (v=2) ─────────► (Writes v=2)  │
       │                      4. Evict Cache ─────────────────────────────► [EVICTED]
       │                           │                      │               │
  5. Set Cache (v=1) ─────────────────────────────────────────────────────► [WRITES v=1]
```
> **Theoretical Race in Case B**: Step 5 could overwrite cache with stale `v=1` **only if** Step 5 happens after Step 4, meaning the DB read in Step 2 took longer than the entire DB write + network roundtrip + cache eviction in Steps 3 and 4 combined. Because a DB write is significantly slower than a DB read, this race is statistically rare ($< 0.001\%$).
> **Production Protection**: Adding a **Delayed Double Deletion** (evict key, update DB, wait $500\text{ms}$, evict key again asynchronously) or utilizing **CDC (Debezium + Kafka)** eliminates even this tiny theoretical window.

---

## 4. Probabilistic Early Expiration: The Optimal Stampede Solution

When a hot key expires under $20,000$ concurrent requests/sec, distributed mutexes (`SETNX`) introduce serialization bottlenecks and thread queuing.

The mathematically optimal solution was published in **VLDB 2015 by Vattani, Chierichetti, and Lowenstein**:
**Optimal Probabilistic Cache Stampede Mitigation (XFetch Algorithm)**.

### Mathematical Formulation:
Instead of serving a key until it expires and then panicking, clients probabilistically recalculate and refresh the cache **before** expiration, proportional to the computing cost $\Delta$ and key access rate:

$$\Delta - \beta \cdot \ln(U) \cdot \delta > \text{TTL}$$

Where:
- $\Delta$: Time taken to compute/fetch the value from the database (in milliseconds).
- $\beta > 0$: Aggressiveness parameter (default $\beta = 1.0$).
- $U \sim \text{Uniform}(0, 1)$: Pseudorandom variable between $0$ and $1$.
- $\delta$: Remaining time until key expiration in milliseconds ($\text{expire\_at} - \text{now}$).
- $\text{TTL}$: Total key lifespan configured.

```
Remaining TTL (δ)    -ln(U) (Random sample)    Probabilistic Recompute Triggered?
─────────────────    ──────────────────────    ───────────────────────────────────
3000 ms              0.1 (common)              No  (Value served from cache)
500 ms               1.5 (moderate)            No  (Value served from cache)
100 ms               3.8 (rare)                YES (1 background thread recomputes)
10 ms                0.5                       YES (Immediate pre-expiry refresh)
```
- **Proof of Zero Herd**: The probability of at least one client triggering recomputation approaches $1.0$ as $\delta \to 0$, while the probability of *multiple* clients triggering simultaneously is strictly bounded and near-zero.
- **Result**: Exactly **one** client refreshes the cache in the background while all other concurrent clients receive sub-millisecond cached responses. The key never experiences a cache miss.

---

## 5. Redis Internal Memory Architecture & Data Structures

Redis is single-threaded for command execution (using an `epoll`/`kqueue` non-blocking I/O multiplexer event loop), but internal data encoding dictates memory density and CPU cache efficiency.

### 5.1 Simple Dynamic String (SDS) Internals
Standard C strings (`char*`) are null-terminated (`\0`), requiring $O(N)$ length scans and risking buffer overflows. Redis wraps all string values in an `sds` struct:

```c
struct __attribute__ ((__packed__)) sdshdr8 {
    uint8_t len;         /* Used bytes (excluding null terminator) */
    uint8_t alloc;       /* Total allocated buffer length */
    unsigned char flags; /* Header type: 5, 8, 16, 32, or 64 bit */
    char buf[];          /* Actual payload data + '\0' */
};
```
- **$O(1)$ length lookup**: `len` is stored directly in the header.
- **Binary Safe**: Can store arbitrary bytes, JPEG images, or Protobuf payloads (null bytes are not treated as terminators).
- **Space Optimization**: Uses flexible headers (`sdshdr8`, `sdshdr16`, `sdshdr32`) depending on payload length, saving up to 7 bytes per string header.

---

### 5.2 Redis Object Overhead (`robj`)
Every entry in Redis is wrapped in a `redisObject`:
```c
typedef struct redisObject {
    unsigned type:4;       /* OBJ_STRING, OBJ_LIST, OBJ_SET, OBJ_ZSET, OBJ_HASH */
    unsigned encoding:4;   /* Raw, embstr, hashtable, quicklist, skiplist, listpack */
    unsigned lru:24;       /* LRU time (24 bits) or LFU frequency counter */
    int refcount;          /* Reference count (4 bytes) */
    void *ptr;             /* Pointer to actual data (8 bytes on 64-bit OS) */
} robj;                    /* TOTAL SIZE = 16 BYTES */
```

#### The `embstr` vs `raw` Optimization:
- If a string is $\le 44$ bytes: Redis allocates the `robj` (16 bytes) + `sdshdr8` (3 bytes) + payload + null byte ($44 + 1 = 45$ bytes) in a **single contiguous 64-byte jemalloc chunk**:
  $$\text{Total} = 16 + 3 + 44 + 1 = 64\text{ bytes}$$
- **Why 64 bytes?** CPU cache lines are 64 bytes! Accessing an `embstr` requires exactly **one CPU cache line fetch**, eliminating pointer chasing.
- If payload $> 44$ bytes, Redis splits allocation into two independent `malloc()` calls (`raw` encoding), causing a CPU cache miss and an extra pointer dereference.

---

### 5.3 Dict Rehashing Mechanics
The Redis keyspace is a hash table (`dict`). When load factor ($\text{used}/\text{size}$) exceeds $1.0$ (or $5.0$ during background BGSAVE/AOF rewrite):
1. Redis allocates a secondary hash table $ht[1]$ of size $2^{\lceil \log_2(\text{used} \times 2) \rceil}$.
2. Instead of freezing the server to rehash millions of keys at once, Redis performs **Incremental Rehashing**:
   - Every read/write command migrates all entries from bucket $ht[0].table[rehashidx]$ to $ht[1]$.
   - `databasesCron` timer migrates buckets for $1\text{ms}$ per tick.
   - Once $ht[0]$ is empty, $ht[0]$ pointer is updated to $ht[1]$, and memory is reclaimed.

---

### 5.4 SkipList (ZSET) Probabilistic Balancing
Sorted sets (`ZSET`) use a combination of a hash table (for $O(1)$ score lookups) and a **SkipList** (for $O(\log N)$ range queries and rank operations `ZRANGEBYSCORE`).

```
Level 3: [1] ──────────────────────────────────────────► [10]
Level 2: [1] ─────────────────────► [5] ───────────────► [10]
Level 1: [1] ────────► [3] ───────► [5] ───────► [7] ──► [10]
Level 0: [1] ──► [2] ─► [3] ─► [4] ─► [5] ─► [6] ─► [7] ─► [10]
```
- Node levels are generated using a geometric distribution: coin flip with $p = 0.25$, max levels = 32.
- **Why SkipList over Red-Black Tree?**
  1. Range iterations (`ZRANGE`) are simple pointer traversals along Level 0; tree traversals require complex in-order stack walks.
  2. Locking or rebalancing is far simpler: modifying a skiplist only touches local adjacent node pointers, without global tree rotations.
  3. Average memory per node is only $\frac{1}{1-p} \approx 1.33$ pointers.

---

## 6. Redis Cluster Topology & Distributed Guarantees

Redis Cluster implements a shared-nothing sharding architecture across up to 1,000 master nodes.

### 6.1 Hash Slot Sharding
The keyspace is statically divided into **16,384 hash slots**:

$$\text{Slot} = \text{CRC16}(\text{key}) \pmod{16384}$$

- **Hash Tags**: If a key contains `{...}`, only the text inside braces is hashed:
  - `user:{1001}:profile` and `user:{1001}:orders` hash the substring `"1001"`.
  - Both keys are guaranteed to reside on the exact same Redis shard, enabling multi-key transactions (`MGET`, Lua scripts) without cross-node network hops.

---

### 6.2 Redirection Protocol: MOVED vs ASK
Redis Cluster does not use an active proxy layer by default; the Java client (Lettuce/Jedis) routes commands directly to the shard master.

```
Client                        Node A (Master)                  Node B (Master)
  │                                  │                                │
  │─── GET key_foo ─────────────────►│                                │
  │    (Slot 5000 is on Node B)      │                                │
  │◄── -MOVED 5000 10.0.0.2:6379 ────│                                │
  │    (Client updates local slot cache)                              │
  │                                                                   │
  │─── GET key_foo ──────────────────────────────────────────────────►│
  │◄── "bar" ─────────────────────────────────────────────────────────│
```
- **`-MOVED slot host:port`**: Slot migration is complete. The client **must update its internal routing table** so future queries for slot 5000 route directly to Node B.
- **`-ASK slot host:port`**: Slot is currently migrating. Client sends an `ASKING` flag followed by the query to Node B for this single request only. The client **must not update its internal routing cache**.

---

### 6.3 Replication & CAP Theorem Reality
Redis Cluster prioritizes **Availability and Partition Tolerance (AP)** over Consistency (C):
- Replication between Master and Replica is **asynchronous** by default.
- When Master receives a write, it acknowledges the client immediately after writing to its local memory buffer, then asynchronously replicates to replicas via the replication stream buffer.

#### Split-Brain and Write Loss Scenarios:
1. **Master Partition Write Loss**:
   - Master A is partitioned on network side with 1 client.
   - Replicas on majority side elect Replica A1 as new Master.
   - Old Master A accepts writes from partitioned client.
   - When partition heals, Old Master A is demoted to replica and truncates its un-replicated writes to sync from A1. **All client writes accepted during partition are permanently lost**.
2. **Mitigation Configuration**:
   ```conf
   # Reject writes if fewer than 1 healthy replica responds within 10 seconds
   min-replicas-to-write 1
   min-replicas-max-lag 10
   ```

---

## 7. Client-Side Caching (RESP3 Tracking)

In traditional multi-tier setups, L1 Caffeine caches must poll or subscribe to Redis Pub/Sub topics to evict stale keys, adding CPU and network overhead.

Redis 6+ with **RESP3 Protocol** natively supports **Server-Assisted Client-Side Tracking**:

```
[ Client / JVM ]                                        [ Redis Master ]
       │                                                       │
  1. CLIENT TRACKING ON BCAST PREFIX product: ────────────────►│ (Enable tracking)
       │                                                       │
  2. GET product:42 ──────────────────────────────────────────►│ (Redis remembers
  │◄── "Widget" ──────────────────────────────────────────────│  Client has cached
  │   (Stores in local Caffeine L1)                            │  product:42)
       │                                                       │
       │                                  [ Other Writer ] ───►│ (SET product:42 "New")
       │                                                       │
  3.◄── PUSH Message: INVALIDATE ["product:42"] ───────────────│ (Redis server pushes
       │                                                       │  eviction directly)
  4. Caffeine.invalidate("product:42")                         │
```
- **RESP3 Push Mode**: Out-of-band invalidation messages arrive on the same TCP connection as standard command responses.
- Eliminates manual Pub/Sub invalidation buses and guarantees microsecond L1 invalidation across all application instances.
