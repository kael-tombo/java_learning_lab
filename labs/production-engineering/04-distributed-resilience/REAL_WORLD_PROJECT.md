# Lab 04: Distributed Resilience — Real World Project

## Scenario: "The partner outage that took down checkout"

You are the tech lead for an order-management platform. Java 21 / Spring Boot, 24 pods, Kubernetes. It calls four external dependencies, one of which — a tax-calculation partner (`taxsvc`) — you do not control.

**The incident**: Tuesday 10:12. `taxsvc` deploys a change and its p99 goes from 60 ms to 6 s, with no errors. Over the next four minutes:

1. Checkout thread pools saturate as calls block for the full read timeout.
2. Database connection pool (`HikariCP`, size 30) is exhausted because order persistence happens after the tax call and threads never reach it.
3. The HTTP client retries each tax call twice, tripling `taxsvc` load; their p99 rises to 9 s.
4. `orders` insert timeouts begin failing, which causes the *checkout* service to return 500s.
5. On-call scales 24 → 60 pods, which sends more concurrent connections to an already-degraded partner, worsening their latency. Rollback of the partner is not ours to trigger.
6. Total impact: 41 minutes of checkout unavailability. Estimated loss: $2.1M.

**Postmortem finding**: "No timeout budget discipline, no bulkheads, breaker configured with `minimumNumberOfCalls = 3`, retries without jitter or budget, and no shedding. The service cannot survive a slow dependency."

**Your job over 4 weeks**: make this service survive the *same* partner incident — and prove it.

**Time**: 25–35 hours | **Difficulty**: Advanced

---

## Phase 1 — Full resilience audit (Day 1–4)

Audit every outbound call and every inbound resource:

| Call site | Timeout | Retries | Jitter | Circuit breaker | Bulkhead | Idempotency | Fallback |
|---|---|---|---|---|---|---|---|
| taxsvc | ? | 2 (none) | none | minCalls=3 | none | N/A | none |

Produce the audit table for all four dependencies plus every inbound path (checkout, order status, refund, catalog, admin).

**Deliverable 1 — Resilience audit** with, for each path:
- Timeout value and its origin (a number someone typed).
- Retry count and whether the operation is idempotent.
- Breaker parameters.
- Concurrency limit on the call.
- What happens when this call returns slowly vs errors vs never returns.
- A one-line blast-radius statement.

Also produce the **cascade chain diagram** for the incident, with named resources: `taxsvc latency → client socket timeout (2000 ms) → exec threads held (24 pods × 200) → HikariCP 30 exhausted → order insert timeout → 500s → retry amplification 3x → partner p99 9 s`.

---

## Phase 2 — Design the fix (Day 4–8)

### 2.1 Timeout budget

Set a real end-to-end budget for checkout: `T_caller = 250 ms` (from your API gateway SLA). Build the propagation:

```
gateway → checkout (10 ms) → taxsvc (120 ms) → persist (40 ms) + serialization (10 ms)
slack = 250 − 180 = 70 ms  →  allocate to retries (≤ 2) and jitter
```

Rules to encode and enforce in code:
- Every outbound call receives `min(remaining_deadline − reserved_local, configured_max)`.
- Connect timeout ≤ 50 ms; read timeout from the budget.
- Jitter ±15% on every timeout.

**Deliverable 2 — Timeout budget table** with the arithmetic, plus the code/framework change that enforces it (interceptor, `Deadline` object, or request-scoped context), and a test that fails if any call site omits a budget.

### 2.2 Bulkheads and shed

Per-dependency semaphores sized from `λ_peak × W_p99` at current traffic, bounded by each partner's realistic concurrency:

| Dependency | `λ_peak` | `W_p99` | `B = λ·W·1.3` | Partner concurrent limit | Chosen B |
|---|---|---|---|---|---|
| taxsvc | 900/s | 0.2 s | 234 | unknown (assume 50/pod) | 120 |
| payments | 300/s | 0.4 s | 156 | 30 | 30 |

Plus **priority shedding**: protect checkout and refund; shed catalog refresh, analytics writes, and non-essential enrichment first. Return `429` + `Retry-After` for shed requests.

**Deliverable 3 — Bulkhead/shed design** with the sizing table and the priority list, implemented behind flags so you can roll out gradually.

### 2.3 Circuit breakers

