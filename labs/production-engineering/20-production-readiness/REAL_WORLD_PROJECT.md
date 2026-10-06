# Lab 20: Production Readiness & SLO Engineering — Real World Project

## Scenario: "Ready For Production?"

You are a staff engineer at a marketplace platform: 16 Spring Boot 3 services, Java 21, Kubernetes, PostgreSQL 15, Redis, Kafka, Elasticsearch. ~120 engineers, 9 squads. Product leadership has a launch date: **a new seller onboarding flow goes to production in 9 weeks**, and it depends on 5 services that have never carried production traffic.

**The situation**:

- `seller-onboarding` (new), `catalog-sync` (new, batch), `document-store` (new, file uploads), `notification-dispatch` (extended), `search-indexer` (extended) — 5 services, no SLOs, no error budgets, no capacity models.
- All 5 have dashboards nobody verified, alerts on CPU and memory only, and no burn-rate alerting anywhere in the platform.
- `document-store` writes to an S3-like object store and has a daily snapshot of a *PostgreSQL* index of the files — the object store's own versioning is off, and nobody has attempted a restore.
- `search-indexer` consumes from Kafka and writes to Elasticsearch. Nobody knows the projection lag tolerance; the last measured lag during peak was 6 minutes.
- Rollback: `catalog-sync` writes rows to a table the old code reads with a different column name. Rollback is not available, and nobody knows that.
- A migration in `notification-dispatch` adds a `NOT NULL DEFAULT` to a 120M-row table with no `lock_timeout`.
- On-call: 14 pages per shift, mostly CPU alerts, and the runbooks for the 5 new services do not exist.

**The ask**: tell product leadership whether the launch is ready, in nine weeks, with evidence — and if it is not, tell them precisely what must change and what you are willing to accept.

**Your job over 4 weeks**: run the readiness review properly. Specify SLOs and budgets, build capacity models, verify lifecycle behaviour, enumerate and inject failure modes, write and exercise runbooks, measure recovery, and produce a defensible launch recommendation with an accepted-risk register.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Define what "working" means (Day 1–4)

### 1.1 SLI/SLO specification per service

For each of the 5 services, four dimensions: availability, latency, correctness, freshness. Each with an explicit `valid` definition and exclusions, a minimum valid-events floor, and a window.

**Deliverable 1 — SLO specification** for all 5 services, with computed error budgets:

| Service | Availability | Latency | Correctness | Freshness | Budget consumed by a 30-min incident |
|---|---|---|---|---|---|
| seller-onboarding | 99.9% (28d) | 99% < 800 ms | 99.95% | n/a | |
| catalog-sync | 99.5% (28d) | batch: within 2 h | 99.9% | data < 2 h stale | |
| document-store | 99.9% | 99% < 1.5 s | 99.99% (no lost files) | n/a | |
| notification-dispatch | 99.9% | 99% < 2 s | 99.9% | 99% within 60 s | |
| search-indexer | 99.5% | batch | — | 99% within 30 s | |

Include the exclusion list with reasons, and the minimum valid-events floor.

**Decision point**: for `search-indexer`, the measured lag at peak is 6 minutes against a proposed 30-second freshness objective. That is either a wrong objective or a real capacity gap. Resolve it with arithmetic before writing the SLO.

**Deliverable 2 — SLO rationale** for the freshness and latency objectives, showing which are achievable from the current architecture and which require work.

### 1.2 Error budgets and the release policy

For each service, the budget in minutes, what a single incident consumes, and the resulting release policy state.

**Deliverable 3 — Error budget table** and the written release policy (`> 50%` ship freely, `25–50%` canary-only, `< 25%` freeze).

### 1.3 Detectability audit

For each SLO: does a metric exist that would detect a burn? Compute the detection lead time from the alert window, and simulate two incident shapes (a 10-minute 5% error spike; a 6-hour 1% degradation) to confirm each fires.

**Deliverable 4 — Detectability audit** with the measured lead times per SLO, and the alert gaps closed.

---

## Phase 2 — Capacity (Day 4–8)

### 2.1 Load test each new service in a production-shaped environment

Same instance types, same database topology, production-shaped data volumes, network-shaped RTT, rate-limited stubs for dependencies, warm-up, three runs.

**Deliverable 5 — Load test reports** per service: the load curve, the knee, the saturation resource, the limiting resource, and the peak at the chosen utilisation target.

### 2.2 Capacity models and N+1

For each service: `safe_rps_per_pod`, the node requirement for peak, the node requirement that survives N+1, and the growth forecast to 18 months.

For the launch specifically: forecast seller registrations. Marketing projects 40,000 sellers in launch week (versus 6,000 currently).

