# Lab 03: Production Debugging — Math Foundation

Debugging is measurement. These formulas convert symptoms into budgets and let you decide whether a signal is noise or a trend.

---

## 1. Latency percentiles

Given a sorted set of `n` request latencies:

```
p_k  = value at index  ceil(k/100 × n) - 1
```

No interpolation — percentiles of real request streams are order statistics, not smooth curves.

**Why p99 matters more than the mean** for a fixed SLO: if `p99 ≤ 250 ms`, at most 1% of requests violate. Define the error budget:

```
error_budget = (1 − SLO) × requests_per_window
```

SLO 99.9% over 1 day at `λ = 8000/s`:

```
allowed_failures = 0.001 × 8000 × 86400 ≈ 691,200 per day
```

Burn rate for a deploy that fails 2% for 10 minutes:

```
burn_rate = 0.02 / 0.001 = 20×
```

At 20x, you exhaust a 30-day budget in **36 hours**, not 30 days. This is why deploys must be gated on burn rate.

---

## 2. Mean vs tail: variance decomposition

If mean latency is stable but p99 worsens, you added variance, not work:

```
p99 ≈ mean + z·σ      with z ≈ 2.33 for a one-sided 99th percentile of a normal distribution
```

Mean 100 ms, p99 150 ms → `σ ≈ 21 ms`. If p99 becomes 400 ms with the same mean → `σ ≈ 129 ms`. Variance grew ~38x while work stayed constant. Candidates: GC pauses, lock waits, or a bimodal downstream.

For bimodal (two-mode) latency — very common with connection-pool acquisition or retries — a single normal-approximation percentile understates the tail. Model it as two components:

```
P(total > t) = 1 − Σ_i p_i · F_i(t)
```

with `p_i` the fraction taking each mode. That is why "average 40 ms, p99 2 s" is not a contradiction and not a reporting bug.

---

## 3. Little's Law again — as a debug instrument

```
L = λ · W
```

Latency is a queueing outcome. If in-flight concurrency `L` is stable while latency `W` rises, then **arrival rate λ must have risen** — or service time rose while λ fell. This decomposition tells you which side to investigate before looking at any code.

Sanity check against your thread pool: `L_max = P` (pool size) ⇒ `W_max = P / λ`. With `P = 200`, `λ = 8000/s`: `W_max = 25 ms`. Any p99 above 25 ms proves your pool is saturated or unbounded queueing is in play.

---

## 4. Utilization and the queueing cliff (Erlang B/C)

```
ρ = λ / (P · μ)          utilization
```

Erlang B (blocked calls lost — retries, i.e. a pool that throws):

```
B(P, a) = (a^P / P!) / Σ_{k=0}^{P} a^k/k!
```

Erlang C (blocked calls queued — a pool that waits) adds the `1/(1−ρ)` waiting term. Blocked-call-retried systems are *worse* than blocked-call-queued systems at the same load, because retries amplify arrival rate.

Worked: `λ = 8000/s`, service `μ = 40/s` per thread, `P = 200`:

```
a = λ/μ = 200       ρ = 1.0     ← exactly saturated; queue diverges
P = 240 → ρ = 0.83
P = 260 → ρ = 0.77
```

Design to `ρ ≤ 0.7`. Note the retry amplification: with 1 retry per call, effective `λ = 16000/s`, so `a` doubles — a 2x traffic regression requires 2x threads, not 1.2x.

---

## 5. Retry amplification

```
amplification = (retries_allowed + 1) ^ call_chain_depth
```

Two nested calls, each with 2 retries: `3^2 = 9x` load on the deepest dependency. With a 3-retry budget: `4^2 = 16x`. Add jittered exponential backoff and the *concurrent* load can still spike even though the average is bounded — model the synchronized-retry case as a brief `N`-fold spike rather than an average increase.

Mitigation arithmetic: with full jitter, `sleep = U(0, min(cap, base·2^n))`, the expected concurrent retry fraction at any instant drops from ~100% (no jitter) to roughly `1/N` where `N` is the number of distinct sleep buckets.

---

## 6. Head-of-line blocking

A single-threaded stage with service time `S` bounds the pipeline:

```
Throughput ≤ 1/S_stage       for the slowest stage
```

A stage with `S = 500 ms` caps the system at 2 req/s no matter how many threads exist elsewhere. Detect it by ranking stages by `mean_service_time × requests_through_stage` — the stage with the largest total service time is the bottleneck candidate, and it is often not the slowest per-call.

For a queue with service times `S_1..S_n` and FIFO order, head-of-line wait adds:

```
W_hol ≈ max_i(S_i)   for the unlucky request
```

So a single 800 ms outlier inflates the *maximum* observed latency even at low utilization. Distinguish "we have one slow request" from "the system is slow" using percentiles plus a max-time histogram.

---

## 7. Percentile-of-percentiles error (the "aggregated p99" trap)

Percentiles do not aggregate. Averaging per-pod p99s understates the global p99 because of sampling bias:

```
naive_avg_p99 = mean(p99_i)        ≈ biased low
true_global_p99 = quantile_99(concat(all samples))
```

For `n` pods each with `m` requests, a pod with an unusually heavy tail contributes proportionally to its sample count, and any *extra* request it serves shifts the true global p99 upward relative to the mean of per-pod p99s. Rule: **compute percentiles at the store (Prometheus `histogram_quantile` over aggregated buckets), not by averaging pod-level percentiles.**

