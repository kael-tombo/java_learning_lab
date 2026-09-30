# INTERVIEW QUESTIONS: Thread Concurrency
## Lab 02 | Senior / Staff / Principal Level

---

## Senior Level (5+ years experience)

**Q1**: What is the difference between `volatile` and `synchronized`?

**Answer**: `volatile` guarantees visibility (every read sees the latest write) for a **single** variable — but gives NO atomicity for compound operations like `i++`. `synchronized` gives both mutual exclusion AND visibility for arbitrary code blocks. Use `volatile` when: single writer, multiple readers, no read-modify-write. Use `synchronized` (or `ReentrantLock`) when: compound operations or coordinating multiple variables.

---

**Q2**: Explain what `AtomicInteger.compareAndSet(expected, update)` does internally.

**Answer**: CAS (Compare-And-Swap) is a single CPU instruction. It atomically: (1) reads the current value, (2) compares it with `expected`, (3) if equal: writes `update` and returns true; if not equal: leaves unchanged and returns false. CAS loops (`while (!cas()) {}`) implement lock-free algorithms. Advantage: no OS lock, no context switch. Disadvantage: ABA problem (value changed A→B→A, CAS doesn't detect the intermediate change — use `AtomicStampedReference` if this matters).

---

**Q3**: You see 200 threads in BLOCKED state on the same monitor in a thread dump. What does that mean and what do you do?

**Answer**: A single lock is a bottleneck — all 200 threads waiting for one thread to release it. Diagnosis: identify the lock object and what code holds it. Solutions: (1) Reduce time holding lock (minimize work inside synchronized). (2) Lock striping: split one lock into N locks (ConcurrentHashMap pattern). (3) Replace lock with lock-free alternatives (AtomicXxx, ConcurrentHashMap.compute). (4) Redesign to eliminate shared state (message-passing).

---

## Staff Engineer Level

**Q4**: Design a thread-safe rate limiter that allows 1000 requests per second. It must be as fast as possible.

**Answer**:
```java
// Token bucket with AtomicLong — lock-free
public class TokenBucketLimiter {
    private final long maxTokens;
    private final long refillNanos;  // Time per token
    private final AtomicLong nextRefillTime;
    private final AtomicLong availableTokens;

    public TokenBucketLimiter(long ratePerSecond) {
        this.maxTokens = ratePerSecond;
        this.refillNanos = 1_000_000_000L / ratePerSecond;  // Nanos per token
        this.availableTokens = new AtomicLong(ratePerSecond);
        this.nextRefillTime = new AtomicLong(System.nanoTime());
    }

    public boolean tryAcquire() {
        refill();
        // CAS decrement — no lock
        long current;
        do {
            current = availableTokens.get();
            if (current <= 0) return false;
        } while (!availableTokens.compareAndSet(current, current - 1));
        return true;
    }

    private void refill() {
        long now = System.nanoTime();
        long next = nextRefillTime.get();
        if (now >= next) {
            long tokensToAdd = (now - next) / refillNanos + 1;
            nextRefillTime.set(next + tokensToAdd * refillNanos);
            availableTokens.getAndUpdate(t -> Math.min(maxTokens, t + tokensToAdd));
        }
    }
}
```

---

**Q5**: What is `ForkJoinPool` work-stealing and when should you use it?

**Answer**: Work-stealing: each thread has a deque of tasks. When idle, it "steals" tasks from the tail of another thread's deque (while the owner pushes/pops from head). Benefits: automatically balances load across threads when subtasks have unequal sizes. Use ForkJoinPool for: recursive divide-and-conquer algorithms, parallel streams (`Stream.parallel()`), `CompletableFuture.supplyAsync()` (uses `commonPool()`). Don't use for: I/O-bound tasks (blocks pool), tasks with very different durations (poor stealing). For I/O-bound work in Java 21: use Virtual Threads instead.

---

**Q6**: A service uses Virtual Threads but throughput is only 800 req/s instead of expected 50,000 req/s. How do you diagnose?

**Answer**:
1. Enable `-Djdk.tracePinnedThreads=full` — look for pinned carrier threads
2. Check for `synchronized` blocks containing I/O (most common cause of pinning)
3. Check DB pool size: 50,000 VTs × each holding a connection = impossible; need bounded semaphore
4. Look for `ThreadLocal` abuse causing memory pressure
5. Check if CPU is the bottleneck (CPU-bound work doesn't benefit from VTs)
6. Profile with async-profiler `-e wall` to see where VTs spend time

---

## Principal Engineer Level

**Q7**: You need to build a distributed lock for a critical resource (deploy one key = one lock) across 50 microservice instances. Java-only solution won't work — how do you design this?

**Answer** (comprehensive):

**Options**:
1. **Redis SETNX + expiry**: `SET lock:key value NX PX 30000` (atomic). Redlock algorithm for HA Redis. Watch: clock skew, GC pauses, network delay can all cause lock expiry before work finishes.
2. **ZooKeeper ephemeral nodes**: Strong consistency, automatic release on node failure. Higher latency (~5ms). Best for infrequent locking (leader election, not per-request).
3. **Database `SELECT FOR UPDATE`**: If already using a DB. Simple, transactional, but DB is bottleneck.
4. **Etcd transactions**: Similar to ZooKeeper, strongly consistent.

**Key design considerations**:
- Lock expiry/renewal: work must heartbeat to renew lock if it takes longer than expected
- What happens if lock holder dies? Expiry + auto-release
- Is the operation idempotent? If yes, relaxed requirements (don't even need true distributed lock — at-least-once with idempotency key is enough)
- For most cases: idempotency key + database unique constraint is simpler and more reliable than distributed locking

---

## Quickfire Round

1. `CountDownLatch` vs `CyclicBarrier`? — Latch: one-time, N events then release. Barrier: all threads meet at a point repeatedly.
2. What is a happens-before violation example? — Double-checked locking without volatile before Java 5
3. `shutdownNow()` vs `shutdown()`? — `shutdown()`: no new tasks, finish queued. `shutdownNow()`: interrupt running, return queued, no guarantees
4. What is ABA problem in CAS? — Value goes A→B→A; CAS sees A and succeeds, missing the intermediate change
5. What is false sharing? — Two variables on same CPU cache line; one thread writes one, invalidates other thread's cache for the other
6. Fix false sharing? — `@Contended` annotation (Java 8+) pads field to its own cache line
7. What does `Thread.yield()` do? — Hints JVM to release CPU. Behavior is OS/JVM-dependent. Rarely useful.
8. Max virtual threads in a JVM? — Millions; limited by heap (each ~1-10KB stack)
9. Can VTs use `ThreadLocal`? — Yes; but millions of VTs × ThreadLocal value = memory pressure. Prefer `ScopedValue`.
10. What is the `ForkJoinPool.commonPool()`? — Shared pool used by parallel streams, CompletableFuture.supplyAsync without executor. Sized = CPU count - 1.
