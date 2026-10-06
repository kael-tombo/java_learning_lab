# Availability - REAL WORLD PROJECT

## Project: Multi-Region Payments Platform with Game-Day Failover

**Time**: 3-5 days (team of 2-3)

**Scenario**: You operate the authorisation layer for a payments processor.
It is a 6-dependency synchronous path. The current stated availability is
"about five nines, probably", which is not a number anyone can defend.

### Target SLOs

| Tier | SLI | SLO | RTO | RPO |
|------|-----|-----|-----|-----|
| Auth (tier 1) | successful non-3xx authorisations | 99.95% | 30 s | 0 (sync replica) |
| Ledger (tier 1) | committed entries / submitted | 99.99% | 5 min | 0 |
| Fraud scoring (tier 2) | scored within 200 ms | 99.5% | 60 s | 0 |
| Dashboards (tier 3) | served | 99.0% | 15 min | 5 min |

### Step 1: Build the Dependency Graph and Do the Arithmetic

```
Client -> Edge/WAF -> API Gateway -> Auth Service -> Fraud Engine -> Acquirer
                                  |         |              |           |
                              Redis     Postgres       Redis      External
                              (cache)   (primary+2 rpl) (session)  (PSP API)
```

Compute availability top-down. Record every hop, its measured MTBF and MTTR,
and its contribution to end-to-end downtime. Present a Pareto chart: which
three hops account for 80% of the risk? The answer is usually the external PSP
API and the primary DB failover — not your own code.

### Step 2: Eliminate Single Points of Failure

- Run primary and sync replica across **availability zones**, not just hosts.
- Replace the per-AZ Redis with a cluster sized so one shard loss is a
  cache-miss event, not an outage.
- Put a regional failover in front: `us-east` primary, `us-west` warm standby,
  single region-level DNS/route change for RTO.
- Remove the hard-coded PSP call from the critical path — make the authorise
  step a *record* plus async enrichment, with the acquirer call moved behind a
  circuit breaker.

### Step 3: Implement Detection That Actually Detects

- Liveness: is the process alive? (shallow, used only to restart)
- Readiness: can this instance serve *this* endpoint with its current
  dependencies? (deep, per-dependency, with a cached 2 s result so probes
  cannot themselves DDoS a slow DB)
- Synthetic: a money-movement canary that runs every 60 s end to end.
- Alert on symptom, not cause: page on auth success-rate burn rate, not on
  "CPU > 80%".

### Step 4: Isolate the Cascade

- Per-dependency circuit breakers with distinct thresholds (Fraud opens at
  50% errors; PSP opens at 30% because it is unrecoverable).
- **Bulkheads**: separate thread pools and connection pools per PSP so one
  slow acquirer cannot starve the fast domestic path.
- Aggressive, *asymmetric* timeouts: 120 ms connect, 400 ms total for fraud;
  generous for the ledger write. A deadline propagated from the gateway stops
  downstream work that nobody is waiting for.
- Load shedding: when the breaker is open, return a fast, honest
  `503 Retry-After` instead of holding connections.

### Step 5: Prove the Failover (the actual deliverable)

Run three game days and write up each:

1. **Kill a zone** during peak. Measure detection time, failover time,
   post-failover p99, and whether the error rate doubled.
2. **Make Redis cold** (flush). Measure database QPS spike, whether the cache
   stampede protection held, and time to recovery.
3. **Slow the PSP to 8 s** (not down — slow is worse than down). Verify the
   bulkhead held and domestic traffic was unaffected.

For each, produce a timeline: `t+0` symptom, `t+N` page, `t+M` mitigated.

### Step 6: Error Budget and Release Policy

```
Error budget (99.95%, 30 days) = (1 - 0.9995) x 2592000 s = 1296 s = 21.6 min
burn_rate = observed_error_rate / (1 - SLO)
  page at 14.4x over 1 h + 5 m burn    (fast burn: ~43 min of budget left)
  page at 6x over 6 h + 30 m burn     (slow burn:  ~4 h of budget left)
```

Wire a budget burn-rate dashboard. Freeze non-reliable releases when the
budget for the quarter is exhausted, and write the policy down so it is a
process rule rather than a personality clash.

### Deliverables

1. Dependency graph with per-hop MTBF/MTTR and a risk Pareto chart.
2. SLO/SLI/RTO/RPO table plus the derived error budget and burn-rate policy.
3. Circuit breaker + bulkhead + deadline-propagation implementation with tests.
4. Three game-day runbooks with measured timelines (not aspirational ones).
5. Load-shedding and `Retry-After` contract documented for clients.
6. Post-mortem for each game day, including the metrics you wish you had.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Arithmetic | Hand-waved "high availability" | Per-hop numbers, Pareto-driven |
| Detection | CPU alerts | Symptom alerts with burn rate |
| Isolation | One shared thread pool | Real bulkheads, per-dependency breakers |
| Failover | "DNS switch" | Measured RTO, flapping analysis |
| Write-up | One page | Timelines, evidence, changed runbook |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- AWS Well-Architected Framework — Reliability pillar guidance on redundancy,
  quotas, and failure-mode analysis.
  https://aws.amazon.com/architecture/framework/
- Kubernetes documentation — pod replicas, readiness/liveness probes, and
  disruption budgets (the canonical `N+2` / no-single-point primitives).
  https://kubernetes.io/docs/concepts/architecture/

Both are living documents. Re-read the reliability/quota sections before
quoting figures, and cite the specific page section rather than the pillar root.