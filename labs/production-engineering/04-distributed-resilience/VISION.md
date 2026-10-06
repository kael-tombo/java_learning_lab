# VISION — Lab 04: Distributed Resilience

> From "wrap calls in try/catch" to a designed, measured, tested failure story.

---

## The Arc

1. **Reframe** — resilience is behavior under stress, not a feature you bolt on. Slow ≠ down; the slow case is the one that kills you.
2. **Budgets** — timeouts, concurrency limits, and deadlines that add up correctly along a call chain.
3. **Containment** — bulkheads, bounded queues, shed priorities, blast-radius control.
4. **Amplification control** — retries with jitter, budgets, hedging rules, idempotency keys.
5. **Detection & isolation** — circuit breakers sized from statistics, half-open probing, fallbacks per endpoint.
6. **Degradation** — stale reads, feature flags, partial responses, read-only mode, honest failure.
7. **Verification** — fault injection, steady-state hypotheses, chaos experiments, recovery-time measurement.

---

## Why this lab exists

Most services are designed for the happy path and for *total* failure of dependencies. The outage that actually happens is the third thing: **partial degradation** — the dependency accepts connections, returns nothing, and holds them for the full timeout. That case turns a latency problem into a connection-exhaustion cascade within a single timeout window.

The specific goal here: **you can look at any service's timeout, retry, pool, and breaker configuration and predict whether a 20x downstream latency spike becomes a graceful degradation or a total outage.**

---

## Milestones (checkable)

- [ ] M1: Draw the cascade chain for your own service (slow dependency → pool exhaustion → upstream failure) with named resources at each hop.
- [ ] M2: Produce a timeout budget table for a 3-hop call chain and prove the sum is under the caller's deadline.
- [ ] M3: Size a bulkhead from `λ_peak × W_p99` and explain what caps it in practice.
- [ ] M4: Configure a breaker with statistically defensible minimum volume and half-open probe count, showing the confidence calculation.
- [ ] M5: Implement bounded retries with full jitter and a retry budget, then measure amplification under a synthetic failure.
- [ ] M6: Define a fallback chain per endpoint (cache → default → queued → explicit failure) and state which responses must never be stale.
- [ ] M7: Run a latency-fault experiment in a lab environment, measure recovery time, and verify no thread/connection growth after recovery.

---

## Anti-Goals

- Retrying everything with no idempotency key.
- Unbounded queues presented as "back-pressure."
- A circuit breaker with `minimumNumberOfCalls = 2`, which trips on noise.
- Timeouts copied from a blog, with no relationship to the caller's budget.
- "Graceful degradation" that returns stale data for balances or auth decisions.
- Chaos experiments with no declared steady-state hypothesis and no abort threshold.

---

## Interview Lens

- "A dependency goes from 50 ms to 2 s. Walk me through what happens in your system, step by step."
- "How do you size a circuit breaker's minimum call volume?"
- "When do you NOT retry?"
- "What is coordinated omission and why does it matter for your load tests?"
- "How do you prove graceful degradation works without causing an outage?"

---

## 30-Day Plan

- **Week 1** — THEORY on queueing, cascades, and budgets; compute Erlang C tables for your own service parameters. M1–M2.
- **Week 2** — EXERCISES: breaker sizing, bulkhead math, retry amplification; QUIZ to 13/15; FLASHCARDS daily. M3–M5.
- **Week 3** — MINI_PROJECT: build the resilience harness and run the latency-fault experiment. M6.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a resilience design review document for a real service; teach-back: "our failure modes, defended" in 10 minutes. M7.

---

## Artifacts you should be able to show

1. A timeout budget table for a real call chain with the arithmetic.
2. A breaker configuration with the statistical justification for each parameter.
3. A measured amplification number for your retry policy under fault.
4. A fallback chain table per endpoint, with a "must never be stale" marker.
5. A fault-experiment report with recovery time and resource-leak verification.

---

## Done = You Can

- Predict the failure mode of a service under dependency degradation, quantitatively.
- Configure timeouts, retries, breakers, and bulkheads with numbers rather than defaults.
- Explain why slow is worse than down, and design for slow.
- Run a controlled fault experiment that produces evidence about recovery, not just drama.
