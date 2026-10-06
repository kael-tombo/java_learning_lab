# Lab 20: Production Readiness & SLO Engineering — Math Foundation

Production readiness is quantified by budgets, headroom, budgets for time, and drift. The PRR question "can we handle it?" is arithmetic before it is a checklist.

---

## 1. Error budget arithmetic

```
budget_minutes = (1 − SLO) × window_minutes
```

| SLO | / 7 days | / 28 days | / 30 days |
|---|---|---|---|
| 99% | 100.8 min | 6.7 h | 7.2 h |
| 99.5% | 50.4 min | 3.4 h | 3.6 h |
| 99.9% | 10.1 min | 40.3 min | 43.2 min |
| 99.95% | 5.0 min | 20.2 min | 21.6 min |
| 99.99% | 1.0 min | 4.0 min | 4.3 min |
| 99.999% | 6 s | 24 s | 26 s |

Design implication — budget as a share of a single incident:

```
share_of_budget = incident_duration / budget_minutes
```

| SLO | Budget (30 d) | A 30-min incident consumes | A 1-hour outage consumes |
|---|---|---|---|
| 99.9% | 43.2 min | 69% | 139% (budget exhausted) |
| 99.95% | 21.6 min | 139% | 278% |
| 99.99% | 4.3 min | 698% | 1,398% |

**Conclusion**: a 30-minute incident is survivable at 99.9% and fatal at 99.95%+. The SLO must be chosen against the incident size your organisation actually has. Two of these are the same operational reality with different promises.

---

## 2. Burn rate and time to exhaustion

```
burn_rate = (1 − SLI_observed) / (1 − SLO)
time_to_exhaust_days = window_days / burn_rate
```

`SLI = 99.2%` against a 99.9% SLO:
```
burn = 0.008 / 0.001 = 8×  →  30/8 = 3.75 days to exhaustion
```

Burn table for a 30-day window:

| Burn rate | Budget exhausted in | Alert action |
|---|---|---|
| 1× | 30 days | ticket |
| 2× | 15 days | ticket |
| 6× | 5 days | page |
| 10× | 3 days | page |
| 14.4× | 2.08 days | page |
| 30× | 1 day | page |
| 100× | 7.2 hours | page + immediate response |
| 1,000× | 43 minutes | the incident is already happening |

**Conclusion**: the difference between "we noticed at 99.2%" and "we noticed at 95%" is 3.75 days versus 9 minutes. That is the entire value of a fast burn-rate alert, and it is why the abort window in a canary and the alert window in production should be minutes, not tens of minutes.

---

## 3. Error-budget policy and release risk

```
remaining_budget_pct = (allowed − consumed) / allowed × 100
```

Policy: `> 50%` ship freely; `25–50%` canary-only; `< 25%` freeze non-essential changes.

Worked: 99.9% SLO, 30-day window. After a 20-minute outage and one 8-minute degradation:
```
consumed = 28 min / 43.2 = 65%   →  remaining 35%  →  canary-only
```
At `remaining = 25%`, consumed `32.4 min`, i.e. a further **4.4 minutes** of degradation forces a release freeze for the rest of the window.

Practical consequence for planning: a single incident typically consumes 50–70% of a three-nines budget, so the freeze applies after essentially every incident. Teams should therefore treat "canary-only" as the normal steady state after an incident, not as an alarm.

---

## 4. Capacity and headroom that survives failure

```
safe_rps_per_pod = cores_per_pod × U_target / cpu_per_request_ms × 1000
nodes_required    = ceil( peak_rps / (safe_rps_per_pod × pods_per_node) )
surviving_capacity = nodes_required × safe_rps_per_pod × pods_per_node × (1 − 1/nodes)
```

`peak_rps = 9,000`, `4 cores/pod`, `U = 0.65`, `cpu_per_request = 4 ms`:
```
safe_rps_per_pod = 4 × 0.65 / 0.004 = 650 rps
nodes (8 pods/node) = ceil(9,000 / (650 × 8)) = 2 nodes
surviving with 1 node lost = 1 × 650 × 8 = 5,200 rps  →  58% of peak   ✗
```

