# Lab 20: Production Readiness & SLO Engineering — Mini Project

## Project: `ReadinessLab` — Review a Real Service With Evidence, Not Checkmarks

**Time**: 12–16 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, Kubernetes (kind or real), PostgreSQL + Redis, Prometheus + Grafana, Alertmanager, Toxiproxy, k6, a logging pipeline

Take a service (build one or adopt one), run a complete production readiness review, and produce evidence for every claim. Where you cannot produce evidence, record an accepted risk with an owner and an expiry — not a tick.

---

## Part 1 — The service

Build or adopt `checkout-api` with realistic properties:

```
POST /checkout          → orders-api (HTTP), payments-api (HTTP → PSP), inventory (HTTP), PostgreSQL, Redis
GET  /checkout/{id}     → PostgreSQL + Redis cache
GET  /checkout/search   → Elasticsearch (stub with WireMock, latency 40 ms)
```

Include these properties, some of which are good and some of which are not:

| Property | Value | Verdict needed |
|---|---|---|
| Warm start | 70 s (JVM + cache fill + 3 connection pools) | needs a startup probe |
| Graceful shutdown | SIGTERM handler, but `terminationGracePeriodSeconds: 20` | likely too short |
| Connection pool | Hikari 200, downstream `maxConnections` 150 | likely over budget |
| Caches | Caffeine 5 min (no jitter), Redis 60 s | stampede risk |
| Retries | `payments-api` 3 attempts, no budget | over budget |
| Deploy | `maxUnavailable: 3`, `maxSurge: 3`, no canary | no blast-radius control |
| Migrations | one `NOT NULL DEFAULT` on a 50M-row table, no `lock_timeout` | unsafe |
| Observability | SLI-less, CPU alert only | not ready |
| Backups | daily snapshot, never restored | unverified |
| Runbooks | one, written by the author, 14 months old | unexercised |

Your job: **determine, with evidence, which of these are acceptable and which are not.**

---

## Part 2 — The evidence template

Every readiness item must carry evidence, not a tick:

```markdown
### Item 4.2 — Shutdown drains without user-visible errors

**Claim**: A rolling restart produces zero 5xx responses.

**Evidence**:
```
# 1. Run load, then roll the deployment, and count 5xx by window.
k6 run -e RATE=800 -e DURATION=10m checkout.js &
./rollout-with-error-counting.sh deploy/checkout-api
# Result: 0 5xx during rollout; 5xx rate before 0.02%, during 0.03%
```

**Arithmetic**: `in_flight = 400`, `throughput = 300/s`, `p99.9 = 11 s`, `preStop = 8 s`
→ `grace = 8 + max(400/300, 11) + 5 = 24 s`; the previous value was 20 s → **inadequate**,
now 45 s.

**Verdict**: FAIL initially (with the measured error count), PASS after the fix.
**Owner / expiry**: — (closed)
```

**Deliverable**: `EVIDENCE_TEMPLATE.md` — the template above, used for every item in the review.

---

## Part 3 — SLI/SLO specification

Four dimensions, with explicit `valid` exclusions:

```yaml
# slo.yaml
service: checkout-api
slis:
  availability:
    definition: "good = HTTP 2xx for POST /checkout and GET /checkout/{id}; valid = all requests to those endpoints minus client-cancelled (499) and synthetic probes"
    slo: 99.9
    window: 28d
  latency:
    definition: "good = server-side duration ≤ 400 ms; valid = same as availability"
    slo: 99          # the 99th percentile must be under 400 ms
    window: 28d
  correctness:
    definition: "good = checkout completed with an order_id present; valid = all checkouts that returned 2xx, excluding the canary account"
    slo: 99.95
    window: 28d
  freshness:
    definition: "good = search index lag < 30 s; valid = all index writes"
    slo: 99.5
    window: 28d
exclusions:
  - { name: client_cancelled,   reason: "user navigated away; not a service failure" }
  - { name: synthetic_probes,  reason: "not user traffic" }
  - { name: canary_account,    reason: "internal load test account" }
minimum_valid_events: 100
```

