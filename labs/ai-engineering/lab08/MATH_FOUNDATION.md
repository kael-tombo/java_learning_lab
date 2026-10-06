# Lab 08: AI Observability — Math Foundation

## 1. Cost Attribution

```
cost_per_request = in_tok*p_in + out_tok*p_out + emb*p_emb + rerank*p_rr + gpu_ms*p_gpu
```

Worked example (RAG request, `$3/M` in, `$15/M` out, `$1/M` rerank, `$0.02/M` embed):

| Line | Tokens | Cost | Share |
|------|--------|------|-------|
| Input | 4,200 | $0.0126 | 50% |
| Output | 180 | $0.0027 | 11% |
| Rerank | 10,000 | $0.0100 | 40% |
| Embed | 1,500 | $0.00003 | 0.1% |
| **Total** | | **$0.0253** | |

The intuitive lever (shorter answers) is 11%. The non-obvious one (rerank `k`) is 40%.
**Measure the breakdown before optimizing.**

Reconciliation: monthly meter total vs invoice. Discrepancy `d` implies either
systematic misattribution or untracked calls; above 2%, every optimization number derived
from the meter is suspect.

## 2. Cost per Successful Outcome

```
cost_per_outcome = cost_per_request / success_rate
```

At `c = $0.0253`:

| success | cost/outcome | vs baseline |
|---------|--------------|-------------|
| 1.00 | $0.0253 | — |
| 0.95 | $0.0266 | +5.3% |
| 0.90 | $0.0281 | +11% |
| 0.82 | $0.0309 | +22% |
| 0.75 | $0.0337 | +33% |

Sensitivity is unbounded as `s -> 0`, and the derivative is
`-c / s^2`: at `s = 0.9` the marginal cost of quality is `c/0.81`, about 23% more per
point than at `s = 1.0`. **Quality work gets more valuable as accuracy drops**, which is
why quality regression and cost regression should share an alert.

## 3. Percentile Estimation

For an unbounded stream, reservoir sampling of size `k` gives an unbiased sample.
The `m`-th order statistic of `k` samples estimates the `m/(k+1)` quantile.

Standard error of the quantile estimate is approximately

```
SE(p_hat) ~ sqrt( p(1-p) / (k * f(x_p)^2) )
```

where `f` is the density at the target quantile. **Tail percentiles are the problem**:
`f(x_0.99)` is small, so `SE` explodes. With `k = 1,000` and a lognormal latency
distribution, p99 is far noisier than p50. t-digest or KLL sketches exist for exactly
this reason; a plain reservoir is acceptable only for medians.

Reported practice: always publish the sketch type and `k` next to any percentile.

## 4. Sampling Budget

Given an eval budget `B`, judge cost `c_j`, and a target interval half-width `h` on a
metric of variance `sigma^2`:

```
n = (z*sigma/h)^2
required_budget = n * c_j
affordable_h = z*sigma / sqrt(B / c_j)
```

Example: `sigma = 0.4, c_j = $0.02, B = $2,000`:
`n = (1.96*0.4/0.05)^2 = 246`; cost = `$4.92`; the remaining budget buys precision on
other strata. So a $2,000/day eval budget at $0.02 per judge call affords roughly 100,000
judgements per day — about 0.1% of traffic at 100k requests/day, so the sampling plan
must allocate deliberately rather than uniformly.

## 5. Stratified Sampling Variance

With strata `g` of size `N_g`, mean `mu_g`, variance `sigma_g^2`, and allocation
`n_g`:

```
Var(mean) = sum_g (N_g/N)^2 * sigma_g^2 / n_g
```

Optimal allocation (Neyman) sets `n_g proportional to N_g * sigma_g`: oversample
high-variance strata. Error strata are usually high-variance, so oversampling them
both improves the estimate and feeds the fix queue — which is why the same sample can
serve both purposes, provided the strata are reported separately.

## 6. PSI

```
PSI = sum_i (p_i - q_i) ln(p_i/q_i)
```

Small deviation: substituting `p = q + delta` and expanding the logarithms,

```
PSI ~ sum_i delta_i^2 / q_i
```

For 10 equal bins each shifted 10% relatively: `PSI ~ 10 * (0.1)^2 = 0.10` — exactly at
the investigate threshold. For bins shifted 25%: `PSI ~ 0.63`, well into "major".

A single bin moving from 5% to 40% while others adjust: the KL term dominates and PSI
exceeds 0.5 immediately. **Rare-category appearance or disappearance is the strongest
drift signal**, which is why empty bins are floored in code rather than skipped.

