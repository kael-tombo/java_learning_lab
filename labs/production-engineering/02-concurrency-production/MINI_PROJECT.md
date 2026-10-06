# Lab 02: Concurrency in Production — Mini Project

## Project: `ConcurrencyBench` — Executor Sizing Lab, Bulkheads, and Leak Detectors

**Time**: 8–12 hours | **Difficulty**: Advanced | **Stack**: Java 21, `ThreadPoolExecutor`, `CompletableFuture`, JFR, `jcmd`

Build a harness that lets you *measure* the concurrency economics of this lab instead of believing them: pool sizing sweeps, bulkhead isolation under a slow dependency, thread-leak detection, and a `ThreadLocal` leak reproducer.

---

## Part 1 — Pool sizing sweep (Part 2 of MATH)

Build a service simulator with a fake downstream that has a configurable latency distribution:

```java
public final class FakeDependency {
    private final long p50Micros;
    private final long jitter;
    private final double failureRate;

    public FakeDependency(long p50Micros, long jitter, double failureRate) {
        this.p50Micros = p50Micros; this.jitter = jitter; this.failureRate = failureRate;
    }

    /** Log-normal-ish latency so tails are realistic. */
    public long callMicros() throws InterruptedException {
        if (ThreadLocalRandom.current().nextDouble() < failureRate) {
            throw new DownstreamException("simulated 503");
        }
        double u1 = ThreadLocalRandom.current().nextDouble();
        double u2 = ThreadLocalRandom.current().nextDouble();
        double z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
        return Math.max(1, p50Micros + (long) (z * jitter));
    }
}

public record SwepPoint(int poolSize, double offeredRps, double achievedRps,
                        long p50, long p99, long p999, double cpuSeconds) {}
```

Sweep `poolSize ∈ {8, 16, 32, 64, 128, 256, 512}` at fixed offered load, driving with a paced load generator:

```java
static SwepPoint sweep(int poolSize, FakeDependency dep, double targetRps, Duration duration)
        throws InterruptedException {
    var queue   = new ArrayBlockingQueue<Task>(poolSize * 2);
    var metrics = new Metrics();
    var pool = new ThreadPoolExecutor(poolSize, poolSize, 0, MILLISECONDS,
            queue, new ThreadPoolExecutor.CallerRunsPolicy());

    long deadline = System.nanoTime() + duration.toNanos();
    long intervalNanos = (long) (1e9 / targetRps);
    long next = System.nanoTime();
    for (long n = 0; System.nanoTime() < deadline; n++) {
        next += intervalNanos;
        sleepUntil(next);
        pool.execute(() -> {
            long start = System.nanoTime();
            try {
                Thread.sleep(Duration.ofNanos(dep.callMicros()));
                metrics.record(System.nanoTime() - start);
            } catch (Exception e) {
                metrics.recordFailure(System.nanoTime() - start);
            }
        });
    }
    pool.shutdown();
    pool.awaitTermination(1, TimeUnit.MINUTES);
    return new SwepPoint(poolSize, targetRps, metrics.achievedRps(targetRps, duration),
            metrics.percentile(50), metrics.percentile(99), metrics.percentile(99.9),
            cpuSecondsUsed());
}
```

**Deliverable**: a table plus the two verdicts:
- Where does p99 start degrading (the `ρ ≈ 0.7` cliff)?
- Which pool size would you ship, and why not the largest?

Record the JDK version and `availableProcessors()` in your report — this result is hardware-dependent.

---

## Part 2 — Bulkheads under a partial outage

Simulate two dependencies, one healthy (20 ms) and one degraded (2 s, 30% errors). Route work through **separate pools** and compare against a single shared pool:

```java
public final class BulkheadConfig {
    private final ExecutorService fastPool;   // healthy dependency
    private final ExecutorService slowPool;   // degraded dependency
    private final Semaphore slowGate;        // hard concurrency cap

    public BulkheadConfig(int fastThreads, int slowThreads, int slowConcurrencyCap) {
        this.fastPool = Executors.newFixedThreadPool(fastThreads);
        this.slowPool  = new ThreadPoolExecutor(slowThreads, slowThreads, 0, SECONDS,
                new ArrayBlockingQueue<>(50), new ThreadPoolExecutor.AbortPolicy());
        this.slowGate = new Semaphore(slowConcurrencyCap);
    }

    public CompletableFuture<String> fetchFast() {
        return CompletableFuture.supplyAsync(this::callFast, fastPool);
    }

    public CompletableFuture<String> fetchSlow() {
        // gate first: reject fast rather than queueing behind a 2s dependency
        if (!slowGate.tryAcquire()) {
            return CompletableFuture.failedFuture(new BulkheadRejected());
        }
        return CompletableFuture.supplyAsync(() -> {
            try { return callSlow(); } finally { slowGate.release(); }
        }, slowPool).whenComplete((r, t) -> slowGate.releaseIfAcquired());
    }
}
```