Compute the budgets:

```
availability 99.9%  / 28d  →  40.3 min
latency 99% of ≤400ms / 28d → effectively a tail objective; track as a burn on the 1% budget
correctness 99.95%  / 28d  →  20.2 min
freshness 99.5%     / 28d  →  3.4 h
```

Recording rules and burn-rate alerts:

```yaml
- record: sli:checkout:availability_ratio5m
  expr: |
    1 - sum(rate(http_server_requests_seconds_count{service="checkout-api",route="/checkout",status=~"5.."}[5m]))
        / sum(rate(http_server_requests_seconds_count{service="checkout-api",route="/checkout"}[5m]))

- alert: CheckoutAvailabilityBurnFast
  expr: |
    (1 - sli:checkout:availability_ratio5m) > (14.4 * 0.001)
    and (1 - sli:checkout:availability_ratio5m:5m) > (14.4 * 0.001)
  for: 2m
  labels: { severity: page, runbook: checkout/availability }

- alert: CheckoutLatencyBurnFast
  expr: |
    (1 - sli:checkout:latency_ok_ratio5m) > (14.4 * 0.01)
    and (1 - sli:checkout:latency_ok_ratio5m:5m) > (14.4 * 0.01)
```

Then **measure the lead time**: replay a historical-style incident (inject a 5% error rate for 10 minutes, and a 1% error rate sustained for 6 hours) and record when each alert fired.

**Deliverable**: `SLO_SPEC.md` — the spec, the budgets, the alerts, and the measured lead times for the two incident shapes.

---

## Part 4 — Capacity readiness

### 4.1 Load test at peak

```javascript
// open-loop, arrival rate, ramped
scenarios: { checkout: { executor: 'ramping-arrival-rate', startRate: 100, timeUnit: '1s',
  preAllocatedVUs: 400, maxVUs: 3000,
  stages: [ {target: 400, duration: '3m'}, {target: 800, duration: '5m'},
            {target: 1200, duration: '5m'}, {target: 1600, duration: '5m'},
            {target: 2000, duration: '5m'} ] } }
thresholds: { http_req_duration: ['p(99)<400'], http_req_failed: ['rate<0.001'] }
```

Produce the load curve, the knee, the peak, and the limiting resource.

### 4.2 The capacity model

```
safe_rps_per_pod = cores_per_pod × U_target / cpu_per_request_ms × 1000
nodes_for_peak   = ceil( peak_rps / (safe_rps_per_pod × pods_per_node) )
nodes_for_n_plus_1 = smallest n with (n−1) × node_capacity ≥ peak_rps
```

### 4.3 Dependency budget

For each downstream: `replicas × pool_max / dependency_capacity` and whether it is under 0.7. For this service: `200 × replicas / 150` — compute the maximum replica count at which it stays under budget, and compare with the current HPA max.

**Deliverable**: `CAPACITY.md` — the load curve, the knee, the model, the N+1 requirement, and the dependency budget with the HPA-max finding.

---

## Part 5 — Startup and shutdown readiness

### 5.1 Startup

- Measure the real cold start: delete the pod, time from `Running` to first successful request.
- Verify the readiness endpoint returns success only once the service can serve (warm pools, caches, downstream reachable).
- Add a startup probe sized at `2 × worst observed` and verify that killing a pod during warm-up does not restart-loop.
- Verify a warming pod does not receive traffic.

### 5.2 Shutdown

- Derive the grace period from the drain arithmetic.
- Set `terminationGracePeriodSeconds` and a `preStop` sleep.
- Roll under load and count 5xx by window; the criterion is zero.
- Repeat three times, because this is a race.

**Deliverable**: `LIFECYCLE.md` — cold-start measurement, the probe configuration, the drain arithmetic, and three rollout-under-load results with the 5xx counts.

---

