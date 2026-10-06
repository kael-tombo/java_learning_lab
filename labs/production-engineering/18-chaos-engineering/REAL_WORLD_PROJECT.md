# Lab 18: Chaos Engineering & Fault Injection — Real World Project

## Scenario: "We Believed We Were Resilient"

You are a reliability engineer at a payments platform: 16 Spring Boot 3 services, Java 21, Kubernetes (multi-AZ), PostgreSQL 15 primary + 2 read replicas, Redis, Kafka, and a team that spent two quarters building what they described as a resilient architecture.

**What you inherit** — a confident claim, with these components:

1. Circuit breakers (Resilience4j) on four of the eleven dependency edges.
2. Timeouts on every outbound HTTP call.
3. Kubernetes replicas spread across three availability zones with PDBs.
4. Kafka consumers with at-least-once delivery and idempotent handlers.
5. A Redis cache with a 60 s TTL.
6. Multi-AZ database replication with automated failover.
7. A runbook per service, written when the services were created, eighteen months ago.

**The situation** — Two recent incidents expose the gap, and both were failures of an *untested assumption*:

- **Incident A (6 weeks ago)** — A 40-second database failover took checkout offline for 4 minutes 10 seconds. The team believed the application would survive a failover with "connection retries and the pool's maxLifetime". Nobody had ever failed over the primary. The pool did not recover: connections established to the old primary were handed out from the pool as "valid" until they failed, and the pool's own retry budget was exhausted in 11 seconds.
- **Incident B (3 weeks ago)** — A Redis failover caused a 25-minute degradation. Nobody had considered that the Caffeine L1 caches (30-minute TTL, no jitter) would all expire within a 30-minute window *after* the failover, sending a synchronised 20× miss storm to Redis, whose CPU then hit 95%. The architecture had a cache; it did not have a cache *strategy*.

**Your job over 4 weeks**: find the untested assumptions before production finds them. Build a chaos programme with the controls that make it safe, run the experiments that matter, run GameDays that test the human system, and produce a coverage metric plus a tracked action list.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Inventory the assumptions (Day 1–4)

### 1.1 Failure-mode inventory

For all 16 services: every dependency, every datastore, every resource limit, every lifecycle event (deploy, cert expiry, failover, scaling, config change), plus network shapes, clocks, and data. Enumerate the failure modes — target 60+ across the platform.

**Deliverable 1 — Failure-mode inventory** with, for each mode: what you believe happens, what evidence supports that belief, and whether it has ever been tested.

### 1.2 Rank by expected blast radius

```
expected_damage = P(failure) × affected_fraction × users × cost_per_user × duration
```

Rank the top 15 by expected damage.

**Deliverable 2 — Ranked inventory** with the arithmetic, so the experiments are chosen by expected value rather than by what is fun to break.

### 1.3 Reconstruct the two incidents

For Incident A: the pool recovery mechanism, the timeline, the retry budget exhaustion, and what a 40-second failover does to an unvalidated connection pool.

For Incident B: the Caffeine expiry arithmetic across the pod fleet, the Redis CPU saturation, and the TTL jitter gap.

**Deliverable 3 — Causal analyses** with the arithmetic for both, and the specific untested assumption named in each.

### 1.4 Check the observability precondition

For each planned experiment, verify that a metric exists that would *detect* the fault. Compute the detection probability from the signal-to-noise ratio of that metric.

**Deliverable 4 — Detectability audit**: which failure modes are invisible with current instrumentation, and what needs to be added before those experiments can run.

---

## Phase 2 — Build the controls (Day 4–8)

### 2.1 Experiment harness

A runner with: a hypothesis field, a pass condition, a steady-state precondition assertion (10–15 minutes of guarded SLI), a machine-evaluated abort using a short aggregation window, a guaranteed restore on a timer *and* on any signal, a steady-state verification after restore, and a fault-applied evidence metric.

**Deliverable 5 — Harness** with the abort *tested*: inject a controlled regression and verify the abort fires within its window and the restore completes.

### 2.2 Staging environment of production shape

