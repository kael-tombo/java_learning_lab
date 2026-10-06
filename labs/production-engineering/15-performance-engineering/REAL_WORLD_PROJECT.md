# Lab 15: Performance Engineering & Load Testing — Real World Project

## Scenario: "Black Friday Capacity Was a Number Somebody Chose"

You are a performance engineer on a retail platform: 16 Spring Boot 3 services, Java 21, Kubernetes, PostgreSQL primary + 2 read replicas, Redis, and a business that plans promotions 6 weeks ahead.

**The situation** — Tuesday, four weeks before the largest promotion of the year. Historically, peak traffic is **9,000 rps** on `catalog-api` and `checkout-api`, sustained for roughly 3 hours, with a hard requirement that checkout stays above 99.5% success.

**The state of your knowledge**:

1. **No capacity model exists.** The Kubernetes HPA says "scale at 65% CPU", the pods are 2 vCPU / 4 Gi, and nobody has run a load test against the current version of `catalog-api` in seven months.
2. **The last load test** (seven months ago, on a different architecture) reported 4,200 rps peak on a 16-core lab box. It was run with a closed-loop tool, with 200k synthetic rows instead of 9M, and with every downstream mocked in-process. The report was a chart with a green tick.
3. **This month's release** added a `recommendedProducts` call to `catalog-api` — a new synchronous dependency, with a client that has a 3-second timeout and retries twice. It went to production three weeks ago. Latency p99 went from 210 ms to 480 ms. The release notes say "no functional change to the request path", which was false.

**The question the business asks you on Wednesday**: "Can we handle Black Friday at 9,000 rps, and what happens at 12,000 if the campaign goes better than expected?"

**Your job over 4 weeks**: build the capacity model, run tests you can defend, find and fix the bottlenecks, and produce an answer with numbers and a stated risk — including the headroom policy for failure tolerance, which the business has never been told about.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Estimate before you measure (Day 1–3)

### 1.1 Build the model on paper

For `catalog-api` and `checkout-api`, from production telemetry (existing dashboards, not new work):

- `λ_peak` and `W` per endpoint class.
- CPU-seconds per request (from `process_cpu_time_total` / request count).
- Memory per request, connection counts, and pool sizes.

Compute:

```
L = λ × W
safe_rps_per_pod = cores_per_pod × U_target / cpu_per_request
pods_for_peak = ceil(λ_peak / safe_rps_per_pod)
pods_with_failure_tolerance = pods sized so surviving capacity still covers peak
```

**Deliverable 1 — Capacity model v0** (estimates only, explicitly labelled as unverified), with the assumptions and the utilisation target stated.

### 1.2 Reconstruct the seven-month-old test

Explain what that test actually measured: closed-loop (coordinated omission), 200k rows (no index behaviour), in-process mocks (no connection pools, no serialization, no network), 16 cores vs production's 2 per pod.

**Deliverable 2 — Methodology critique** with a per-dimension table (arrival model, data volume, downstream realism, CPU ratio, network RTT) and an estimate of how much each distortion inflated the result.

### 1.3 Establish the true baseline

Before changing anything, run a defensible measurement of the current production version: open-loop, production-shaped data (a 9M-row copy with production skew), rate-limited stubs with realistic latency, network shaped to production RTT, three runs, warmed up.

**Deliverable 3 — Measured baseline** for `catalog-api` and `checkout-api`: load curve, knee, peak throughput, p50/p99/p999, CPU per request, DB queries per request, and the safe capacity at the chosen utilisation target.

### 1.4 The gap

```
modelled_peak_9,000 rps  vs  measured_safe_capacity  vs  required 9,000 (and 12,000)
```

**Deliverable 4 — Gap analysis** with the arithmetic and the list of what must be fixed to close it.

---

## Phase 2 — Find the bottlenecks (Day 3–8)

### 2.1 Profile under load

async-profiler (cpu, alloc, lock, wall) plus JFR on both services at 70% of measured safe capacity.

**Deliverable 5 — Profiles** with the flame graphs, the allocation hot spots, the lock contention, and the phase-timing breakdown.

### 2.2 Dependency attribution

Where does `W_total` go: `W_db`, `W_dep`, `W_map`, `W_serialize`? For `catalog-api`, quantify the new `recommendedProducts` call.

**Deliverable 6 — Phase attribution** per endpoint, with the Amdahl analysis: if `W_dep` is 40%, a 10× improvement there buys `1/(0.6 + 0.4/10) = 1.6×`.

### 2.3 Database analysis

`pg_stat_statements` by total time, query plans with `EXPLAIN (ANALYZE, BUFFERS)`, N+1 detection, index inventory versus query predicates, lock waits, replica lag.