Now solve for the node count that survives N+1:
```
nodes × (n−1)/n × 5,200 ≥ 9,000
nodes ≥ 9,000 / (5,200 × (n−1)/n)
n = 3:  nodes ≥ 9,000/3,467 = 2.60 → 3 nodes   (surviving = 6,933 → 77%, still short)
n = 4:  nodes ≥ 9,000/3,900 = 2.31 → 3 nodes   (surviving = 5,850 → 65% ✗)
n = 4 nodes, 3 remaining: 3 × 5,200 = 15,600 ≥ 9,000 ✓
```
**Final requirement: 4 nodes for a 9,000 rps peak.** Sizing for peak alone would have said 2 — a design that cannot survive losing a node, and therefore converts any node event into an outage.

---

## 5. Startup and shutdown budgets

```
drain_time     = max( in_flight / throughput , p99.9_request_time )
grace_needed   = preStop_sleep + drain_time + slack
```

`in_flight = 400`, `throughput = 300/s`, `p99.9 = 12 s`, `preStop = 10 s`:
```
drain  = max(1.33, 12) = 12 s
grace  = 10 + 12 + 5 = 27 s  →  set 45 s (the K8s default 30 s is too short)
```
Default `terminationGracePeriodSeconds: 30` with a `p99.9` of 25 s (one slow dependency path):
```
drain = 25 s  →  25 + 10 + 5 = 40 s > 30 s default  →  requests cut every deploy
```

Startup:
```
startup_budget = 2 × slowest_observed_cold_start
observed worst = 75 s  →  startup probe budget 150 s  (30 × periodSeconds 5)
```
Cost of warm-up pods competing for capacity during a rollout:
```
maxSurge_pods × cpu_per_request_warmup
1 pod at 2 cores with 75 s of JIT = 150 core-seconds of work taken from serving pods
```
On a 4-node, 8-cores-each cluster with 650 rps/pod:
```
warm-up cost ≈ 1 pod for 75 s at peak = 650 × 75/60 = 812 requests of reduced capacity
```
**Conclusion**: warm-up is part of the capacity plan on every rollout, and it is why `maxSurge: 1` must be verified against the memory budget too.

---

## 6. Rollout availability

```
available_pods = replicas − maxUnavailable
peak_pods      = replicas + maxSurge
```

`replicas = 24`, `maxUnavailable = 0`, `maxSurge = 1`:
```
available at all times = 24  (100%)
peak pods = 25  →  +4.2% capacity demand, plus one pod of JIT warm-up
```
With `maxUnavailable = 3`, `maxSurge = 3`:
```
available = 21 (87.5%)  →  12.5% capacity reduction for the rollout duration
at peak this means the surviving capacity must still cover peak:
21/24 = 87.5%  →  if peak utilisation is already 70%, rollout pushes it to 80%  →  into the steep curve
```
**Conclusion**: `maxUnavailable > 0` during peak is a latency risk, not just an availability one. Compute `U / (1 − maxUnavailable/replicas)` before allowing it.

---

## 7. Detection budget and observability readiness

```
detection_objective = 2 × metric_window + scrape_interval + evaluation_delay
```

Burn-rate alert at a 5-minute window, 30 s scrape, 30 s Prometheus evaluation:
```
detection ≤ 5 + 0.5 + 0.5 = 6 min
```
At a 1-minute window:
```
detection ≤ 1 + 0.5 + 0.5 = 2 min
```

Fraction of a 3.75-day (99.2%) burn caught before budget exhaustion:
```
burn visible for 3.75 days; detection 2–6 min  →  caught with 99.97–99.98% of the budget remaining
```
So a fast-window burn alert detects a slow burn essentially immediately. **The alert window, not the burn threshold, is what determines lead time.** Widening the window to 5 minutes to reduce noise buys nothing and halves the lead time.

---

## 8. Dependency capacity readiness

