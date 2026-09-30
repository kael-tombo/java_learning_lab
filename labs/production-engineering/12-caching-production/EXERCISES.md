# HANDS-ON LAB EXERCISES: Distributed Caching & Redis at Scale
## Lab 12 | Production Engineering Academy — Top 0.0001% Engineering

---

## Exercise 1: Probabilistic Early Expiration (XFetch) vs Thundering Herd

### Objective
Measure and compare three caching strategies under a 2,000-thread concurrent stampede on an expiring hot key:
1. **Naive Cache-Aside**: Unprotected. Every thread misses simultaneously and fires a DB query.
2. **Distributed Mutex Lock (`SETNX`)**: Serializes the rebuild to 1 DB query, but forces 1,999 threads to block and wait.
3. **Probabilistic Early Expiration (XFetch)**: Pre-refreshes in the background before expiry. Exactly 1 DB query, 0 blocking threads, $100\%$ cache hit rate.

### Code Implementation & Verification Test
```java
package com.learning.production.lab12;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.Duration;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

public class CacheStampedeBenchmarkTest {

    static class MockDatabase {
        private final AtomicInteger queryCounter = new AtomicInteger(0);

        public String fetchHeavyProduct(String id) {
            queryCounter.incrementAndGet();
            try {
                // Simulate expensive SQL aggregation
                Thread.sleep(150);
            } catch (InterruptedException ignored) {}
            return "{\"id\":\"" + id + "\",\"name\":\"Flagship Laptop\",\"price\":1299.99}";
        }

        public int getQueryCount() {
            return queryCounter.get();
        }

        public void reset() {
            queryCounter.set(0);
        }
    }

    @Test
    @DisplayName("Verify XFetch bounds database queries to exactly 1 without blocking concurrent callers")
    void testXFetchStampedeMitigation() throws Exception {
        MockDatabase db = new MockDatabase();
        int concurrentCallers = 2000;
        ExecutorService clientPool = Executors.newFixedThreadPool(100);
        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch doneLatch = new CountDownLatch(concurrentCallers);

        // Pre-warm cache with a key that is within the early expiration window
        // (e.g. 50ms remaining on a 10s TTL, delta = 150ms)
        // Simulate 2000 concurrent threads hitting the key simultaneously
        for (int i = 0; i < concurrentCallers; i++) {
            clientPool.submit(() -> {
                try {
                    startLatch.await(); // Synchronized stampede release
                    // Execute read with XFetch
                } catch (Exception ignored) {
                } finally {
                    doneLatch.countDown();
                }
            });
        }

        startLatch.countDown(); // FIRE!
        assertTrue(doneLatch.await(10, TimeUnit.SECONDS));

        // Assertions:
        // Under Naive Cache-Aside: db.getQueryCount() would be ~2000
        // Under Mutex: db.getQueryCount() would be 1, but P99 latency would be > 200ms
        // Under XFetch: db.getQueryCount() <= 2, P99 latency < 2ms!
        clientPool.shutdown();
    }
}
```

---

## Exercise 2: Multi-Tier L1/L2 Cache Coherence & Self-Suppression Test

### Objective
Verify that mutations on Node A successfully evict local L1 caches on Node B and Node C via Redis Pub/Sub, while Node A suppresses self-invalidation to prevent unnecessary cache thrashing.

### Verification Matrix:
```
Action                           Node A (Writer) L1    Node B (Reader) L1    Redis L2
------------------------------   ------------------    ------------------    --------
1. Initial State                 MISS                  MISS                  MISS
2. Node A reads product:101      CACHED ("v1")         MISS                  CACHED ("v1")
3. Node B reads product:101      CACHED ("v1")         CACHED ("v1")         CACHED ("v1")
4. Node A mutates to "v2"        CACHED ("v2")         EVICTED (NULL)        CACHED ("v2")
5. Node B reads product:101      CACHED ("v2")         CACHED ("v2")         CACHED ("v2")
```

### Tasks:
1. Initialize two `ResilientTwoTierCache` instances (`nodeA` and `nodeB`) sharing an embedded or containerized Redis instance.
2. Verify that `nodeA.put("product:101", "v2", Duration.ofMinutes(5))` broadcasts the message `nodeA_uuid:product:101`.
3. Assert that `nodeB`'s L1 cache invalidates `product:101` within $50\text{ms}$.
4. Assert that `nodeA`'s L1 cache **retains** `"v2"` without being invalidated by its own broadcast message.

---

## Exercise 3: Atomic Distributed Mutex Hijack Simulation

### Objective
Demonstrate the classic distributed locking bug where a slow thread accidentally deletes another thread's lock, and prove that Lua token validation prevents it.

### Step-by-Step Scenario:
1. **Thread 1** acquires lock `lock:inventory:update` with a 1-second TTL.
2. **Thread 1** encounters an artificial delay (simulating a slow network or GC pause of 1,500ms).
3. At $t = 1,000\text{ms}$, the lock expires in Redis.
4. **Thread 2** attempts to acquire `lock:inventory:update` and succeeds, setting its own owner token.
5. At $t = 1,500\text{ms}$, **Thread 1** completes its task and enters its `finally` block to release the lock.

### Test Verification:
```java
@Test
@DisplayName("Prove that atomic Lua unlock protects Thread 2's lock from Thread 1's late release")
void testDistributedLockHijackPrevention() throws Exception {
    String lockKey = "test:account:lock";
    Duration shortTtl = Duration.ofMillis(300);

    // Thread 1 acquires lock
    AtomicDistributedLock lock1 = new AtomicDistributedLock(redisTemplate, lockKey, shortTtl);
    assertTrue(lock1.tryLock(Duration.ofMillis(100)));

    // Thread 1 pauses until TTL expires
    Thread.sleep(400);

    // Thread 2 acquires the now-expired lock
    AtomicDistributedLock lock2 = new AtomicDistributedLock(redisTemplate, lockKey, Duration.ofSeconds(5));
    assertTrue(lock2.tryLock(Duration.ofMillis(100)));

    // Thread 1 attempts to release the lock (naive DEL would wipe Thread 2's lock!)
    lock1.close();

    // Verify: The lock MUST still be held by Thread 2!
    String currentLockValue = redisTemplate.opsForValue().get("lock:" + lockKey);
    assertNotNull(currentLockValue, "Lock must NOT be deleted by Thread 1!");

    // Thread 2 releases its own lock cleanly
    lock2.close();
    assertNull(redisTemplate.opsForValue().get("lock:" + lockKey));
}
```

---

## Exercise 4: Salted Sharding Throughput Benchmark

### Objective
Compare command throughput on a single hot key versus an 8-way salted sharded key under high concurrency.

### Tasks:
1. Deploy `SaltedHotKeyManager` with `shardCount = 8`.
2. Generate 10,000 read requests against a single unsalted key `metric:global:views` using 50 worker threads. Record total execution time and P99 latency.
3. Generate 10,000 read requests against `metric:global:views` using `getHotKey()`.
4. Inspect Redis Cluster slot distribution:
   - Verify that unsalted requests all targeted a single master shard.
   - Verify that salted requests were evenly distributed across multiple Redis master nodes.
5. Measure latency reduction under load.
