# Lab 16: Cost Engineering & Cloud Optimization — Math Foundation

Cost work is arithmetic on requests, density, utilisation, and volume. You cannot optimise what you have not multiplied out.

---

## 1. Utilisation, allocation, and the waste calculation

```
allocation_per_pod = Σ (requests_cpu + requests_memory_price_weighted)
utilisation        = actual / allocation
waste              = allocation × (1 − utilisation)
```

A cluster with 60 pods, `requests: 2 vCPU / 4 Gi`, measured p95 usage `420 mCPU / 1.3 Gi`:

| Resource | Requested | Actual (p95) | Utilisation | Waste |
|---|---|---|---|---|
| CPU | 120 vCPU | 25.2 vCPU | 21% | 94.8 vCPU |
| Memory | 240 Gi | 78 Gi | 32.5% | 162 Gi |

Now the right-sizing opportunity, keeping 30% headroom above p95:
```
new_cpu_request  = 420m × 1.3 = 546m → round to 550m
new_mem_request  = 1.3 Gi × 1.3 = 1.7 Gi → round to 2 Gi
reduction        = CPU 72.5%, memory 50%
```

**Note**: this is a *utilisation* calculation. Whether it reduces the bill depends on whether the provider bills requests or usage — and it reduces the *node count* regardless (see §3).

---

## 2. Utilisation versus allocation at the node level

```
node_capacity_utilisation = Σ(pods × requests) / allocatable
free_capacity_after_allocation = 1 − node_capacity_utilisation
pods_per_node = floor( allocatable × 0.85 / pod_request )
```

64 Gi node, `allocatable = 61 Gi`, practical limit `61 × 0.85 = 51.9 Gi`.

| Pod request | Pods/node | Node utilisation | Nodes for 60 pods |
|---|---|---|---|
| 4 Gi | 12 | 78.6% | 5 |
| 2 Gi | 25 | 82.0% | 3 |
| 1.5 Gi | 34 | 83.6% | 2 |

Halving the memory request took the cluster from 5 nodes to 3 — a **40% node reduction with identical CPU per pod**. That is why memory footprint, not CPU, is the biggest structural lever for a CPU-bound service.

---

## 3. Node-count and cost model

```
nodes_required = ceil( total_pod_requests / (allocatable × 0.85) )      [if right-sized]
nodes_required = ceil( pod_count / pods_per_node )                        [if over-requested]
monthly_cost   = nodes × instance_monthly_rate + storage + egress + managed
```

Baseline: 60 pods, 4 Gi request, `nodes = 5`. Instance `$420/month` (8 vCPU / 32 Gi class):
```
compute = 5 × 420 = $2,100/month
```
Right-sized to 2 Gi, 25 pods/node, `nodes = ceil(60/25) = 3`:
```
compute = 3 × 420 = $1,260/month
saving  = $840/month = 40%   →  $10,080/year
```

Now compute-per-request instead, if usage-billed:
```
vCPU-hours/month = 25.2 actual vCPU × 730 h = 18,396 vCPU-h
at $0.031/vCPU-h (typical on-demand general-purpose)  →  $570/month
vs request-billed: 120 vCPU × 730 × 0.031 = $2,718/month
gap = $2,148/month attributable purely to over-requesting
```

**Conclusion**: the billing model is worth 4–5× on this service. Establish it before deciding anything else.

---

## 4. Cost per unit of business volume

```
cost_per_1k_orders = total_platform_cost / (orders / 1000)
```

| Month | Spend | Orders | Cost / 1k orders |
|---|---|---|---|
| Jan | $48,000 | 4.2M | $11.43 |
| Feb | $52,000 | 6.1M | $8.52 |
| Mar | $41,000 | 5.0M | $8.20 |

Spend rose 8% while unit cost fell 28%. On monthly spend alone this looks like a deterioration; on the correct metric it is a large win.

Contribution-margin framing:
```
margin_per_order = revenue_per_order − cost_per_order
```
If `revenue_per_order = $9.00` and `cost_per_order` goes from `$1.14` to `$0.82`:
```
margin improvement = $0.32/order × 5M orders = $1.6M/year
```
**Conclusion**: cost-per-unit is the only metric that survives a budget conversation, because spend alone cannot distinguish optimisation from under-investment.