```
own_share = replicas × pool_max / dependency_capacity
ready iff own_share ≤ 0.7
```

`orders-api` 30 replicas × pool 20, calling a `pricing` service with `maxConnections = 400`:
```
own_share = 600 / 400 = 1.5  →  150%: at maximum replicas this service cannot get connections
```
Right-sized:
```
pool = 0.7 × 400 / 30 = 9  →  own_share = 270/400 = 67.5%  ✓
```
Across the fleet, the same arithmetic summed per dependency (Lab 06) is a *readiness* check, not just a scaling check — if the estate already exceeds 70% at today’s replica counts, the service is not ready for a traffic increase even if nothing has broken yet.

---

## 9. Data-loss budget and RPO readiness

```
RPO_measured = time_since_last_verified_backup_point_at_restore
RTO_measured = time_from_failure_request_to_service_restored
```

A restore test: a 2.4 TB database, 90 MB/s restore throughput:
```
RTO_floor = 2.4 TB / 90 MB/s = 7.4 h   (plus index rebuilds: typically +40% → ~10.4 h)
```
Stated RTO objective: 4 h.
```
gap = 6.4 h  →  the stated objective is unachievable with the current backup mechanism
resolution: continuous archiving + WAL shipping, or an accept-and-document decision
```
**Conclusion**: the RTO is set by the restore mechanism, not by the objective. A readiness review that reads "RTO: 4 h" from a document and never restores has verified nothing.

RPO with 15-minute WAL archiving:
```
RPO = 15 min of writes
stated RPO = 5 min  →  gap 10 min  →  either archive more frequently, or state the real number
```

---

## 10. Cost of readiness gaps

```
expected_annual_loss = Σ_gaps P(gap_materialises/yr) × cost
```

Gaps found in a typical PRR:

| Gap | P/yr | Cost | EAL |
|---|---|---|---|
| No pool-saturation alert | 0.5 | $45,000 | $22,500 |
| Rollback never drilled | 0.3 | $80,000 | $24,000 |
| Shutdown grace too short | 0.6 | $3,000 (deploy 502s) | $1,800 |
| Restore never tested | 0.1 | $2,000,000 | $200,000 |
| No SLO, so no burn alert | 0.8 | $60,000 | $48,000 |
| **Total** | | | **~$296,300/yr** |

Cost of closing them: ~6 engineer-weeks for alerts and tests, ~1 engineer-week for grace-period fixes, plus a documented (or architectural) answer for the restore gap — roughly `$90,000` of engineering time.

```
ratio = 296,300 / 90,000 = 3.3:1 in year one, and the restore gap alone dominates
```
**Conclusion**: readiness work is cheap relative to the exposure it removes, and one item (the untested restore) carries two-thirds of the expected loss. This is the arithmetic to present when someone asks whether the PRR gate is worth the delay.

---

## 11. Readiness drift

```
drift_score = (items_no_longer_evidenced) / (total_items)
```

A PRR completed 9 months ago:
- 42 items evidenced.
- 12 have no current evidence: 4 dashboards replaced, 3 runbooks unverified, 3 pools resized (budgets changed), 2 new dependencies added with no test.

```
drift = 12/42 = 28.6%  →  nearly a third of the readiness claim is unverified
```

Cost of drift as a function of review cadence (assumed `P(gap causes an incident in the period)` rising with age):

| Months since PRR | Items stale (approx) | Expected loss |
|---|---|---|
| 0–3 | 2 | $30,000 |
| 3–6 | 6 | $95,000 |
| 6–12 | 12 | $296,000 |
| >12 | 20+ | $500,000+ |

```
re-review every 6 months  →  expected loss ≈ 2 × $95,000 = $190,000/yr
re-review annually        →  $296,000 + $500,000 = $796,000/yr
```
**Conclusion**: a readiness review is a *lease*, not a certificate. Re-reviewing on a 6-month cadence plus on material change roughly halves the exposure of the same estate.

---

## 12. Availability arithmetic for the whole request path

