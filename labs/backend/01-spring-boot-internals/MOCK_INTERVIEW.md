# Mock Interview: In-Memory Cache with TTL and Eviction Policies

**Role:** Senior Backend Engineer (Staff Level)  
**Duration:** 55 minutes  
**Difficulty Progression:** Easy, Medium, Hard

---

## Round 1: Easy — Problem Understanding and API Design

**Interviewer:** We need to design an in-memory cache. Walk me through the high-level API and data structures you would use.

**Candidate:** The API surface is straightforward with four core operations:

1. put(K key, V value, long ttlMillis) — stores a value with an optional TTL
2. get(K key) — retrieves a value returning null if expired or absent
3. remove(K key) — explicitly removes an entry
4. clear() — removes all entries

The core backing store is a ConcurrentHashMap K, CacheEntry V where CacheEntry holds the value and the absolute expiration timestamp in milliseconds. I separate data storage from eviction logic using the Strategy pattern with an EvictionPolicy interface and concrete implementations for LRU, LFU, and FIFO.

**Interviewer:** Why ConcurrentHashMap instead of a synchronized HashMap?

**Candidate:** ConcurrentHashMap uses fine-grained locking (striped locks) allowing concurrent reads without blocking and concurrent writes to different segments. A synchronized HashMap serializes all operations becoming a bottleneck under high throughput. For a cache handling thousands of reads per second this difference is critical. The trade-off is that ConcurrentHashMap iterators are weakly consistent reflecting state at some point since the iterator was created. For a cache eventual visibility of entries is acceptable.

**Interviewer:** How does the TTL mechanism work at a detailed level?

**Candidate:** There are two complementary mechanisms:

1. Lazy eviction on get() — before returning the value I check System.currentTimeMillis() > entry.expiryTime. If expired I remove the key and return null.

2. Background cleaner — a PriorityQueue ExpiryEntry K ordered by expiry time. A single-threaded ScheduledExecutorService runs every second polls the queue and removes entries whose expiry has passed.

The dual approach ensures prompt cleanup on access and guaranteed eventual cleanup of unaccessed entries. The priority queue provides O(log n) insertion and O(1) peek for the next expiring entry.

---

## Round 2: Medium — Eviction Policies

**Interviewer:** Walk me through the LRU eviction implementation in detail.

**Candidate:** LRU evicts the least recently accessed entry when the cache reaches capacity. My implementation uses a LinkedHashMap K, Boolean constructed with accessOrder=true and overridden removeEldestEntry(). In access-order mode every get() or put() moves the entry to the end of the doubly-linked list. When removeEldestEntry() is called after each insertion if the map size exceeds maxCapacity it returns true and the eldest entry at the head is automatically removed. This gives O(1) eviction.

The downside is that LinkedHashMap is not thread-safe so I wrap read and write operations in the ReentrantLock. For a read-heavy workload this lock serializes writes but reads are still fast.

**Interviewer:** Now the LFU implementation. Why is it harder?

**Candidate:** LFU evicts the least frequently used entry. The naive approach scans all entries to find the minimum frequency resulting in O(n) eviction. The classic O(1) optimization uses a HashMap frequency, LinkedHashSet keys and tracks the minimum frequency globally. On access we move the key from its current frequency bucket to the next one incrementing frequency. If the old bucket becomes empty and was the minimum we increment the minimum. On eviction we remove any key from the min-frequency bucket.

This algorithm is described in "An O(1) algorithm for implementing the LFU cache eviction scheme" by Shah et al. It uses two hash maps and a doubly-linked list per frequency bucket giving O(1) for both access and eviction.

**Interviewer:** Compare FIFO with LRU. When would you choose FIFO?

**Candidate:** FIFO evicts the oldest inserted entry regardless of access pattern. It is simpler and cheaper with no access-tracking overhead. FIFO performs poorly for workloads with temporal locality where recently added entries are most likely to be accessed again. However FIFO excels when the access pattern is a sequential scan processing a stream of records where you cache results per record and never revisit them. LRU suffers from scan resistance issues where a single scan can replace the entire cache. FIFO does not have this problem.

**Interviewer:** Explain scan resistance more deeply.

