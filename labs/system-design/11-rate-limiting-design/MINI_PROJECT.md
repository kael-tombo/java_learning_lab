# Rate Limiting Design - MINI PROJECT

## Project: A Two-Tier Rate Limiter That Survives a Load Test

**Time**: 8-12 hours

**Goal**: Implement four limiters, prove their behavioural differences with
tests, then build the layered limiter you would actually deploy — and watch it
behave correctly when its backing store dies.

### Step 1: Fixed Window (and Prove Its Flaw) (1 h)

```java
// Key -> (windowStart, count)
public boolean allow(String key) {
    long window = nowMillis() / WINDOW_MILLIS;
    Counter c = counters.computeIfAbsent(key, k -> new Counter(window, 0));
    if (c.window != window) { c.window = window; c.count = 0; }   // NOT atomic!
    return ++c.count <= limit;
}
```

**Required test:** send `limit` requests at `t = windowEnd - 10ms`, then
`limit` more at `t = windowEnd + 10ms`. Assert `2 * limit` succeeded in 20 ms.
Then write in the file: *"this is a 2x burst vulnerability."*

Note the non-atomic reset above — fix it with `compute()` and add a
concurrency test proving exactly `limit` succeed from 100 threads.

### Step 2: Sliding Window Counter (1 h)

```java
// Key -> (prevWindowCount, currWindowCount, currWindowStart)
```
Interpolate between windows (formula in `MATH_FOUNDATION.md`). Tests:
- A steady 100/s for 10 s admits ~1,000. Assert within 2% of ideal.
- A boundary burst no longer gets 2x.
- A client that used its budget at the end of window *k* cannot immediately
  spend window *k+1*'s budget.

### Step 3: Token Bucket with a Fake Clock (2 h)

The most important test asset: a `FakeClock` so you can test refill behaviour
without sleeping.

Required tests:
- Burst to `bucket_size` immediately, then the next request is denied.
- After `elapsed * refill_rate`, exactly the right number is admitted. Assert
  **exact integer** counts (use integer microtokens, not doubles).
- Clock moving **backwards** (NTP step): assert the limiter does not break.
  This test is why you use `nanoTime`, not `currentTimeMillis`.
- Bucket size is respected: a long idle period never accumulates more than
  `bucket_size`.

### Step 4: Concurrency Limiter (1 h)

A semaphore plus a timeout. Tests:
- 20 permits, 100 concurrent callers, assert observed concurrency never
  exceeds 20. **Instrument with an in-flight counter** — do not infer it from
  timings.
- Waiters time out and get a distinguishable error from "denied".
- Report throughput vs. Little's Law (`permits / mean_service_time`) and check
  the measurement matches the theory.

### Step 5: The Two-Tier Limiter (2 h)

```
request -> local limiter (per-instance, in-memory, fast)
       -> global limiter (Redis-equivalent store)
       -> handler
```

Local limit derived, not guessed:
```
G = 10,000/s global;  N = 40 instances
local_limit = ceil(G / N) * 1.2 = 300/s
```

Required tests:
- **Single noisy instance**: one instance sends 10,000/s. Assert the global
  limiter still admits at most `G` overall, and that other instances are not
  starved beyond their share.
- **Store down**: assert degraded mode falls back to the local limit rather than
  allowing unbounded traffic or denying everything.
- **Store slow (200 ms)**: assert a local cache with a short TTL (e.g. 250 ms)
  keeps p99 latency sane, and state the accuracy you give up by caching
  decisions.

### Step 6: The Client Contract (1 h)

Implement the full response contract and assert it exactly:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 3
RateLimit-Limit: 100
RateLimit-Remaining: 0
RateLimit-Reset: 3
```

Then implement **full-jitter retry** in a test client and run the load test
through it. Assert: the server's admitted-request rate stays at the limit
rather than oscillating, and the retry herd does not synchronise. Compare
against no-jitter (expected: oscillation) and record both graphs' numbers.

### Step 7: Load Test and Report (2 h)

Drive 5,000 req/s for 60 s across all four algorithms. Record:

| Algorithm | Admitted | 429s | p50/p99 latency | Store ops/s | Boundary burst observed |
|-----------|----------|------|-----------------|-------------|------------------------|
| Fixed window | | | | | |
| Sliding window counter | | | | | |
| Token bucket | | | | | |
| Concurrency (20 permits) | | | | | |

**Write the conclusion:** which algorithm for which endpoint class, with the
measured numbers as evidence.

### Deliverables

1. Four limiters with correctness tests.
2. The 2x boundary-burst test that condemns fixed window.
3. Token bucket with a fake clock, integer arithmetic, and a clock-regression
   test.
4. Concurrency limiter with an instrumented in-flight counter proving the bound.
5. Two-tier limiter with a noisy-instance test and a store-down degraded-mode
   test.
6. Full `429` contract plus a full-jitter retry client, with the oscillation
   comparison.
7. Load test table and a written algorithm-per-endpoint recommendation.

### Stretch

- Add weighted fair queuing across three plan tiers and verify each tier's
  share matches `w_i / sum(w)` within 1% over 60 s.
- Add a **hot-key sharding** strategy for the global store (N shards keyed by
  hash of identity) and show it scales the store's write throughput roughly
  linearly.