```
A_path = Π A_hop        latency_path = Σ p99.9_hop
```

Four hops: checkout → payments → ledger → gateway, each with a three-nines SLO:
```
A_path = 0.999^4 = 0.996  →  0.4% downtime from chaining alone
```
For a 99.95% path SLO:
```
required per-hop = 0.9995^(1/4) = 0.999875  →  99.9875% per hop
```
Latency budget of 300 ms across 4 hops with 50 ms of local overhead:
```
per-hop p99.9 ≤ (300 − 50)/4 = 62.5 ms
```
If one hop's measured p99.9 is 120 ms, the path cannot meet the SLO regardless of the other three. **Readiness must therefore include per-hop latency budgets and per-hop SLOs** — a single end-to-end SLO conceals that one dependency is the entire problem.

---

## 13. Quick drills

1. 99.9% / 30 days budget, and a 30-minute incident. **Answer: 43.2 min budget, incident consumes 69%.**
2. `SLI = 99.2%` vs 99.9% SLO. Burn and time to exhaustion? **Answer: 8×, 3.75 days.**
3. Burn 1,000× on a 30-day budget. **Answer: exhausted in 43 minutes — the alert is already late.**
4. Remaining budget 25% after a 20-min outage + 8-min degradation (99.9%). **Answer: 35% remaining → canary-only; 4.4 more minutes of degradation forces a freeze.**
5. 9,000 rps, 4-core pods, U=0.65, 4 ms CPU/req. Nodes for peak, and for N+1? **Answer: 650 rps/pod; 2 nodes for peak, but 1-node-loss surviving is 5,200 rps → 4 nodes for N+1.**
6. `in_flight 400`, 300/s, p99.9 12 s, preStop 10 s. Grace period? **Answer: 10 + 12 + 5 = 27 s → set 45 s; the 30 s default is too short.**
7. Cold start 75 s. Startup probe budget? **Answer: 150 s (30 × 5 s).**
8. 24 replicas, `maxUnavailable 0`, `maxSurge 1`. Available and peak pods? **Answer: 24 available (100%), 25 peak; +4.2% plus one pod of JIT warm-up.**
9. Burn alert with a 5-min vs 1-min window. Detection? **Answer: ~6 min vs ~2 min. The window, not the threshold, sets lead time.**
10. 30 replicas × pool 20 against 400 connections. Own share and safe pool? **Answer: 150%; pool ≤ 9 for a 70% share.**
11. 2.4 TB restore at 90 MB/s + 40% index rebuild. RTO? **Answer: ~10.4 h vs a 4 h stated objective → 6.4 h gap.**
12. PRR gaps: total EAL and cost-to-close ratio. **Answer: ~$296,300/yr expected loss; ~$90,000 to close → 3.3:1, with the untested restore alone at $200,000.**
13. PRR 9 months old, 12/42 items stale. Re-review every 6 months vs annually? **Answer: ~$190k vs ~$796k expected loss — roughly 4× better.**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `budget = (1−SLO) × window` | and choose the SLO against your real incident size |
| `burn = (1−SLI_obs)/(1−SLO)`; `exhaust = window/burn` | alerting and the release policy |
| `safe_rps_pod = cores × U / cpu_per_req` | capacity, with `U = 0.6–0.7` |
| `nodes for N+1 ≥ peak/(node_capacity × (n−1)/n)` | headroom that survives failure |
| `grace = preStop + max(in_flight/thr, p99.9) + slack` | shutdown readiness |
| `startup_budget = 2 × worst_cold_start` | startup probe |
| `detection = window + scrape + eval` | pick alert windows for lead time |
| `own_share = replicas × pool / dep_capacity ≤ 0.7` | dependency capacity readiness |
| `RTO = size / throughput × (1 + index_overhead)` | the RTO is set by the restore mechanism |
| `A_path = Π A_hop`; `per_hop_p99 ≤ (budget − local)/hops` | per-hop SLOs and latency budgets |
| `drift = stale_items / total_items` | readiness is a lease; re-review every ~6 months |
