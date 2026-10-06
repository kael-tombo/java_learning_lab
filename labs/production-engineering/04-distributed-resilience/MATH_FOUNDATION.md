# Lab 04: Distributed Resilience — Math Foundation

Resilience without numbers is superstition with a circuit breaker. These formulas decide when to shed, how big a bulkhead is, and how much load a retry policy multiplies.

---

## 1. Queueing math: the foundation of cascading failure

M/M/c queue:

```
a = λ / μ                    offered load (traffic intensity) in Erlangs
ρ = a / c = λ / (c·μ)        utilization (per server, < 1 for stability)
```

**Stability requires `ρ < 1`.** If `λ ≥ c·μ`, arrivals outpace service and the queue grows without bound — latency → ∞, memory → ∞. This is not a slow system; it is a diverging one.

P(an arrival must wait) — Erlang C:

```
C(c,a) = ( a^c / (c! · (1−ρ)) ) / ( Σ_{k=0}^{c−1} a^k/k! + a^c/(c!·(1−ρ)) )
```

Mean waiting time in queue (Erlang-C, exponential service):

```
W_q = C(c,a) · ρ / (c·μ − λ) = C(c,a) / (c·μ(1−ρ))
```

Worked example: `λ = 500 req/s`, `μ = 20/s` (50 ms service), `c = 30` threads:

```
a  = 500/20 = 25
ρ  = 25/30  = 0.833
C(30,25) ≈ 0.71
W_q = 0.71 / (30·20·(1−0.833)) = 0.71 / 100 ≈ 7.1 ms
W   = W_q + 1/μ = 7.1 + 50 = 57.1 ms
```

**Design rule**: keep `ρ ≤ 0.7`. At `ρ = 0.833` the queue already doubles effective latency; at `ρ = 0.95` it is 10x.

Sanity table for `λ = 500/s`, `μ = 20/s`:

| c | ρ | C(c,a) | W_q | W total |
|---|---|---|---|---|
| 25 | 1.00 | — | ∞ | diverges |
| 27 | 0.93 | 0.90 | 63 ms | 113 ms |
| 30 | 0.83 | 0.71 | 7 ms | 57 ms |
| 35 | 0.71 | 0.42 | 2 ms | 52 ms |
| 50 | 0.50 | 0.13 | 0.3 ms | 50 ms |

Going 27 → 35 threads cuts p99-ish latency by an order of magnitude; 35 → 50 buys almost nothing. **Capacity planning is about the cliff, not the max.**

---

## 2. Little's Law as a resilience tool

```
L = λ · W
```

When a dependency degrades, `W` grows. With `L` (in-flight, e.g. HTTP client max connections) fixed, the system must shed load:

```
λ_max = L / W
```

Example: `L = 100` in-flight, normal `W = 0.05 s` → `λ_max = 2000 req/s`.
Dependency slows to `W = 2 s` → `λ_max = 50 req/s`. **96% of your traffic has nowhere to go but a queue.**

This is why a 20x latency degradation in a dependency behaves like a 40x traffic surge against you. Design for it:

```
required_in_flight = λ_peak × W_p99_dependency
required_in_flight(2s degraded) = 2000 × 2 = 4000   ← exceeds capacity 40x
```

The only survivable response is bounded in-flight (bulkhead) + fast rejection.

---

## 3. Retry amplification

```
amp = (r + 1)^depth
```

| retries per layer r | depth 2 | depth 3 |
|---|---|---|
| 1 | 4x | 8x |
| 2 | 9x | 27x |
| 3 | 16x | 64x |

With `amp = 16x`, a 50% capacity loss means the dependency receives `8x` its healthy load. Recovery becomes impossible — this is the mathematical definition of a retry storm.

**Retry budget** (the fix): cap retries at fraction `β` of total volume:

```
λ_total = λ_original · (1 + β) ≤ capacity
```

With `β = 0.1` and a 50% capacity loss: `0.5·1.1 = 0.55` of healthy load — survivable. Without a budget: `0.5·16 = 8x` — collapse.

---

## 4. Jitter effectiveness

Without jitter, retries synchronize: effective concurrent retry load spikes to `N·(r+1)` briefly.

Full jitter `sleep ~ U(0, min(cap, base·2^n))` desynchronizes. Expected number of clients retrying in any 100 ms window (out of N clients, backoff ~`B`):

```
E[concurrent retries] ≈ N · (window / B)
```

`N = 10,000`, `B = 1 s`, `window = 100 ms` → ~1000 concurrent retries spread evenly instead of 10,000 synchronized. **A 10x reduction in retry peak.**

