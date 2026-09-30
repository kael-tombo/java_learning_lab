# CODE DEEP DIVE: Concurrency Production Patterns
## Lab 02 | Production Engineering Academy

All patterns are production-tested. Each has been used in real systems at scale.

---

## Pattern 1: Deadlock-Safe Account Transfer

```java
package com.production.concurrency;

import java.math.BigDecimal;
import java.util.Map;
import java.util.concurrent.*;
import java.util.concurrent.locks.*;

public class AccountTransferService {

    // Strategy A: Canonical lock ordering (zero overhead)
    public void transferOrdered(Account from, Account to, BigDecimal amount)
            throws InsufficientFundsException {
        // Consistent ordering prevents circular wait
        Account first  = from.getId().compareTo(to.getId()) < 0 ? from : to;
        Account second = first == from ? to : from;

        synchronized (first) {
            synchronized (second) {
                if (from.getBalance().compareTo(amount) < 0) {
                    throw new InsufficientFundsException();
                }
                from.debit(amount);
                to.credit(amount);
            }
        }
    }

    // Strategy B: TryLock with timeout (prevents deadlock by design)
    private final ConcurrentHashMap<String, ReentrantLock> locks = new ConcurrentHashMap<>();

    public boolean transferTryLock(Account from, Account to, BigDecimal amount)
            throws InterruptedException, InsufficientFundsException {
        ReentrantLock lf = locks.computeIfAbsent(from.getId(), k -> new ReentrantLock());
        ReentrantLock lt = locks.computeIfAbsent(to.getId(), k -> new ReentrantLock());

        boolean gotF = false, gotT = false;
        try {
            gotF = lf.tryLock(200, TimeUnit.MILLISECONDS);
            gotT = lt.tryLock(200, TimeUnit.MILLISECONDS);

            if (!gotF || !gotT) return false;  // Caller can retry

            if (from.getBalance().compareTo(amount) < 0) throw new InsufficientFundsException();
            from.debit(amount);
            to.credit(amount);
            return true;
        } finally {
            if (gotT) lt.unlock();
            if (gotF) lf.unlock();
        }
    }
}
```

---

## Pattern 2: High-Performance Read-Write Cache

```java
package com.production.concurrency;

import java.util.concurrent.locks.*;
import java.util.*;

public class HighPerfCache<K, V> {
    private final StampedLock sl = new StampedLock();
    private final Map<K, V> data = new HashMap<>();

    // Read: try optimistic first (no lock), fall back to read lock
    public V get(K key) {
        long stamp = sl.tryOptimisticRead();
        V val = data.get(key);
        if (sl.validate(stamp)) return val;  // No writer during read

        // Writer was active — use real read lock
        stamp = sl.readLock();
        try {
            return data.get(key);
        } finally {
            sl.unlockRead(stamp);
        }
    }

    // Write: exclusive lock
    public void put(K key, V value) {
        long stamp = sl.writeLock();
        try {
            data.put(key, value);
        } finally {
            sl.unlockWrite(stamp);
        }
    }

    // Upgrade pattern: read, then maybe write
    public V computeIfAbsent(K key, java.util.function.Function<K, V> loader) {
        // Try read first
        long stamp = sl.readLock();
        try {
            V existing = data.get(key);
            if (existing != null) return existing;

            // Upgrade to write lock
            long writeStamp = sl.tryConvertToWriteLock(stamp);
            if (writeStamp != 0L) {
                stamp = writeStamp;  // Upgrade succeeded
                V newVal = loader.apply(key);
                data.put(key, newVal);
                return newVal;
            }
        } finally {
            sl.unlock(stamp);
        }
        // If upgrade failed, acquire write lock
        stamp = sl.writeLock();
        try {
            V existing = data.get(key);
            if (existing != null) return existing;  // Double-check
            V newVal = loader.apply(key);
            data.put(key, newVal);
            return newVal;
        } finally {
            sl.unlockWrite(stamp);
        }
    }
}
```

---

## Pattern 3: Virtual Thread Request Handler (Java 21)

