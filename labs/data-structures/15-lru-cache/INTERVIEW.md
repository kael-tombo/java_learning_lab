# Interview Questions: LRU Cache

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| [LC 146 LRU Cache](https://leetcode.com/problems/lru-cache/) | Medium | Amazon, Meta, Google, Microsoft, Apple, Oracle | HashMap + Doubly Linked List |
| [LC 460 LFU Cache](https://leetcode.com/problems/lfu-cache/) | Hard | Google, Amazon, Meta, Microsoft | HashMap of frequency buckets |
| [LC 432 All O(1) Data Structure](https://leetcode.com/problems/all-oone-data-structure/) | Hard | Google, Amazon, Meta | HashMap + linked hash set |
| [LC 1797 Design Authentication Manager](https://leetcode.com/problems/design-authentication-manager/) | Medium | Amazon, Google, Meta | HashMap + TTL management |
| [LC 1472 Design Browser History](https://leetcode.com/problems/design-browser-history/) | Medium | Amazon, Google, Meta, Apple | Linked list / two stacks |
| [LC 1429 First Unique Number](https://leetcode.com/problems/first-unique-number/) | Medium | Amazon, Google | Doubly linked list + HashMap |

## NeetCode Reference
NeetCode 150: Linked List category includes LRU Cache as an advanced problem. Essential for system design.

## Company-Specific Questions

### Google
- Design LRU Cache with O(1) get and put — implement from scratch (HashMap + doubly linked list)
- How would you make LRU cache thread-safe without locking on every operation?
- Design a multi-level cache (L1: LRU, L2: LFU) — how do items promote/demote between levels?
- How does Google's Guava Cache (LoadingCache) implement LRU-like eviction?

### Microsoft
- Design LRU Cache with TTL (time-to-live) expiration combined with LRU eviction
- How would you implement an LRU cache for a distributed system (consistent hashing for sharding)?
- Compare LRU vs LFU vs FIFO eviction policies — which would you use for a CDN?

### Meta
- LRU Cache — why is HashMap + doubly linked list the optimal solution? What about LinkedHashMap?
- Design LFU Cache — maintain a HashMap of frequency → LinkedHashSet for O(1) operations
- How would you implement a cache that supports batch operations (putIfAbsent, replace)?

### Amazon
- LRU Cache is one of the most frequently asked Amazon interview problems
- Design DynamoDB's cache layer — how does LRU work with adaptive capacity (DAX)?
- How would you implement a write-through vs write-back LRU cache?

### Apple
- Design a disk-backed LRU cache (thumbnails, app icons) — what changes when data is on disk vs in memory?
- How would you implement image caching with LRU eviction and async loading?
- Design a cache that supports prefetching (predictive loading of next likely items)

### Oracle
- Design an LRU cache for database connection pooling
- How does Oracle's buffer cache implement LRU with touch counts and hot/cold lists?
- What is the difference between LRU and Clock (Second Chance) eviction? Why might Clock be preferred in OS contexts?

## Real Production Scenarios

- **Scenario 1: Web Application Cache** — An e-commerce site caches product pages (HTML fragments) in an LRU cache. Popular products stay cached; stale products (not accessed recently) are evicted. The cache handles 10K requests/second with 95% hit rate. A Bloom filter checks cache key existence before querying the database.

- **Scenario 2: Database Buffer Pool** — A relational database uses an LRU-like algorithm (often with optimizations — LRU-K, Clock) for its buffer pool. Pages read from disk are cached in memory. When the buffer is full, the least recently used clean page is evicted. Dirty pages (modified) are written to disk first.

- **Scenario 3: Content Delivery Network** — A CDN edge server caches images, videos, and static assets using LRU eviction. Popular content stays hot; new content displaces cold content. The LRU cache is combined with popular content pre-warming and predictive prefetching based on traffic patterns.

## Interview Tips

- Time: O(1) for both get and put in a properly implemented LRU cache
- Space: O(capacity) — each key-value pair stored as a linked list node
- Common edge cases: get on non-existent key (return -1/null), put on full cache (evict LRU), put of existing key (update value + move to front)
- Access-order vs insertion-order: LRU access-order tracks most recently used; insertion-order is for FIFO
- LinkedHashMap implements access-order with `accessOrder=true` and overridable `removeEldestEntry()`
- LFU requires a HashMap of frequency → LinkedHashSet (ordered set) for O(1) operations

## Java-Specific Considerations

- `LinkedHashMap<K,V>` — simplest LRU implementation: `new LinkedHashMap<K,V>(capacity, 0.75f, true)` with `removeEldestEntry()`
- `LinkedHashMap` is not thread-safe — wrap with `Collections.synchronizedMap()` or use concurrent variant
- Custom LRU: `class Node { int key, val; Node prev, next; }` + `HashMap<Integer, Node>` — manual pointer management
- Thread-safe LRU: `ConcurrentHashMap` + `ConcurrentLinkedDeque` for reference tracking (best-effort LRU)
- Guava's `CacheBuilder.newBuilder().maximumSize(cap).expireAfterAccess(...)` — production-ready LRU
- Caffeine (Java 8+) — modern high-performance cache, W-TinyLFU policy, outperforms Guava
- For LRU with TTL: store timestamp in the node; check expiration during get; evict expired on access
- `Ehcache`, `Hazelcast` — distributed cache implementations with LRU/LFU eviction
- Memory: custom LRU with Node objects → 3 references (key, value, prev, next) + header overhead; LinkedHashMap adds less overhead