Three AZs, the same instance types, the same database topology (including a primary and standbys), Redis with a sentinel-managed failover, Kafka with three brokers, and production-shaped data volumes. Otherwise staging experiments prove nothing about production-only properties.

**Deliverable 6 — Staging environment** with the topology and the known differences documented.

### 2.3 Injection tooling

Toxiproxy for network faults (latency, jitter, reset, bandwidth) at the boundary; a CPU burner or cgroup limiter for resource faults; a deliberate defect toggle for deployment experiments; a scriptable Postgres proxy or a fault-injecting proxy for datastore faults; CM4SB or Resilience4j decoration for in-code business-path faults.

**Deliverable 7 — Tooling** with each injection type labelled as boundary or in-code, and an inverse operation documented for every one.

### 2.4 Approval and abort policy

Production chaos requires: a named experiment owner, a written hypothesis, the blast radius, the abort threshold, a business sign-off, dashboards open during the run, and a kill switch anyone can invoke. Document it; it is what makes the experiments approvable.

**Deliverable 8 — Policy document** plus the kill-switch implementation and its test.

---

## Phase 3 — Run the experiments (Week 2)

Prioritised by Phase 1.2, minimum 12 experiments:

| # | Injection | Hypothesis to test |
|---|---|---|
| X1 | 40-second Postgres primary failover (the real incident) | Connection pool recovers within 60 s without manual intervention |
| X2 | Postgres primary failover + load | p99 stays within SLO; no connection storm on the new primary |
| X3 | Redis failover | Cache-miss storm is bounded (jitter present) and Redis CPU stays < 60% |
| X4 | `checkout-api` 3 s dependency latency | p99 stays under the budget; concurrency amplification is bounded |
| X5 | `checkout-api` 8 s dependency latency | Bulkhead sheds; good-path p99 degrades < 15% |
| X6 | `psp-stub` unavailable | Circuit breaker opens within target; fallback is correct |
| X7 | `psp-stub` 400 ms latency | Retry rate stays within the 10% budget |
| X8 | Kafka broker loss (1 of 3) | Consumer lag blips and recovers; no order loss |
| X9 | Pod killed mid-request under load | No in-flight order lost; graceful shutdown works |
| X10 | Node drained during peak | PDB respected; capacity survives; no 502s |
| X11 | Memory pressure: node at 95% | Guaranteed-QoS pods are evicted last; payment path survives |
| X12 | Certificate expiry on an internal dependency | Predicted by an alert, or discovered at expiry? |
| X13 | A zone's network degraded (200 ms extra RTT) | Cross-AZ assumptions hold or the topology is wrong |
| X14 | Clock skew on one node (30 s fast) | Token expiry and cache TTL logic survive |

For each: hypothesis, steady-state window, radius, injected values, fault-applied evidence, before/during/after metrics, abort behaviour, undo time, and pass/fail.

**Deliverable 9 — Experiment report** with all 14, plus the experiment registry.

---

## Phase 4 — GameDays (Week 2–3)

Two GameDays with the on-call, in business hours, with coordination:

**GameDay 1 — Database failure story**
| Time | Event |
|---|---|
| 09:00 | Inject 3 s latency on the database's read path |
| 09:25 | Real failover of the primary (scheduled maintenance window, chaos-mixed) |
| 09:50 | Inject `psp-stub` unavailable |
| 10:15 | All cleared |

**GameDay 2 — Deployment story**
| Time | Event |
|---|---|
| 14:00 | Inject Kafka lag by slowing a consumer |
| 14:30 | Deploy a version with a deliberate 5% error rate |
| 14:50 | Revoke the responder's cluster-admin access |
| 15:15 | All cleared |

Measure per injection: time to detect, time to declare, time to first correct hypothesis, whether the runbook worked, every point a human was blocked, and every incorrect hypothesis that was formed and later corrected.

**Deliverable 10 — GameDay reports** with the human-system timings and the defect list (runbook commands that no longer exist, dashboards behind a VPN, escalation paths to people who have left, alerts routed to nobody).

---

