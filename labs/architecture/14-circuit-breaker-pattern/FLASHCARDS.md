# Circuit Breaker Pattern Flashcards

## Core Concepts

**Q: What is the Circuit Breaker pattern?**
**A:** A resilience pattern that detects failures and stops requests to a failing service, preventing cascading failures. Three states: CLOSED (normal), OPEN (blocking), HALF_OPEN (testing recovery).

**Q: What problem does it solve?**
**A:** Cascading failures — when a downstream service is slow/down, upstream callers block threads waiting, exhausting resources (thread pools, connections).

**Q: Three states & meanings?**
**A:** 
- **CLOSED**: Normal operation, requests pass through, failures counted
- **OPEN**: Short-circuiting, requests fail fast immediately, timer running
- **HALF_OPEN**: Trial period after timeout, limited probe requests allowed

**Q: CLOSED → OPEN transition?**
**A:** Failure threshold reached (count-based: N failures, or rate-based: X% failures in sliding window).

**Q: OPEN → HALF_OPEN transition?**
**A:** `waitDurationInOpenState` elapsed (configurable timeout).

**Q: HALF_OPEN → CLOSED transition?**
**A:** Probe request(s) succeed (configurable `permittedNumberOfCallsInHalfOpenState`).

**Q: HALF_OPEN → OPEN transition?**
**A:** Probe request fails.

---

## Configuration

**Q: Sliding window types?**
**A:** 
- **COUNT_BASED**: Last N calls (e.g., 100 calls)
- **TIME_BASED**: Last N seconds (e.g., 10 seconds)

**Q: When to use COUNT_BASED vs TIME_BASED?**
**A:** COUNT_BASED for high-throughput (stable statistics). TIME_BASED for low-throughput (avoids stale windows).

**Q: failureRateThreshold vs failureThreshold?**
**A:** 
- `failureRateThreshold`: Percentage (e.g., 50%) — rate-based
- `failureThreshold`: Absolute count (e.g., 5 failures) — count-based

**Q: What is waitDurationInOpenState?**
**A:** Time circuit stays OPEN before attempting recovery (HALF_OPEN). Typical: 10-60s.

**Q: What is permittedNumberOfCallsInHalfOpenState?**
**A:** Max probe requests allowed in HALF_OPEN (typically 1-10). Limits blast radius if still failing.

**Q: slowCallRateThreshold & slowCallDurationThreshold?**
**A:** Treat slow calls as failures. e.g., > 2s = slow, > 50% slow = trip. Prevents thread exhaustion from latency.

---

## Implementation Patterns

**Q: Circuit Breaker + Retry — correct order?**
**A:** **Retry inside Circuit Breaker** (or CB wraps Retry). 
- If Retry outside CB: retries count as separate failures → trips CB faster
- If CB outside Retry: CB sees only final result after retries

**Resilience4j**: `@CircuitBreaker` → `@Retry` (CB outer, Retry inner)

**Q: Circuit Breaker + Bulkhead — relationship?**
**A:** Complementary. Bulkhead limits **concurrency** (semaphore/thread pool). CB limits **calls over time**. Use both.

**Q: Fallback for read vs write operations?**
**A:** 
- **Read**: Return cache, default, stale data — safe
- **Write**: Never fake success. Queue (outbox), return error, async processing

**Q: How to make fallback thread-safe?**
**A:** Fallback runs on caller thread. Must be fast, non-blocking. No external calls.

**Q: Distributed Circuit Breaker — shared state?**
**A:** Each instance has own CB state. For global view: aggregate metrics (Prometheus), alert on fleet-wide OPEN. Don't share CB state (split-brain risk).

---

## Monitoring & Operations

**Q: Key metrics to export?**
**A:** State (0/1/2), failure rate, slow call rate, call throughput, latency p50/p99, buffer capacity (bulkhead).

**Q: Alerting on CB state?**
**A:** Alert if OPEN > 1 minute. HALF_OPEN → OPEN repeatedly = flapping.

**Q: How to test CB in production?**
**A:** 
- Chaos: inject latency/errors in downstream
- Observe: state transitions, fallback activation, recovery
- Verify: no thread exhaustion, graceful degradation

**Q: Common misconfigurations?**
**A:** 
- Window too small → flapping
- waitDuration too short → hammer recovering service
- No slow call threshold → latency kills threads silently
- Fallback does I/O → blocks caller thread

---

## Advanced

**Q: Circuit Breaker for async/reactive?**
**A:** Works on `Mono`/`Flux` (Project Reactor) or `CompletableFuture`. Trips on error signals. Fallback returns alternative publisher.

**Q: CB for gRPC / HTTP/2?**
**A:** Same principles. Per-method CB useful (some RPCs critical, others not). Use `io.github.resilience4j:resilience4j-grpc`.

**Q: CB in Service Mesh (Istio/Linkerd)?**
**A:** Mesh provides **outlier detection** (similar to CB) at sidecar level. Application CB still needed for business logic fallbacks.

**Q: CB for batch/stream processing?**
**A:** Different model — checkpointing, backpressure. CB applies to external service calls within processing.

---

## Failure Injection Testing

**Q: What failures to inject?**
**A:** 
- Network: latency (100ms, 1s, 10s), packet loss, partition
- Service: HTTP 5xx, timeout, connection reset, slow response
- Resource: CPU saturation, OOM, thread pool exhaustion

**Q: Expected CB behavior under injection?**
**A:** 
- Latency injection → slow call rate triggers OPEN
- Error injection → failure rate triggers OPEN
- Partition → connection failures trigger OPEN
- Recovery → HALF_OPEN probes succeed → CLOSED

**Q: Metrics to verify during chaos?**
**A:** State transitions logged, fallback invoked, no thread pool exhaustion, upstream latency bounded.