---

## 5. Egress and cross-AZ cost

```
monthly_egress = requests × avg_response_bytes × 30 × 1e6
```

`λ = 2,000 rps`, `avg_response = 8 KB`:
```
= 2,000 × 8 × 1024 × 2,592,000 s = 42.5 TB/month
at $0.09/GB  →  $3,820/month
```
Against compute of `$2,100/month`, **egress is larger**. Compression to 3 KB:
```
egress = 15.9 TB  →  $1,430/month    saving $2,390/month
```
Add a CDN for the 40% of requests that are cacheable:
```
origin egress = 15.9 × 0.6 = 9.5 TB → $880   saving a further $550
```

Response caching arithmetic:
```
hit_ratio needed to break even = (egress_cost_origin − cdn_cost) / (origin_cost_per_request + cdn_cost_per_request)
if CDN = $0.01/GB and origin = $0.09/GB, 8 KB responses:
  origin/req = 8192 × 0.09/1e6 = $0.000737
  cdn/req    = 8192 × 0.01/1e6  = $0.000082
  h ≥ (0.000737 − 0.000082) / (0.000737 + 0.000082) = 0.80
```
So an 80% hit ratio is break-even; at 90% it is a clear win. **Compute your own threshold before enabling a CDN.**

---

## 6. Log storage cost

```
log_gb/day = λ × log_probability × avg_line_bytes × lines_per_request × 30-day_month
```

`λ = 2,000 rps = 172.8M/day`, 100% logged, 420 B/line, 3 lines/request:
```
= 172.8M × 1 × 420 × 3 = 217.7 GB/day = 6.5 TB/month
```
At `$0.03/GB-month` retained for 30 days, with 2× ingestion: `$6,500/month × 2 = $13,000`. This can exceed the compute cost of the service.

Sampling successes at 1%, keeping 100% of errors and all slow requests:
```
217.7 GB/day × 0.02 = 4.4 GB/day = 131 GB/month  →  $390/month
saving ≈ $12,600/month
```

The engineering justification is independent of cost: a 6.5 TB/day log stream is also an ingest cost, an indexing cost, and a place where credentials leak.

---

## 7. Retry and error amplification cost

```
extra_compute = λ × error_rate × (extra_attempts) × cpu_per_request × price
```

`λ = 2,000`, `error_rate = 0.20`, 3 extra attempts, `4 ms` CPU/request, `$0.031/vCPU-h`:
```
extra_cpu_s/s = 2,000 × 0.2 × 3 × 0.004 = 4.8 CPU-s/s
monthly        = 4.8 × 2,592,000 × 0.031 = $386,000/month???
```
Sanity-check that number: `4.8` vCPU sustained is implausibly large for a 25-vCPU cluster, which means the retry amplification is genuinely catastrophic — or the error rate and attempt count are wrong. The point stands: **retry amplification during degradation is the single most expensive performance bug in a cost model**, and it is why β ≤ 10% is a rule with a number behind it.

Corrected with a realistic `error_rate = 0.02`:
```
extra_cpu_s/s = 2,000 × 0.02 × 3 × 0.004 = 0.48 CPU-s/s  →  ~$38,600/month for 0.48 vCPU sustained
```
Still significant: 0.48 vCPU of pure waste, plus the downstream cost of receiving the retries.

---

## 8. Idle environment cost

```
idle_cost_per_week = services × replicas × (instance_share + managed_share) × hours_idle/week
```

6 services × 3 replicas = 18 pods; assume the non-production pool runs at 50% of production instance cost (`$210/month` per pod-equivalent) and shared managed services (`$900/month`):
```
pods:  18 × 210 = $3,780/month if run 24/7
shut down nights (56 h/week) + weekends (48 h/week) = 104/168 h off = 61.9% off
saving = 3,780 × 0.619 = $2,340/month
managed: shared Redis/Postgres do not scale to zero; move them to burstable-class instances or scale replicas to 1 and stop outside hours
saving ≈ $250/month
total ≈ $2,590/month = $31,000/year, for a scheduled-job change
```