## Phase 5 — Act on the findings (Week 3)

For every failure: a tracked action with an owner, a date, a definition of done, and a **scheduled re-run** of the experiment that found it. Specific ones already visible from Phase 1.3:

- Connection pool: validate connections on borrow (`connection-test-query`), set `maxLifetime` below the database's idle-kill, cap retries, and add pool-recovery alerts.
- Caffeine caches: add TTL jitter and a refresh-ahead policy everywhere; add a cache-miss-rate alert with a saturation threshold.
- Circuit breakers: review every edge for window/threshold suitability (the Lab 18 E3 finding pattern — a 60 s window cannot meet a 30 s open target).
- Retry policies: enforce a global retry budget and alert when any client exceeds it.

**Deliverable 11 — Action tracker** with re-run schedule per action, and the first re-run results for the two incident-class fixes (database failover, cache stampede).

---

## Phase 6 — Production experiments (Week 3–4)

Only after staging validation. Candidates chosen because they concern production-only properties:

| Experiment | Radius | Why production only |
|---|---|---|
| Real database failover (during a maintenance window) | whole platform, but planned | The staging failover is not the production one |
| Regional/AZ latency increase | 1 AZ only | Production network path is unique |
| Pod kill in a real AZ | 1 pod | Verifies production graceful shutdown |
| Certificate rotation on a live certificate | 1 dependency | Real cert infrastructure |

Each with: written hypothesis, radius, abort threshold, business sign-off, dashboards open, kill switch, and a post-experiment report.

**Deliverable 12 — Production experiment reports** with the approval path, the measured result, and the residual risk.

---

## Phase 7 — Make it a programme (Week 4)

- **Experiment registry**: searchable, with hypotheses, results, and the finding-to-action links.
- **Coverage metric**: distinct failure modes with a *passing* experiment divided by declared failure modes — tracked per quarter, with a target.
- **Cadence**: two experiments per week per team, permanently. Consistency, not intensity.
- **Detector rule**: chaos is blocked from running if the previous experiment's finding is unresolved. This is the mechanism that turns chaos into improvement rather than entertainment.
- **New-service requirement**: a new service's failure modes must be enumerated before launch, and its top three experiments must run before it handles production traffic.
- **GameDay cadence**: one per quarter, scheduled in business hours, with the on-call.

**Deliverable 13 — Programme design** with the registry, the coverage metric and its trajectory, the cadence, the detector rule, and the launch requirement.

---

## Phase 8 — Quantify and institutionalize (Week 4)

| Metric | Before | After |
|---|---|---|
| Failure modes with a tested behaviour | unknown; 0 formally | 14 tested, ~45 assessed |
| Chaos coverage (passing experiments / declared modes) | 0% | 23% in the first month |
| Incidents caused by untested assumptions (12 mo) | 6 | target < 1 |
| Recurrence of "DB failover" class | 2 in 12 mo | 0 after the re-run |
| Recurrence of "cache stampede" class | 2 in 12 mo | 0 after the re-run |
| GameDays per quarter | 0 | ≥ 1, scheduled |
| Findings turned into tracked actions | n/a | 100% |
| Findings with a verification re-run | n/a | 100% |
| Mean time to detect (from experiments) | not measured | measured per experiment class |
| Circuit breakers meeting their open targets | 2 of 11 edges | all edges verified |
| Retry budget violations | unknown | 0, enforced and alerted |
| Confidence in the resilience architecture | assumed | measured |

Present the numbers with an honest caveat: chaos reduces the probability of *unknown* failures; it does not eliminate them, and the coverage percentage is the honest statement of what you do not know.

**Deliverable 14 — Business case + institutionalization**, including the two incidents' cost against the programme cost, and the explicit list of failure modes still untested.

---

## Deliverables checklist

