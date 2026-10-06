# Lab 04: Distributed Resilience — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. What distinguishes resilience from reliability?**
- A) They are synonyms
- B) Reliability = probability of correct behavior over time; resilience = the *ability to degrade gracefully and recover* when failure occurs
- C) Resilience is measured in uptime, reliability in latency
- D) Resilience applies only to software, reliability only to hardware

**Answer: B** — A perfectly reliable component that cannot survive a slow dependency is not resilient. Resilience is about behavior under stress: fail fast, shed, degrade, recover.

---

**Q2. Little's Law (`L = λ·W`) applied to a circuit breaker means?**
- A) Break the circuit when concurrency exceeds `P`
- B) With a fixed concurrency limit, latency `W` is bounded by `L/λ`; once `W` grows, throughput is capped and the queue is where failure actually lives
- C) Break when `λ < L`
- D) `λ` and `W` are unrelated to breaker design

**Answer: B** — Circuit breakers protect resources (connections, threads, memory), not latency. The resource limit is `L`; the arithmetic tells you what latency that limit implies.

---

**Q3. Why is jitter mandatory on retry backoff?**
- A) It reduces total retries
- B) Without jitter, clients that failed together retry together, converting a partial outage into a synchronized thundering herd
- C) Jitter improves cache hit rates
- D) Jitter reduces p99 but raises p50

**Answer: B** — Exponential backoff alone keeps retries synchronized. Full jitter (`U(0, min(cap, base·2^n))`) desynchronizes them.

---

**Q4. A retry storm's real damage is best described as?**
- A) Duplicate successful writes only
- B) Load amplification: `amp = (retries+1)^depth`, which can exceed the recovery capacity of the already-struggling dependency
- C) Increased TLS handshake cost
- D) Slower garbage collection

**Answer: B** — A 3-retry, 2-deep chain is 16x load on the deepest hop. During an incident that amplification *is* the outage.

---

**Q5. What is the correct default for retryable operations?**
- A) Retry everything up to 3 times
- B) Retry only idempotent operations, with a total deadline budget, capped attempts, jitter, and a circuit breaker
- C) Retry on any exception
- D) Never retry

**Answer: B** — Retrying a non-idempotent operation can double-charge or duplicate a payment. Retryability is a property of the operation, decided with the caller.

---

**Q6. What does a "half-open" circuit breaker state do?**
- A) Routes all traffic to the fallback
- B) Allows a limited number of probe requests through to test whether the dependency recovered, then re-closes or re-opens
- C) Reports circuit state as unknown
- D) Bypasses the breaker

**Answer: B** — Half-open with a bounded probe count prevents both immediate re-failure and a flood of trial traffic against a struggling dependency.

---

**Q7. Hedging requests: when is it acceptable?**
- A) Never
- B) Only for idempotent, read-only operations, sent to a second replica, cancelled when the first wins, and with a delay so only the tail is hedged
- C) Always — it halves latency
- D) Only for writes

**Answer: B** — Hedging trades duplicate load for tail latency. It is only safe for idempotent reads and only worthwhile above a latency percentile threshold (e.g. p95).

---

**Q8. What does an exponential backoff *without* a cap risk?**
- A) Integer overflow in the scheduler
- B) Unbounded delay — a retry scheduled for 30 minutes holds a thread/connection and looks like a hung request
- C) JVM thread starvation
- D) Duplicate messages

**Answer: B** — Cap the backoff and honor a total deadline; otherwise a single unlucky request occupies resources far longer than any timeout you configured.

---

**Q9. Graceful degradation differs from failover how?**
- A) They are identical
- B) Degradation serves a reduced but correct function (stale cache, partial response, feature flag off) in-place; failover moves traffic to another component or region
- C) Failover is cheaper
- D) Degradation requires a restart

**Answer: B** — Degradation keeps serving from degraded inputs; failover changes the serving topology. Real systems do both, often simultaneously.

---

**Q10. Why do bulkheads belong in resilience, not just performance?**
- A) They improve throughput
- B) They bound the blast radius: a failed dependency can consume only its own permit pool, not the whole process's concurrency
- C) They reduce memory
- D) They are required by the JDK

**Answer: B** — Isolation is the property that turns "one dependency down" into "one feature down." Without it, a single slow dependency consumes every thread and connection.

---

**Q11. What is a retry budget / token-bucket retry limiter?**
- A) A JVM feature
- B) A per-caller or global cap on retry volume (e.g. retries ≤ 10% of total requests), so retries cannot exceed capacity during an incident
- C) A circuit-breaker configuration
- D) A connection pool setting

**Answer: B** — Resilience4j and similar libraries expose retry "limits" precisely so retry traffic stays a bounded fraction of normal load.

---

**Q12. Coordinated omission means?**
- A) A duplicate request
- B) Load generators skip work when the system is slow, so latency measurements are optimistic and hide tail latency in production
- C) Two services coordinating a timeout
- D) Circuit-breaker misconfiguration

**Answer: B** — Recorded-latency benchmarks underestimate tail behavior. Correct for it with HdrHistogram-style coordinated-omission correction or open-loop load models.

---

**Q13. In a cascading failure, which resource fails first, typically?**
- A) Memory
- B) Connection pools / in-flight request slots — because upstream timeouts exceed downstream capacity, so queues build and pool acquisitions never return
- C) Disk
- D) CPU

**Answer: B** — Timeout-based queueing converts a latency problem into a connection-exhaustion problem within one timeout window. That is why connect/read timeouts and pool sizes must be designed together.

---

**Q14. What does "fail fast" buy in a distributed system?**
- A) Lower average latency in the healthy case
- B) Bounded resource consumption: a rejected request costs microseconds instead of holding a thread for the full timeout, preserving capacity for requests that can succeed
- C) Better error messages
- D) Automatic retries

**Answer: B** — Under saturation, throughput is maximized by rejecting fast. Failing fast converts an unbounded queueing delay into bounded resource usage.

---

**Q15. The most important single number in a resilience design review is usually?**
- A) Average latency
- B) The end-to-end deadline and the sum of all timeout budgets along the path, verified to be less than the caller's timeout
- C) Pod count
- D) JVM heap size

**Answer: B** — If timeout budgets exceed the caller's deadline, every layer must eventually abandon work; if they are much smaller than the caller's budget, you fail unnecessarily. Verify the sum, per hop.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and the chaos experiments.
- 12–10: revisit THEORY on breakers, budgets, and queueing; redo EXERCISES 4–7.
- <10: re-read the resilience checklist cold and retake in 48 hours.
