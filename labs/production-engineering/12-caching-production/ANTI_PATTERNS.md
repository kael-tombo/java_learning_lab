# ANTI-PATTERNS: Caching & Redis in Production
## Lab 12 | Production Engineering Academy — Top 0.0001% Engineering

---

## Anti-Pattern 1: The `KEYS *` Command — Single-Thread Event Loop Killer

### The Mistake
```java
// Runs in a web request or scheduled job
Set<String> keys = redisTemplate.keys("user:session:*"); // BLOCKS REDIS GLOBALLY
```

### Why It Is Catastrophic
Redis uses a **single event loop thread**. `KEYS *` is O(N) — it scans every single key in
the keyspace before returning. With 50 million keys:
- Redis blocks for 10–30 seconds.
- Every other microservice waiting to read/write times out.
- Connection pools exhaust across the entire platform → cascading Sev-1 outage.

### The Fix: Non-Blocking Cursor Scan
```java
// SCAN is O(1) per call, cursor-based, non-blocking
ScanOptions options = ScanOptions.scanOptions()
    .match("user:session:*")
    .count(1000)  // Hint: return ~1000 keys per iteration (not guaranteed)
    .build();

try (Cursor<byte[]> cursor = redisTemplate.getConnectionFactory()
        .getConnection().scan(options)) {
    while (cursor.hasNext()) {
        byte[] key = cursor.next();
        // process key — each iteration yields control back to Redis event loop
    }
}
```
> **Rule**: `KEYS`, `SMEMBERS` (large sets), `HGETALL` (large hashes), `LRANGE 0 -1` (full lists)
> are ALL blocked in production via Redis ACL:
> ```bash
> ACL SETUSER appuser -keys -smembers -hgetall on >password ~* +@all
> ```

---

## Anti-Pattern 2: Caching Without TTL — The Infinite Accumulator

### The Mistake
```java
redisTemplate.opsForValue().set("product:123", product); // No TTL!
```

### Why It Fails
Memory grows without bound until `maxmemory` is hit. Then:
- **`noeviction` policy**: Redis rejects all new writes → application errors on cache set calls.
- **`allkeys-lru` policy**: Redis evicts recently used hot keys to make room for old stale data.
- Both outcomes are worse than not caching at all.

### The Fix: Always Explicit TTL + Jitter
```java
// Base TTL = 1 hour. Jitter = ±5 minutes (prevents thundering herd on mass expiry)
long jitter = ThreadLocalRandom.current().nextLong(-300, 300); // seconds
long ttlSeconds = 3600 + jitter;

redisTemplate.opsForValue().set(
    "product:" + id,
    product,
    Duration.ofSeconds(ttlSeconds)
);
```

---

## Anti-Pattern 3: Cache Stampede (Thundering Herd)

### The Mistake
10,000 concurrent requests all miss on the same expired cache key and simultaneously hit the database:
```java
Product product = redisTemplate.opsForValue().get("product:" + id);
if (product == null) {
    product = productRepository.findById(id); // 10,000 threads hit DB simultaneously!
    redisTemplate.opsForValue().set("product:" + id, product, Duration.ofHours(1));
}
```

### Why It Happens
At T=0, key expires. 10,000 in-flight requests all find `null`. All 10,000 query the DB.
Result: DB CPU spikes to 100%, connection pool exhausts, query latency p99 → 5s, cascading timeout.

### The Fix: Probabilistic Early Expiration (PER) + Redis Mutex Lock

**Option A — PER (recommended, zero locking)**:
```java
// Re-compute cache BEFORE expiry, with some probability proportional to remaining TTL
// Source: "Optimal Probabilistic Cache Stampede Prevention" (Vattani et al., 2015)
public Product getWithPER(String id) {
    ValueWithTTL<Product> cached = getWithRemainingTTL("product:" + id);
    if (cached != null) {
        double remainingTTL = cached.getRemainingTtlMs();
        double beta = 1.0; // higher = more eager recompute
        double gap = -remainingTTL * beta * Math.log(Math.random());
        if (gap <= 0) {
            // Hasn't expired yet — serve cached value
            return cached.getValue();
        }
        // Proactively recompute even before expiry
    }
    return recomputeAndCache(id);
}
```