- [ ] Phase 1 failure-mode inventory, ranked with arithmetic, two causal analyses, detectability audit.
- [ ] Phase 2 harness with tested abort, production-shaped staging, injection tooling, approval/abort policy.
- [ ] Phase 3 fourteen experiments with hypotheses and pass conditions.
- [ ] Phase 4 two GameDays with human-system timings and the defect list.
- [ ] Phase 5 action tracker with verification re-runs.
- [ ] Phase 6 production experiments with the approval path.
- [ ] Phase 7 programme design with the registry and coverage metric.
- [ ] Phase 8 before/after business case with the untested-modes list.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Inventory | "We should test failover" | 60+ enumerated modes, ranked by expected damage with arithmetic |
| Diagnosis | "The failover broke us" | Pool recovery mechanism, retry budget exhaustion, expiry arithmetic across the fleet |
| Precondition | "It was healthy" | Detectability audit: which modes are invisible with current metrics, and the fix |
| Harness | "We ran a chaos tool" | Hypothesis, pass condition, automated precondition, machine abort on a short window, trap-based restore, fault evidence |
| Experiments | "We tested latency" | 14 experiments, ranked, with pass/fail including the null results and what nulls prove |
| GameDays | "We did a drill" | Coordinated scenarios, measured human-system timings, non-technical defects found and tracked |
| Actions | "We fixed the pool" | Every finding → action with owner, date, definition of done, and a verification re-run |
| Production | "We tested in prod carefully" | Written approval path, 1 AZ/pod radius, tested kill switch, residual risk stated |
| Programme | "We run chaos" | Registry, coverage metric with trajectory, detector rule, new-service launch requirement |
| Honesty | "We are now resilient" | Explicit list of untested modes; chaos reduces unknowns, it does not eliminate them |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Principles of Chaos Engineering** — https://principlesofchaos.org/ — the canonical statement of the method: understand the steady state, hypothesize behaviour under turbulence, try to *disprove* the hypothesis (verification, not observation), and establish new hypotheses. Also the definition of the steady state as "a normal, active functioning of the system... sufficiently metriced", which is the justification for the detectability audit in Phase 1.4. Use it to anchor the "verify, don't observe" framing, and cite the principles rather than asserting that chaos finds bugs.
2. **Google SRE Workbook — "Managing Incidents" and "Postmortem Culture"** — https://sre.google/workbook/managing-incidents/ and https://sre.google/workbook/postmortem-culture/ — the authoritative source for the argument that chaos findings should be handled through the incident process (command, timeline, postmortem) rather than fixed in the moment, because that is where the organisational learning comes from. Also the basis for the GameDay framing as an exercise in the human system, and for the blameless-but-accountable action-item discipline that the findings tracker in Phase 5 must satisfy.

Additional anchors worth verifying: Toxiproxy's toxic types and their semantics (latency/jitter/bandwidth/`timeout`/`reset_peer`/`slicer`), and whether it can be run per-listener with programmatic creation (it can — this is what makes hypothesis-driven experiments scriptable); Resilience4j's circuit-breaker window/threshold/slow-call configuration and its sliding versus count-based windows (the "60 s window cannot meet a 30 s open target" finding in Phase 5 depends on which window type you configure); HikariCP's `connectionTestQuery`/`aliveBypassWindow`/`maxLifetime` semantics for your version, since the Incident A pool-recovery fix depends on exactly those behaviours; and your Kubernetes version's behaviour for `NotReady` node pod eviction timing and PDB interaction with node drains.

---

## Reflection questions

1. The team built breakers, timeouts, PDBs, and idempotent consumers and still lost 4 minutes to a database failover. Which specific assumption was never tested, and what does that tell you about the value of "having" a resilience component versus "knowing it works"?
2. The cache stampede was a Lab 12 problem (un-jittered TTLs) reappearing inside a chaos incident. How would you detect that class of bug before it causes an incident, and where does it belong in your standard?
3. Chaos coverage is 23% after the first month. Which untested modes worry you most, and would you run a production experiment for any of them?
4. The detector rule (block chaos if the previous finding is unresolved) sounds restrictive. What happens to the programme if teams start closing findings quickly to unblock it, and how would you detect that?
5. If chaos prevents incidents by proving behaviour, and monitoring detects them faster, which one should get the next month of investment? Defend it with the numbers.
