# Lab 06: AI Pipeline Orchestration — Math Foundation

## 1. Latency Composition

For a sequential chain:

```
T_total = sum_i T_i
```

For a DAG with parallel branches, latency follows the **critical path**:

```
T_total = max over paths P of ( sum_{i in P} T_i )
```

Example: `ingest(50ms) -> validate(20ms) -> [transform(200ms) || embed(300ms)]
-> infer(800ms) -> emit(30ms)`

- Critical path: `ingest + validate + embed + infer + emit = 1200 ms`.
- The `transform` branch (200 ms) fits inside `embed` (300 ms) and adds nothing.

**Optimizing a non-critical stage is wasted work** — the most common pipeline
optimization mistake, and the reason critical-path analysis matters more than
per-stage profiling.

## 2. Throughput

For a stage with service time `T_i` and concurrency `c_i`:

```
throughput_i = c_i / T_i
pipeline_throughput = min_i throughput_i
```

The pipeline runs at the throughput of its slowest stage, which makes stage-level
bottleneck analysis a routing decision: which stage do you add capacity to?

With `ingest 50ms/c=4 -> 80/s`, `validate 20ms/c=4 -> 200/s`, `embed 300ms/c=8 ->
26.7/s`, `infer 800ms/c=16 -> 20/s`: pipeline throughput is `20/s`, limited by
inference. Adding ingest concurrency achieves nothing.

## 3. Utilization and Queueing

```
rho_i = arrival_rate / (c_i / T_i)
```

At `rho = 0.9` the mean wait is `10 * T_i`; at `0.6` it is `2.5 * T_i`. Same as any
queueing system, which is why **queue depth is a leading indicator** for scaling and
GPU utilization is a lagging one.

## 4. Little's Law per Stage

```
L_i = lambda * W_i     (items in stage i = throughput * total time in stage)
```

Total residency for a sequential pipeline is `W_total = sum W_i`, so

```
L_total = lambda * sum_i W_i
```

Memory needed for in-flight work is therefore proportional to latency sum, not to any
single stage. Adding a 200 ms stage increases memory residency by
`lambda * 0.2` items — visible under load, invisible in a single-run benchmark.

## 5. Amdahl for Stage Optimization

If a stage accounts for fraction `f` of total latency and you speed it up by factor `s`:

```
T_new = T_total * (1 - f + f/s)
speedup = 1 / (1 - f + f/s)
```

For `f = 0.67` (inference in the 1200 ms path) and `s = 2`: `speedup = 1/(0.33+0.335) =
1.50`. Halving inference time gives 1.5x, not 2x. Optimizing the 50 ms ingest stage
gives essentially nothing.

## 6. Cache Benefit

```
speedup_i = 1 / (1 - h_i + h_i/s_i)
```

with `h` the hit rate. With `h = 0.7` and a cached stage 10x faster:
`speedup = 1/(0.3+0.07) = 2.70`.

Memory cost: a cache of `C` entries with average size `S` bytes costs `C*S`. To be
worth it, the saved compute must exceed the memory pressure:

```
cache_worthwhile: h * C_recompute > C_mem * price_of_memory
```

A 70% hit rate on an expensive embed stage almost always qualifies; on a 20 ms
validate stage, almost never. **Cache the expensive deterministic stages.**

## 7. Error Budget Allocation

If each stage has failure probability `p_i` and the pipeline requires end-to-end
reliability `R`:

```
prod_i (1 - p_i) >= R
```

With `R = 0.999` and `k` stages, the average per-stage budget is
`p_i <= 1 - R^(1/k)`. For `k = 6`: `p_i <= 1.7e-4`. Budget accordingly, and spend it
where recovery is possible: a retried transient failure costs nothing in reliability,
while a validation rejection is a permanent failure.

## 8. Retry Amplification

With retry probability `p_r` and bounded attempts `m`:

```
E[attempts] = (1 - p_r^(m+1)) / (1 - p_r) ~ 1/(1-p_r)
```

Amplification multiplies downstream load. With `p_r = 0.3` and `m = 3`: `1.43x` per
failing stage. Five stages each amplifying `1.43x`: `6x` load on the deepest stage
during an incident. **Retry budgets must be global, not per stage**, or retries
cascading through a pipeline will look like a traffic spike.

