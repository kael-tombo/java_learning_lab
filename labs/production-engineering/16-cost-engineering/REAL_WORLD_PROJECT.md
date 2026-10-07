# Lab 16: Cost Engineering & Cloud Optimization — Real World Project

## Scenario: "The Bill Doubled and Nobody Knows Why"

You are a platform engineer with a mandate to reduce cloud spend without touching reliability. Context: a subscription SaaS platform, 16 Spring Boot 3 services, Java 21, Kubernetes (managed, request-billed), PostgreSQL, Redis, Kafka, and a growing non-production footprint.

**The situation** — The infrastructure bill has grown from **$86k/month to $171k/month** in five months. Engineering leadership has asked for a plan to get it back under $120k/month within a quarter, with the explicit constraint: "no reliability regression, and the Q4 peak is in seven weeks."

**What you know when you start:**

1. There is no cost attribution. All spend appears against one account. Nobody knows what `catalog-api` costs.
2. There is no baseline. You cannot prove a saving, so any number you produce is a guess.
3. The estates have obvious, unexamined waste: a `legacy-admin` service with 2 replicas running 24/7 for an internal tool four people use; a `reporting-batch` that runs 00:00–04:00 but runs all day; two non-production environments running 24/7 including weekends; `catalog-api` logging full request objects at INFO on 2,000 rps.
4. Pods request 2 vCPU / 4 Gi across the board, from a template. Measured p95 usage across the fleet is roughly 350 mCPU / 1.4 Gi.
5. The HPA minimums are set at 3–6 replicas "to be safe", and the cluster autoscaler removes nodes after 10 minutes of emptiness, so bursty services leave paid-for nodes behind.
6. A release three weeks ago added unbounded retries to a failing notification call. Error-rate metrics are not attributed to cost, so nobody connected them.

**Your job over 4 weeks**: attribute the spend, remove waste, rightsize with evidence, protect the Q4 peak, and produce a number leadership can hold you to — plus the honest list of what you will not cut.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Attribute and baseline (Day 1–4)

### 1.1 Billing export

Pull six months of billing data at every available granularity: account, service, resource type, region, and usage type (on-demand, spot, committed-use, storage class, data transfer). Reconcile the provider's bill against your own arithmetic — discrepancies are normal and finding them is part of the job.

**Deliverable 1 — Billing dataset** with the reconciliation, and the cost breakdown by service (once tagged), region, and resource type.

### 1.2 Add cost allocation tags

Kubernetes labels surfaced into the billing export: `app`, `team`, `env`, `tier`. Backfill tags for anything untagged (14 resources are currently untagged — that is $9k/month nobody owns).

**Deliverable 2 — Tag coverage** at 100%, plus the shared-cost allocation rule (ingress by request count, NAT by egress bytes, log storage by ingested bytes, control plane by pod count) written down and agreed.

### 1.3 Build the baseline

For the last 30 days, per service and per environment: allocated CPU-hours, allocated GiB-hours, actual CPU usage, actual memory usage, log volume, egress bytes, and business volume.

**Deliverable 3 — Baseline** with:
- cost per unit of business volume per service,
- the `actual / requested` ratio per service,
- the waste quantified in vCPU-hours, GiB-months, and dollars under **both** billing models,
- the four obvious waste items quantified separately (legacy-admin, reporting-batch, non-prod, logging).

### 1.4 Explain the doubling

Decompose the 5-month increase: which service, which resource type, which usage-type change (did committed-use expire? did traffic grow? did someone add a region? did a log volume explode?).

**Deliverable 4 — Growth decomposition** with the arithmetic, so the reduction plan addresses the actual cause rather than the symptom.

---

## Phase 2 — Remove waste (no reliability risk) (Day 4–8)

### 2.1 Non-production lifecycle

- Scheduled shutdown nights and weekends; scale-to-zero where the cold start fits; a wake script for developers; a separate node pool using burstable/spot-class instances for what remains running.
- Compute the saving and the developer friction, and handle the friction (wake script, documented policy) rather than accepting it.

**Deliverable 5 — Non-production lifecycle** with the saving, the friction measured, and the policy.

### 2.2 Batch workloads run on a schedule

`reporting-batch` and every other scheduled job: run as a `CronJob` with a bounded resource spec, not as a permanently deployed Deployment. Verify the runtime contract (does it finish inside its window? does a restart resume?) and add idempotency if not.

**Deliverable 6 — Scheduled workloads converted** with the runtime and idempotency verification, and the saving.

### 2.3 Retire what nobody uses

`legacy-admin`: measure actual usage (access logs, last 90 days of requests, active users). If it is 4 internal users, replace it with a read-only dashboard or a scheduled report, then delete the service. Also inventory unattached volumes, orphaned load balancers, forgotten snapshots, and long-dead preview environments.

**Deliverable 7 — Retirement plan** with usage evidence for each candidate, the replacement, and the total saving.

### 2.4 Logging volume

Sample successes (1%), keep 100% of errors and slow requests, templatize URIs (Lab 08), set retention tiers with a lifecycle policy, and cap the payload sent to aggregators.

