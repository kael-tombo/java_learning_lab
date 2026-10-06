# Lab 05: Prompt Engineering at Scale — Math Foundation

## 1. Sample Size for a Proportion

For an observed rate `p̂` from `n` samples, the Wald 95% half-width is

```
h = 1.96 * sqrt(p̂(1-p̂)/n)
```

Worst case at `p̂ = 0.5`:

```
h = 0.98/sqrt(n)   ->   n = 960/h^2   for h in proportion units
```

For a desired resolution `d` in percentage points (`h = d/100`):

```
n = 960 / (d/100)^2 * ...   ->   n ≈ 960/d^2   with d in points
```

| Resolution | n |
|-----------|---|
| 20 pts | 2 |
| 10 pts | 10 |
| 5 pts | 38 |
| 3 pts | 107 |
| 2 pts | 240 |
| 1 pt | 960 |

The `5 pts -> 38` row is a trap: that is a **proportional** resolution. Detecting a
5-point *absolute* change on a base rate of 80% (80% -> 85%) needs far more, because the
comparison is against a known baseline. Treat the table as a lower bound and compute the
required `n` from the actual expected rates.

Wilson intervals beat Wald for small `n` or `p̂` near 0 or 1, where Wald can produce
impossible bounds below 0.

## 2. Paired Variance Reduction

Let `d_i = a_i - b_i` be the per-item score difference. The paired standard error is

```
SE_paired = sd(d) / sqrt(n)
```

versus the unpaired

```
SE_unpaired = sqrt( (sd(a)^2 + sd(b)^2) / n )
```

With items positively correlated between systems (`corr(a,b) = rho`):

```
sd(d)^2 = sd(a)^2 + sd(b)^2 - 2*rho*sd(a)*sd(b)
```

So for `sd(a) = sd(b) = s` and `rho = 0.8`:

```
sd(d)^2 = 2s^2 (1 - 0.8) = 0.4 s^2     -> sd(d) = 0.632 s
SE_ratio = sqrt(0.4/2) = 0.447
```

**The paired test needs 4.5x fewer items for the same precision.** This is why comparing
a candidate against the incumbent on identical items is not a nicety.

## 3. Win Rate with Ties

Discarding ties inflates the win rate. Correct handling:

```
b = #(variant wins), c = #(control wins), t = ties, N = b + c + t
head_to_head = b / (b + c)                        among decisive comparisons
overall       = (b + 0.5*t) / N                   treats ties as half
```

Report both. `overall` is the honest number when ties are common (many prompts produce
identical output for easy items), and `head_to_head` is what stakeholders expect. The gap
between them is a useful diagnostic: a large gap means the variant mostly ties rather
than wins.

## 4. Bootstrap Confidence Interval

```
for b in 1..B:
    I_b = random indices with replacement
    delta_b = mean(score_variant[I_b] - score_control[I_b])
CI = [percentile_2.5(delta), percentile_97.5(delta)]
```

With `B = 10,000` and items resampled **together** (same index for both systems), the
pairing is preserved. Independent resampling destroys the covariance cancellation and
inflates the interval by up to `1/sqrt(1-rho^2)`.

## 5. Ladder Sample Budget

With per-step minimum `n` and traffic fractions `f_i`:

```
total_requests = n * sum_i (1/f_i)
```

For 1/5/25/100 with `n = 400`: `400 * (100 + 20 + 4 + 1) = 50,000` requests.

At 50k requests/day: 1 day. At 2k/day: 25 days. Low-volume products must use shadow
evaluation to build the sample size cheaply.

## 6. Cost per Correct Outcome

```
cost_per_correct = cost_per_request / accuracy
```

A 5-point accuracy improvement at 2x cost is a **net loss**:

```
baseline: 0.01 / 0.80 = 0.01250
variant:  0.02 / 0.85 = 0.02353      nearly 2x worse
```

The comparison that decides prompt changes is therefore always the pair
`(accuracy, cost)`, never accuracy alone. Plot both; the efficient frontier is what
gets shipped.

## 7. Rollout Risk

```
expected_cost = blast_radius * impact_per_affected_request * detection_delay
```