**Option B — Redis SET NX mutex (distributed lock)**:
```java
String lockKey = "lock:product:" + id;
Boolean acquired = redisTemplate.opsForValue()
    .setIfAbsent(lockKey, "1", Duration.ofSeconds(10)); // NX PX 10000

if (Boolean.TRUE.equals(acquired)) {
    try {
        Product p = productRepository.findById(id);
        redisTemplate.opsForValue().set("product:" + id, p, Duration.ofHours(1));
        return p;
    } finally {
        redisTemplate.delete(lockKey);
    }
} else {
    // Lock not acquired — serve stale value or short sleep + retry
    Thread.sleep(50);
    return redisTemplate.opsForValue().get("product:" + id);
}
```

---

## Anti-Pattern 4: Hot Key Skew — One Key Saturates the Redis Node

### The Mistake
```java
// Every request for ANY product reads the "homepage-products" key
List<Product> featured = redisTemplate.opsForValue().get("homepage-products");
// At 50,000 req/s, one Redis node handles 50,000 GET operations/sec on a single key
```

### Why It Fails
Redis is single-threaded per node. At 50,000 GET/sec on one key, the node CPU hits 100%.
All other keys on that node also experience latency increase — collateral damage.

### The Fix: Local JVM Cache for Extreme Hot Keys + Read Replicas
```java
// Caffeine local cache with short TTL (absorbs 99% of reads in-process)
LoadingCache<String, List<Product>> localCache = Caffeine.newBuilder()
    .expireAfterWrite(Duration.ofSeconds(5))  // 5s stale — acceptable for homepage
    .maximumSize(100)
    .build(key -> {
        // Miss: fetch from Redis (only 1 in 100,000 requests reach Redis now)
        return redisTemplate.opsForValue().get(key);
    });

// For read-heavy keys: use Redis Read Replicas
// Route reads to replicas, writes to primary
LettuceClientConfiguration config = LettuceClientConfiguration.builder()
    .readFrom(ReadFrom.REPLICA_PREFERRED) // prefer replica, fallback to primary
    .build();
```

---

## Anti-Pattern 5: Caching Large Objects (> 100 KB per Key)

### The Mistake
```java
// Caching an entire order history list — grows unboundedly
redisTemplate.opsForValue().set("user:" + id + ":orders", allOrders); // Can be 10 MB!
```

### Why It Fails
- Serialization/deserialization of 10 MB objects: ~100ms CPU per operation.
- Network transfer of 10 MB per request: saturates Redis bandwidth (typically 1–10 Gbps).
- Redis memory fragmentation increases when large allocations are frequently written and expired.
- One 10 MB object evicts ~200 small 50 KB objects under LRU pressure.

### The Fix: Paginate + Cache Only the Hot Page
```java
// Cache only the first page (most users never scroll past page 1)
String cacheKey = "user:" + userId + ":orders:page:1";
List<Order> page1 = redisTemplate.opsForValue().get(cacheKey);
if (page1 == null) {
    page1 = orderRepository.findByUserId(userId, PageRequest.of(0, 20)); // only 20 records
    redisTemplate.opsForValue().set(cacheKey, page1, Duration.ofMinutes(10));
}
```

> **Rule**: If a single cached value exceeds 100 KB, it should NOT be in Redis.
> Use Redis for hot, small, frequently-read data. Use CDN or S3 for large payloads.

---

## Anti-Pattern 6: Using Cache as Source of Truth

### The Mistake
```java
// Business logic reads ONLY from Redis — database is never consulted for this data
Order order = redisTemplate.opsForValue().get("order:" + id);
if (order == null) {
    throw new OrderNotFoundException(id); // NOT checking the database!
}
```

### Why It Is Catastrophic
- Redis `maxmemory` policy evicts keys silently (no error thrown on eviction).
- Redis node restart (OOM, maintenance) clears all data unless persistence is enabled.
- Network partition between app and Redis: all reads return null → application thinks data is gone.

### The Fix: Cache-Aside Pattern (Always DB as Source of Truth)
```java
// Cache-Aside (Read-Through) — correct pattern
public Order getOrder(String id) {
    Order cached = redisTemplate.opsForValue().get("order:" + id);
    if (cached != null) return cached;

    // Cache miss → DB is always authoritative
    Order order = orderRepository.findById(id)
        .orElseThrow(() -> new OrderNotFoundException(id));

    redisTemplate.opsForValue().set("order:" + id, order, Duration.ofMinutes(30));
    return order;
}
```

