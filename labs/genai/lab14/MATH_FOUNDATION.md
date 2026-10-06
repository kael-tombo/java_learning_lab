# Lab 14: LLMOps (LLM Operations) — Math Foundation

## 1. Percentiles Without Sorting Streams

For p50/p95/p99 over an unbounded stream, use a hierarchical sketch:

```
first level:  uniform random reservoir of size k  (unbiased sample)
second level: t-digest / KLL  (cluster by value; bound accuracy per quantile)
```

For the reservoir of size `k`, the `m`-th order statistic has expected value

```
E[X_(m)] = mu + sigma * Phi^{-1}( m / (k+1) )
```

so with `k = 1000`, estimating the 95th percentile uses roughly the `951`-th order
statistic of a 1,000-sample reservoir. Standard error of the estimate is roughly

```
SE(p) ~ (1 / f(x_p)) * sqrt(p(1-p) / k)
```

where `f` is the density at the target quantile. Practical rule: for tail percentiles
you need `k` large — `k = 1000` gives p99 to roughly ±1 point on a smooth
distribution, and much worse on a heavy tail (which latency distributions are).

## 2. Sample Size for a Proportion

For an observed rate `p̂` from `n` samples, the 95% Wald interval half-width is

```
h = 1.96 * sqrt(p̂(1-p̂)/n)
```

Worst case at `p̂ = 0.5`: `h = 0.98/sqrt(n)`.

```
n    half-width   resolves a ...
100     9.8 pts    10-point change
400     4.9 pts    5-point change
1000    3.1 pts    3-point change
2500    2.0 pts    2-point change
```

Rule: to resolve a `d`-point change you need `n ≈ 960/d²`. For a 5-point gate,
`n ≈ 385`. This is why "we looked at 40 responses and it looked fine" is not evidence.

Wilson intervals are preferred over Wald for small `n` or `p̂` near 0 or 1, because
Wald can produce impossible bounds.

## 3. Paired Comparison for Canary Gates

Canary and control serve the same users' *distribution*, so treat the comparison as
paired on item characteristics rather than independent:

```
delta_i = score_i(candidate) - score_i(control)
delta_bar = mean(delta_i)
SE = std(delta) / sqrt(n)
CI = delta_bar +- 1.96 SE
```

With heterogeneous `delta_i` (some items improve a lot, some regress), `std(delta)`
is large and you need more samples than a simple proportion test suggests. Compute
`std(delta)` empirically from a pilot; do not assume a Bernoulli model.

## 4. Sequential Testing

Stopping a canary as soon as it looks bad saves time but inflates false positives.
Group-sequential boundaries (Lan-DeMets spending function) are the standard fix:

```
z_alpha(k) boundary widens with the number of looks
budget: spend 5% total alpha across all looks
```

Practical simplification: require both (a) a breach of the point estimate and
(b) `p < 0.01` on the one-sided test, plus a minimum sample size. This is
conservative and appropriate for a canary, where a false rollback costs a little
time and a false ship costs an incident.

## 5. Drift: PSI

```
PSI = sum_i (p_i - q_i) * ln(p_i / q_i)
```

Derivation: `PSI = KL(p||q) - KL(q||p)` symmetrized to a pointwise form. Properties:
`PSI >= 0`, zero iff `p = q`, and it grows quadratically for small deviations:

```
p = q + delta  ->  PSI ≈ sum delta² / q
```

so for `delta/q = 0.1` on 10 bins: `PSI ≈ 10 * 0.01 = 0.1`. A uniform 10% shift
across all bins lands exactly at the "significant" boundary — a useful calibration.

```
PSI < 0.10   stable
0.10 - 0.25  moderate shift, investigate
> 0.25       major shift
```

Binning matters: quantile bins (10-20) are more sensitive than equal-width for skewed
distributions such as prompt length.

## 6. Drift vs Quality

There is no guarantee that drift changes quality. The operational chain is:

```
drift -> does quality change? -> measure
```

So drift alerts trigger **investigation**, not automatic rollback. Quality regression
triggers rollback. Conflating them produces alarm fatigue; separating them keeps
drift alerts useful.

## 7. Cost per Successful Outcome

Let `q` be the per-request success probability and `c` the cost per request:

```
cost_per_success = c / q
```

Sensitivity to `q` is unbounded: at `c = $0.01`,

```
q = 1.00   ->  $0.0100
q = 0.90   ->  $0.0111   (+11%)
q = 0.75   ->  $0.0133   (+33%)
q = 0.50   ->  $0.0200   (+100%)
```

A 10-point quality drop doubles cost per success. This is the quantitative reason
quality gates belong in cost discussions: they are the same conversation.

Compare across configurations:

```
qac = q / c     quality per cent
```

## 8. Sampling Budget Allocation

Given a judging budget `B` and `c_j` per judge call, choose rates `r_g` per segment:

```
subject to   sum_g N_g * r_g * c_j <= B
maximize     sum_g N_g * r_g * Var_g          (variance reduction)
```

Uniform allocation minimizes the variance of the overall estimate; targeted
allocation minimizes the number of *known* defects. Use both: uniform for the
headline metric, targeted for the fix queue, reported separately.

## 9. Time-to-Diagnose in Drills

For an incident drill with `T_alert`, `T_triage`, `T_diagnose`, `T_contain`:

```
MTTD = T_alert + T_triage + T_diagnose
MTTC = MTTD + T_contain
```

Model the diagnosis step as a decision tree:

```
E[search cost] ≈ sum over nodes of (P(node reached) * time_at_node)
```

so pre-writing the top three branches at each node removes most of the search. A
runbook with a per-alert first question, owner, decision tree, and tested
containment action typically cuts `T_diagnose` by 5-10x versus free-form
investigation.

## 10. Error Budget and Release Freeze

With an SLO of 99.9% monthly availability, the monthly error budget is

```
budget = 0.001 * requests_per_month
```

Burn-rate alerting: freeze releases when the short-window error rate consumes budget
faster than `14.4x` the sustainable rate (the standard multi-window approach):

```
burn_rate = observed_error_rate / sustainable_rate
freeze if burn_rate > 14.4 for 1h  AND  > 6 for 6h
```

The point for LLM systems: **quality and safety have error budgets too**
(refusal rate regression, citation validity below floor). Freeze on those too.

## 11. Cache Hit Rate Impact

Let `h` be the prefix-cache hit rate, `S` the stable-prefix tokens, `V` volatile:

```
cached_discount = h * (S/(S+V)) * (1 - alpha)
```

If a deployment changes the prompt template and a timestamp enters the prefix,
`S` effectively becomes `0` and the discount collapses. Hit rate collapse is
therefore a **deployment bug detector**, not just a cost metric.

## 12. Retry Amplification

With a retry probability `p` per failure and a retry causing another attempt:

```
expected_attempts = sum_{k>=0} p^k = 1 / (1 - p)
```

`p = 0.2` -> 1.25x. `p = 0.5` -> 2x. `p = 0.9` -> 10x. Under load, timeouts
correlate with saturation, which increases `p` — a positive feedback loop:

```
saturation -> timeouts -> retries -> more load -> more saturation
```

Detect by monitoring `attempts / requests` per trace. A ratio above 1.2 sustained is
a retry storm.

## 13. Load Shedding Priority

Let traffic be `interactive` (SLO 400ms), `standard`, and `batch` (no SLO):

```
shed order: batch -> standard long-context -> standard -> interactive (last)
protected_fraction = interactive_requests / total
```

With traffic mix 10% interactive, 40% standard, 50% batch, shedding 50% protects:

```
protected = 10% interactive + 20% of the standard half = 50% of total good traffic
```

Always protect interactive; a batch tier that has no SLO is the correct shock
absorber.

## 14. Rollout Math

With per-step gates and a requirement of `n` samples per step:

```
total_requests_to_full = n * (1/0.01 + 1/0.10 + 1/0.50 + 1)
                       = n * (100 + 10 + 2 + 1) = 113 n
```

With `n = 400` (resolving a 5-point change): `45,200` requests before the ladder
finishes. For a low-traffic product, that may be days. Practical adaptations:
shadow evaluation to build sample size cheaply, longer dwell at 1%, or relax the
gate at low steps with a compensating stricter gate later.

## Worked Numbers

Product: 50k requests/day, 20k interactive, 10k standard, 20k batch. Cost per request
`$0.004`, success rate `q = 0.82`.

- Cost/day: `50,000 * 0.004 = $200`; `cost per success = 0.004/0.82 = $0.00488`.
- Quality drops 5 points to `q = 0.77`: `0.004/0.77 = $0.00519`, **+6.4%** cost per
  success for what looks like a small quality change.
- Under a 30% overload, shedding batch first absorbs it: shed 15k batch, protect
  `35k` requests (70%).
- Canary ladder with `n = 400` per step: `45,200` requests = 21 hours at this volume.
  Acceptable; at 2k requests/day it would take 22 days — so shadow eval becomes
  mandatory, and that is a volume-driven architectural decision.
- PSI check: intent mix shifted 3 points in one bucket out of 10 -> `PSI ≈ 0.09`,
  below threshold. Shift 8 points -> `PSI ≈ 0.64`, major shift. So a 10% relative
  shift in one bucket is a genuine alert, not a rounding artefact.

## Self-Check Questions

1. Compute the sample size to resolve a 2-point change on a rate near 0.5.
2. Derive the quadratic small-deviation behaviour of PSI.
3. Show that a 10% relative shift in one of 10 bins gives `PSI ≈ 0.1`.
4. Compute expected attempts at `p = 0.35` and explain the feedback loop.
5. Derive total requests for a canary ladder with `n` and steps 1/10/50/100%.