**Deliverable 8 — Logging cost fix** with measured volume before/after and the dollar figure, plus the secondary benefit (fewer tokens in logs — Lab 09).

### 2.5 The retry amplification

Find the unbounded retry, bound it with a global retry budget, and add the alert that catches it: `retry_attempts / total_requests` per service, and a cost-linked alert when retry volume exceeds 10% of request volume.

**Deliverable 9 — Retry fix** with the measured amplification, the corrected cost, and the alert.

---

## Phase 3 — Rightsize with evidence (Week 2)

### 3.1 Per-service measurement

Fourteen days of per-pod CPU and memory percentiles (p50, p95, p99), plus the JVM's live set and NMT breakdown per service class. Do not rightsize from an average or from a Tuesday.

**Deliverable 10 — Utilisation dataset** with the distribution, not the mean.

### 3.2 Compute the proposal

```
request_cpu  = ceil(p95_cpu × 1.3) to the nearest 50m
request_mem  = ceil(live_set × 1.3 + native_measured) to the nearest 128 Mi
node_recompute = ceil(total_requests / (allocatable × 0.85))
```

Apply it in tiers: Tier 1 (safe, high-confidence services), Tier 2 (mid-size), Tier 3 (latency-critical, one at a time with a load test and a canary).

**Deliverable 11 — Rightsizing proposal** per service with the evidence, the headroom retained, and the node-count recomputation.

### 3.3 Verify under load

For every Tier 2 and Tier 3 service: three-run load test before and after, plus a soak at peak, plus the SLO comparison. If anything regressed, investigate rather than reverting silently — a right-sized service that needs more memory is telling you something about the working set.

**Deliverable 12 — Rightsizing verification** with the per-service before/after throughput, p99, and error rate, and the exceptions explained.

---

## Phase 4 — Instance and commitment strategy (Week 2–3)

### 4.1 Node type and size selection

Map each service to a node size from its *post-rightsizing* request. Consider mixed-instance policies (a baseline of general-purpose with burstable/spot mixed in for non-critical pools) and Graviton-class or other cheaper families where the architecture supports it.

**Deliverable 13 — Instance mix** per pool with the cost table and the compatibility notes.

### 4.2 Spot classification

Classify every workload: batch, CI, non-prod, async consumers, read-heavy stateless services, latency-critical paths, databases. Compute the expected-interruption cost per workload against the discount, and place each accordingly. Diversify the spot pool across families, sizes, and AZs.

**Deliverable 14 — Spot plan** with the classification table and arithmetic, plus the interruption-handling requirements (graceful shutdown, checkpointed offsets, idempotency) verified for each spot workload.

### 4.3 Commitment strategy

Compute the baseline usage (the part that runs 24/7 regardless of traffic) and match commitments to it. Model the risk of over-committing: what does a 30% traffic *drop* do to your effective per-unit cost if you committed to the old baseline?

**Deliverable 15 — Commitment plan** with the baseline calculation, the discount, and the downside case.

---

## Phase 5 — Reduce traffic-shaped costs (Week 3)

- **Egress**: measure per service and per region. Enable compression, conditional GET, and a CDN for cacheable content. Compute the CDN break-even hit ratio before enabling it.
- **Cross-region**: find any traffic that should be intra-region. This is often a misconfigured client default and is both a cost and a latency bug.
- **Ingress**: batch where the workload allows; check whether per-request pricing makes fewer/larger requests cheaper.
- **Inter-cluster/NAT**: consolidate.

**Deliverable 16 — Traffic cost work** with the measured volumes, the fixes, and the before/after dollars, plus the latency effect of each.

---

## Phase 6 — Make it durable (Week 3–4)

### 6.1 Cost observability

- A per-service daily cost dashboard, with a `waste` metric (`allocated − used`) as a first-class series.
- Unit economics: `cost per order`, `cost per 1k API calls`, `cost per GB processed` — with a monthly trend.
- Cost anomaly alerts: daily spend versus the day-of-week baseline per service and per team; per-service budget alerts with a hard threshold and a defined action; an untagged-spend alert.
- Alerts that tie cost to the signals you already have: retry ratio, log volume, replica-hours, idle environments.

**Deliverable 17 — Cost observability stack**: dashboards, unit-economics trend, anomaly alerts, budget alerts.

### 6.2 Guardrails in CI and in the platform

- A lint/sizing check: a new Deployment must declare requests, and its request must be within the measured band for its class.
- A policy: no environment may run 24/7 without an exception.
- A required field for cost-relevant settings: replica min/max, memory request, log level.
- A tag check at admission: no pod runs untagged.

**Deliverable 18 — Guardrails** with the CI check and the admission policy, each blocking a deliberately non-compliant manifest.

---

## Phase 7 — Quantify and communicate (Week 4)

