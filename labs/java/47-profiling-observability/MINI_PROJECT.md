# MINI PROJECT — Profiling & Observability: Find the Hidden 300ms

## Goal (2 weeks, ~8–10h)
Instrument a deliberately slow checkout service (hidden N+1, boxed
churn, contended lock, chatty downstream) and ship a dashboard +
postmortem naming each culprit with flame/JFR proof.

## Requirements
### Functional
1. JFR continuous: `JFR.start` on boot (100MB ring, `profile`
   settings); dump on demand; `jdk.*` events queryable via JMC + `jfr`
   CLI excerpts committed.
2. async-profiler quad: cpu + alloc + lock + wall collapses per
   endpoint; differential flame (before/after one fix) rendered.
3. Metrics: Micrometer → Prometheus: `http_server_requests_seconds`
   histogram, JVM (GC pause, threads, pools), downstream client
   timings; Grafana (or text) dashboard with RED per endpoint.
4. Tracing: trace ids across gateway → pricing → inventory (OTel or
   MDC); exemplar links slow trace → flame/JFR recording id.
5. Find all four planted bugs: N+1 fee lookup, `synchronized` cache
   on hot path, boxed-stream pricing churn, 3x redundant auth call —
   each with event/flame line pointer.
6. Fix + re-profile: one fix per category; p99 delta + CPU/alloc/lock
   deltas tabulated; recording ids referenced.

### Non-functional
- Overhead proof: JFR on vs off RPS delta <2%; profiler only ad-hoc.
- 12+ tests: metric presence, trace propagation, JFR file validity,
  dashboard-query smoke (PromQL returns series).
- Runbook snippet: "p99 alert → which recording → which flame →
  which fix" in README (10 lines).
- All artifacts reproducible via `scripts/profile.sh`.

## Starter Layout
```
src/main/java/com/lab47/shop/{CheckoutService,PricingRepo,AuthClient}.java
scripts/{profile.sh,jfr-dump.sh,flames.sh}
dashboards/{red.json,prom-queries.md}  results/{jfr,collapsed,flames}
```

## Phases
### Week 1 — Instrument (4–5h)
- JFR + profiler + metrics/traces wired; first quad captured.
- Deliverable: dashboard + four suspect frames named.
### Week 2 — Prove + Fix (4–5h)
- Fixes with differential flames + postmortem.
- Deliverable: culprit table with event/flame pointers.

## Test Plan
- Planted-bug coverage: each bug maps to ≥1 test that fails pre-fix.
- Trace test: 100 requests, 100% carry trace id end-to-end.
- Metric test: p99 query returns value within 5% of load-driver stat.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| JFR | Continuous + event-ranked | Recorded | Missing |
| Quad flames | 4 modes + diff flame | CPU only | No flames |
| Metrics/traces | RED + exemplars | Metrics only | Logs only |
| Bug hunt | 4/4 with pointers | 2–3 found | Guessed |
| Fixes | Measured deltas each | Fixed | Unproven |

Pass ≥ 70. Stretch: continuous-profiling agent (Pyroscope/JFR
upload) + auto-regression alert on top-frame delta.

## Demo Checklist
- [ ] Live p99 alert → open recording → flame → culprit line
- [ ] Diff flame: hot frame shrinks visibly after fix
- [ ] Trace → exemplar → JFR event chain in one click/flow
- [ ] Overhead slide: JFR <2%, profiler ad-hoc only

## Common Traps
Averaging latencies, profiling only in dev, high-cardinality tags
(user ids), CPU-only profiling of an I/O stall.
