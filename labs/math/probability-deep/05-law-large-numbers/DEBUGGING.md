# Debugging: Law of Large Numbers and CLT

### Symptom: sample mean never settles as n grows
Check the assumptions in order: (1) does E|X| exist? (sample of a Pareto with α ≤ 1 wanders forever); (2) is the variance finite (α ≤ 2 → mean's SE isn't σ/√n); (3) are draws independent (autocorrelated series drift together); (4) is there an accumulating bug — e.g. summing in float32 over 10⁸ values loses precision (pairwise/Kahan summation fixes it). Diagnose with a QQ-plot of block means: normal ⇒ CLT active, heavy tail ⇒ stable law.

### Symptom: measured SE doesn't shrink by 2 when n × 4
Run the same simulation at n and 4n: SE must halve (σ/√n). If it doesn't: draws aren't i.i.d. (shared RNG state across parallel workers — each thread got the *same* seed), n was silently capped, or you measured the SE of a single path instead of across independent replications (SE of a mean is estimated across R replications, not along one path).

### Symptom: 95% CI covers the truth 88% of the time
Undercoverage means the SE is understated: usually dependence (using n instead of n_eff = n/(1 + 2Σρₖ)), estimated parameters (σ estimated from the same data adds a df correction the normal interval ignores — use t), or selection (reporting only the interval for the best of k metrics: 1 − 0.95¹⁰ = 40% coverage for the winner of 10).

### Symptom: CLT applied to maxima returns nonsense
"The average of 10 000 request latencies is normal" ≠ "latencies are normal." For maxima the correct limit is extreme-value (Gumbel/Weibull/Fréchet), not Gaussian — checking a histogram of maxima against N(μ, σ²/√n) will fail by construction. Route tail/max statistics to EVT; the CLT only governs sums and means.

### Symptom: quantiles from simulated block means are not symmetric
For skewed X, block-mean distributions converge to normal *under the CLT*, but at finite n retain skewness ≈ skew(X)/√n. With skew = 4 and n = 16, residual skew ≈ 1 — visibly asymmetric intervals. Either increase n or use BCa bootstrap (lab 06) rather than ±1.96·SE.

### Symptom: strong law "violated" in a long run
Law of the iterated logarithm: the running deviation of X̄ₙ − μ is of order √(n log log n)/n infinitely often — paths *will* wander outside any fixed √n-shaped envelope infinitely often while SLLN still holds. Do not tune an algorithm against one trajectory; test across replications.

## Debugging triage: limit-theorem lab

| Symptom | Most likely cause | Evidence to collect first |
|---|---|---|
| Mean wanders forever with n | Infinite mean/variance data (Pareto α ≤ 2), or drift in the data source itself | Tail index / QQ of log-exceedances; rerun on a reshuffled copy of the same sample |
| SE does not halve when n × 4 | Dependent draws, reused seeds across workers, or n capped by a buffer | ACF of the stream; correlation between parallel workers' outputs; actual array length |
| 95% CI covers ~88% | n used instead of n_eff; σ estimated then treated as known; selection of the best metric | Recompute with n_eff; switch z → t; count *all* intervals, not the winner's |
| Coverage fine for latencies, terrible for p99 | CLT applied to a quantile/max | QQ of block maxima against Gumbel, not against N(μ, σ²/√n) |
| Asymmetric interval from block means | Residual skew ≈ skew(X)/√n at finite n | Sample skew of block means; if ≈ skew/√n, increase n or use BCa bootstrap |
| Berry–Esseen bound exceeds 1 | ρ/σ³ computed on badly scaled or shifted data, or n tiny | Recompute scale-free ratio; the bound is vacuous (>1) when it must be — clamp to 1 and say so |
| Coverage harness disagrees with theory | The harness itself: replications not independent, or `covers()` tested against wrong μ | Shuffle replication seeds; test on μ with a known closed-form interval first |

## Two-minute pre-flight

- Run the SE-scaling test: n, 4n, 16n → ratios must be 1, 1/2, 1/4.
- Check E|X| and E[X²] are finite on your sample (they are estimates — a growing sample kurtosis is a warning, not a proof).
- ACF before any σ²/n claim; quote n_eff next to every published error bar.