**Deliverable 7 — Database analysis** with the top-10 queries by total time, the plans, the missing indexes, and the replication-lag behaviour under write load.

### 2.4 The release that was "no functional change"

Establish exactly how much of the regression is the new dependency, with and without it.

**Deliverable 8 — Regression attribution**: p99 before 210 ms, after 480 ms. The share from the new call, the share from retry amplification under load, and the share from pool growth.

---

## Phase 3 — Fix in Amdahl order (Week 2)

In order of the fraction of time each addresses, one change per measured run:

1. **Make the new dependency non-blocking or bounded** — call it asynchronously with a short timeout and serve without it; or cache it; or make it a circuit-broken optional enrichment. Quantify the p99 improvement.
2. **Remove the N+1** — a batch/join fetch in the list path.
3. **Add the missing indexes** — concurrently, with `lock_timeout`.
4. **Reduce allocation in the mapper** — allocation rate before/after, GC pause rate before/after.
5. **Right-size the pools** — `min(λ × W × safety, dependency capacity)`, with the shared-dependency arithmetic for all 16 services.
6. **Fix the logging** — no object formatting at INFO.
7. **Fix the retry policy** — a global retry budget, no retries on non-idempotent paths, circuit breaker with a measured fallback.

**Deliverable 9 — Fix log** with per-fix: fraction addressed, throughput, p99, CPU per request, and the incremental effect (the fixes interact; measure cumulatively).

---

## Phase 4 — Model and verify the target (Week 2–3)

### 4.1 The model

```
safe_rps_per_pod = cores_per_pod × U_target / cpu_per_request_after_fixes
peak_with_growth = 9,000 × 1.2 = 10,800
stress_case      = 12,000
failure_case     = surviving pods must still cover 9,000
```

Compute pods for: normal peak, growth case, stress case, and N+1 failure. State the utilisation target and what it costs.

**Deliverable 10 — Capacity plan** with all four scenarios, the pod counts, the node requirement, and the cost.

### 4.2 Verify by test, at production shape

Run in a production-shaped environment: same pod spec, same data volume, same network shape, same downstream stubs (rate-limited), at the target load.

**Deliverable 11 — Verification report**: at 9,000, 10,800, and 12,000 rps — throughput, p99, error rate, CPU, DB, and pass/fail against the 99.5% success requirement.

---

## Phase 5 — Prove the failure modes (Week 3)

| Scenario | Injection | Success criteria |
|---|---|---|
| S1 | One pod's node lost during peak | capacity covers peak with N−1 pods; no checkout failures |
| S2 | `recommendedProducts` at 3 s for 5 min | enrichment is skipped/absent; checkout p99 unaffected; breaker opens |
| S3 | Replica lag 60 s | reads served from replica are within the staleness bound; writes unaffected |
| S4 | Database failover mid-peak | reconnect within 60 s; no connection storm; error rate < 0.5% |
| S5 | Redis unavailable | cache miss path holds p99 under the target; no cascade |
| S6 | A new pod starting during peak | warm-up does not consume production capacity (JIT/class loading) |
| S7 | 30% traffic from a single hot key | no per-key hot spot (cache or DB) becomes the limiter |
| S8 | Autoscaler slow to react (2-min scale-up) | queued load absorbed by headroom |
| S9 | 12,000 rps (stress) | graceful degradation: checkout priority preserved, catalogue search shed first |
| S10 | Load left at peak for 4 hours (soak) | no heap, FD, or log growth; no p99 drift |

**Deliverable 12 — Resilience-under-load report** with all ten scenarios, measured results, and the fixes for anything missed.

---

## Phase 6 — Ongoing measurement (Week 3–4)

- **Synthetic production probe**: a small, constant-rate k6 check (200 rps, 24/7) against production, so capacity problems surface before the promotion. This is the control that makes the whole exercise durable.
- **Nightly load test** in staging at 60% of modelled peak, tracked as a trend, alerting on a throughput or p99 regression.
- **Perf gates in CI**: JMH micro-benchmarks with a 5% regression threshold, plus a short load test against stubs.
- **Dashboards**: CPU per request, DB queries per request, pool wait, cache hit ratio per class, p99 per endpoint, and `L = λ × W` as a live panel.

**Deliverable 13 — Ongoing performance programme**: synthetic probe, nightly load test, CI gates, and dashboards, each with an owner and an alert threshold.

---

## Phase 7 — Quantify and communicate (Week 4)