Half-jitter keeps a floor (`delay/2`) — safer for latency SLOs, weaker desync. Full jitter is preferable for protecting the dependency.

---

## 5. Circuit-breaker parameter sizing

**Failure threshold and minimum volume.** Breaker opens when:

```
failure_rate_window ≥ θ  AND  volume_window ≥ v_min
```

Sizing `v_min` from statistical confidence: to distinguish a 5% error rate from 0.5% with 95% confidence, need roughly

```
v_min ≈ z²·p(1−p)/ε²  ≈  1.96²·0.05·0.95/0.045² ≈ 185 samples
```

So `v_min = 200` per rolling window is a defensible floor. `v_min = 2` (common default) trips on noise.

**Open duration.** Choose from dependency recovery time:

```
open_duration ≥ typical_recovery_time / 2
```

A dependency needing 30 s to warm caches (cold start) with `open = 5 s` will trip repeatedly — flapping breaker. Use 30–60 s and consider increasing `open` on repeated opens:

```
open_duration_k+1 = min(open_duration_k · 2, max_open)
```

**Half-open probes.** `k` probes with required success fraction `s`:

```
P(at least s·k succeed | true_recovery) = Σ_{i=s·k}^{k} C(k,i)·p_recovery^i·(1−p_recovery)^(k−i)
```

With `k = 10`, `s = 0.6`, `p_recovery = 0.9`: `P ≈ 0.998`. Safe. With `k = 2`: `P ≈ 0.19` — a coin flip per cycle.

---

## 6. Bulkhead sizing

Permit count for a dependency:

```
B = ceil( λ_peak × W_p99_dependency × safety )   capped by dependency concurrency limit
```

`λ_peak = 2000/s`, `W_p99 = 0.2 s`, safety = 1.3:

```
B = ceil(2000 × 0.2 × 1.3) = 520 permits
```

But also bound by what the dependency can actually serve concurrently:

```
B ≤ dependency_max_concurrency / concurrent_callers
```

With 20 callers and the dependency serving 200 concurrent: `B ≤ 10` per caller — this is the constraint that actually matters, and it is why per-caller bulkheads must be coordinated, not per-instance.

**Combined with a queue:** allow `q = k·B` queued requests (`k = 0.1–0.5`). `k > 1` reintroduces latency-hiding that becomes an outage; `k = 0` rejects every burst. `k = 0.2` is a common starting point.

---

## 7. Timeout budget propagation

For a call chain `A → B → C → D`, the deepest call must know its true budget:

```
t_D ≤ T_caller − (t_A_overhead + t_B_overhead + t_C_overhead + network + serialization)
```

With `T_caller = 250 ms`, overheads `20 + 15 + 10 = 45 ms`, network 3×2 ms = 6 ms, serialization 4 ms:

```
t_D ≤ 250 − 45 − 6 − 4 = 195 ms
```

**Sum-of-timeouts violation**: if each layer sets 200 ms independently, the total worst case is `200 × 3 = 600 ms > 250 ms`. The caller has abandoned; the callees are still working. Amplification factor on recovery: `600/250 = 2.4x` wasted work.

**Percentile budget check** — deadlines must cover tails, not means:

```
P(sum of p99.9 latencies ≤ T) < 1   ⇒ sum of p99.9s may exceed T
```

Practical rule: sum the *means* of downstream latency plus `3 × ` the largest downstream σ, and verify `≤ 0.6 × T_caller` — leaving 40% for retries and local work.

---

## 8. Load shedding

With capacity `μ_c = c·μ` and arrival `λ`, shed rate when saturated:

```
shed_fraction = 1 − μ_c/λ     (λ > μ_c)
```

`μ_c = 500/s`, burst `λ = 2000/s` → shed `75%`. If you cannot shed that much, you queue and the queue diverges.

For **priority shedding**, with class shares and only high-value traffic protected:

```
capacity reserved for high priority = λ_high_p99_target
shed_low = λ_total − μ_c
accept_high = min(λ_high, reserved + (μ_c − reserved))
```

The economic framing: shed the lowest `value/cost` traffic first. Cost engineering (Lab 16) makes this quantitative — an expensive query serving a 0.1%-conversion browse is a bad first sacrifice.

---

## 9. Availability and correlated failure

Independence assumption: `A = Π A_i`. With `n` replicas each `A_i = 0.99` and independent failure:

```
A(5 replicas) = 0.99^5 = 0.951   → 4.9% downtime/year  (way beyond 3-nines)
```

