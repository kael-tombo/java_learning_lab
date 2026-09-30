# EXERCISES: Thread Concurrency
## Lab 02 | Hands-On Exercises | Production Engineering Academy

---

## Exercise 1: Fix the Race Condition (Beginner)

The following inventory service has a race condition. Find and fix it.

```java
public class InventoryService {
    private int stock;

    public InventoryService(int initialStock) {
        this.stock = initialStock;
    }

    public boolean reserve() {
        if (stock > 0) {
            stock--;
            return true;
        }
        return false;
    }

    public int getStock() { return stock; }
}
```

**Task**: Run 100 threads concurrently, each calling `reserve()` 10 times. Stock starts at 500. Without fix: final stock will be negative.

**Starter test**:
```java
@Test
void shouldNotGoNegative() throws InterruptedException {
    InventoryService service = new InventoryService(500);
    ExecutorService pool = Executors.newFixedThreadPool(50);
    CountDownLatch latch = new CountDownLatch(1000);

    for (int i = 0; i < 1000; i++) {
        pool.submit(() -> {
            service.reserve();
            latch.countDown();
        });
    }
    latch.await(5, TimeUnit.SECONDS);
    pool.shutdown();

    assertTrue(service.getStock() >= 0, "Stock went negative: " + service.getStock());
}
```

**Fix hint**: AtomicInteger with CAS.

---

## Exercise 2: Deadlock Detection and Fix (Intermediate)

The following code deadlocks intermittently. Find the deadlock and fix it.

```java
public class BankService {
    void transferAtoB(Account a, Account b, double amount) {
        synchronized (a) {
            try { Thread.sleep(10); } catch (InterruptedException e) {}
            synchronized (b) {
                a.debit(amount);
                b.credit(amount);
            }
        }
    }

    void transferBtoA(Account a, Account b, double amount) {
        synchronized (b) {   // Lock order reversed!
            try { Thread.sleep(10); } catch (InterruptedException e) {}
            synchronized (a) {
                b.debit(amount);
                a.credit(amount);
            }
        }
    }
}
```

**Task**:
1. Write a test that reliably reproduces the deadlock
2. Explain why it deadlocks
3. Fix using canonical lock ordering
4. Fix alternatively using `tryLock` with timeout

---

## Exercise 3: Virtual Thread Pinning Fix (Intermediate)

Convert this code to use virtual threads. Fix the pinning issue.

```java
@Service
public class ProductService {
    private final Map<String, Product> cache = new HashMap<>();

    public synchronized Product getProduct(String id) {
        if (!cache.containsKey(id)) {
            // Simulated HTTP call
            Product p = externalApi.fetchProduct(id);  // 100ms blocking I/O
            cache.put(id, p);
        }
        return cache.get(id);
    }
}
```

**Steps**:
1. Enable virtual threads in Spring Boot (`spring.threads.virtual.enabled=true`)
2. Run with `-Djdk.tracePinnedThreads=full` and observe pinning
3. Fix by replacing `synchronized` with `ReentrantLock`
4. Measure throughput before and after

---

## Exercise 4: Thread Pool Sizing (Advanced)

A service has the following operation profile:
- 60% of requests: DB query, 5ms average, 20ms p99
- 30% of requests: External API call, 200ms average, 2000ms p99
- 10% of requests: CPU computation (PDF generation), 500ms average

The machine has 8 cores and 16GB RAM. Expected peak: 2000 concurrent requests.

**Tasks**:
1. Calculate optimal thread pool sizes for each operation type
2. Configure three separate `ThreadPoolExecutor` instances
3. Implement routing logic to dispatch to the right pool
4. Add Micrometer metrics to monitor each pool
5. Add Actuator endpoint to dump pool stats

---

## Exercise 5: Fix the CompletableFuture Error Handling (Advanced)

This code has multiple issues. Find and fix them.

```java
public CompletableFuture<DashboardData> loadDashboard(String userId) {
    CompletableFuture<User> userFuture = CompletableFuture.supplyAsync(
        () -> userService.getUser(userId));

    CompletableFuture<List<Order>> ordersFuture = CompletableFuture.supplyAsync(
        () -> orderService.getOrders(userId));

    return CompletableFuture.allOf(userFuture, ordersFuture)
        .thenApply(v -> new DashboardData(userFuture.join(), ordersFuture.join()));
}
```

**Issues to find**:
1. No error handling — exception causes unhandled future
2. No timeout — can block forever
3. No explicit executor — uses ForkJoinPool.commonPool() (wrong for I/O)
4. No cancellation — if user request times out, futures keep running

**Fix**: Use Structured Concurrency (Java 21) or properly configured CompletableFuture with all issues addressed.

---

## Exercise 6: Build a Thread-Safe In-Memory Cache (Advanced)

Build a production-grade in-memory cache with:
- Get, put, remove operations
- Configurable max size with LRU eviction
- TTL (time-to-live) per entry
- Thread-safe (concurrent reads, concurrent writes)
- Metrics: hit rate, miss rate, eviction count
- No external dependencies (Caffeine not allowed for this exercise)

**Acceptance tests**:
- 100 concurrent readers + 10 concurrent writers — no data corruption
- After TTL, entry not returned
- When max size reached, LRU entry evicted
- Hit rate > 95% for repeated reads

---

## Solutions

Solutions are in `solutions/` directory. **Try yourself first!** The learning is in the struggle, not the answer.

| Exercise | Difficulty | Time | Key Concepts |
|----------|-----------|------|--------------|
| 1 | Beginner | 20min | AtomicInteger, CAS |
| 2 | Intermediate | 45min | Deadlock, canonical ordering, tryLock |
| 3 | Intermediate | 30min | VT pinning, ReentrantLock |
| 4 | Advanced | 1hr | Pool sizing, bulkhead |
| 5 | Advanced | 45min | CF error handling, timeout, structured concurrency |
| 6 | Advanced | 2hr | LRU, TTL, concurrent data structures |