## Part 6 — Failure-mode inventory and injections

```markdown
| # | Failure mode | Injection | Pass condition | Result | Action |
|---|---|---|---|---|---|
| F1 | `payments-api` unavailable | Toxiproxy reset | circuit breaker opens < 30 s; checkout completes with a clear failure, not a 500 | | |
| F2 | `payments-api` 2 s latency | Toxiproxy latency | retry rate stays < 10%; p99 < 1.2 s | | |
| F3 | `inventory` unavailable | Toxiproxy reset | bulkhead sheds; other paths unaffected | | |
| F4 | PostgreSQL unavailable | stop the container | readiness fails; no writes accepted; recovers within 60 s | | |
| F5 | Redis unavailable | stop the container | cache-miss path holds p99 < 900 ms; no cascade | | |
| F6 | Search index unavailable | WireMock 503 | checkout completes; search degrades visibly | | |
| F7 | Pod killed mid-request | `kubectl delete pod` | no order in an indeterminate state; no duplicate order | | |
| F8 | CPU limited to 200m | cgroup | p99 degrades proportionally; sheds before collapse | | |
| F9 | JVM heap exhausted | allocate until OOM | `ExitOnOutOfMemoryError` → fast restart, not a limp | | |
| F10 | Node drained during peak | `kubectl drain` | PDB respected; no 5xx | | |
| F11 | Migration runs at boot with 3 pods | scale to 3 at once | one migration applies; no lock pile-up | | |
| F12 | Rollback after a schema change | deploy bad, roll back | rollback behaviour known and documented | | |
```

Run at least F1–F5 and F7. For each, record the hypothesis, the pass condition, the metric series, and the result.

**Deliverable**: `FAILURE_MODES.md` — the inventory with results, and every failure converted into a tracked action.

---

## Part 7 — Runbooks and on-call

Take the existing 14-month-old runbook and test it:

1. Pick an engineer who did not write it.
2. Give them the alert that fires and the runbook link.
3. Time them. Note every command that fails, every dashboard that is inaccessible, every ambiguous step.
4. Rewrite the runbook with expected outputs for every step.

Then verify the alert→runbook pairing: every paging alert links to a runbook that has been executed successfully at least once.

**Deliverable**: `RUNBOOK_REVIEW.md` — the timed walkthrough, the defects found, the rewritten runbook, and the alert-to-runbook coverage table.

---

## Part 8 — Data, recovery, and rollback drills

### 8.1 Restore test

```bash
# Restore the latest snapshot into a clean instance and time it.
aws rds restore-db-instance-from-db-snapshot ... # or local equivalent
time pg_restore -j 8 --no-owner --no-privileges dump.sql
```

Measure: restore duration, index rebuild overhead, and the data-loss point (RPO) from the WAL/binlog position. Compare with the stated objectives.

### 8.2 Rollback drill

Deploy a version with a deliberate 2% error rate, roll back, and time from "decision" to "verified recovered". Repeat for a service with a schema change to establish whether rollback is available there.

**Deliverable**: `RECOVERY.md` — the restore test with real RTO/RPO and the gap to the stated objectives, plus the rollback drill timings and the availability statement per service.

---

## Part 9 — The review record and the gate

### 9.1 The PRR record

```markdown
# Production Readiness Review: checkout-api v2.4.0

Date: <today>   Reviewer: <you>   Accountable: <tech lead>

| Area | Items | Pass | Fail | Accepted risk |
|---|---|---|---|---|
| SLIs & SLOs | 6 | 6 | 0 | 0 |
| Capacity | 7 | 5 | 2 | 1 (N+1 not yet funded; expires <date>) |
| Startup & shutdown | 5 | 5 | 0 | 0 |
| Dependencies & failure modes | 12 | 9 | 3 | 0 |
| Observability & alerting | 8 | 6 | 2 | 0 |
| Runbooks & on-call | 6 | 4 | 2 | 1 |
| Deployment & rollback | 7 | 6 | 1 | 0 |
| Data & recovery | 6 | 4 | 2 | 1 (restore gap; expires <date>) |

**Verdict**: NOT READY — 10 failures, 3 accepted risks. Re-review after remediation.
```