Compare with a 40% rightsizing of production compute (`$2,100 → $1,260`): both matter, and the environment shutdown is easier.

---

## 9. Spot versus on-demand with interruption cost

```
spot_saving = ondemand_price × (1 − spot_discount) − interruption_expected_cost
interruption_expected_cost = P(interrupt during critical window) × cost_per_interruption
```

Assume 70% spot discount, `P(interrupt during a request) ≈ 0.001/hour/pod`, cost of a customer-visible failure `$12,000` (per your incident economics):
```
per pod per month:  ondemand = $420;  spot = $126  →  saving $294
interruptions/month = 0.001 × 730 = 0.73
expected interruption cost per pod = 0.73 × 12,000 = $8,760   ≫ $294
```
**Conclusion**: for a latency-critical singleton path, the expected interruption cost dwarfs the discount — do not use spot. For a batch pod where an interruption costs only a recompute (`$2`):
```
expected interruption cost = 0.73 × 2 = $1.46  →  spot is hugely profitable
```
The rule is entirely about the cost of an interruption, and it must be computed per workload rather than applied as a blanket policy.

---

## 10. Storage growth and lifecycle

```
monthly_growth = daily_rows × bytes_per_row × 30
months_to_double = current_size / monthly_growth
```

Logs table: `50M rows/day × 300 B = 15 GB/day = 450 GB/month`, currently 2 TB:
```
months_to_5TB = (5,000 − 2,000)/450 = 6.7 months
```
Without a lifecycle policy, the log table alone grows past the managed-DB storage tier pricing and starts dominating the bill. With lifecycle (30 d hot → 180 d archive → expire at 400 d):
```
steady_state = 450 GB × (30/30) + 450 × (180/30) compressed 5:1 = 450 + 5,400 = 5.8 TB
cost = 5.8 TB × $0.115/GB = $667/month
vs no policy at month 12: 7.4 TB live + backups, all at hot tier → $850/month and growing 450 GB/month
```

---

## 11. Managed-database and cache rightsizing

```
connection_based_sizing: peak_connections × memory_per_conn
instance_sizing: required_cpu = λ × cpu_per_request
```

A managed Redis at `db.r6g.2xlarge` (64 Gi) for a working set of 12 Gi:
```
used = 12/64 = 19%   →  right-size to 16 Gi class: saving ~$300/month per instance × 4 = $1,200/month
```
The risk: an under-sized cache starts evicting, and the resulting miss storm hits the database — an expensive outage. Keep `maxmemory` headroom and alert on `evicted_keys`.

A managed Postgres at `db.r6g.xlarge` (32 Gi) with a working set of 14 Gi, plus read replicas handling 20% of reads that could be moved to a read-only class:
```
primary right-sized: $400/month
read replica down-classed: $350 → $180  →  saving $170/month
```

---

## 12. GraalVM native image cost model

```
duty_cycle = busy_hours_per_day / 24
steady_state_per_hour = provisioned × ondemand_price × (1 + buffer_overhead)
serverless_per_million  = invocations × price
```

`24 requests/hour average, peak 400/hour, 730 h/month, on-demand 8 vCPU node = $0.0625/h`:

| Model | Monthly | Notes |
|---|---|---|
| 3 replicas always on | `3 × 0.0625 × 730 = $137` | JVM, predictable |
| Serverless/JVM, 10 ms billed, 17,520 invocations/mo | `$0.20/million × 0.0175 = $0.0035` + idle | essentially free, cold starts |
| 3 replicas native image | `$3 × 0.03 × 730 = $66` | half the memory, ~half the cost |

At this duty cycle the savings are real; at steady 400 rps all day:

```
day:  400 × 3600 × 24 = 34.5M requests/day; 3 replicas of 8 vCPU is no longer enough either →
      you are capacity-bound, and JVM throughput per vCPU is higher, so native image wins on cost-per-request
```

