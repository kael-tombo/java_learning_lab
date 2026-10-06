# Lab 15: Performance Engineering & Load Testing — Math Foundation

Performance work is estimation before measurement, and measurement before change. The formulas below are the ones you need to size a system and then verify the sizing.

---

## 1. Little's Law

```
L = λ × W
```

`λ = 2,000 req/s`, `W = 80 ms = 0.08 s`:
```
L = 2,000 × 0.08 = 160 concurrent requests in flight
```

Sizing a pool from it:
```
pool_max ≥ L + safety × sd(L)
if p99 = 220 ms → L_p99 = 2,000 × 0.22 = 440   →  pool ≥ 440
```

Growth under latency regression:
```
latency 80 ms → 800 ms (10×) at constant λ
L = 160 → 1,600 concurrent   →  a 10× concurrency increase with no traffic change
```
That is why a latency regression becomes a pool-exhaustion outage: the queue is invisible, and the *concurrency* is what actually explodes.

**Validity**: `L = λ × W` holds in steady state. During overload, arrival and service time become coupled (slower service → larger backlog → more concurrency), so the identity becomes a description of the runaway rather than a prediction.

---

## 2. Queueing and the utilization knee

Approximate wait time relative to service time (M/M/1-style intuition):

```
W_total/W_service ≈ 1/(1 − ρ) + const
```

| Utilization ρ | Approximate wait amplification |
|---|---|
| 0.50 | ~1.5× |
| 0.70 | ~2.5× |
| 0.85 | ~5× |
| 0.90 | ~9× |
| 0.95 | ~19× |
| 0.99 | ~99× |

From 70% to 90% utilization: capacity is 22% lower, but wait time is ~3.6× worse. **This is the entire capacity-planning argument for latency-critical services**: run at 60–70% so a 30% traffic increase degrades gracefully instead of falling off a cliff.

---

## 3. Saturation point detection

```
throughput_max = max over load levels of completed_rps
knee = smallest load where d(throughput)/d(load) < 0.2
```

Measured curve (service with a 20-connection downstream pool):

| Offered rps | Completed rps | p99 | Pool pending |
|---|---|---|---|
| 1,000 | 1,000 | 90 ms | 0 |
| 2,000 | 2,000 | 110 ms | 2 |
| 2,500 | 2,440 | 400 ms | 38 |
| 2,800 | 2,300 | 1,900 ms | 210 |
| 3,000 | 1,850 | 4,200 ms | 400 (pool max) |
| 3,200 | 1,100 | 9,000 ms | 400 |

```
knee ≈ 2,500 rps  (d(throughput)/d(load) ≈ 0.2 there)
peak ≈ 2,440 rps at 2,500 offered
beyond the knee: more load ⇒ less work done
```

Headroom policy:
```
target_peak_utilisation = 0.7   →  safe capacity = 0.7 × 2,440 = 1,700 rps
```
Peak is 1,700 rps, not 2,440 — because at 2,440 you are already in the steep part of the curve.

---

## 4. Coordinated omission correction

Closed-loop: N users, each sends, waits, repeats. Latency measured only on requests actually sent.

```
true_mean_latency = (Σ intended_request_latency) / (requests that should have been issued in the window)
```

Offered 1,000 rps (1 ms interval), N=50 users, and the service stalls for 10 s:
```
requests a correct test issues in 10 s = 10,000
a closed-loop test issues = 50 users × (10s / W_normal)
if W_normal = 0.1 s →  50 × 100 = 5,000 issued; 5,000 never recorded
```

Measured p99 with omission:
```
of the 5,000 issued, ~4,950 are fast → p99 of recorded = ~0.1 s   → looks fine
true p99 over the window = the stalled requests are 50% of intended traffic → p99 = the stall duration
```

**Conclusion**: closed-loop testing can report 100 ms p99 for a service that was returning errors for ten seconds. This is the single most important methodological point in the lab.

---

## 5. Amdahl's Law and where to optimise

```
speedup_total = 1 / ( (1 − f) + f/s )
```

`s` = speedup of the optimised fraction `f`:

| f (serial/slow fraction) | s = 10× | s = 100× | s = ∞ |
|---|---|---|---|
| 0.05 | 1.05× | 1.05× | 1.05× |
| 0.20 | 1.22× | 1.25× | 1.25× |
| 0.50 | 1.82× | 1.98× | 2.0× |
| 0.80 | 3.57× | 4.76× | 5.0× |

**Conclusion**: finding the dominant fraction comes first. Optimising a 5% slice by 100× buys 5%. That is why "profile before you optimise" is an arithmetic requirement, not a slogan.

---

## 6. Thread pool and connection pool sizing

CPU-bound:
```
threads ≈ cores × (1 + wait/service) ≈ cores for pure CPU work
```
16 cores → 16–32 threads. More threads add context switching without throughput.