### 9.2 Accepted-risk register

```markdown
| Risk | Why accepted | Owner | Compensating control | Expires |
|---|---|---|---|---|
| Restore RTO 10.4 h vs 4 h objective | Continuous archiving is a 6-week project | SRE lead | Daily restore test of a sample dataset; documented escalation to a manual failover runbook | 2026-08-01 |
```

### 9.3 The gate itself

Turn the review into an automated gate so it is not a ceremony:

```bash
#!/usr/bin/env bash
# check-readiness.sh <repo>   — blocks a release to production without evidence
fail=0
# 1. SLO spec exists and covers all four dimensions
grep -q 'availability:' slo.yaml && grep -q 'latency:' slo.yaml && \
grep -q 'correctness:' slo.yaml && grep -q 'freshness:' slo.yaml || { echo "FAIL: incomplete SLO spec"; fail=1; }
# 2. Burn-rate alerts exist for availability and latency
grep -q 'BurnFast' alerts.yaml || { echo "FAIL: no burn-rate alert"; fail=1; }
# 3. Every paging alert links to a runbook that has been exercised
comm -23 <(grep 'severity: page' -A5 alerts.yaml | grep -o 'runbook: .*' | cut -d' ' -f2 | sort -u) \
         <(grep -l 'last_exercised:' runbooks/*.md | sed 's|runbooks/||;s|\.md||' | sort -u) | \
  while read -r m; do echo "FAIL: paging alert without an exercised runbook: $m"; done
# 4. A readiness record exists with no open failures
python3 prr_check.py . || fail=1
# 5. No migration in this release without lock_timeout
./check-migrations.sh db/migration || fail=1
exit $fail
```

**Acceptance**: the gate blocks a release missing an SLO, a burn alert, an exercised runbook, or a completed readiness record — with a specific message for each.

**Deliverable**: `PRR_RECORD.md` — the review with evidence links, the accepted-risk register, and the gate implementation with its blocking demonstrations.

---

## Acceptance Criteria

- [ ] `EVIDENCE_TEMPLATE.md` used for every item; no item accepted without a measurement or a cited artifact.
- [ ] `SLO_SPEC.md`: four dimensions, explicit exclusions, event floor, computed budgets, burn-rate alerts, and measured detection lead times for two incident shapes.
- [ ] `CAPACITY.md`: load curve, knee, saturation resource, capacity model, N+1 node requirement, and the dependency-budget finding against the HPA max.
- [ ] `LIFECYCLE.md`: measured cold start, probe configuration, drain arithmetic, and three rollout-under-load results with zero 5xx.
- [ ] `FAILURE_MODES.md`: 12 modes enumerated, at least 6 executed with pass conditions, every failure converted into an action.
- [ ] `RUNBOOK_REVIEW.md`: timed walkthrough by a second engineer, defects found, rewritten runbook, and alert-to-runbook coverage.
- [ ] `RECOVERY.md`: measured RTO/RPO versus objectives, and a rollback drill with the availability statement per service.
- [ ] `PRR_RECORD.md` with the eight-area table, the accepted-risk register with owners and expiries, and a gate that blocks a release on four specific failures.

---

## Stretch

- Run the PRR on a service you did not build, and write the review as the receiving team would.
- Re-run the review after 6 months and measure drift: how many items are no longer evidenced, and what did it cost?
- Automate the capacity item: run a nightly load test at 60% of peak and fail the build if throughput or p99 regresses by more than 10%.
- Convert the most-used runbook into an executable script the responder runs rather than reads, and measure the reduction in mitigation time.
- Build a "readiness as a lease" tracker: for each service, the date of the last review, the number of stale items, and the expected loss from the drift arithmetic.
