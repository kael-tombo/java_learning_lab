# THEORY: Thread Concurrency & Virtual Threads
## Lab 02 | Production Engineering Academy

---

## 1. Java Memory Model (JMM) — The Foundation

### 1.1 Why JMM Exists

Modern CPUs have multi-level caches (L1/L2/L3) and reorder instructions for performance. Without explicit rules, thread A writing to a variable may not be visible to thread B — even if A wrote "first" in wall-clock time.

The JMM defines when writes by one thread are guaranteed visible to other threads.

### 1.2 Happens-Before (HB) — The Core Rule

Write W **happens-before** Read R means: R is guaranteed to see what W wrote.

**The six HB rules**:
1. **Program order** — Each action HB every later action in the same thread
2. **Monitor lock** — `unlock(m)` HB every subsequent `lock(m)` on m
3. **Volatile field** — Write to volatile HB every subsequent read of same field
4. **Thread.start()** — Actions before `t.start()` HB any action in thread t
5. **Thread.join()** — All actions in thread T HB return of `t.join()`
6. **Transitivity** — A HB B and B HB C implies A HB C

```java
int data = 0;
volatile boolean ready = false;

// Thread Writer:
data = 42;         // Program order: HB ready=true write
ready = true;      // Volatile write: HB any subsequent volatile read of `ready`

// Thread Reader (separate thread):
while (!ready) {}  // Volatile read sees the write
// By transitivity: data=42 write HB ready=true write HB ready volatile read
// Therefore: reader is GUARANTEED to see data=42
```

### 1.3 What Volatile Does NOT Do

```java
volatile int counter = 0;

// Thread A and B both run counter++:
// Thread A: read(0), increment, write(1)
// Thread B: read(0), increment, write(1)   <- Lost update!
// Result: 1 instead of 2

// volatile only guarantees visibility of each individual read/write.
// Compound operations (read-modify-write) are NOT atomic.
// Use AtomicInteger for atomic compound operations.
```

---

## 2. Lock Hierarchy: synchronized vs ReentrantLock vs StampedLock

### 2.1 `synchronized` — Simple, Correct, Standard

```java
// Intrinsic monitor on an object's mark word
synchronized (myLock) {
    // Exclusive access: only one thread at a time
    // Visibility: writes before unlock visible after lock
}

// Java 21: biased locking removed. Now uses thin lock (CAS) -> inflated monitor
// Performance: ~10ns uncontended, microseconds-ms under contention
```

### 2.2 `ReentrantLock` — Flexible, Interruptible, Timed

```java
ReentrantLock lock = new ReentrantLock(true);  // fair=true: FIFO ordering

// Timed tryLock prevents deadlock by giving up
if (lock.tryLock(100, TimeUnit.MILLISECONDS)) {
    try {
        // Critical section
    } finally {
        lock.unlock();  // MUST be in finally — even if exception thrown
    }
} else {
    throw new LockTimeoutException("Could not acquire lock in 100ms");
}
```

### 2.3 `StampedLock` — Highest Performance for Read-Heavy

```java
StampedLock sl = new StampedLock();
Point point = new Point(0, 0);

// OPTIMISTIC READ — zero locking cost!
long stamp = sl.tryOptimisticRead();
double x = point.x;  // Possibly stale read
double y = point.y;  // Possibly stale read
if (!sl.validate(stamp)) {
    // A writer was active during our read — fall back to real read lock
    stamp = sl.readLock();
    try { x = point.x; y = point.y; }
    finally { sl.unlockRead(stamp); }
}
// Use for: many readers (>90%), very short reads, rare writers
// Not reentrant — thread that holds write lock cannot re-acquire any stamp
```

### 2.4 Decision Matrix

| Scenario | Use |
|----------|-----|
| Simple exclusive access | `synchronized` |
| Need timed/interruptible acquire | `ReentrantLock` |
| 95%+ reads, rare writes, fast reads | `StampedLock` |
| Many readers, occasional writers, read is slow | `ReadWriteLock` |
| Single variable atomic ops | `AtomicXxx` |
| High-contention counter | `LongAdder` |

---

## 3. java.util.concurrent — Production Toolkit

### 3.1 Thread Pool Sizing Rules

**I/O-bound services** (DB, HTTP, file I/O):
```
Threads = CPU_cores × (1 + wait_time / compute_time)
Example: 8 cores, DB query 50ms wait / 5ms compute = ratio 10
Pool size = 8 × (1 + 10) = 88 threads
```