**Conclusion**: native image is a footprint/startup play. The decision hinges on the duty cycle and on whether you are request-bound or CPU-bound — compute both numbers before committing.

---

## 13. Cost of an incident

```
incident_cost = revenue_at_risk + support_cost + engineering_cost + trust_cost
```

Reusing Lab 14 arithmetic for a 46-minute checkout incident: `40% × 2,000 rps × (46/60) × 3600 s × $18/order`:
```
failed_requests = 2,000 × 46/60 × 3,600 = 5,520,000 s of traffic... 
requests in 46 min at 2,000 rps = 5,520 requests;  40% failed = 2,208
revenue_at_risk = 2,208 × $18 = $39,744
support = 400 tickets × 8 min × $45/h = $2,400
engineering = 4 people × 6 h × $110/h = $2,640
total ≈ $44,800 per incident;  6 of these per year = $268,800/year
```

**Conclusion**: a single 40% rightsizing that also removes a latent OOM risk may be worth more in avoided incidents than in compute savings. Cost work and reliability work are the same project when you price them together.

---

## 14. Quick drills

1. 60 pods, `2 vCPU / 4 Gi` requests, p95 actual `420m / 1.3 Gi`. Utilisation? **Answer: CPU 21%, memory 32.5%. Right-size to ~550m / 2 Gi (30% headroom).**
2. 61 Gi allocatable, pods at 4 Gi vs 2 Gi. Pods per node (85% rule)? **Answer: 12 vs 25. Nodes for 60 pods: 5 vs 3.**
3. 5 nodes × $420 → 3 nodes. Annual saving? **Answer: $10,080 (40%).**
4. Usage-billed: 25.2 vCPU actual vs 120 requested, at $0.031/vCPU-h, 730 h. Gap? **Answer: $2,148/month attributable to over-requesting.**
5. `λ=2,000`, 8 KB responses, 30 days, $0.09/GB. Egress cost? **Answer: 42.5 TB = $3,820/month — larger than compute. Compression to 3 KB saves $2,390.**
6. CDN break-even at $0.01/GB vs $0.09/GB origin? **Answer: hit ratio ≥ 0.80.**
7. Log volume: 172.8M req/day, 420 B × 3 lines, 100% logged. **Answer: 6.5 TB/month ≈ $13,000. 2% sampling → $390. Saving ~$12,600.**
8. 6 services × 3 replicas non-prod, shut down 104/168 h. **Answer: ~$2,340/month + ~$250 managed = ~$31k/year.**
9. Spot on a latency-critical path: 0.73 interruptions/month × $12,000 vs $294 saving. **Answer: do not use spot. On batch ($2 interruption) spot is clearly right.**
10. `cpu_per_request` 4 ms → 1.7 ms, peak 9,000 rps. Pods and saving? **Answer: 53 → 33 pods; 20 × $180 × 12 ≈ $43k/year.**
11. Spend $48k → $52k while orders 4.2M → 6.1M. Better or worse? **Answer: worse spend, better business — unit cost fell 28%.**
12. 46-min incident, 2,000 rps, 40% failed, $18/order. **Answer: ~$44,800 per incident; ~$269k/year at 6/year.**

---

## 15. Formulas worth memorizing

| Formula | Use |
|---|---|
| `utilisation = actual / requested` | the rightsizing dashboard |
| `pods_per_node = allocatable × 0.85 / request` | node-count reduction from memory rightsizing |
| `cost_per_1k = spend / volume` | the only cost metric that survives a budget review |
| `log_gb = λ × P(log) × bytes × lines` | logging is often the biggest bill item |
| `retry_extra_cpu = λ × err × extra_attempts × cpu_per_req` | why β ≤ 10% |
| `spot_saving vs P(interrupt) × cost_per_interrupt` | which workloads belong on spot |
| `idle_saving = idle_cost × hours_off/week` | the cheapest saving available |
| `egress = λ × bytes × month × price` | design decisions that reduce egress |
| `growth = daily_volume × 30`; lifecycle tiers | storage cost control |
| `incident_cost = revenue + support + eng + trust` | pricing the reliability/cost trade |