I/O-bound (blocking downstream at `W_dep`):
```
threads_or_conns ≈ λ × W_dep × safety
```
`λ = 2,000/s`, `W_dep = 30 ms`, safety 1.3:
```
pool = 2,000 × 0.030 × 1.3 = 78
```

Ceiling — the dependency's capacity:
```
pool_max ≤ downstream_max_concurrency
```
If the downstream database `max_connections = 200` shared by 6 services:
```
per_service_pool ≤ 0.7 × 200 / 6 = 23   →  a pool of 78 would be reckless
```

**Conclusion**: for I/O services the correct pool size is `min(λ × W × safety, dependency share)`, and the two are frequently in conflict — which is a capacity finding, not a tuning problem.

---

## 7. Database query cost and N+1

```
db_time_per_request = base_query_ms + n_rows × per_row_query_ms
```
List endpoint with limit=100 and a lazy-loaded association:
```
1 (list) + 100 (per row) = 101 queries × 1.2 ms = 121 ms per request
at 500 rps → 50,500 queries/s
```
Fixed with a join/projection:
```
1 query × 8 ms = 8 ms  →  500 queries/s  →  100× less DB load, 15× lower latency
```

Missing-index case:
```
indexed lookup    ~ 0.2 ms
sequential scan   ~ 120 ms  (10M rows × 12 ns/row)
```
One unindexed filter on a hot path is a 600× regression — larger than any JVM tuning you can do.

---

## 8. GC pause and tail latency

```
gc_pause_p99_share_of_tail = gc_pause / request_latency
mean_invisible = pause / total_samples  (the trap)
```

`10,000 requests/s`, one 40 ms stop-the-world pause every 30 s:
```
pauses per hour = 120
requests affected = 120 × 40 ms × 10,000 rps = 48,000 requests
fraction = 48,000 / 36,000,000 = 0.13%
mean impact = 0.0013 × 40 ms = 0.05 ms  →  invisible
p99.9 impact = the 0.1% tail is entirely GC  →  p99.9 = 40 ms extra
```

Allocation rate driving pause frequency:
```
pause_frequency = allocation_rate / young_gen_size
allocation 1 GB/s, young gen 256 MB → 4 pauses/s  (and if 40 ms each: 16% of wall time in GC)
```
Reducing allocation from 1 GB/s to 200 MB/s is a 5× improvement; buying a faster collector is a ~1.2× improvement. **Allocation first.**

---

## 9. Cache hit ratio and origin load

```
origin_load = λ × (1 − h)
origin_cpu_capacity_check: origin_load ≤ C_origin × U_target
```
`λ = 5,000`, `C_origin = 8,000`, `U_target = 0.7` → safe origin load `5,600`:
```
required h ≥ 1 − 5,600/5,000  →  already satisfied
```
Now with `λ = 9,000` (peak growth):
```
required h ≥ 1 − 5,600/9,000 = 0.378
```
At h=0.20 measured: origin load `7,200` = 90% utilisation → into the steep curve. So the cache hit ratio becomes a *capacity requirement*, derived from the same arithmetic.

---

## 10. Environment ratio matching

```
production_load_per_core = λ_prod / cores_prod
test_load_per_core      = λ_test / cores_test
ratio_error = test_load_per_core / production_load_per_core
```

Production: `λ = 3,000 rps`, `W = 40 ms` CPU → `120 CPU-seconds/s` = 1.2 cores at full utilisation → at 60% utilisation, `2.0 cores`.
Test box: 16 cores. Matching rps naively: `3,000 × 0.040 / 16 = 7.5%` utilisation — the test will show 40 ms latency and pass.

Correct target utilisation: `2.0 / 16 = 12.5%` still matches; the problem appears when the test box has *no* other constraint (network, DB). So the discipline is: **match utilisation ratios on every resource, and list which resources the test environment cannot constrain** (e.g. a real network RTT) and compensate deliberately.

```
network effect: RTT_test = 0.1 ms vs RTT_prod = 2 ms
at W = 40 ms: test total = 40.1 ms (0.25% error)  →  acceptable
at W = 8 ms:  test total = 8.1 ms, prod = 10 ms   →  21% error  →  must add shaping
```
Rule: if the service's latency is within ~20% of the RTT difference, shape the network.

---

## 11. Load-test statistics

Three runs, throughput and p99:

| Run | rps | p99 (ms) |
|---|---|---|
| 1 | 2,410 | 402 |
| 2 | 2,455 | 388 |
| 3 | 2,398 | 419 |

```
median rps = 2,410      median p99 = 402
spread rps = 2.4%       spread p99 = 7.8%
```
An "improvement" smaller than the spread is not an improvement. Report median and range, and require a delta greater than the spread to claim a win.

Statistical significance for a p99 comparison (Mann–Whitney U or bootstrap on the raw samples) is stricter than comparing medians: p99 has ~1% of samples, so a single 5-minute run gives ~3,000 samples in the 99th-percentile bucket. That is thin. **Longer runs, not more runs**, improve p99 confidence.