---

## 8. Log-volume arithmetic

```
log_rate = λ × log_bytes_per_request
```

`λ = 8000/s`, 800 B/request with structured fields: `6.4 MB/s ≈ 553 GB/day`. That is not affordable at 30-day retention ($X/GB) and it slows serialization.

Sampling for debuggability:

```
kept_fraction = 1% → 5.5 GB/day  (keep 100% of errors + 100% of slow requests)
```

Rule of thumb: keep 100% of errors, 100% of p99+ requests, and 1% of the rest. Cost drops ~50x while keeping ~all diagnostic value, because almost every incident is visible in the error and tail samples.

---

## 9. Trace sampling math

Head sampling at rate `p` keeps a fraction `p` of requests. Requirements:

```
required_traces_per_sec = min(traces_needed_to_diagnose, λ·p)
```

`λ = 8000/s`, `p = 0.01` → 80 traces/s → 6.9M traces/day. At ~10 KB each: **69 GB/day**. Head sampling at 1% is often unaffordable; tail sampling (keep all errors + all slow) is dramatically cheaper for the same diagnostic value. Budget traces by *retention window* (hours), not by rate, and compute the number you can afford first:

```
affordable_traces_per_day = storage_GB_day / kb_per_trace
```

---

## 10. Debug sampling validity

For a stochastic failure with probability `p`, to observe it with confidence `1 − α`:

```
observations n ≥ ln(α) / ln(1 − p)
```

For a 1-in-10,000 failure (`p = 1e-4`) with 95% confidence: `n ≥ 29957` — about 30,000 requests. If your load test only ran 5,000 requests, **you have not proven the bug is fixed**; you have proven you did not see it 39% of the time.

For a 1% race: `n ≥ 299`. This is the honest statistical floor for "the race is fixed" claims, and it belongs in test design.

---

## 11. Change attribution during incidents

If a deploy happens at time `t0` and latency regresses, quantify:

```
Δmean = mean_after − mean_before        over equal windows either side
step_test_p ≈ 1.64 · σ_diff / SE_diff   (two-sample z ≈ 1.64 for 90% two-sided)
SE_diff = sqrt(σ₁²/n₁ + σ₂²/n₂)
```

With `n₁ = n₂ = 50,000`, `σ = 80 ms`: `SE = 0.51 ms`. A `Δmean = 4 ms` is ~8σ — attribution is solid. This is why "it feels slower" needs numbers before you declare a deploy guilty.

---

## 12. Cache math for debugging latency

Hit ratio and cost model:

```
mean_cost = hit_ratio · C_hit + (1 − hit_ratio) · C_miss
C_miss = C_backend + C_populate
```

`C_hit = 1 ms`, `C_backend = 20 ms`, `C_populate = 2 ms` ⇒ `C_miss = 22 ms`.
At 90% hit ratio: `mean = 0.9·1 + 0.1·22 = 3.1 ms`.
At 80%: `mean = 0.8·1 + 0.2·22 = 5.2 ms` — a 10-point hit-ratio drop raised mean by 68%.

Also: `hit_ratio_needed` to hit a target `T`:

```
hit_ratio ≥ (T − C_miss) / (C_hit − C_miss) = (1 − 22)/(1 − 22) = 0.955
```

To keep mean ≤ 1 ms you need ~95.5% hit ratio. Latency SLOs are cache-hit-ratio SLOs in disguise.

---

## 13. Debounce and hysteresis for alerts

Flapping alerts destroy trust. Require both a threshold breach and a dwell time:

```
alert_fires  if  breach persists ≥ T_hold
alert_clears if  breach persists < T_clear   and T_clear > T_hold
```

With `T_hold = 5m`, `T_clear = 15m`, a 60-second GC pause spike pages once, not sixty times.

---

## 14. Quick drills

1. `λ = 8000/s`, `P = 200` threads, 25 ms service → `ρ = ?` **Answer: `λ/(P·μ) = 8000/(200·40) = 1.0`. Saturated — you need ≥ 229 threads for ρ ≤ 0.7.**
2. Failure rate 2% for 10 minutes, SLO 99.9% → burn rate? **Answer: 20x.**
3. `p = 1e-4` race, 95% confidence → `n`? **Answer: ~29,957.**
4. Mean 100 ms, p99 400 ms → implied `σ` before/after? **Answer: 21 ms → 129 ms.**
5. `λ = 8000/s`, 1% head sampling, 10 KB/trace → storage/day? **Answer: 69 GB/day.**

---

## 15. Formulas worth memorizing

| Formula | Use |
|---|---|
| `p99 ≈ mean + 2.33σ` | tail diagnosis from two numbers |
| `error_budget = (1−SLO)·requests` | SLO arithmetic |
| `burn_rate = actual/SLO_target` | deploy gating |
| `L = λ·W` | which side to investigate |
| `ρ = λ/(P·μ)`, keep ≤ 0.7 | pool sizing and saturation proof |
| `amp = (r+1)^depth` | retry storm magnitude |
| `n ≥ ln α / ln(1−p)` | "is it really fixed?" |
| `Throughput ≤ 1/max(S_stage)` | head-of-line bottleneck |
| `mean = hr·C_hit + (1−hr)·C_miss` | cache hit-ratio impact |