**Deliverable 6 — Capacity plan** with the per-service model, the N+1 requirement, the forecast, and the launch-week capacity plan with the specific pod and node counts.

### 2.3 Dependency budget

For every dependency edge of the 5 services: `replicas × pool_max / dependency_capacity`, and the maximum replica count at which each stays under 0.7.

**Deliverable 7 — Dependency budget matrix**, with the findings that will bind at launch-week replica counts, and the required pool resizing.

### 2.4 HPA configuration

Verify each HPA: correct metric (not CPU for I/O services), correct target, stabilisation windows, behaviour policy, and a **minimum replica count that survives a single node loss**.

**Deliverable 8 — HPA configuration** with per-service settings and the justification, including the observed oscillation if any service is oscillating.

---

## Phase 3 — Lifecycle (Week 2)

### 3.1 Startup

For each service: measure the real cold start, configure a startup probe at `2 × worst observed`, verify readiness gates traffic until servable, and verify a warming pod does not receive traffic or consume serving capacity on rollout.

`document-store` is the risk case: it validates uploaded files against an index at startup.

**Deliverable 9 — Startup evidence** per service: cold-start measurement, probe configuration, and the readiness gate verification.

### 3.2 Shutdown

For each service: derive the grace period from the drain arithmetic, add a `preStop` sleep, set `maxUnavailable: 0`, then roll under load three times and count 5xx by window.

**Deliverable 10 — Shutdown evidence** per service: the drain arithmetic, the configuration, and three rollout-under-load results with zero 5xx.

### 3.3 Rollout strategy

Canary with pre-declared analysis (error rate, latency, saturation) and automatic rollback, sized by sample size. For the batch services, a different strategy: a release window plus a rerunnable job.

**Deliverable 11 — Rollout configuration** for all 5 services, with the step durations derived from the sample-size calculation.

---

## Phase 4 — Dependencies and failure modes (Week 2)

### 4.1 Inventory

For each of the 5 services: 15+ failure modes — dependencies (up, down, slow, throttled, malformed), datastores, resource limits, lifecycle events, network shapes, clocks, data conditions.

**Deliverable 12 — Failure-mode inventory**, 15+ per service, ranked by expected blast radius.

### 4.2 Inject

Execute the top three per service (15+ experiments) with hypotheses, pass conditions, and aborts.

**Deliverable 13 — Injection results**, with every failure becoming a tracked action and a scheduled re-run.

### 4.3 Migration safety

The `notification-dispatch` migration: rewrite as `ADD COLUMN` nullable + backfill + `NOT NULL` via `NOT VALID`/`VALIDATE`, with `lock_timeout`.

**Deliverable 14 — Migration remediation** with the measured lock times before and after.

### 4.4 Rollback availability

Establish, per service, whether rollback is available and, if not, what the fix-forward playbook is. `catalog-sync` will be unavailable until the schema is fixed in the next release.

**Deliverable 15 — Rollback availability register** with the fix-forward playbooks.

---

## Phase 5 — Observability and runbooks (Week 2–3)

### 5.1 Dashboards

Per service: SLI vs SLO line, budget remaining, burn rate (fast and slow), volume, latency percentiles, error rate by status, saturation, JVM, dependency latency, freshness (for the projection services).

