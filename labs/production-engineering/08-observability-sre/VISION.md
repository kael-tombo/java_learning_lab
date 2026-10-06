# VISION — Lab 08: Observability — Logs, Metrics, Traces

> From "we have a dashboard" to "I knew, I knew where to look, and I knew what to do."

---

## The Arc

1. **What to measure** — SLIs grounded in what a user experiences, not what the JVM exposes.
2. **The budget** — error budget arithmetic, what an SLO actually promises, and why three nines on a 30-day window is 43 minutes.
3. **Metrics done right** — counter vs gauge vs histogram vs summary, bucket design, cardinality budgets, recording rules.
4. **Logs done right** — structured layout, correlation, MDC discipline across thread pools, sampling.
5. **Traces done right** — OTel context propagation, `http.route` vs raw URLs, async span leaks, sampling policy.
6. **Alerting on symptoms** — burn rates, multi-window confirmation, the page/ticket split.
7. **Joining the pillars** — exemplars, `trace_id` in logs, the click-path from metric to trace to log line.
8. **Operating it** — SLO reviews, alert-quality metrics, MTTD vs MTTR.

---

## Why this lab exists

Most production incidents are not solved by a better debugger; they are solved by already knowing which one of forty dashboards to open. Instrumentation is an engineering decision with a cost model, a sampling policy, and a failure mode of its own (cardinality explosions, lost trace context, unsampled errors).

The specific goal here: **you can define an SLI from a user-visible behaviour, compute its error budget, design instrumentation that will actually measure it, and alert on budget consumption rather than on arbitrary thresholds.**

---

## Milestones (checkable)

- [ ] M1: Write SLI + SLO definitions for a real service with explicit `good`, `valid`, and exclusion criteria, and compute the error budget in minutes.
- [ ] M2: Design a latency histogram whose buckets make the SLO computable, and show what a wrong bucket set hides.
- [ ] M3: Find and remove one cardinality bomb in a real service's metrics, with a before/after series count.
- [ ] M4: Implement W3C `traceparent` propagation including a `CompletableFuture` path, and demonstrate no orphan spans.
- [ ] M5: Implement a tail-based sampling policy and show that 100% of errors survive it at <5% of full-fidelity volume.
- [ ] M6: Write multi-window multi-burn-rate alerts for a three-nines service and demonstrate the flapping reduction against a naive threshold alert.
- [ ] M7: Go metric → exemplar → trace → log line for one real slow request, in under two minutes.

---

## Anti-Goals

- Summaries (`quantile{...}`) in production metrics.
- Raw URL paths or user IDs as metric labels.
- Per-request `INFO` logging at 100% on high-QPS paths.
- Head-based sampling that drops your slow and errored traces.
- Paging on CPU, memory, or queue depth when the user-visible SLI is fine.
- Alert thresholds picked by rounding.
- An SLI with no `valid_events` floor at low traffic.

---

## Interview Lens

- "How do you decide what to alert on?"
- "Why histograms instead of summaries?"
- "Our p50 is fine but users complain. What do you check?"
- "Explain burn-rate alerting and why two windows."
- "How do you keep observability costs under control?"

---

## 30-Day Plan

- **Week 1** — THEORY: SLI/SLO design, PromQL, metric types, bucket design. Hands-on: build an instrumented Spring service and scrape it. M1–M2.
- **Week 2** — EXERCISES: budget math, quantile math, cardinality audit; QUIZ to 13/15; FLASHCARDS daily. M3.
- **Week 3** — MINI_PROJECT: full OTel pipeline (SDK → Collector → Tempo/Jaeger + Prometheus + Grafana), structured logs with `trace_id`, exemplars, burn-rate alerts. M4–M6.
- **Week 4** — REAL_WORLD_PROJECT war story; write an SLO + alerting proposal for a real service; teach-back: "here is our error budget and what we will do with it" in 10 minutes.

---

## Artifacts you should be able to show

1. An SLO specification document with SLI definition, exclusions, window, and budget.
2. A dashboard with SLI, budget remaining, burn rate, volume, and saturation — plus a runbook link.
3. A cardinality audit with before/after series counts.
4. A trace of one slow request with the exemplar path from metric → trace → log.
5. A multi-window burn-rate alert pack with a flapping-reduction measurement.

---

## Done = You Can

- Define an SLI someone else could implement identically from your spec.
- Explain, numerically, why your alert fires when it does.
- Instrument a Java service so that metrics, traces, and logs share a correlation id.
- Budget the cost of observability and justify the sampling policy.