**CPU-bound tasks** (computation, crypto, encoding):
```
Threads = CPU_cores (or CPU_cores + 1)
More threads = context switching overhead with no benefit
```

**Java 21 Virtual Threads** (I/O-bound):
```
Use newVirtualThreadPerTaskExecutor()
Platform carrier threads = CPU_cores (JVM manages automatically)
Virtual threads = as many as needed (millions OK)
```

### 3.2 Proper ThreadPoolExecutor Configuration

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    10,                             // corePoolSize: always-alive threads
    50,                             // maximumPoolSize: peak threads
    60, TimeUnit.SECONDS,           // keepAliveTime: extra threads die after idle
    new ArrayBlockingQueue<>(1000), // BOUNDED queue — critical for backpressure!
    new ThreadFactory() {
        AtomicInteger n = new AtomicInteger();
        public Thread newThread(Runnable r) {
            Thread t = new Thread(r, "payment-worker-" + n.incrementAndGet());
            t.setDaemon(false);     // Non-daemon: JVM waits for these
            t.setUncaughtExceptionHandler((thread, ex) ->
                log.error("Uncaught exception in {}", thread.getName(), ex));
            return t;
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy()  // Backpressure: block caller if full
);

// Register shutdown hook
Runtime.getRuntime().addShutdownHook(new Thread(() -> {
    executor.shutdown();
    try { executor.awaitTermination(30, TimeUnit.SECONDS); }
    catch (InterruptedException e) { executor.shutdownNow(); }
}));
```

### 3.3 CompletableFuture Patterns

```java
// Pattern 1: Pipeline with different executors per stage
CompletableFuture
    .supplyAsync(() -> db.findOrder(id), dbPool)           // DB thread
    .thenApplyAsync(o -> enrichOrder(o), apiPool)          // API call thread
    .thenApplyAsync(o -> calculatePrice(o), cpuPool)       // CPU thread
    .thenAcceptAsync(o -> notify(o), notificationPool)     // Fire-and-forget
    .exceptionally(ex -> { log.error("Failed", ex); return null; });

// Pattern 2: Fan-out and join (run in parallel, collect results)
var f1 = CompletableFuture.supplyAsync(() -> getUser(id), apiPool);
var f2 = CompletableFuture.supplyAsync(() -> getOrders(id), dbPool);
var f3 = CompletableFuture.supplyAsync(() -> getRecs(id), mlPool);

CompletableFuture.allOf(f1, f2, f3)
    .thenApply(v -> new Dashboard(f1.join(), f2.join(), f3.join()))
    .get(5, TimeUnit.SECONDS);  // Overall timeout

// Pattern 3: Race — first to complete wins
CompletableFuture.anyOf(
    fetchFromPrimaryCache(key),
    fetchFromSecondaryCache(key)
).thenApply(result -> (CacheEntry) result);
```

---

## 4. Virtual Threads (Java 21) — Production Deep Dive

### 4.1 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    JVM Scheduler                         │
│                                                          │
│   VT-1  VT-2  VT-3  ...  VT-9999  VT-10000             │
│    │     │     │              │        │                  │
│    └──┬──┘     │              └───┬────┘                  │
│       │        │                  │                       │
│  ┌────▼─┐  ┌──▼───┐  ┌──────┐  ┌▼─────┐                │
│  │  CT1  │  │  CT2  │  │  CT3  │  │  CT4  │   Carrier    │
│  │(OS T) │  │(OS T) │  │(OS T) │  │(OS T) │   Platform   │
│  └───────┘  └───────┘  └──────┘  └───────┘   Threads     │
└──────────────────────────────────────────────────────────┘

VT = Virtual Thread (millions OK, tiny heap segment stack)
CT = Carrier Thread (= CPU cores, OS-managed, expensive)

When VT hits blocking I/O:
  1. JVM parks VT (saves state to heap object)
  2. Unmounts VT from CT
  3. CT picks up next runnable VT
  4. When I/O completes, VT re-mounted on any available CT
```

### 4.2 Code Migration: Platform → Virtual

```java
// Before Java 21: limited by thread pool size
@Bean
ExecutorService executor() {
    return Executors.newFixedThreadPool(200);  // Hard limit: 200 concurrent
}

// Java 21: unlimited concurrency for I/O-bound work
@Bean
ExecutorService executor() {
    return Executors.newVirtualThreadPerTaskExecutor();  // Millions of concurrent VTs
}

// Spring Boot 3.2+: enable virtual threads for Tomcat
// application.properties:
// spring.threads.virtual.enabled=true
```

### 4.3 Critical: Virtual Thread Pitfalls

```java
// PITFALL 1: synchronized + blocking I/O = PINNED carrier thread
// (Carrier thread blocked, cannot serve other VTs → defeats the purpose)
synchronized (this) {
    response = httpClient.send(req, bodyHandler);  // I/O inside synchronized = BAD
}

// FIX: Use ReentrantLock (allows VT to unmount during I/O)
lock.lock();
try {
    response = httpClient.send(req, bodyHandler);  // OK with ReentrantLock
} finally { lock.unlock(); }

// PITFALL 2: DB connection pools
// 10,000 VTs × each wants a DB connection → PROBLEM: DB only handles 100
// FIX: Bounded semaphore limits concurrent DB access
Semaphore dbSlots = new Semaphore(50);  // Max 50 concurrent DB ops

// PITFALL 3: ThreadLocal with millions of VTs
// Each VT gets its own ThreadLocal copy → millions of copies → memory pressure
// FIX: ScopedValue for propagated context (Java 21)
ScopedValue<RequestContext> CONTEXT = ScopedValue.newInstance();
ScopedValue.where(CONTEXT, ctx).run(() -> processRequest());
```

### 4.4 Structured Concurrency (Java 21)

```java
// Problem with CompletableFuture: if one subtask fails, others orphaned
// StructuredTaskScope: automatic cancellation of all subtasks on failure

try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var userTask   = scope.fork(() -> fetchUser(userId));    // VT 1
    var ordersTask = scope.fork(() -> fetchOrders(userId));  // VT 2
    var recsTask   = scope.fork(() -> fetchRecs(userId));    // VT 3

    scope.join().throwIfFailed();  // Wait; if any fails, cancel all 3

    // All succeeded
    return new Page(userTask.get(), ordersTask.get(), recsTask.get());
}
// Scope guarantees: no VT outlives the try block. No orphaned work.
```

---

## 5. Deadlock Prevention Strategies

### 5.1 Strategy 1: Lock Ordering (canonical)

Always acquire multiple locks in a consistent order across all code paths.

```java
// System-wide rule: always lock lower accountId first
void transfer(Account from, Account to) {
    Account first  = from.id() < to.id() ? from : to;
    Account second = first == from ? to : from;
    synchronized (first) {
        synchronized (second) {
            // Guaranteed no deadlock: ordering is consistent
        }
    }
}
```

### 5.2 Strategy 2: Timed TryLock (give up and retry)

```java
boolean transferWithRetry(Account from, Account to, BigDecimal amount)
        throws InterruptedException {
    int retries = 3;
    while (retries-- > 0) {
        if (tryTransfer(from, to, amount)) return true;
        Thread.sleep(ThreadLocalRandom.current().nextInt(10, 50)); // Jitter
    }
    throw new TransferException("Could not acquire locks after 3 attempts");
}
```

### 5.3 Strategy 3: Avoid Multiple Locks Entirely

Use atomic operations or message-passing instead of multiple locks.

```java
// Instead of locking two accounts, use a serialized transfer event
eventBus.publish(new TransferEvent(fromId, toId, amount));
// Single consumer processes transfers sequentially — no multi-lock needed
```

---

## 6. Thread Dump Analysis

```bash
# Capture thread dump
jcmd $(pgrep java) Thread.print > dump-$(date +%H%M%S).txt

# Key states to understand:
# RUNNABLE    — executing or waiting for OS CPU slice
# BLOCKED     — waiting for a monitor lock (synchronized)
# WAITING     — Object.wait(), LockSupport.park(), Thread.join()
# TIMED_WAITING — above with timeout
# TERMINATED  — finished

# Find deadlocks
grep -A2 "Found.*deadlock" dump.txt

# Count threads by state
grep "java.lang.Thread.State:" dump.txt | sort | uniq -c | sort -rn

# Find hottest lock contention
grep "waiting to lock" dump.txt | grep -oP '<0x[0-9a-f]+>' | sort | uniq -c | sort -rn
```