With correlated failure (shared zone, shared control plane, shared deploy), effective availability is closer to `min(A_i)`. **Redundancy buys nothing against correlated failure.** Quantify the correlation term:

```
A ≈ Π A_i · (1 − ρ_corr)   where ρ_corr = probability failures co-occur
```

This is why zone diversity, independent deploys, and separate control planes are resilience requirements, not availability theater.

---

## 10. Recovery math

**Queue drain time** after a burst of `B` arrivals with arrival rate `λ_a` and drain rate `μ_c`:

```
t_drain = B / (μ_c − λ_a)
```

`B = 10,000`, `μ_c = 600/s`, `λ_a = 300/s` → `t_drain = 33 s`. During that window, latency is elevated and any new fault re-triggers the queue. If your breaker `open_duration < t_drain`, you will flap.

**Retry avalanche duration** ≈ `cap × attempts × depth` (worst case). With `cap = 2 s`, `attempts = 3`, `depth = 2`: 12 s of concentrated retries per recovering client batch. Add jitter; keep monitoring for at least `3×` that.

**Brownout cost**: if service runs at 50% of normal capacity for `T` hours,

```
lost_capacity_hours = 0.5 × T × peak_rps × value_per_request
```

For `T = 6 h`, `peak = 2000 rps`, value `$0.05/request`: `0.5 × 6 × 3600 × 2000 × 0.05 = $1.08M`. This is the number that justifies chaos-engineering investment (Lab 18).

---

## 11. Reliability math for review

Availability over a period with `n` incidents of duration `d_i`:

```
A = 1 − (Σ d_i) / period
```

Error budget for SLO 99.95%/month (30 days):

```
allowed_down = 0.0005 × 2,592,000 s = 1296 s = 21.6 min/month
```

One 25-minute degradation exhausts the month. One 5-minute blip uses 23%. This converts "we should improve resilience" into a budget conversation.

MTBF/MTTR:

```
MTBF = 1/λ_failure       MTTR = mean time to detect + diagnose + mitigate
availability = MTBF / (MTBF + MTTR)
```

With `MTBF = 30 days` and `MTTR = 1 h`: `A = 720/744 = 96.8%`. **Reducing MTTR is often cheaper than increasing MTBF** — a 4x MTTR improvement (to 15 min) yields `A = 98.0%`.

---

## 12. Coordinated omission correction

For a closed-loop generator, the reported p99 understates the true p99. Corrected percentile (HdrHistogram / Gil Tene):

```
corrected_latency = recorded_latency + (ideal_interval_count − actual_interval_count) × interval
```

Worked: ideal 1,000 req/s for 60 s = 60,000 completions. Generator records only 40,000 because it self-throttles; at the 99th percentile recorded = 800 ms:

```
missing = 20,000 samples → the true p99 is the 60,000th value overall,
not the 39,600th of the recorded set.
```

Rule: **all latency claims from load tests must state whether the generator was open-loop (arrival schedule independent of response) or closed-loop.** Closed-loop without correction is not evidence about p99.

---

## 13. Quick drills

1. `λ = 500/s`, `μ = 20/s`, `c = 27` → `ρ = ?` **Answer: 0.926. p99-ish latency ~113 ms; unstable at c = 25.**
2. In-flight `L = 100`, dependency `W = 2 s` → max sustainable λ? **Answer: 50 req/s (vs 2000 healthy).**
3. 2 retries, depth 2 → amplification? **Answer: 9x. With 50% capacity, 4.5x healthy load — collapse.**
4. `λ_peak = 2000`, `W_p99 = 0.2 s`, safety 1.3 → bulkhead? **Answer: 520 permits, before the dependency's own concurrency limit binds.**
5. SLO 99.95%/month → allowed downtime? **Answer: 21.6 min. One 25-min incident exhausts the budget.**
6. `MTBF = 30 d`, `MTTR = 1 h` → availability? **Answer: 96.8%. MTTR to 15 min → 98.0%.**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `ρ = λ/(c·μ)`, keep ≤ 0.7 | stability and latency cliff |
| `C(c,a)`, `W_q = C/(c·μ(1−ρ))` | expected queueing delay |
| `λ_max = L/W` | capacity collapse under slow dependency |
| `amp = (r+1)^depth` | retry storm magnitude |
| retry budget `β ≤ 10%` | surviving partial outages |
| `B = λ_peak·W_p99` | bulkhead permit count |
| `A = MTBF/(MTBF+MTTR)` | where to invest |
| `t_drain = B/(μ_c − λ_a)` | recovery time; sets breaker `open` duration |
| `shed = 1 − μ_c/λ` | how much to shed at peak |