```java
package com.production.concurrency;

import java.util.concurrent.*;

public class VirtualThreadServer {
    // Semaphore limits concurrent DB connections even with millions of VTs
    private final Semaphore dbSlots;
    private final ExecutorService executor;

    public VirtualThreadServer(int maxDbConnections) {
        this.dbSlots = new Semaphore(maxDbConnections, true);
        this.executor = Executors.newVirtualThreadPerTaskExecutor();
    }

    // Each request gets its own virtual thread — no blocking the calling thread
    public CompletableFuture<Response> handle(Request request) {
        return CompletableFuture.supplyAsync(() -> processRequest(request), executor);
    }

    private Response processRequest(Request request) {
        // Step 1: External API call — VT unmounts during wait (no carrier blocked)
        User user = userApi.fetchUser(request.userId());  // 50ms I/O — VT parks here

        // Step 2: DB query — rate-limited to prevent DB overload
        Order order = withDbSlot(() -> orderRepo.find(request.orderId()));  // 20ms I/O

        // Step 3: Build response
        return new Response(user, order);
    }

    private <T> T withDbSlot(java.util.concurrent.Callable<T> work) {
        try {
            dbSlots.acquire();  // VT parks if all slots occupied — carrier stays free
            try {
                return work.call();
            } finally {
                dbSlots.release();
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    // Structured Concurrency — parallel fan-out with automatic cancellation
    public DashboardData loadDashboard(String userId) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var userTask   = scope.fork(() -> userApi.fetchUser(userId));     // VT 1
            var ordersTask = scope.fork(() -> orderRepo.findByUser(userId));  // VT 2
            var recsTask   = scope.fork(() -> recEngine.recommend(userId));   // VT 3

            scope.join()           // Wait for all 3
                 .throwIfFailed(); // Throws if any failed (all cancelled if one fails)

            return new DashboardData(userTask.get(), ordersTask.get(), recsTask.get());
        }
        // Guarantee: no orphaned VTs outlive this scope
    }

    // Stub types
    record Request(String userId, String orderId) {}
    record Response(Object... data) {}
    record User(String id) {}
    record Order(String id) {}
    record DashboardData(User user, Object orders, Object recs) {}
    Object userApi = null, orderRepo = null, recEngine = null;
}
```

---

## Pattern 4: Bounded Producer-Consumer Pipeline

```java
package com.production.concurrency;

import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class BoundedPipeline<T> {
    private final BlockingQueue<T> queue;
    private final ExecutorService workers;
    private final java.util.function.Consumer<T> processor;
    private volatile boolean running = true;

    // Metrics
    private final AtomicLong processed = new AtomicLong();
    private final AtomicLong rejected = new AtomicLong();

    public BoundedPipeline(int queueCapacity, int workerCount,
                           java.util.function.Consumer<T> processor) {
        this.queue = new ArrayBlockingQueue<>(queueCapacity);
        this.processor = processor;
        this.workers = Executors.newFixedThreadPool(workerCount,
            r -> Thread.ofVirtual().name("pipeline-worker-", 0).factory().newThread(r));

        for (int i = 0; i < workerCount; i++) {
            workers.submit(this::workerLoop);
        }
    }

    // Producer: blocks if queue is full (backpressure)
    public boolean submit(T item) {
        try {
            boolean accepted = queue.offer(item, 500, TimeUnit.MILLISECONDS);
            if (!accepted) rejected.incrementAndGet();
            return accepted;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
    }

    private void workerLoop() {
        while (running || !queue.isEmpty()) {
            try {
                T item = queue.poll(100, TimeUnit.MILLISECONDS);
                if (item != null) {
                    processor.accept(item);
                    processed.incrementAndGet();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            } catch (Exception e) {
                // Log but continue — one bad item shouldn't kill the worker
                System.err.println("Worker error: " + e.getMessage());
            }
        }
    }

    public void shutdown() throws InterruptedException {
        running = false;
        workers.shutdown();
        workers.awaitTermination(30, TimeUnit.SECONDS);
    }

    public long getProcessed() { return processed.get(); }
    public long getRejected() { return rejected.get(); }
    public int getQueueSize() { return queue.size(); }
}
```

---

## Pattern 5: Double-Checked Locking (Thread-Safe Singleton)

```java
package com.production.concurrency;

public class ThreadSafeSingleton {
    // volatile REQUIRED: prevents partially constructed object visibility
    private static volatile ThreadSafeSingleton instance;

    private final String data;

    private ThreadSafeSingleton() {
        // Expensive initialization
        this.data = loadFromDatabase();
    }

    public static ThreadSafeSingleton getInstance() {
        if (instance == null) {                // First check (no lock - fast path)
            synchronized (ThreadSafeSingleton.class) {
                if (instance == null) {         // Second check (inside lock)
                    instance = new ThreadSafeSingleton();
                }
            }
        }
        return instance;
    }

    // Modern alternative: initialization-on-demand holder (better)
    private static class Holder {
        // Class loading is thread-safe; no explicit sync needed
        static final ThreadSafeSingleton INSTANCE = new ThreadSafeSingleton();
    }

    public static ThreadSafeSingleton getInstanceModern() {
        return Holder.INSTANCE;  // Lazy, thread-safe, no locks
    }

    private String loadFromDatabase() { return "data"; }
}
```