Measure and report: p99 of the *fast* path with shared pool vs bulkheaded pool; the rejection rate of the slow path; total threads held.

**Expected finding**: with a shared pool, the degraded dependency starves the fast path and the good-path p99 degrades 50–100x. With bulkheads, good-path p99 is unchanged and the slow path fails fast.

---

## Part 3 — Thread leak detector

Write a detector you could ship as a diagnostics endpoint:

```java
public final class ThreadLeakDetector {
    private final Map<String, AtomicInteger> byName = new ConcurrentHashMap<>();

    public Map<String, Integer> census() {
        Thread[] all = new Thread[Thread.activeCount() * 2];
        int n = Thread.enumerate(all);
        for (int i = 0; i < n; i++) {
            String key = normalize(all[i].getName());   // pool-1-thread-7 -> pool-1
            byName.computeIfAbsent(key, k -> new AtomicInteger()).incrementAndGet();
        }
        return byName.entrySet().stream().collect(
            Collectors.toMap(Map.Entry::getKey, e -> e.getValue().get()));
    }

    private static String normalize(String name) {
        return name.replaceAll("-thread-\\d+$", "");
    }
}
```

Add a growth check: `census()` every 60s, alert when any normalized pool name grows monotonically for 5 samples.

**Reproduce the leak** with a deliberately bad executor factory, prove detection, then fix it:

```java
// BAD: a new pool per request
static ExecutorService leaky() {
    return Executors.newFixedThreadPool(20);
}

// GOOD: shared, named, shutdown on lifecycle
static final ExecutorService SHARED = new ThreadPoolExecutor(
        20, 20, 60, SECONDS, new ArrayBlockingQueue<>(200),
        new NamedThreadFactory("checkout-calls"),   // name them or you can't census them
        new ThreadPoolExecutor.AbortPolicy());
```

---

## Part 4 — `ThreadLocal` leak reproducer

Simulate a container thread pool that never gets replaced, set a `ThreadLocal` without cleanup, and show retained growth:

```java
public final class RequestContext {
    private static final ThreadLocal<RequestContext> CURRENT = new ThreadLocal<>();

    public static void begin(RequestContext ctx) { CURRENT.set(ctx); }
    public static void clear() { CURRENT.remove(); }     // never omit this

    static void simulateRequests(int requests) throws InterruptedException {
        var pool = Executors.newFixedThreadPool(4);
        for (int i = 0; i < requests; i++) {
            pool.submit(() -> {
                RequestContext ctx = new RequestContext(new byte[128 * 1024]); // "session"
                RequestContext.begin(ctx);
                // ... handler runs and "forgets" to clear ...
            });
        }
        pool.shutdown();
        pool.awaitTermination(1, MINUTES);
    }
}
```

Then: (1) run with `System.gc()` + `jcmd <pid> GC.class_histogram` and record the growth, (2) add `finally { RequestContext.clear(); }`, (3) re-run and show the difference.

---

## Part 5 — Deadlock lab

Plant a lock-ordering inversion, capture it, and annotate it:

```java
// Path A
synchronized (lockA) { synchronized (lockB) { doWork(); } }
// Path B — same resources, opposite order
synchronized (lockB) { synchronized (lockA) { doWork(); } }
```

Trigger both from two threads, then run `jcmd <pid> Thread.print` and identify:
- The two `BLOCKED (on object monitor)` threads,
- The lock owner of each,
- The cycle in the `Found one Java-level deadlock` section.

Then apply the prevention rule: a global lock acquisition order enforced by convention plus a test that runs all two-lock acquisitions in both orders.

---

## Acceptance Criteria

- [ ] Sweep table shows the `ρ ≈ 0.7` degradation cliff, with hardware and JDK recorded.
- [ ] Bulkhead experiment shows good-path p99 is unchanged by a degraded neighbor; numbers included.
- [ ] Thread-leak census identifies the leaked pool by normalized name and reports growth over time.
- [ ] `ThreadLocal` leak proven and fixed with before/after histogram evidence.
- [ ] Deadlock captured in a thread dump, cycle annotated, and an order-enforcement test added.
- [ ] You can state, in one sentence, the difference between "the pool is too small" and "the pool is too big."

---

## Stretch

- Add `LongAdder` vs `AtomicLong` contended-counter benchmarks and plot the crossover point.
- Implement a semaphore-bounded virtual-thread executor and compare against a fixed pool for 10k-concurrency fan-out.
- Capture JFR `jdk.JavaMonitorEnter` events and report total blocked time per monitor.
