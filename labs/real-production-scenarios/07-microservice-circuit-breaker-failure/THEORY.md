# THEORY — Lab 07: Microservice Circuit-Breaker Failure

## 1. Mechanics: How One Slow Service Kills Fifteen
- `payment-service` latency 50ms→500ms+; callers block threads waiting (30s timeout).
- Circuit breaker stays CLOSED (threshold 80% too high; timeouts not counted as failures fast enough).
- Little's Law: W↑ → queued L↑ → 20-thread pools exhaust → gateway queues → all services degrade.
- Retries amplify: each slow call retried 2–3x consumes more threads (retry storm).

## 2. Circuit-Breaker States
- CLOSED: pass-through, monitor failure rate in sliding window.
- OPEN: fail fast + fallback; no downstream calls for `waitDurationInOpenState`.
- HALF_OPEN: probe with N calls; success→CLOSED, fail→OPEN.
- Key params: `failureRateThreshold` (50% sane, not 80%), `slidingWindowSize` (10–20), `minimumNumberOfCalls`, `waitDuration` (30–60s).

## 3. Bulkhead Pattern
- Per-dependency thread pools (e.g., 5 threads each) isolate slow payment from healthy inventory.
- Semaphore bulkhead limits concurrency without extra threads.
- Without bulkhead: one slow dep starves all; with: only payment fallback triggers.

## 4. Timeouts, Retries, Fallbacks
- Timeout 3–5s (not 30s); fail fast so breaker can count failures.
- Retry: max 2, exponential backoff + jitter, never retry when OPEN.
- Fallback: cached/default/queued response; must not throw; must emit metric.

## 5. Detection: Signals
- Thread-pool queue depth, active threads, breaker state metric (`resilience4j_circuitbreaker_state`).
- Trace waterfall (Zipkin): fan-out from payment-service; latency histogram shift.
- Alerts: pool saturation >80%, breaker transitions flapping, downstream p99 >1s.
- Dashboard: per-service breaker state + fallback rate + retry rate.

## 6. Graceful Degradation
- Order without live fraud check → accept with review flag; catalog from cache.
- Define degradation tiers per endpoint; test with chaos (inject 2s latency).

## 7. Common Misconfigs
- Threshold 80% + window 100 + minCalls 50 → needs 40 failures before opening; too slow.
- `waitDuration 60s` + 10 half-open probes → thundering retry on still-sick service.
- Shared pool + long timeout + aggressive retry = guaranteed cascade.

## 8. Triage Order
1. Identify origin via traces (slowest leaf). 2. Force-open breaker on sick edge. 3. Shed load (rate-limit retries). 4. Drain pools. 5. Tune config + verify.

## 9. Key Takeaways
- Breakers must open fast; timeouts must be short; pools must be isolated.
- Monitor breaker state, not just error rate.