| Metric | Before | After |
|---|---|---|
| Monthly spend | $171,000 | target < $120,000 |
| Cost per 1,000 orders | $X | $Y |
| Untagged spend | $9,000 | $0 |
| Fleet `actual / requested` (CPU) | ~17% | ~60% |
| Fleet `actual / requested` (memory) | ~35% | ~70% |
| Non-prod running hours/week | 168 | ~62 |
| Non-prod spend | $31,000 | $12,000 |
| Log volume/month | 210 TB | 9 TB |
| Logging cost | $26,000 | $1,100 |
| Retry amplification cost | $11,000 | < $1,000 |
| Spot share of non-critical workloads | 0% | 78% |
| Nodes for the same workload | 34 | 21 |
| Cost anomaly detection | monthly invoice | < 4 hours |
| Budget alerts | none | per service + per team |

**Three questions leadership will ask, answered explicitly:**

1. **Can we serve the Q4 peak at this cost?** Yes/no, with the pod and node plan and the headroom.
2. **What did you cut, and what did you refuse to cut?** Refusals: observability, backups, multi-AZ failover, redundancy for the latency-critical path, and the headroom needed for `maxSurge` during rollouts.
3. **How do we know this will not drift back?** The CI sizing check, the admission tag policy, the anomaly alerts, the budget alerts, and the monthly unit-economics review with an owner.

**Deliverable 19 — Business case + committed plan**, with the reduction plan by month, the risk register (including the Q4 peak and the commitment downside), and the review at which it is approved.

---

## Deliverables checklist

- [ ] Phase 1 billing dataset + reconciliation, tag coverage + allocation rule, baseline, growth decomposition.
- [ ] Phase 2 five waste removals with measured savings.
- [ ] Phase 3 utilisation dataset, rightsizing proposal, verification under load.
- [ ] Phase 4 instance mix, spot plan with arithmetic, commitment plan with downside case.
- [ ] Phase 5 traffic cost work with before/after dollars.
- [ ] Phase 6 cost observability stack and guardrails.
- [ ] Phase 7 before/after business case with the explicit plan, refusals, and risk register.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Attribution | "The bill went up" | Six-month dataset, reconciliation, tags at 100%, stated shared-cost allocation rule |
| Diagnosis | "Traffic grew" | Growth decomposed by service, resource type, and usage type; the actual cause named |
| Baseline | "Here's last month's number" | Per-service utilisation *distribution*, live set + NMT, waste quantified under both billing models |
| Waste removal | "Turned off legacy-admin" | Five categories with measured savings and friction handled (not just accepted) |
| Rightsizing | "Lowered requests" | p95-based proposal with headroom, node recomputation, three-run load verification per service |
| Strategy | "Bought reservations" | Spot classification with interruption-cost arithmetic, diversified pool, commitment downside modelled |
| Traffic costs | "Enabled compression" | Measured egress per service, CDN break-even computed, latency effect of each fix |
| Durability | "We documented it" | CI sizing check, admission tag policy, anomaly + budget alerts, monthly unit-economics owner |
| Communication | "We saved $51k" | Explicit answers on peak, refusals, and drift prevention; risk register with the commitment downside |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Kubernetes — `concepts/configuration/manage-resources-containers` and `concepts/scheduling-eviction/node-pressure-eviction`** — https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ — the authoritative source for the request/limit model, QoS classes, and the overcommit implications for eviction ("when a node is under memory pressure, the kubelet evicts pods in a specific order: first those whose requests are the greatest over their usage, then those exceeding requests, by how much"). That eviction-order rule is also the strongest available justification for rightsizing: an over-requested pod is *more* likely to be evicted than a correctly sized one, so waste is also a resilience defect. Verify the current QoS and eviction-order text for your Kubernetes version.
2. **Martin Fowler — "Cost of a Server" / cloud cost architectural patterns** — (link removed) — the reference for the architecture-versus-spend distinction (the choice of *how* to run something often dwarfs the price of *what* you run it on), and for the framing that a cloud bill is a design output rather than a procurement event. Use it to justify why the rightsizing proposal in Phase 3 is a design review item and not a procurement action, and to support the "measure unit economics, not monthly spend" argument.

Additional anchors worth verifying: your provider's actual billing dimensions and rate cards — whether requests or usage is billed for each resource type, the data-transfer matrix (intra-AZ, inter-AZ, inter-region, internet egress), spot interruption notice and pricing-cap semantics, and committed-use/ savings-plan coverage and term structures. These differ materially between providers and change frequently, and the entire spot/right-sizing arithmetic in this lab depends on them. Also verify your cost-allocation tool's tag propagation (whether Kubernetes labels reach the billing export in your provider) and its handling of shared cluster costs (load balancer, NAT, control plane, cluster management fee).

---

## Reflection questions

1. The bill doubled. Which of the six Phase 1.4 causes would you have found first with only the billing export, and which required tags you did not yet have?
2. Your fleet runs at 17% of requested CPU. What are the three other reasons that number matters besides cost?
3. Engineering said "no reliability regression" and you found $31k/month of non-production running 24/7. What is the fastest way to prove that shutting it down does not hurt, and what is the honest answer if it does hurt a little?
4. The fleet is 34 nodes for the same workload at 21. What breaks operationally when node count drops, beyond cost?
5. If you committed to a purchase based on today's baseline and traffic drops 30%, what happens to your per-unit cost, and would you still call the commitment a success?