Per dependency, with statistically defensible parameters. Show the calculation for `minimumNumberOfCalls` (target: distinguishing a 5% from a 0.5% error rate at 95% confidence needs ≈ 185 samples → use 200). Include slow-call thresholds from measured p99 × multiplier, `waitDurationInOpenState` from the partner's cold-start time, and `permittedNumberOfCallsInHalfOpenState = 10`.

**Deliverable 4 — Breaker configuration document** with the statistics and the reasoning per parameter.

### 2.4 Retry policy

- Only idempotent operations retried.
- Full jitter, `maxAttempts = 3`, `base = 80 ms`, `cap = 1 s`.
- **Retry budget**: retries capped at 10% of total volume, enforced per dependency.
- Idempotency keys on every write that might be retried.
- No retries on 4xx, 401/403, or validation errors.

**Deliverable 5 — Retry policy** with the amplification math, and a load test that measures actual amplification against a failing dependency.

### 2.5 Degradation

Define what checkout does when `taxsvc` is unavailable. Work with the business to decide — candidates:
- Serve an order marked `TAX_PENDING` and reconcile asynchronously when the partner returns.
- Use cached tax rates with a max staleness (e.g. 24 h) and a visible flag.
- Serve zero-rated for low-risk jurisdictions (compliance check required).

Produce a **fallback chain per endpoint** and a `RUNBOOK_DEGRADED.md` describing each mode, how to enable it (feature flag), and how to detect it's active.

**Deliverable 6 — Degradation design** including the business sign-off record and the flag names.

---

## Phase 3 — Implement behind flags, canary, harden (Week 2–3)

1. Implement all of the above behind feature flags, defaulting **off**.
2. Canary at 5% of pods for 24 h. Compare: p99, error rate, retry volume to `taxsvc`, thread count, connection pool utilization, and shed rate.
3. Ramp to 25%, then 100%, with a rollback trigger per stage.
4. Add the missing dashboards and alerts (§Phase 4) *before* the ramp completes.
5. Add tests to CI:
   - A test that fails if any outbound client call site lacks a configured timeout/bulkhead/breaker (ArchUnit-style).
   - A fault-injection test: a WireMock dependency that delays 2 s — assert the endpoint still returns within budget and the shed path activates.
   - An idempotency test for retried writes (exactly-once effect under retry).

**Deliverable 7 — Canary report** with the before/after table and the ramp decision, plus the new CI tests.

---

## Phase 4 — Instrument for the failure you now expect (Week 3)

Metrics (per dependency):
- `http_client_requests_total{dep,outcome,attempt}` — attempt count is what exposes amplification.
- `http_client_duration_seconds{dep}` histogram with SLO-relevant buckets.
- `bulkhead_available_permits{dep}`, `bulkhead_rejected_total{dep,priority}`.
- `breaker_state{dep}` (0/1/2 as gauge), `breaker_transitions_total{dep,to}`.
- `retry_total{dep}` and `retry_budget_exhausted_total{dep}`.
- `shed_total{endpoint,priority}`.
- `degraded_mode_active{feature}`.
- Deadline propagation: `deadline_remaining_ms` histogram at each hop (the single most diagnostic series).

Alerts:
- `breaker_state == OPEN` for > 5 min → warn; > 15 min → page.
- `shed_total` rate > 1% for 5 min → warn (you are load shedding in production).
- `retry_total / requests_total > 10%` → page (retry budget violated).
- `in_flight / bulkhead_size > 0.9` for 5 min → warn (next latency spike will fail).
- `degraded_mode_active == 1` → page (customers are seeing degraded service).

**Deliverable 8 — Observability for resilience**, with each alert's threshold justified against the derived numbers.

---

## Phase 5 — Prove it (Week 3–4)

Run the exact incident again, safely:

1. **Staging full-scale replay** — deploy the partner's degraded behavior in a proxy (2 s p99, no errors) and run the original peak load profile. Verify: budget holds, shed activates, breaker opens, no thread/connection growth, and no amplification.
2. **Production chaos, tightly scoped** — inject 2 s latency on 5% of `taxsvc` traffic for 5 minutes, business hours, with a kill switch. Pre-declared abort thresholds: error rate > 5% for 30 s, pod restarts > 0, shed rate > 10%.
3. **Simulated partner outage** — route `taxsvc` traffic to a stub returning 100% errors for 3 minutes. Verify breaker opens within budget, degraded mode activates, and no retry storm.
4. **Recovery test** — restore traffic and measure the retry-avalanche window. Verify jitter kept peak retry volume within the 10% budget.

