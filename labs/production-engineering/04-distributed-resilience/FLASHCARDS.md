# Lab 04: Distributed Resilience — Flashcards

~60 cards. Every answer should be a number, a name, or a rule — not a vibe.

---

## Framing

Q: Reliability vs resilience?
A: Reliability = correctness over time; resilience = behavior under failure (degrade, shed, recover).

Q: Why does "the dependency is slow" break systems designed for "the dependency is down"?
A: Slower ≠ down: no fast error, no circuit trip, timeouts hold resources → queues → pool exhaustion → cascade.

Q: Define a blast radius.
A: The set of users/functionality affected by one failure. Bulkheads, quotas, and degradation shrink it.

Q: What is the resilience triad?
A: (1) Bound resource use, (2) Degrade gracefully, (3) Recover without manual intervention.

Q: What is "failure amplification"?
A: A fault causing load, latency, or error volume many times larger than the original trigger (retries, fan-out, thundering herds).

Q: Name three amplification mechanisms.
A: Retries without jitter, unhedged fan-out, client reconnects, cache stampedes, thundering herd on a restarted service.

---

## Timeouts & Budgets

Q: Why is a default timeout a bug?
A: Some timeout is always wrong; missing timeouts mean a hung dependency holds resources forever.

Q: Connect vs read timeout?
A: Connect = TCP establishment (keep small); read = server processing (must match the real p99+ budget).

Q: Why must the timeout sum be < the caller's deadline?
A: Otherwise inner layers keep working after the caller gave up — wasted work, amplified load, leaked permits.

Q: Rule for a downstream timeout?
A: ≤ (remaining caller budget − expected local work) × safety factor; never a round number from a blog.

Q: What is a deadline propagation header?
A: Absolute deadline passed along the call chain so each hop computes its own remaining budget.

Q: Why does a timeout need jitter?
A: Fixed timeouts cause synchronized retries; add ±10–20% jitter or full-jitter backoff.

Q: What happens if read timeout > HTTP client connection pool timeout?
A: Connections are recycled while requests are still in flight → protocol errors, 502s, and connection leaks.

---

## Circuit Breakers

Q: Breaker states?
A: `CLOSED` (normal), `OPEN` (fail fast), `HALF_OPEN` (probe with limited requests).

Q: Breaker parameters?
A: Failure/slow-call rate threshold, minimum call volume (samples), rolling window size, open duration, half-open permitted calls, and wait duration in half-open.

Q: Why a minimum call volume?
A: A threshold on 2 failures in 5s is noise; require enough samples to make a rate meaningful.

Q: What counts as a failure?
A: Exceptions, timeouts, and (important) *slow* calls above threshold — or latency is invisible to the breaker.

Q: Sliding window count vs time window?
A: Count-based = last N calls (stable rate independence); time-based = last T seconds (rate sensitive). Prefer count-based for spiky traffic.

Q: Breaker trips to OPEN — what happens to calls?
A: Immediate failure (fast reject) plus optional fallback: cached value, default, queue for later, or 503 with Retry-After.

Q: Does an open breaker protect the callee or the caller?
A: Both: the caller stops consuming callee resources, and the caller stops consuming its own (thread, permit, memory).

Q: Breaker placement: per dependency or per call site?
A: Per dependency per logical operation. Per call site can mask a partially-failing endpoint; per dependency is usually right.

Q: What is "half-open storm"?
A: Too many half-open probes hitting a still-recovering dependency. Cap probes and set a wait duration.

---

## Retries

Q: Exponential backoff formula?
A: `delay = min(cap, base × 2^attempt)`.

Q: Full jitter vs equal jitter vs decorrelated?
A: Full: `U(0, delay)` (best desync, Resilience4j default); equal: `delay/2 + U(0, delay/2)`; decorrelated: `U(base, prev × 3)`.

Q: Why jitter is non-negotiable?
A: Without it, clients that failed together retry together → synchronized retry storm on the recovering dependency.

Q: Retry amplification formula?
A: `amp = (retries+1)^call_depth` — 3 retries × 2 depth = 16x load.

Q: Retry budget?
A: Cap retries at a fraction of total volume (e.g. ≤ 10%) so retries never exceed capacity (Resilience4j `limit`).

Q: Retry only what?
A: Idempotent/commutative operations, transient errors (timeouts, 429, 502/503/504), with a total deadline and attempt cap.

Q: Never retry?
A: Non-idempotent writes without an idempotency key; 4xx validation errors; 401/403; business rejections.

Q: What is a retry storm's fingerprint?
A: Downstream 5xx/timeout spikes, elevated error rate, rising queue depth, and CPU/network saturation on the dependency.

Q: Where should retries live — client or server?
A: Usually client (only the caller knows the deadline), but keep total attempts under a budget shared across layers to avoid stacked amplification.

---

## Bulkheads, Queues, Shed

Q: What is a bulkhead in code?
A: A bounded semaphore or dedicated executor per dependency so its in-flight count is capped.

Q: Bulkhead sizing?
A: From the dependency's healthy capacity: `permit_count ≈ λ_peak × W_p99`, capped by the dependency's own concurrency limit.

Q: What is a queue-based bulkhead and its tradeoff?
A: Allow a short bounded queue for smoothing; it adds latency and hides overload. Keep it small (≈ few × concurrency) and always bounded.

Q: Load shedding vs fail fast?
A: Shedding = reject a fraction/priority of load deliberately; fail fast = reject when no capacity remains. Shedding is proactive (protects the good path); fail fast is reactive.

Q: What is a priority shed?
A: Reject low-priority requests (search, batch, refresh) before high-value ones (checkout, payments) during saturation.