## 7. Retry Amplification

```
E[attempts] = 1 / (1 - p_retry)
```

| p_retry | E[attempts] |
|---------|-------------|
| 0.10 | 1.11x |
| 0.20 | 1.25x |
| 0.35 | 1.54x |
| 0.50 | 2.00x |

Under saturation, timeouts and retries are positively correlated: load rises, timeouts
rise, retries rise, effective `p_retry` rises, more load. The fixed point is collapse.
Detecting `attempts/request > 1.2` is early warning; waiting for the invoice is late.

## 8. Guardrail Attribution

For `L` layers and `F` failures, each attributed to the first layer that caught it:

```
attribution(i) = F_i / F,   sum_i attribution(i) = 1
```

If 15% fail at L1, 22% at L2, 48% at L3, 73% at L4, 22% at L5, and 20% uncaught (over
100 due to multiple-attribution rounds — in a single-shot attribution it sums exactly to
1), the interpretation is that L3 and L4 carry the system and L1/L2 are under-invested.

The uncaught fraction is the most important number: it is the measured attack surface
that has no defence.

## 9. Observability Cost

```
obs_cost/day = spans_per_day * span_cost
            + series_count * resolution_samples * price
            + judge_calls * c_judge
```

Span count scales with throughput. Sampling reduces it proportionally but reduces
debuggability. A common compromise: sample 100% of errors and 1-5% of successes, which
preserves the failure signal at a fraction of the volume.

Metric cost is driven by **series count** (labels' cardinality product), not by sample
count. Ten labels with four bounded values each = up to 10,000 series; one label with
10,000 distinct values = 10,000 series for one metric. Bounded labels are the whole game.

## 10. Anomaly Detection with Seasonal Baselines

For a metric with weekly seasonality, model `x(t) = trend * seasonal * noise`. Residual
score:

```
r(t) = (x(t) - median(seasonal_window(t))) / MAD(seasonal_window(t))
```

Alert when `|r| > 3` for several consecutive windows. The median/MAD form is robust to
the very spikes you are trying to detect, which a mean/sigma baseline is not — a single
outlier inflates sigma and hides the next one.

## 11. Anomaly Rate and Precision

With `F` failures per quarter and a gate that must block regressions:

```
blocked_regressions / total_regressions = detection rate
true_regressions / total_blocks = block precision
```

A gate that blocks on noise has low precision, and the team learns to retry the deploy
until it passes — which converts a gate into a suggestion. Target block precision above
80% and detection rate above 90% for safety categories; quality gates may accept lower
detection in exchange for near-perfect precision.

## Worked Numbers

Platform with 50,000 requests/day, average `c = $0.0253`, success rate `s = 0.82`.

- Daily spend: `50,000 * 0.0253 = $1,265`.
- Cost per outcome: `0.0253/0.82 = $0.0309`.
- A 5-point success drop (`0.82 -> 0.77`) at constant cost: `$0.0329`, **+6.3%**. At
  constant *budget*, serving the same volume requires more requests, so cost rises by
  `0.82/0.77 = 1.065`.
- Eval budget `$2,000/day`, judge `$0.02`, target `h = 0.05`, `sigma = 0.4`:
  `n = 246` judgements per stratum.
- With one random stratum plus three targeted strata at 1/3 the size each: total
  `246 * (1 + 3/3) = 492` judgements = `$9.84/day`. The remaining ~$1,990 buys a weekly
  full-judge pass over ~7,400 items, i.e. roughly 15% of a day's traffic per week.
- Retry ratio at 20% timeout with 3 retries: `1.25x`. Offered load becomes 62,500
  equivalent requests/day, pushing utilization past the target and triggering shedding —
  which is exactly the incident pattern seen in the field.
- PSI: intent mix shifting 3 points in one of 10 buckets gives `PSI ~ 0.09`, below
  threshold; 8 points gives `PSI ~ 0.64`, major. So a 10% relative shift in a single
  bucket is a genuine alarm, not rounding.

## Self-Check Questions

1. Recompute the cost breakdown if rerank drops from 50 to 20 candidates.
2. Compute cost per outcome at `c = $0.01`, `s = 0.60` versus `s = 0.95`.
3. Derive `E[attempts]` at `p_retry = 0.45`.
4. Compute PSI for 5 bins moving from `[0.2]*5` to `[0.6, 0.1, 0.1, 0.1, 0.1]`.
5. Show that removing one bounded label of cardinality 4 reduces series count by how
   much.