**Deliverable 16 — Dashboards** with the documented reading order (the on-call's first 60 seconds).

### 5.2 Logs and traces

Structured logs with `trace_id`/`request_id`; sampling policy; PII scrubbing (note: `document-store` handles identity documents — this is a compliance-relevant area).

**Deliverable 17 — Logging and tracing evidence**, including the scrubbing test over a captured sample for the document service.

### 5.3 Alerts

Burn-rate alerts per SLO, saturation alerts, freshness-lag alerts, DLT/lag alerts for Kafka consumers, and the alert→runbook pairing. Delete the CPU alerts that have never caused an action.

**Deliverable 18 — Alert pack**, with the measured pages-per-shift before and after, and the alert→runbook coverage table.

### 5.4 Runbooks

One runbook per paging alert for the 5 services. **Test each with an engineer who did not write it**, time the walkthrough, and record every defect.

**Deliverable 19 — Runbooks** with the timed walkthrough results and the defect list, all fixed.

---

## Phase 6 — Data and recovery (Week 3)

### 6.1 Restore tests

`document-store`: restore the PostgreSQL index *and* verify that the object-store objects referenced by it are present and readable. This is the launch's single largest expected-loss item.

`catalog-sync`, `notification-dispatch`: restore the database into a clean instance and time it.

**Deliverable 20 — Restore test report** with measured RTO and RPO for each service, versus the stated objectives, and the remediation where they fall short.

### 6.2 Retention and personal data

`document-store` handles identity documents. Define retention per class, the erasure path across all surfaces (object store, index, cache, search, logs, backups), and the propagation arithmetic.

**Deliverable 21 — Retention and erasure plan** with per-surface propagation and coverage arithmetic.

### 6.3 Kafka retention and lag

Verify that Kafka retention for the search-indexer's topic exceeds the maximum tolerable projection outage, and set the lag alerts accordingly.

**Deliverable 22 — Retention verification** with the arithmetic and the lag alert thresholds.

---

## Phase 7 — The launch-week runbook and gates (Week 3–4)

### 7.1 Launch gates

Automated checks that block a production deploy without evidence:

```bash
# check-launch-gate.sh <service>
fail=0
grep -q 'availability:' slo.yaml || { echo "FAIL: no availability SLO"; fail=1; }
grep -q 'BurnFast' alerts.yaml || { echo "FAIL: no burn-rate alert"; fail=1; }
python3 prr_check.py "$SERVICE" || { echo "FAIL: readiness record has open failures"; fail=1; }
./check-runbook-exercise.sh "$SERVICE" || { echo "FAIL: a paging alert has no exercised runbook"; fail=1; }
./check-migrations.sh db/migration || { echo "FAIL: unsafe migration"; fail=1; }
grep -q 'last_exercised:' "rollback-drill/$SERVICE.md" || { echo "FAIL: no rollback drill"; fail=1; }
exit $fail
```

**Deliverable 23 — Launch gates** with each of the six checks blocking a deliberately non-compliant release with a specific message.

### 7.2 Launch-week plan

A minute-by-minute plan for launch day: capacity already scaled, canary steps with decision points, the rollback command (or the fix-forward playbook), the kill switches, the communication plan, the abort criteria, and the named decision-maker at each step.

**Deliverable 24 — Launch-week runbook**, reviewed with the on-call and the product owner.

### 7.3 Game day

Run the launch-day scenario in staging: a canary regression, a dependency failure, and a rollback drill — with the on-call in business hours, measuring detection and diagnosis times.

**Deliverable 25 — Game day report** with the timings and the defects found.

---

## Phase 8 — Decide and communicate (Week 4)

### 8.1 The readiness verdict

```
| Area | Items | Pass | Fail | Accepted risk |
|---|---|---|---|---|
| SLIs & SLOs | 20 | 20 | 0 | 0 |
| Capacity | 35 | 30 | 5 | 2 |
| Startup & shutdown | 15 | 15 | 0 | 0 |
| Dependencies & failure modes | 75 | 62 | 13 | 3 |
| Observability & alerting | 40 | 34 | 6 | 1 |
| Runbooks & on-call | 25 | 20 | 5 | 1 |
| Deployment & rollback | 30 | 24 | 6 | 2 |
| Data & recovery | 25 | 18 | 7 | 3 |
```

A verdict with a date, the blocking items, the accepted risks with owners and expiries, and the conditions under which you would say no.

**Deliverable 26 — Readiness verdict** — go / conditional go / no-go, with the evidence and the conditions.

### 8.2 The business memo

One page to the product owner and the CTO: are we ready for 40,000 sellers in launch week? What is the capacity plan and its cost? What is the single largest expected-loss item? What are we accepting, and until when? What happens if we launch a week late?

Include the "do nothing" option (launch without this work) priced honestly, so the choice is real.

**Deliverable 27 — Business memo** with an explicit ask and a confidence range.

### 8.3 Institutionalize

- The readiness review becomes a required gate in the launch process (Section 7.1), automated rather than ceremonial.
- The SLO spec is a required artifact for every new service.
- The runbook-exercise requirement is enforced by the alert pack.
- The review is repeated on material change and every 6 months, with a drift tracker per service.
- The platform templates ship the SLO stub, the burn-rate alert templates, the drain calculation, and the launch gate script.

**Deliverable 28 — Institutionalization package**: templates, gate script, drift tracker, and the review cadence.

---

## Phase 8 metrics — what leadership will see

| Metric | Before | After |
|---|---|---|
| Services with SLOs and error budgets | 0 / 5 | 5 / 5 |
| Services with a measured capacity model | 0 / 5 | 5 / 5 |
| Services surviving N+1 at launch-week load | 0 / 5 | 5 / 5 (2 via accepted risk with expiry) |
| Startup probes configured | 0 / 5 | 5 / 5 |
| Grace periods derived and verified with 0 5xx | 0 / 5 | 5 / 5 |
| Failure modes enumerated / tested | 0 / 60 | 60 / 18 |
| Burn-rate alerts | 0 | 12 |
| Pages per on-call shift | 14 | ≤ 3 actionable |
| Runbooks exercised by a second person | 0 / 5 | 5 / 5 |
| Measured RTO/RPO vs stated | unknown | measured for 5 / 5 |
| Services with a verified rollback or fix-forward playbook | 1 / 5 | 5 / 5 |
| Migration lock risks in the launch path | 3 | 0 |
| Expected annual loss from readiness gaps | $296,300 (typical PRR finding) | ~$38,000 |
| Launch verdict | unknown | conditional go, with conditions and dates |

**Deliverable 29 — Final summary**: the metrics table, the accepted-risk register, and the conditions for the launch.

---

## Deliverables checklist

- [ ] Phase 1 SLO specs with budgets, release policy, detectability audit.
- [ ] Phase 2 load tests, capacity plan (including launch-week), dependency budget, HPA configuration.
- [ ] Phase 3 startup/shutdown evidence, rollout configuration.
- [ ] Phase 4 failure-mode inventory, 15+ injections, migration remediation, rollback availability register.
- [ ] Phase 5 dashboards, logging/tracing evidence, alert pack, exercised runbooks.
- [ ] Phase 6 restore tests, retention/erasure plan, Kafka retention verification.
- [ ] Phase 7 launch gates, launch-week runbook, game day.
- [ ] Phase 8 readiness verdict, business memo, institutionalization, metrics summary.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| SLOs | "99.9% uptime" | Four dimensions, explicit exclusions, event floors, budgets, and a rationality check on the freshness objective |
| Detectability | "We have alerts" | Measured lead times per SLO against two replayed incident shapes |
| Capacity | "It should scale" | Production-shaped load tests, knee, N+1 requirement, launch-week forecast, dependency budget at HPA max |
| Lifecycle | "It starts and stops" | Cold-start measurement, drain arithmetic, three rollout-under-load runs with zero 5xx |
| Failure modes | "We tested failover" | 60 enumerated, 18 executed with pass conditions, every failure tracked with a re-run |
| Observability | "Grafana is set up" | Reading order, burn-rate alerts, pages-per-shift measured, alert→runbook pairing verified |
| Runbooks | "They exist" | Timed walkthrough by a second engineer, defects fixed, coverage table |
| Recovery | "We have backups" | Measured RTO/RPO including the object-store-plus-index case |
| Launch | "It looks fine" | Automated gates, minute-by-minute launch plan, game day, and a verdict with conditions and dates |
| Communication | "We're ready" | One-page memo with the single largest expected-loss item, the accepted risks, and a priced do-nothing option |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Google SRE Workbook — "Service Level Objectives" and "Implementing SLOs"** — https://sre.google/workbook/service-level-objectives/ and https://sre.google/workbook/implementing-slos/ — the authoritative source for the SLI/SLO/error-budget chain, the guidance on choosing SLIs that reflect *user-visible* behaviour (rather than internal proxies), the treatment of "valid events" and why exclusions must be explicit, and the error-budget-as-release-policy pattern. Use it for Phase 1 and for the SLO rationale; cite it for the framing rather than asserting that these are good practices.
2. **Google SRE Workbook — "Production Readiness Review"** — https://sre.google/sre-book/managing-load/testing-for-failure/ (and the SRE book's readiness-review chapter) — the canonical description of the PRR as a review that asks *whether the service will work when we deploy it, whether it will behave as expected, and whether we'll be able to diagnose problems when it doesn't* — i.e. the operational, evidence-based framing that this whole lab is built on. Also useful for the launch-readiness framing of a bounded, staged rollout with monitoring between stages. Verify the exact section reference in your edition of the book, since chapter numbering differs between print editions.

Additional anchors worth verifying: your platform's actual Kubernetes defaults that affect readiness — `terminationGracePeriodSeconds` (30 s) and `preStop` semantics — plus the actual drain arithmetic for your ingress/proxy propagation delay, which determines the correct `preStop` sleep in Section 3; whether your S3-like object store supports versioning and cross-region replication, and its own retention/restore semantics, since the Phase 6 restore test depends on it; and your alerting tool's support for multi-window multi-burn-rate expressions (Prometheus/Alertmanager does; verify any commercial tool before relying on it).

---

## Reflection questions

1. Five services have no SLOs and launch is in nine weeks. What is the fastest path to defensible SLOs — perfect, or shipped-and-burned-down?
2. `search-indexer`'s measured peak lag is 6 minutes against a proposed 30-second objective. Is the objective wrong, or is this a capacity gap? How do you tell, and what do you tell the team?
3. `catalog-sync` cannot be rolled back. What is the cost of accepting that through the launch, and what would you need to change to make rollback available?
4. The readiness review found ~$296k/year of expected loss and costs ~$90k to close. Present that to a product owner who wants a launch date. What is the honest argument?
5. Nine weeks is enough time to close most of the gaps. Which ones would you *not* close, and how do you write the accepted risk so that it is a decision rather than an excuse?