Q: Why a bounded queue, always?
A: Unbounded queueing converts overload into unbounded latency and memory growth (the "death by queue" pattern).

Q: What is back-pressure in a resilient system?
A: Propagating saturation upstream so producers slow down; without it, queues absorb the overload invisibly until collapse.

Q: What is "fast fail with Retry-After"?
A: Reject immediately with a header telling the client when to come back — cheap for the server, honest to the client.

---

## Degradation & Fallbacks

Q: Stale-while-revalidate — what does it degrade?
A: Serves slightly stale cached data with a background refresh; acceptable staleness buys availability.

Q: What is a feature-flag-based degradation?
A: Ship a kill switch that disables a non-critical dependency's call path in one config change, no deploy.

Q: What is a fallback chain?
A: Primary → cache → static default → queued async processing → explicit failure. Define it per endpoint before the incident.

Q: When is returning stale data wrong?
A: Payments, balances, auth decisions, anything where correctness is safety-critical. Degrade by failing, not by lying.

Q: What is a "shadow mode" for degradation?
A: Run the non-critical dependency call but ignore the result, so removing it later is a config-only change.

Q: Partial response / field-level degradation?
A: Return the fields you can compute, mark the rest as unavailable; pair with a client contract that tolerates absence.

---

## Cascades & Recovery

Q: What is the cascade chain?
A: dependency slow → callers hold connections → upstream timeouts → upstream pools exhausted → upstream slow → repeat outward.

Q: Which knob most reliably breaks the chain?
A: Bounded timeouts + bounded in-flight (semaphore) so a slow callee can never accumulate unbounded caller-side waiting.

Q: What is a retry avalanche?
A: Many services retry in sync after a shared outage ends, re-overloading the dependency that just recovered.

Q: What is a thundering herd on restart?
A: All clients reconnect at once when a service restarts; stagger reconnection with jittered backoff and connection warm-up.

Q: What is the "circuit breaker + jittered retry + bulkhead" trio for?
A: Fail fast, desynchronize retries, and bound resource use — the standard three-layer defense.

Q: Why does the breaker need a half-open *wait* period?
A: Prevents immediate re-probing; lets the dependency stabilize before receiving trial traffic.

Q: Recovery checklist after a cascade ends?
A: Verify pools drained, breakers closed, queues empty, and watch for the retry avalanche for at least one full timeout window.

Q: What is a slow-recovery "brownout"?
A: Service technically available but continuously degraded for hours; danger is premature optimization/failover that re-triggers load.

---

## Testing & Chaos

Q: What is a fault injection point set?
A: Latency, errors, packet loss, CPU/GC pressure, disk-full, connection reset, and "slow body" (headers fast, body slow).

Q: Why "slow" beats "down" in tests?
A: Slow produces the cascade; down produces a clean error. Test slow to find the queueing bug.

Q: What is a steady-state hypothesis?
A: Declare the metric range that proves the system is healthy (e.g. p99 < 200 ms, error < 0.1%, threads < 600) before injecting faults.

Q: Blast-radius rules for chaos in prod?
A: One zone, ≤5% traffic, business hours, named kill switch, pre-agreed abort thresholds.

Q: What does a chaos experiment prove that unit tests cannot?
A: That the whole system's composed behavior under a fault matches the steady-state hypothesis.

Q: Coordinated omission — why it matters for fault tests?
A: A closed-loop generator under-reports tail during slowness; use open-loop pacing or HdrHistogram correction.

Q: What is a "sabotage" vs a "chaos experiment" here?
A: Real human-induced fault vs automated controlled fault; both valid, different risk profiles.

---

## Data Resilience

Q: Replication modes?
A: Synchronous (durability + latency, may block), async (fast, possible data loss), semi-sync (ack after relay).

Q: What is RPO vs RTO?
A: RPO = tolerable data loss (time); RTO = tolerable downtime (time). Backups define RPO; failover design defines RTO.

Q: Why is a single-region replica not a backup?
A: Logical corruption, accidental deletion, and ransomware replicate too. Backups need immutability + restore tests.

Q: What is a failover trigger you should distrust?
A: Health-check-only triggers; prefer quorum/consensus or independent signal to avoid split-brain.

Q: What is a thundering-herd failover risk?
A: All clients switch to a cold standby simultaneously; warm it and stagger switches.

Q: Idempotency keys in the resilience layer?
A: Make retries safe at the API so the resilience layer can retry freely; also dedupe replayed requests after a failover.

Q: What is a queue-based retry (delayed retry topic)?
A: Instead of blocking retries, re-enqueue with a delay topic so failures don't pile up in caller threads.

Q: When should you open a circuit on your own database?
A: When a specific failure mode (pool timeouts, deadlock victim) dominates and retrying makes it worse; then degrade to read-only or queue writes.

---

## Numbers to memorize

Q: Retry budget default?
A: Retries ≤ 10% of total request volume.

Q: Typical bulkhead semaphore size?
A: `λ_peak × W_p99`, e.g. 200 rps × 0.2 s ≈ 40 permits.

Q: Typical half-open probe count?
A: 5–10 requests, then wait for success rate before re-closing.

Q: Typical breaker open duration?
A: 30–60 s, then half-open; longer for expensive recovery.

Q: Amplification for 2 retries, 2 hops?
A: 9x. For 3 retries, 2 hops? 16x.

Q: Backoff parameters that are usually sane?
A: `base = 50–100 ms`, `cap = 1–2 s`, attempts ≤ 3, full jitter.

Q: How long to watch for a retry avalanche after recovery?
A: At least one max-timeout window plus a few backoff caps (~2–5 minutes).

Q: Load-shed thresholds?
A: Shed when utilization > 0.8 or queue wait > budget; priority order defined in advance.
