# PRODUCTION SCENARIOS: Thread Concurrency
## Lab 02 | Production Engineering Academy

---

## Scenario 1: The Tuesday Deadlock (Banking Transfer)

### Context
Core banking system. Java 11, Spring Boot. Interbank transfers. Every Tuesday morning: 3-5 threads deadlock. Service requires restart. Customers can't transfer money.

### Thread Dump Evidence
```
"transfer-worker-12" prio=5 os_prio=0 tid=0x... nid=0x...
  java.lang.Thread.State: BLOCKED (on object monitor)
    - waiting to lock <0x7f3a2290> (held by "transfer-worker-8")
    at com.bank.AccountService.transfer(AccountService.java:89)
    - locked <0x7f3a1180>

"transfer-worker-8" prio=5 os_prio=0 tid=0x... nid=0x...
  java.lang.Thread.State: BLOCKED (on object monitor)
    - waiting to lock <0x7f3a1180> (held by "transfer-worker-12")
    at com.bank.AccountService.transfer(AccountService.java:89)
    - locked <0x7f3a2290>

Found one Java-level deadlock.
```

### Root Cause
```java
// BROKEN — lock order depends on caller, causing circular dependency
void transfer(Account from, Account to, BigDecimal amount) {
    synchronized (from) {           // Thread A: locks account-100
        synchronized (to) {         // Thread A: wants account-200
                                     // Thread B: locked account-200, wants account-100
            from.debit(amount);      // DEADLOCK — neither can proceed
            to.credit(amount);
        }
    }
}
```

### Fix
```java
// FIXED — canonical ordering: always lock lower ID first
void transfer(Account from, Account to, BigDecimal amount) {
    Account first  = from.getId().compareTo(to.getId()) < 0 ? from : to;
    Account second = first == from ? to : from;
    synchronized (first) {
        synchronized (second) {
            from.debit(amount);
            to.credit(amount);
        }
    }
}
```

### Why Only Tuesdays?
A batch job ran at 7 AM Tuesday processing reverse-direction transfers (B→A instead of A→B). This was the only code path that created the circular dependency. Undetected for 6 months.

**Post-Mortem Action Items**:
- Added deadlock detection via JMX `ThreadMXBean.findDeadlockedThreads()` — alert if found
- Added unit test that spawns 100 concurrent bidirectional transfers and verifies no deadlock
- Added `tryLock` with 200ms timeout as fallback

---

## Scenario 2: Race Condition in Flash Sale Inventory

### Context
E-commerce platform. Flash sale: 10,000 items. After sale: inventory shows -47. 47 customers bought nonexistent stock. Company had to honor orders anyway (legal obligation) — cost: $34,000.

### Root Cause
```java
// BROKEN — read-check-write is not atomic
@Service
public class InventoryService {
    private int stock = 10000;  // Not thread-safe!

    @Transactional  // Transaction doesn't help for in-memory state!
    public boolean reserve() {
        if (stock > 0) {    // Thread A: reads 1 (last item)
                             // Thread B: reads 1 (last item) — race!
            stock--;         // Both decrement → -1
            return true;
        }
        return false;
    }
}
```

### Fix — AtomicInteger with CAS
```java
private final AtomicInteger stock = new AtomicInteger(10000);

public boolean reserve() {
    // CAS loop: atomically check and decrement only if positive
    while (true) {
        int current = stock.get();
        if (current <= 0) return false;
        if (stock.compareAndSet(current, current - 1)) return true;
        // If CAS fails (another thread changed it), retry
    }
}
// Simplified with Java 9+:
public boolean reserveSimple() {
    return stock.getAndUpdate(s -> Math.max(0, s - 1)) > 0;
}
```

### Fix — Database Optimistic Locking (preferred for distributed systems)
```sql
-- Atomically decrement only if positive
UPDATE inventory SET stock = stock - 1
WHERE product_id = ? AND stock > 0
-- Check rows affected: 0 = out of stock, 1 = success
```

---

## Scenario 3: Virtual Thread Pinning Wall

### Context
Java 21 service with virtual threads. Expected 50,000 req/s. Actual: 800 req/s. CPU at 100% on 8 platform carrier threads.