**Candidate:** If a workload scans through N items where N exceeds cache capacity LRU evicts all existing entries and replaces them with the scan. When the application references the original working set again every access is a cache miss. LFU avoids this because frequency accumulation protects frequently accessed entries from being evicted by a one-time scan. LRU-K (tracking the last K accesses) and ARC (Adaptive Replacement Cache) address scan resistance by maintaining multiple lists for recent and frequent entries.

---

## Round 3: Hard — Concurrency and Edge Cases

**Interviewer:** You are using a single ReentrantLock. Can you do better?

**Candidate:** A single global lock serializes all writes. For read-heavy workloads (95% reads) this is acceptable. For write-heavy workloads I would use striped locking sharding entries by key hash into N segments each with its own lock. ConcurrentHashMap does this internally. The challenge is that eviction and expiry cleanup need a consistent view across shards. I would use a generation clock approach where each shard maintains a generation counter and eviction picks the shard with the oldest average generation.

Another approach uses ConcurrentSkipListMap with NavigableMap for the expiry queue providing lock-free reads and logarithmic-time writes.

**Interviewer:** How do you handle the case where put is called with a new TTL for an existing key?

**Candidate:** The new entry overwrites the ConcurrentHashMap entry with the new expiry time. The old ExpiryEntry in the PriorityQueue becomes stale because its expiry time no longer matches. In the background cleaner I verify the match by checking map.get(entry.key).expiryTime == entry.expiryTime. If they differ the entry is stale and I skip it. This is lazy cleanup of stale queue entries. The queue may temporarily exceed the number of actual entries but growth is bounded by the rate of TTL updates.

**Interviewer:** Memory management — how do you prevent OOM?

**Candidate:** I would add a maxMemoryBytes configuration and use java.lang.instrument.Instrumentation or the jamm library to estimate object sizes. When estimated memory exceeds the limit I trigger eviction regardless of count. A simpler approach uses SoftReference V for values allowing the GC to reclaim soft references before OOM. However soft references are GC-policy dependent leading to unpredictable eviction. I combine both count-based and memory-based capacity evicting when either limit is reached.

**Interviewer:** How would you add metrics and observability?

**Candidate:** AtomicLong counters for hits, misses, evictions, and total puts. Expose a CacheStats record via a metrics endpoint. Important metrics: hit rate (hits / total gets), eviction count (indicates under-provisioning), average TTL remaining, and heap usage of cached entries. Export via Micrometer or JMX. Alert when hit rate drops below 90% for sustained periods.

---

## Round 4: Hard — Distributed Caching and Trade-offs

**Interviewer:** How would you scale this cache across multiple instances?

**Candidate:** Use Redis or Memcached as an L2 backing store with the in-memory cache as an L1 client-side cache. The L1 cache uses a short TTL (seconds) and subscribes to invalidation events via pub/sub. This is the cache-aside pattern: read from L1, miss to L2, populate L1. Writes use write-through or write-behind to L2. Cache invalidation across instances uses Redis pub/sub with per-key invalidation messages.

**Interviewer:** What are the key trade-offs in your design?

**Candidate:** 1. Single global lock vs striped locking: simplicity vs write throughput.
2. Lazy + background TTL eviction vs eager eviction: immediate reclamation vs lower overhead.
3. Strategy pattern for eviction: extensibility vs virtual method dispatch cost (negligible).
4. In-memory only vs distributed: operational simplicity vs scalability.
For a single-node application under 10K req/s the current design is optimal.

**Interviewer:** How would you test this cache for correctness?

**Candidate:** Three levels:
1. Unit tests: verify each eviction policy with sequential operations.
2. Integration tests: verify TTL expiry with Thread.sleep() and concurrent access with CountDownLatch.
3. Property-based tests (jqwik): generate random sequences of puts, gets, and sleeps verifying invariants like get never returns a value after TTL expiry and cache size never exceeds maxCapacity.

---

## Round 5: Wrap-up

**Interviewer:** If you had to improve one thing what would it be?

**Candidate:** Replace the single ReentrantLock with ReentrantReadWriteLock. Reads only need the read lock (shared) while writes need the write lock (exclusive). Since caches are predominantly read-heavy this dramatically reduces contention. The background cleaner acquires the write lock only when actually removing entries. For LRU access tracking during get() I would use a concurrent LinkedHashMap like from Caffeine library to avoid locking on reads entirely.

**Interviewer:** Good. This covers the essential aspects of cache design.