## 9. Backpressure Goodput

Under overload with load shedding at threshold `k`:

```
goodput = min(1, k/service_rate) * service_rate * success_rate
```

Expressing it as `k` when `k < service_rate`: serving `k` requests perfectly beats
serving `service_rate` requests where `1 - 1/k` of them fail from resource exhaustion.
Shedding at 80% utilization keeps 100% success; running at 100% utilization typically
yields 60-70% success because of timeouts and retries. **Shedding early is strictly
better.**

## 10. Partial Failure Cost

For fan-out over `n` items with per-item failure `p`, and aggregate policies:

```
all_or_nothing:   E[value] = (1-p)^n * V          -> collapses fast
best_effort:      E[value] = (1 - p^k) * V          (k = min required)
fractional:       E[value] = (1-p) * V
```

At `p = 0.1, n = 10`: all-or-nothing yields `0.349`; best-effort with `k=3` yields
`0.999`. The policy is worth orders of magnitude, so it must be declared rather than
defaulted.

## 11. Batching Economics

Batching `n` items into one call:

```
T_batch(n) = T_fixed + n * T_marginal
T_per_item(n) = T_fixed/n + T_marginal
```

Latency per item decreases with `n` while `T_fixed` dominates, so there is an optimal
batch size determined by the latency budget. If the SLO is 200 ms and `T_fixed = 120 ms`
with `T_marginal = 8 ms`, then `n = (200-120)/8 = 10` per batch for latency, while
throughput wants more. **Two different optima**, resolved by whether the endpoint is
latency- or throughput-sensitive.

## 12. Cost Attribution

```
cost_per_request = sum_i cost_i
```

with per-stage costs: compute (`ms * rate`), tokens (`tokens * price`), and external
calls (per request). The stage with the largest cost share is where optimization pays
— and it is frequently token-consuming stages in a generation pipeline, not the
"interesting" feature stages.

## Worked Numbers

Chain: `ingest(50, c=4) -> validate(20, c=4) -> transform(200, c=8) || embed(300, c=8)
-> infer(800, c=16) -> emit(30, c=8)`

**Latency**: critical path `50 + 20 + 300 + 800 + 30 = 1200 ms`. Halving `transform`
to 100 ms changes nothing (it is off the path). Halving `embed` to 150 ms gives
`1050 ms`, a 1.14x speedup.

**Throughput**: per stage `c/T`: ingest 80/s, validate 200/s, transform 40/s,
embed 26.7/s, infer 20/s, emit 267/s. Pipeline = **20/s**, limited by inference.

**Amdahl**: inference is `f = 800/1200 = 0.667` of latency. A 2x inference speedup
gives `1/(0.333+0.333) = 1.50x`; a 4x gives `1/(0.333+0.167) = 2.0x`.

**Error budget**: `R = 0.999`, `k = 6` -> `p_i <= 1.7e-4` per stage. A stage at
`1e-3` failure with retries at 90% success has an effective `1e-4`, which fits; the
same stage without retries does not.

**Cache**: embedding at 70% hit rate with a 5x cheaper recompute gives
`1/(0.3+0.14) = 2.27x` on that stage, and `300 ms -> 132 ms` on the critical path,
giving `1200 -> 1032 ms`.

**Backpressure**: at 25 rps arrival with 20/s service, shedding at 18/s keeps 100%
success on 18 requests/s. Running unbounded yields 25 admitted with timeouts and
retries; observed goodput is typically 13-15/s. Shedding wins.

## Self-Check Questions

1. Compute the critical path latency for a diamond DAG: `A(100) -> B(50), C(200) ->
   join -> D(400)`.
2. Find the bottleneck stage for `c/T` values of 40, 120, 25, 200.
3. Compute the Amdahl speedup for `f = 0.4`, `s = 5`.
4. Compute `E[value]` for all-or-nothing vs best-effort(k=2) at `p=0.15, n=8, V=1`.
5. Derive the retry amplification across 4 stages at `p_r = 0.25`.