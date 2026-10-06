# Microservices - REAL WORLD PROJECT

## Project: Decomposing a Monolith into 8 Services Without an Outage

**Time**: 4-6 weeks (team of 5)

**Scenario**: A 4-year-old e-commerce monolith. 50 engineers, 8-minute
builds, a deploy every two weeks, change failure rate 22%, and a team of 60
engineers blocked behind each other. 400k orders/day at peak. Requirements:

- **No outage and no downtime maintenance window.** Every step is reversible.
- No change in customer-visible behaviour or data semantics.
- Deploy frequency must rise without the change failure rate rising with it.

### Step 1: Establish the Baseline Before Changing Anything

Measure first, or you cannot prove improvement:

| Metric | Baseline |
|--------|----------|
| Deploy frequency | 0.5/week (release train) |
| Change failure rate | 22% |
| Mean time to restore | 4 hours |
| Lead time for a change | 11 days |
| p99 checkout latency | 1,900 ms |
| Services in the incident path | 1 (everything) |

Also sample **20 recent changes** and count how many touched each module. This
becomes the decomposition's first evidence: the modules that change together
are candidates for the *same* service, and the modules that never change
together are candidates for *different* services.

**Deliverable:** the baseline table plus the change-coupling matrix. Every later
claim in this project is measured against these numbers.

### Step 2: Decomposition by Business Capability

Eight services, each with its own database, each owned by a team of 6-8:

```
catalog       product info, pricing, categories
inventory     stock levels, reservations
cart          shopping carts
order         order lifecycle state machine
payment       authorisations, captures, refunds
fulfilment    shipping, labels, tracking
customer      accounts, addresses, preferences
search        search index + query
```

Rules enforced in code review and CI:
- No cross-service table reads. Enforce with a CI check that greps for foreign
  schema references and fails the build.
- Every cross-service data need is satisfied by an **event-driven projection**
  or a **sync API call**, and the choice is justified per case.
- Every sync dependency has an explicit timeout, a breaker, and a bulkhead.

**Deliverable:** the boundary document with, per boundary, the reason it exists,
the change-coupling evidence, and the data-copy strategy.

### Step 3: Data Migration with a Verification Window

Migrate in dependency order, hardest data last. Per capability:

```
1. IDENTIFY the writer        (app code? trigger? ETL? report job?)
2. EXTRACT schema             to the new service's database
3. DUAL WRITE                 monolith writes both
4. BACKFILL                   in batches, resumable from a checkpoint
5. VERIFY                     continuous diff, alerted (not a script)
6. SWITCH reads               new service authoritative
7. DUAL READ window           fallback to monolith, log every fallback
8. SHRINK                     remove from the monolith after one full release
```

The verification step is the discipline. Requirements:
- The diff job is a **first-class alerting component**, with a documented
  runtime and an owner.
- Contract phase is gated on **access analytics** (no deployed binary
  references the old column), never on a calendar date.
- Every phase is independently reversible, and reversibility is *tested* by
  actually exercising the rollback in staging.

**Deliverable:** per-capability migration timings, diff-job alert history, and a
tested rollback for each phase.

### Step 4: The Cutover Plan for Traffic

- Route traffic by capability at the gateway, with a per-capability kill switch
  that reverts to the monolith within one request.
- **Shadow traffic**: mirror production reads to the new service without
  serving responses, and diff the results. Run this for a minimum of one week
  per capability before switching. Shadow diffs are how you find the rounding
  difference and the missing filter.
- Load-shedding: if the new service degrades, the kill switch routes back to the
  monolith rather than failing customers.

**Required drill:** flip the kill switch during peak traffic and measure how many
requests were served by the monolith versus the service. The switch must be
auditable and leave no partial state.

### Step 5: Latency and Isolation Budgets

Decomposition adds hops. Compute the budget for the new checkout path (6 hops):

```
budget: gateway 20 + order 80 + inventory 60 + payment 90 + fulfilment 40
        + network 5 hops * 2 ms + shaping 20 = ~320 ms
        p99 with tail compounding: budget for 700-900 ms

  target: p95 < 400 ms, p99 < 900 ms
```
Bulkheads sized from measured per-dependency traffic (Little's Law), breakers
tuned per dependency, and deadline propagation so a slow hop does not waste
downstream work.

**Required:** a latency comparison table, monolith vs. service, at p50/p95/p99
with the same traffic shape. If the new path is materially slower, explain and
fix it before proceeding — do not declare victory.

### Step 6: Observability and SLOs

- W3C trace context propagated from the gateway across all 8 services. One
  order's trace must be readable end to end.
- Per-service RED metrics; per-dependency latency and error rate.
- **Per-service SLOs and error budgets**, with the platform SLO derived from
  them. A platform SLO with no per-service budget has no owner when it burns.
- Cardinality control in CI: reject any metric whose label set includes a
  request, user, or order id.
- Distributed alerting: page on the customer's symptom, route the investigation
  by dependency rather than by paging every team.

**Deliverable:** the SLO table, the trace of a sample order, and an alert with a
runbook per symptom.

### Step 7: Failure Drills

1. **One service fully down during peak.** Verify only its capabilities are
   affected, optional dependencies degrade cleanly, and the kill switch works.
   Measure the blast radius precisely — this is the metric that proves isolation.
2. **Slow (not down) service at 3 s.** Verify breakers do not open, bulkheads
   contain it, and healthy traffic is unaffected. This is the failure that
   actually causes outages.
3. **Shared database of a migrated service degraded.** Verify no other service's
   latency is affected — the isolation claim for data ownership.
4. **Mid-migration rollback.** Roll back a capability that has been dual-writing
   for a week. Verify no data loss and no duplicate business effects.
5. **Bad deploy to one service.** Verify rollback is service-scoped and does not
   require reverting others.
6. **Outbox drain failure for 30 minutes.** Verify the business path is
   unaffected and that drain lag alerts before projections go visibly stale.

### Deliverables

1. Baseline metrics table and change-coupling matrix.
2. Boundary document with justification and data strategy per boundary.
3. Per-capability migration record with verification-window diffs and a tested
   rollback for every phase.
4. Kill switch with a peak-traffic drill and measured split.
5. Latency comparison, monolith vs. services, at p50/p95/p99.
6. Per-service SLOs, error budgets, and runbooks.
7. Six drill reports with blast-radius measurements.
8. Updated metrics showing deploy frequency, change failure rate, MTTR, and
   lead time — measured, not projected.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Baseline | "It felt slow" | Measured table everything else is judged against |
| Boundaries | Table-per-service | Capability-per-service with coupling evidence |
| Data | Cross-service reads | CI-enforced zero, projection strategy per case |
| Verification | Manual spot checks | Continuous alerted diff with per-phase rollback tested |
| Latency | Declared success | p50/p95/p99 comparison, degradation fixed not excused |
| Isolation | "Services are independent" | Blast radius measured by drill |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Martin Fowler — *Microservices* (with James Lewis): the canonical definition
  — services organised around business capabilities, each owning its data,
  independently deployable, with centralised but different-purpose governance.
  Quote the "business capabilities" and "decentralised data" characteristics
  when arguing a boundary decision.
  https://martinfowler.com/articles/microservices.html
- Kubernetes documentation — Deployment rolling-update strategy and readiness
  probes: the reference for graceful rollout and traffic shifting during the
  strangler phases, including how readiness gates drain connections before an
  old pod is terminated.
  https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

Both are stable references, but re-read the Kubernetes rollout documentation for
the exact behaviour of `maxUnavailable`/`maxSurge` and the handling of
`preStop` hooks in your version — migration cutovers depend on those semantics
precisely, and they have changed across releases.