# Lab 04: Distributed Resilience — Mini Project

## Project: `ResilienceHarness` — Make Degradation Measurable

**Time**: 10–14 hours | **Difficulty**: Advanced | **Stack**: Java 21, Resilience4j (or hand-rolled primitives), Micrometer, Testcontainers

Build a two-service system with a fault-injection proxy between them, then run a battery of degradation experiments and produce a **resilience scorecard**. The goal is that every resilience claim in this lab has a number attached.

---

## Part 1 — The two services

**Service A (caller)** — exposes `POST /checkout`, calls Service B with a configured budget:

```java
@RestController
@RequestMapping("/checkout")
public class CheckoutController {
    private final InventoryClient client;
    private final OrderStore orders;

    @PostMapping
    public ResponseEntity<?> checkout(@RequestBody OrderRequest req,
                                     @RequestHeader(value = "X-Deadline", required = false) Long deadlineMs) {
        Deadline dl = Deadline.fromNowOrDefault(deadlineMs, Duration.ofMillis(250));
        BulkheadResult<Stock> stock;
        try {
            stock = bulkhead.executeSupplier(() -> client.reserve(dl, req.sku(), req.qty()));
        } catch (BulkheadFullException e) {
            // fast fail: shed instead of queueing into a timeout
            metrics.counter("checkout.shed").increment();
            return ResponseEntity.status(429).header("Retry-After", "1")
                    .body(new ErrorBody("BUSY", "try again shortly"));
        } catch (DeadlineExceededException e) {
            metrics.counter("checkout.timeout").increment();
            return ResponseEntity.status(504).body(new ErrorBody("UPSTREAM_SLOW", "inventory unavailable"));
        }
        if (stock.isStale()) {
            metrics.counter("checkout.stale_fallback").increment();
            // acceptable degradation: serve from cache, flag it
        }
        Order order = orders.create(req, stock.value());
        return ResponseEntity.ok(order);
    }
}
```

**Service B (callee)** — exposes `GET /stock?sku=`, with fault modes injectable at runtime:

```java
@RestController
public class StockController {
    private final StockRepository repo;

    @GetMapping("/stock")
    public Stock stock(@RequestParam String sku) {
        FaultProfile f = faults.current();
        if (f.errorRate() > 0 && random() < f.errorRate())
            throw new UpstreamUnavailable("injected");
        if (f.latencyMs() > 0) sleepUninterruptibly(f.latencyMs());
        if (f.poolExhaustion()) { pool.acquire(); /* hold forever until released */ }
        return repo.findBySku(sku);
    }
}
```

**Fault profile** (mutable via an admin endpoint so you can change the fault without redeploying):

```java
public record FaultProfile(Duration latency, double errorRate,
                            boolean socketReset, boolean poolExhaustion,
                            Duration hangTimeout, double slowBodyRate) {}
```

Implement the "slow body" fault (headers fast, body slow) explicitly — it is the fault that produces the most realistic production cascade and the one that breaks naive timeout configurations.

---

## Part 2 — Resilience primitives, hand-rolled first

Before using Resilience4j, implement each primitive so the mechanics are yours:

```java
public final class CircuitBreaker {
    private enum State { CLOSED, OPEN, HALF_OPEN }
    private final AtomicReference<State> state = new AtomicReference<>(State.CLOSED);
    private final int minCalls;          // statistical floor, e.g. 200
    private final double failureRatio;   // e.g. 0.5
    private final Duration openDuration;
    private final int halfOpenMaxCalls;  // e.g. 10
    private final SlidingWindow window;  // count-based

    public <T> T call(CheckedSupplier<T> op) throws Exception {
        if (state.get() == State.OPEN && !halfOpenEligible()) throw new CircuitOpen();
        if (state.get() == State.HALF_OPEN && halfOpenInFlight() >= halfOpenMaxCalls) {
            throw new CircuitOpen();     // prevent half-open storm
        }
        long id = window.record();
        try {
            T v = op.get();
            window.success(id);
            if (state.get() == State.HALF_OPEN) close();
            return v;
        } catch (Exception e) {
            window.failure(id);
            evaluate();
            throw e;
        }
    }

    private void evaluate() {
        Stats s = window.snapshot();
        if (s.total() >= minCalls && s.failureRate() >= failureRatio) {
            state.set(State.OPEN);
            openedAt = System.nanoTime();
        }
    }
}
```

Also implement: a **count-based sliding window**, a **deadline propagator**, a **semaphore bulkhead with metrics**, and a **full-jitter backoff**.

Then write the equivalent Resilience4j configuration and **compare** — the exercise is noticing which defaults differ from your derivation:

```yaml
resilience4j:
  circuitbreaker:
    instances:
      inventory:
        slidingWindowType: COUNT_BASED
        slidingWindowSize: 100
        minimumNumberOfCalls: 20
        failureRateThreshold: 50
        slowCallRateThreshold: 60
        slowCallDurationThreshold: 250ms
        waitDurationInOpenState: 30s
        permittedNumberOfCallsInHalfOpenState: 10
        automaticTransitionFromOpenToHalfOpenEnabled: true
  retry:
    instances:
      inventory:
        maxAttempts: 3
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
        enableRandomizedWait: true
        randomizedWaitFactor: 1.0     # full jitter
        retryExceptionPredicate: only transient
  timelimiter:      # apply timeouts to async paths too
    instances:
      inventory:
        timeoutDuration: 120ms
```