---

## 12. Capacity projection

```
cpu_per_request_ms = cpu_time_total / requests
cores_required     = λ_peak × cpu_per_request_ms / U_target / 1000
memory_per_pod     = heap + native + λ_per_pod × W × bytes_per_conn
replicas           = ceil(λ_peak / (cores_per_pod × U_target))
```

`λ_peak = 9,000 rps`, `cpu_per_request = 4 ms`, `U = 0.65`, 4-core pods:
```
cores = 9,000 × 0.004 / 0.65 = 55.4 cores → 14 pods (4 cores each)
memory: 9,000/14 = 643 rps/pod × 0.08 s × 10 KB = 0.5 MB → negligible vs 4 GB heap
```
With N+1 failure tolerance (one node down, 3 pods lost):
```
available = 11 pods × 4 × 0.65 = 28.6 cores → 4,600 rps capacity
→ the projected peak exceeds surviving capacity  →  need 20 pods, not 14
```
That last step — sizing for failure, not for average — is the one most capacity models omit.

---

## 13. Cost of a performance fix

```
throughput_gain → capacity_saved = (replicas_before − replicas_after) × cost_per_replica_month
```
`2,440 rps` peak with 14 pods → after fixing the N+1, `3,900 rps` with 14 pods:
```
new_required_pods = 9,000/3,900 × 14 = 32 pods?? no:
pods needed at 3,900 rps per 14 pods = 14 × (9,000/3,900)...
```
Carefully: each pod does `2,410/14 = 172 rps` before, `3,900/14 = 279 rps` after.
```
pods_needed_after = 9,000 / 279 = 33 pods   →  worse? no: this is the wrong comparison.
```
Recompute properly: `pods_needed = λ_peak / (rps_per_pod × U_already_applied)`. With the fix, `rps_per_pod` rises from 172 to 279:
```
pods_before = 9,000/172 = 53
pods_after  = 9,000/279 = 33
saving = 20 pods × $180/month = $3,600/month → $43,200/year
```
One query fix (a join instead of 101 queries) paid for itself in a month. **Performance work is usually a cost project, not a latency project** — that framing gets it funded.

---

## 14. Quick drills

1. `λ=2,000`, `W=80 ms`. Concurrency? **Answer: 160. At 800 ms latency: 1,600 — a 10× regression becomes a 10× concurrency explosion.**
2. Utilization 0.70 vs 0.90. Wait amplification? **Answer: ~2.5× vs ~9×.**
3. Throughput peaks at 2,440 rps, knee ~2,500. Safe capacity at 70%? **Answer: 1,700 rps.**
4. Closed-loop N=50, 10 s stall, W_normal=100 ms. Unrecorded requests? **Answer: 5,000 of 10,000 intended — coordinated omission.**
5. 5% of a request path, optimised 100×. Overall speedup? **Answer: 1.05×.**
6. `λ=2,000`, `W_dep=30 ms`, safety 1.3. Pool size? **Answer: 78, but capped by the dependency share (23 in the shared-DB example).**
7. `limit=100`, 101 queries × 1.2 ms at 500 rps. Fix impact? **Answer: 121 ms → 8 ms; 50,500 → 500 queries/s.**
8. 40 ms GC every 30 s at 10,000 rps. Requests affected/hour and mean impact? **Answer: 48,000 requests (0.13%); mean impact 0.05 ms (invisible), p99.9 hit.**
9. Production 1.2 CPU-cores of work, test box 16 cores. Matched utilisation? **Answer: 7.5% vs 7.5% — match on utilisation, and shape the network if W < ~20 ms.**
10. Three runs: rps 2,410 / 2,455 / 2,398. Claim a 3% gain? **Answer: no — spread is 2.4%; need a delta above the spread.**
11. rps/pod 172 → 279 after a fix, peak 9,000. Pods and annual saving? **Answer: 53 → 33 pods, 20 × $180 × 12 ≈ $43k/year.**

---

## 15. Formulas worth memorizing

| Formula | Use |
|---|---|
| `L = λ × W` | latency ↔ concurrency; pool sizing |
| `wait ≈ 1/(1−ρ)` | why 70% is the design target |
| `knee = d(throughput)/d(load) < 0.2` | find saturation empirically |
| `safe_capacity = U_target × peak_throughput` | headroom policy |
| `speedup = 1/((1−f) + f/s)` | find the dominant fraction first |
| `pool = min(λ × W × safety, dep_share)` | I/O pool sizing with a hard ceiling |
| `db_time = base + n_rows × per_row` | N+1 arithmetic |
| `GC_pause_freq = alloc_rate / young_gen` | allocation first, collector second |
| `origin_load = λ(1−h)` | hit ratio as a capacity requirement |
| `run spread` vs `delta` | no claim below the noise floor |