**Deliverable 9 — Resilience test report** with the four scenarios, the metrics before/after, and the measured recovery time. Include a comparison table: same fault, before vs after.

---

## Phase 6 — Operationalize (Week 4)

- `RUNBOOK_TAXSVC.md`: symptoms → dashboards → diagnosis → mitigation (including "enable degraded mode") → verification → escalation to the partner. Written for an on-call who did not build the service.
- **Partner-facing SLO document**: what we measure, what we expect, and what we will do (shed, degrade) if they breach it.
- A **quarterly chaos game day** on the calendar, with the same four scenarios.
- A **regression guard**: the fault-injection test runs in CI on every PR (no staging dependency — use a stub server with configurable latency).

**Deliverable 10 — Operational package**: runbook, partner SLO, game-day plan, CI fault test.

---

## Phase 7 — Quantify the result (Week 4)

Present to leadership:

| Scenario | Before | After |
|---|---|---|
| Partner 2 s latency | 41 min full outage, $2.1M | degraded mode, X% of orders succeed, recovery in Y min |
| Partner 100% errors | outage | breaker opens in Z s, degraded mode, no outage |
| Max amplification | 3x observed, 9x theoretical | ≤ 1.2x measured |
| MTTR for this class | 12 min (from postmortem) | 2 min (runbook, degraded-mode flag) |
| Availability for this class | 99.92%/quarter | 99.99%/quarter |

**Deliverable 11 — Business case** with the numbers, and the requested annual budget (engineering days + infra cost) justified by recovered outage-hours.

---

## Deliverables checklist

- [ ] Phase 1 audit table for all paths + cascade diagram.
- [ ] Phase 2 all five design documents (timeout, bulkhead, breaker, retry, degradation) with arithmetic.
- [ ] Phase 3 canary report + CI tests.
- [ ] Phase 4 resilience observability with justified thresholds.
- [ ] Phase 5 four-scenario resilience test report with before/after.
- [ ] Phase 6 runbook, partner SLO, game day, CI fault test.
- [ ] Phase 7 business case with numbers.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Diagnosis | "Retries caused the outage" | Full cascade chain with named resources and amplification math |
| Timeouts | Set to 2 s "to be safe" | Budget derived from the caller's deadline, propagated, enforced, tested |
| Isolation | One global pool + a breaker | Per-dependency bulkheads with priority shedding |
| Breaker | Copied defaults | Statistically justified min-calls, slow-call thresholds, half-open probing |
| Retries | 2 retries, no jitter | Idempotency + full jitter + enforced retry budget |
| Degradation | "Return 500" | Named degraded modes with business sign-off and flags |
| Proof | Load test with the dependency down | Slow-latency replay (the actual incident shape) + measured recovery |
| Business | Technical only | Outage-hours and dollars, with an ask |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Resilience4j documentation (CircuitBreaker, Retry, Bulkhead, TimeLimiter)** — https://resilience4j.readme.io/docs/getting-started-3 — canonical parameter names and defaults (`minimumNumberOfCalls`, `slidingWindowType`, `waitDurationInOpenState`, `permittedNumberOfCallsInHalfOpenState`, `enableRandomizedWait`). Defaults have changed across versions; confirm the exact semantics for the version you pin.
2. **AWS Builders' Library — Timeouts, retries, and backoff with jitter** — https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/ — the reference treatment of retry amplification, token-bucket retry limits, and why jitter is required. The "avoiding retries entirely" and "idempotency" sections are directly applicable to the design above.

Also verify before citing: your HTTP client's connection-pool and request-acquisition timeout semantics (e.g. whether acquisition timeout exists and its interaction with read timeout), and your partner's published SLO terms before writing the partner-facing document.

---

## Reflection questions

1. Scaling from 24 to 60 pods made the incident worse. What is the general lesson for every scale-up decision during an incident?
2. Your service cannot know the partner will degrade. What can you control, and how much of the outage was actually yours?
3. If the partner's p99 rose to 600 ms instead of 6 s, would your design have behaved differently? Where is the cliff?
4. Which degraded mode would your business have accepted, and what would it have cost them?
5. What is the one metric that would have made the partner's degradation visible in the first two minutes?