### Diagnosis
```bash
# Detect pinning
java -Djdk.tracePinnedThreads=full -jar app.jar

# Output:
Thread[#47,ForkJoinPool-1-worker-1,5,CarrierThreads]
    com.company.CacheService.get(CacheService.java:42)
    <synchronized block>
        com.company.HttpWrapper.fetch(HttpWrapper.java:78)  <- I/O while pinned!
            ...java.net.http.HttpClient.send(...)
```

### Root Cause
```java
// BROKEN — synchronized + blocking I/O pins the carrier thread
// 8 carrier threads × pinned = 8 requests max concurrent
public class CacheService {
    private final Map<String, Object> cache = new HashMap<>();

    public synchronized Object get(String key) {
        if (!cache.containsKey(key)) {
            // HTTP call while holding synchronized lock!
            // VT cannot unmount → carrier thread BLOCKED
            Object value = httpClient.send(request, bodyHandler).body();
            cache.put(key, value);
        }
        return cache.get(key);
    }
}
```

### Fix
```java
public class CacheService {
    private final ConcurrentHashMap<String, Object> cache = new ConcurrentHashMap<>();
    private final ReentrantLock lock = new ReentrantLock();  // Not synchronized!

    public Object get(String key) {
        Object cached = cache.get(key);
        if (cached != null) return cached;  // Fast path — no lock needed

        lock.lock();  // ReentrantLock: VT can unmount during I/O
        try {
            cached = cache.get(key);  // Double-check
            if (cached != null) return cached;

            Object value = httpClient.send(request, bodyHandler).body();  // VT unmounts here OK
            cache.put(key, value);
            return value;
        } finally {
            lock.unlock();
        }
    }
}
// Result: 47,000 req/s (from 800 req/s)
```

---

## Scenario 4: ThreadLocal Leak Under Load

### Context
Spring Boot REST API. Memory growing 200MB/day. Heap dump shows thousands of stale `RequestContext` objects referencing old HTTP requests.

### Root Cause
```java
// BROKEN — ThreadLocal not cleaned up
@Component
public class RequestContextFilter implements Filter {
    private static final ThreadLocal<RequestContext> CONTEXT = new ThreadLocal<>();

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        CONTEXT.set(new RequestContext((HttpServletRequest) req));
        chain.doFilter(req, res);
        // MISSING: CONTEXT.remove()
        // Tomcat thread pool reuses threads → context accumulates in each thread
        // HttpServletRequest reference in context → prevents GC of entire request
    }
}
```

### Fix
```java
@Override
public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
        throws IOException, ServletException {
    CONTEXT.set(new RequestContext((HttpServletRequest) req));
    try {
        chain.doFilter(req, res);
    } finally {
        CONTEXT.remove();  // ALWAYS remove — even on exception path
    }
}
```

---

## Scenario 5: The Thundering Herd on Cache Miss

### Context
News website. Redis cache. One popular article expires at midnight. At 00:00:00, 10,000 concurrent readers all get cache miss simultaneously. All 10,000 query the database. Database CPU spikes to 100%. All queries timeout. Cache stampede.

### Fix — Probabilistic Early Expiry (PER Algorithm)
```java
public Optional<Article> getArticle(long id) {
    String key = "article:" + id;
    CachedItem<Article> item = cache.get(key);

    if (item != null) {
        // Early refresh: with probability that increases as expiry approaches
        double timeLeft = item.expiresAt - System.currentTimeMillis();
        double earlyRefreshProbability = Math.exp(-timeLeft / (item.delta * Math.log(Math.random())));

        if (earlyRefreshProbability < 0) {
            // Refresh asynchronously — only ONE thread does this
            if (refreshLock.tryLock()) {
                try {
                    executor.submit(() -> refreshCache(id));
                } finally { refreshLock.unlock(); }
            }
        }
        return Optional.of(item.value);
    }
    return loadWithSingleFlightGuard(id);  // Single-flight pattern below
}

// Single-flight: only one concurrent load per key
private final ConcurrentHashMap<Long, CompletableFuture<Article>> inFlight = new ConcurrentHashMap<>();

private Optional<Article> loadWithSingleFlightGuard(long id) {
    CompletableFuture<Article> future = inFlight.computeIfAbsent(id,
        k -> CompletableFuture.supplyAsync(() -> {
            Article a = db.findById(k);
            cache.put("article:" + k, a, 300);
            inFlight.remove(k);
            return a;
        }));

    return Optional.of(future.join());  // All concurrent requests wait for one DB load
}
```