---

## Anti-Pattern 7: Non-Atomic Read-Modify-Write Without Lua Script

### The Mistake
```java
// Race condition: two threads can both read 100, both compute 101, both write 101
Long current = redisTemplate.opsForValue().get("inventory:" + productId);
if (current > 0) {
    redisTemplate.opsForValue().set("inventory:" + productId, current - 1);
}
```

### Why It Fails
Between `GET` and `SET`, another thread may have already decremented the inventory.
Two concurrent requests both read `inventory=1`, both write `inventory=0` —
but both reservations succeed. Inventory oversold by 1.

### The Fix: Atomic Lua Script (Executes as Single Redis Command)
```java
// Lua executes atomically — no other command can interleave
String luaScript = """
    local current = tonumber(redis.call('GET', KEYS[1]))
    if current and current > 0 then
        redis.call('DECR', KEYS[1])
        return 1  -- success
    end
    return 0  -- out of stock
    """;

DefaultRedisScript<Long> script = new DefaultRedisScript<>(luaScript, Long.class);
Long result = redisTemplate.execute(script, List.of("inventory:" + productId));
if (result == 0) throw new OutOfStockException(productId);
```

---

## Anti-Pattern 8: Connection Pool Exhaustion — Synchronous Redis in Async Context

### The Mistake
```java
// In a Spring WebFlux handler (reactive, non-blocking)
@GetMapping("/products/{id}")
public Mono<Product> getProduct(@PathVariable String id) {
    // Synchronous Redis call blocks a Netty event loop thread!
    Product cached = redisTemplate.opsForValue().get("product:" + id);
    return Mono.justOrEmpty(cached);
}
```

### Why It Fails
Netty event loop threads are precious (typically 8 total). A blocking `redisTemplate.get()`
blocks the event loop thread for 1–5ms waiting for the Redis network response.
At 10,000 concurrent requests × 2ms = **all 8 threads blocked simultaneously**.
The entire service freezes — no new HTTP connections can be accepted.

### The Fix: Reactive Redis Template
```java
@Autowired
private ReactiveRedisTemplate<String, Product> reactiveRedis;

@GetMapping("/products/{id}")
public Mono<Product> getProduct(@PathVariable String id) {
    return reactiveRedis.opsForValue()
        .get("product:" + id)
        .switchIfEmpty(
            productRepository.findById(id)  // reactive JPA / R2DBC
                .flatMap(product -> reactiveRedis.opsForValue()
                    .set("product:" + id, product, Duration.ofMinutes(30))
                    .thenReturn(product))
        );
    // All I/O is non-blocking — Netty thread never blocks
}
```

**Dependency for Reactive Redis**:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis-reactive</artifactId>
</dependency>
```


---

## Anti-Pattern 1: The `KEYS *` Command on Production Redis

### The Mistake
Running `redisTemplate.keys("user:session:*")` or CLI `KEYS *` in a web request or scheduled job.

### Why It Fails
- Redis executes commands using a **single event loop thread**.
- `KEYS *` scans every single key in the database (e.g. 50 million keys), blocking the Redis server thread for 10–30 seconds.
- Every other microservice waiting to read or write to Redis times out.
- Connection pools exhaust across the entire organization, turning a simple debug query into a Sev-1 cluster outage.

### The Correct Production Fix
Never execute `KEYS *`. Use cursor-based non-blocking scanning: `SCAN 0 MATCH "user:session:*" COUNT 1000`.

---

## Anti-Pattern 2: Caching Without Expiration (The Infinite Accumulator)

### The Mistake
Inserting keys with `SET key value` without specifying a Time-To-Live (TTL).

### Why It Fails
Memory grows indefinitely. Eventually, `maxmemory` is reached. If eviction policy is `noeviction`, Redis starts rejecting all write commands. If eviction is LRU, Redis starts discarding hot operational data to make room for old abandoned keys.

### The Correct Production Fix
Mandate explicit TTL on **every single cached key**, paired with randomized TTL jitter.
