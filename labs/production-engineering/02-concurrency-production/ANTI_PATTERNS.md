# ANTI-PATTERNS: Concurrency in Production
## Lab 02 | Production Engineering Academy

---

## Anti-Pattern 1: Using `HashMap` as Shared State

```java
// BROKEN — not thread-safe, can infinite-loop on resize (Java 6), corrupt data
static Map<String, Session> sessions = new HashMap<>();
void addSession(String id, Session s) { sessions.put(id, s); }

// FIXED
static Map<String, Session> sessions = new ConcurrentHashMap<>();
// OR: if you need compute atomics:
sessions.compute(id, (k, existing) -> mergeOrCreate(existing, s));
```

**War Story**: Java 6 HashMap resize caused two threads to create a circular linked list in the internal table. CPU hit 100%. No exception — infinite loop in `HashMap.get()`. Took hours to diagnose.

---

## Anti-Pattern 2: Swallowing `InterruptedException`

```java
// BROKEN — clears interrupt flag, thread can never be stopped cleanly
try {
    Thread.sleep(1000);
} catch (InterruptedException e) {
    log.warn("Interrupted", e);  // Swallowed! Thread continues.
}

// FIXED option A: restore interrupt flag
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
    return;  // Exit task
}

// FIXED option B: rethrow
} catch (InterruptedException e) {
    throw new RuntimeException("Task interrupted", e);
}
```

---

## Anti-Pattern 3: `new Thread()` in Business Code

```java
// BROKEN — unmanaged, unnamed, unmonitored
new Thread(() -> {
    sendPaymentNotification(orderId);
}).start();  // Thread #3847 — where did it go? No tracking, no backpressure

// FIXED — use managed executor
@Autowired ExecutorService notificationExecutor;
notificationExecutor.submit(() -> sendPaymentNotification(orderId));
```

---

## Anti-Pattern 4: Unbounded Thread Pool

```java
// BROKEN — creates new thread for EVERY task under load
ExecutorService pool = Executors.newCachedThreadPool();
// Under spike: 10,000 tasks = 10,000 threads = OOM crash

// FIXED
ExecutorService pool = new ThreadPoolExecutor(10, 100, 60L, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(1000),  // bounded!
    new CallerRunsPolicy());         // backpressure!
```

---

## Anti-Pattern 5: Holding Lock During I/O

```java
// BROKEN — all other threads blocked during slow HTTP call
synchronized (cache) {
    if (!cache.containsKey(key)) {
        String result = restClient.get(url).block();  // 200ms HTTP inside lock!
        cache.put(key, result);
    }
    return cache.get(key);
}

// FIXED — I/O outside lock, lock only for cache access
String cached = getCached(key);                    // Lock, read, unlock
if (cached == null) {
    String result = restClient.get(url).block();   // I/O without lock
    putCached(key, result);                        // Lock, write, unlock
    cached = result;
}
return cached;
```

---

## Anti-Pattern 6: Using `volatile` for Compound Operations

```java
// BROKEN — volatile doesn't make ++ atomic
volatile int hits = 0;
void recordHit() { hits++; }  // READ-MODIFY-WRITE — not atomic!

// FIXED
AtomicInteger hits = new AtomicInteger();
void recordHit() { hits.incrementAndGet(); }
// High contention: LongAdder (faster writes, less precise read)
LongAdder hits = new LongAdder();
void recordHit() { hits.increment(); }
long getHits() { return hits.sum(); }
```

---

## Anti-Pattern 7: ThreadLocal Not Cleaned Up

```java
// BROKEN — ThreadLocal grows without bound in thread pools
static ThreadLocal<RequestCtx> CTX = new ThreadLocal<>();

void doFilter(request, response, chain) {
    CTX.set(buildContext(request));
    chain.doFilter(request, response);
    // MISSING: CTX.remove() — leaked!
}

// FIXED
void doFilter(request, response, chain) {
    CTX.set(buildContext(request));
    try {
        chain.doFilter(request, response);
    } finally {
        CTX.remove();  // Always in finally
    }
}
```

---

## Anti-Pattern 8: Calling `System.exit()` from Thread Pool Tasks

```java
// BROKEN — kills entire JVM, in-flight requests lost, data corruption possible
executor.submit(() -> {
    try { riskyOperation(); }
    catch (FatalException e) { System.exit(1); }  // NEVER DO THIS
});

// FIXED — fail gracefully, let health check detect and trigger restart
executor.submit(() -> {
    try { riskyOperation(); }
    catch (FatalException e) {
        log.error("Fatal error — marking instance unhealthy", e);
        healthIndicator.markDown();  // Kubernetes will restart pod
        // OR: publish to dead-letter queue for retry
    }
});
```

---

## Anti-Pattern 9: Double-Checked Locking Without volatile

```java
// BROKEN — JVM can publish partially-constructed object
private static Config instance;  // Missing volatile!

public static Config getInstance() {
    if (instance == null) {
        synchronized (Config.class) {
            if (instance == null) {
                instance = new Config();  // DANGER: reference published before constructor done
            }
        }
    }
    return instance;
}

// FIXED — volatile ensures full construction before reference is visible
private static volatile Config instance;  // volatile required!
```

---

## Anti-Pattern 10: Virtual Thread + synchronized + I/O (Pinning)

```java
// BROKEN — synchronized pins the carrier thread during I/O (Java 21 VTs)
// 8 CPU cores = max 8 pinned VTs = 8 concurrent requests max (defeats VT purpose)
public synchronized Data load(String key) {
    return remoteCache.get(key);  // I/O inside synchronized = carrier pinned
}

// FIXED — use ReentrantLock (VT can park without pinning carrier)
private final ReentrantLock lock = new ReentrantLock();
public Data load(String key) {
    lock.lock();
    try {
        return remoteCache.get(key);  // VT parks, carrier serves other VTs
    } finally {
        lock.unlock();
    }
}
```