| Metric | Before | After |
|---|---|---|
| Measured peak throughput (`catalog-api`) | unknown (est. 4,200 from a flawed test) | X rps (measured, production shape) |
| Safe capacity at U=0.7 | unknown | Y rps |
| Pods for 9,000 rps with N+1 tolerance | unknown (HPA would have discovered under load) | Z pods |
| p99 at 9,000 rps | unknown (480 ms at low load) | target met |
| CPU per request | 4.1 ms | 1.7 ms |
| DB queries per list request | 101 | 2 |
| Time to answer "can we handle Black Friday?" | never asked, or guessed | 1 day, repeatable |
| Compute cost per 1,000 orders | A | B (with the delta explained) |
| Regression detection for the next regression | days to weeks | minutes (synthetic probe) |
| Capacity model staleness | unknown | re-verified per release via the CI gate |

Present three answers to the business: **9,000 rps — yes, with pod count Z and utilisation U. 12,000 rps — yes/no, with the specific change required. If a node is lost — yes/no, and what degrades first.**

**Deliverable 14 — Capacity answer + business case**, with the risk statement (what is unmodelled: a marketing campaign that changes behaviour, a dependency you do not control, an unmodelled data skew).

---

## Deliverables checklist

- [ ] Phase 1 capacity model v0, methodology critique, measured baseline, gap analysis.
- [ ] Phase 2 profiles, phase attribution with Amdahl, database analysis, regression attribution.
- [ ] Phase 3 fix log with per-fix and cumulative measurement.
- [ ] Phase 4 capacity plan (4 scenarios) and verification report at 9,000 / 10,800 / 12,000 rps.
- [ ] Phase 5 ten-scenario resilience-under-load report.
- [ ] Phase 6 ongoing programme (synthetic probe, nightly test, CI gates, dashboards).
- [ ] Phase 7 capacity answer, business case, and risk statement.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Estimation | "Let's test and see" | Capacity model before testing, with assumptions and utilisation target stated |
| Methodology | "Load test passed" | Open-loop arrival rate, production data volume, rate-limited stubs, shaped network, three runs with spread |
| Critique | "The old test was fine" | Per-dimension distortion table with an estimate of the inflation |
| Attribution | "It's slow" | Phase attribution (`W_db`/`W_dep`/`W_map`) plus Amdahl analysis before optimising |
| Fixes | "We optimised the mapper" | Largest-fraction-first, one change per measured run, cumulative effect reported |
| Verification | "We hit the target in staging" | Production-shaped verification at 9,000 / 10,800 / 12,000 with N+1 failure tolerance |
| Resilience | "The load test passed" | Ten failure-mode scenarios including dependency latency, DB failover, hot keys, soak |
| Durability | "We wrote a doc" | Synthetic probe, nightly load test, CI perf gates, live `L = λ × W` panel |
| Communication | "We can handle it" | Three explicit answers plus a stated risk list and the cost delta |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Google SRE Workbook — "Load Balancing" and "Monitoring Distributed Systems"** — https://sre.google/workbook/load-balancing/ and https://sre.google/workbook/monitoring-distributed-systems/ — the canonical treatment of load-balancer behaviour under overload (queue growth, load shedding, the recommendation to shed load before requests queue indefinitely) and of the resource-utilisation tail that reveals saturation: CPU saturating at ~60% with high steal or throttling, or network bandwidth at ~80%, indicates a bottleneck well before latency breaks. Also the source for the "monitor the four golden signals and watch the utilisation tail" framing used in Phase 6.
2. **Martin Fowler — "Load Balancer" / "Circuit Breaker" / "Tail at Scale" (via martinfowler.com/articles)** — https://martinfowler.com/bliki/CircuitBreaker.html — the reference for the retry/timeout/circuit-breaker triad that Fix 7 addresses, including the explicit warning that retries without a budget amplify load during an outage (the retry storm). Use it to justify the retry-budget arithmetic and the breaker configuration rather than asserting them.

Additional anchors worth verifying: k6's executor semantics for your version — `ramping-arrival-rate`/`constant-arrival-rate` maintain the arrival rate independently of VU availability, and `dropped_iterations` is the counter that proves it; whether your version reports "expected" versus "actual" response-time series (this is the mechanism for coordinated-omission detection); Gatling's equivalent open-workload behaviour and its injector configuration; async-profiler's current mode names and its `--traces`/`--cstack` options; and your JVM's GC logging flags and `jfr` event names for the version you run, since event names have changed across JDK releases.

---

## Reflection questions

1. The seven-month-old test said 4,200 rps on a 16-core box. Which single distortion inflated it most, and how would you have known?
2. A release note said "no functional change to the request path" and added a synchronous 3 s dependency. What CI check would have caught that claim?
3. You sized pods for peak. What does the N+1 failure case cost, and should the business be told the number?
4. Your safe capacity at U=0.7 is Y rps and your peak is 9,000. If the campaign hits 12,000, what degrades first and who decides what to shed?
5. The synthetic probe is 200 rps against production. What could go wrong, and what guard rails would you add before running it continuously?