---

## Part 3 — The experiment matrix

For each experiment record: throughput, p50/p95/p99/p999, error rate by class, A-side thread count, connection-pool utilization, breaker state timeline, and **recovery time** (from fault removal to all metrics inside the steady-state band).

| # | Fault | Duration | Hypothesis to test |
|---|---|---|---|
| E1 | Baseline | 5 min | Establish steady-state band |
| E2 | B latency 200 ms | 3 min | Latency budget holds; no shed |
| E3 | B latency 2 s | 3 min | Deadline propagates; fast fail; no thread growth |
| E4 | B latency 2 s + 30% errors | 3 min | Breaker opens; amplification ≤ 1.2x |
| E5 | B 100% errors | 2 min | Breaker opens within budget; fallback serves |
| E6 | B socket reset | 2 min | Retries with jitter; no correlated spike |
| E7 | B "slow body" | 3 min | Read timeout fires; connections released |
| E8 | B hangs forever | 2 min | Timeouts bound resource use; pool does not leak |
| E9 | Fault removed | 5 min | No retry avalanche; recovery < 60 s |

**Expected finding for E3/E8** (the important one): if `W_p99` doubles and your timeout budget does not shrink, A's in-flight count grows, connections leak, and B's effective load multiplies. Compare measured amplification to the theoretical `amp = (r+1)^depth`.

---

## Part 4 — Load generator with coordinated-omission correction

Use an **open-loop** generator (arrival schedule independent of response) and record with `HdrHistogram`:

```java
final class OpenLoopDriver {
    private final HdrHistogram histogram = new HdrHistogram(TimeUnit.SECONDS.toNanos(30), 3);

    void run(Duration duration, double targetRps, ExecutorService callers) {
        long intervalNanos = (long) (1_000_000_000L / targetRps);
        long start = System.nanoTime();
        long issued = 0, completed = 0;
        long next = start;
        while (System.nanoTime() - start < duration.toNanos()) {
            next += intervalNanos;
            sleepUntil(next);                        // never skip: that is coordinated omission
            issued++;
            final long sched = next;
            callers.submit(() -> {
                long t0 = System.nanoTime();
                try { callServiceA(); histogram.recordValue(System.nanoTime() - t0); }
                catch (Exception e) { failures.increment(); }
                finally { completed++; }
            });
        }
        // Report BOTH achieved RPS (issued/time) and completed RPS — a gap is saturation
        report(issued, completed, histogram);
    }

    void report(long issued, long completed, HdrHistogram h) {
        System.out.printf("issuedRps=%.1f completedRps=%.1f  loss=%.2f%%  p50=%dms p99=%dms p999=%dms max=%dms%n",
            issued / elapsedSecs(), completed / elapsedSecs(),
            100.0 * (issued - completed) / issued,
            h.getValueAtPercentile(50) / 1_000_000,
            h.getValueAtPercentile(99) / 1_000_000,
            h.getValueAtPercentile(99.9) / 1_000_000,
            h.getMaxValue() / 1_000_000);
    }
}
```

---

## Part 5 — Resilience scorecard

Produce `RESILIENCE_SCORECARD.md`:

| Experiment | p99 (ms) | Error % | Threads (max) | Pool util % | Breaker open at | Amplification | Recovery (s) | Verdict |
|---|---|---|---|---|---|---|---|---|
| E1 | 42 | 0.02 | 210 | 41 | — | 1.0x | — | PASS |
| E3 | 251 | 6.1 | 640 | 98 | 41 s | 1.1x | 22 | FAIL: pool saturated |
| ... | | | | | | | | |

Then write the **top three fixes**, each with the arithmetic that shows the expected improvement, and re-run E3 to verify the fix moved the number.

---

## Part 6 — A chaos-style steady-state declaration

Before running anything, write this down (and treat violating it as an abort condition):

```
STEADY-STATE HYPOTHESIS (Service A)
  - completed RPS        ≥ 98% of target
  - p99 latency          < 250 ms
  - error rate           < 0.1%
  - live threads         < 300
  - pool utilization     < 70%
  - breaker              CLOSED
ABORT THRESHOLDS (stop the experiment immediately)
  - error rate           > 25% for 15 s
  - thread count         > 900 (risk of native thread OOM)
  - A restart count      > 1
```

---

## Acceptance Criteria

- [ ] All nine experiments executed with results recorded.
- [ ] E3 or E8 demonstrates the cascade (or its absence) and you can explain which.
- [ ] Measured retry amplification is within 20% of the theoretical `(r+1)^depth`.
- [ ] Recovery time measured after fault removal, with no thread or connection growth.
- [ ] Scorecard has top three fixes with arithmetic, and at least one verified by re-run.
- [ ] Steady-state hypothesis and abort thresholds declared before experiments.

---

## Stretch

- Add a second caller instance to show correlated-retry thundering herd vs jittered retry.
- Add a slow *consumer* of A's queue to demonstrate unbounded-queue failure, then fix with shedding.
- Inject GC pauses into A (e.g. `-XX:+UseZGC` with a huge heap) and verify the deadline path still holds.
- Convert E9's retry-avalanche window into an explicit alert threshold.