With `blast_radius` from feature-flag scope. A prompt at 1% canary has 1% of the
expected cost of a 100% release — which is the argument for long dwells at low traffic
rather than fast progression.

## 8. Drift Significance

PSI over binned distributions:

```
PSI = sum_i (p_i - q_i) ln(p_i/q_i)
```

Small-deviation behaviour: `PSI ≈ sum (delta^2 / q)`. For 10 equal bins each shifted
by 10% relatively: `PSI ≈ 10 * (0.1)^2 = 0.1` — right at the "investigate" threshold.
So a 10% uniform shift is a genuine signal, not rounding noise.

## 9. Multiple Comparisons

Comparing `m` variants against one control at level `alpha` inflates the family-wise
error rate:

```
P(any false positive) = 1 - (1 - alpha)^m
```

At `m = 10, alpha = 0.05`: `0.40`. Four in ten comparisons will look significant by
chance. Bonferroni correction (`alpha/m = 0.005`) or Holm's step-down procedure is
required for a multi-variant sweep, and the report must state which was used.

## 10. Judge Agreement Calibration

If a judge agrees with humans at rate `p_j`, then measured win rates are biased toward
the judge's own preferences. With `p_j = 0.8`:

```
observed_delta ≈ true_delta * (2*p_j - 1) = true_delta * 0.6
```

So a measured 6-point improvement corresponds to roughly 10 points of true delta. Judge
agreement is a **correction factor** on effect size, not just a quality gate.

## 11. Prefix Cache Savings

```
savings = prefix_fraction * hit_rate * (1 - cached_price_fraction)
```

If a template change accidentally moves a timestamp into the prefix, `prefix_fraction`
collapses to 0 and savings go to zero instantly. Hit rate is therefore a **deployment
bug detector**, not merely a cost metric.

## 12. Prompt Portfolio Optimization

With `n` prompts and a fixed quality floor `Q_min`, minimize total cost:

```
minimize  sum_i cost_i(p_i)
subject to sum_i w_i * quality_i(p_i) >= Q_min
         sum_i traffic_i = 1
```

This is a linear program. The dual prices are the marginal cost of a quality point per
prompt, which tells you where optimization effort is worth spending. In practice this
reduces to: optimize the highest-traffic prompts first, then the lowest-headroom ones.

## Worked Numbers

Support assistant: 50k requests/day, 12 intents, prompt families per intent.

**Experiment sizing.** To detect a 5-point absolute change on a base rate of 0.80:

```
Wald on the difference: SE = sqrt( p1(1-p1)/n + p2(1-p2)/n )
                        = sqrt( 0.8*0.2/n + 0.85*0.15/n ) = sqrt( 0.2875/n )
n for a 0.05 half-width at 95%:  (1.96*0.536/0.05)^2 = 442
```

So `n ≈ 440` per variant per intent for a 5-point absolute change. For a pooled
measurement across 12 intents (traffic-weighted), a 3-point change needs ~2,000 items.

**Ladder time.** `n = 440`, ladder 1/5/25/100: `440 * 125 = 55,000` requests.
At 50k/day: **1.1 days**. At 2k/day: 27.5 days -> shadow evaluation mandatory.

**Cost per correct.** Current: `$0.004/request, 0.80 accuracy` -> `$0.005/correct`.
Variant A: `$0.0045, 0.83` -> `$0.00542` (worse).
Variant B: `$0.0035, 0.81` -> `$0.00432` (**12% better**).
Variant A is the "accuracy winner" and loses on the metric that matters.

**Multi-variant sweep.** 8 variants vs control at `alpha = 0.05`: family-wise error
`1 - 0.95^8 = 0.34`. With Bonferroni at `0.00625`, a measured 4-point delta may not
survive.

## Self-Check Questions

1. Compute `n` to detect a 7-point absolute change from 0.70 to 0.77 at 95%.
2. Show the paired SE ratio for `rho = 0.6`.
3. Compute `expected cost/correct` for `$0.01/0.75` and `$0.008/0.79`.
4. Compute the family-wise error for 6 comparisons at `alpha = 0.05`.
5. Compute total requests for a ladder 2/10/50/100 with `n = 300`.