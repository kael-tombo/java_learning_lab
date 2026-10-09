# Debugging: Random Variables Implementation

### Symptom: variance comes back negative (or exactly 0)
Computed as E[X²] − μ² with catastrophic cancellation on large-mean data. Fix: Welford's single pass (`m2 += (x - mean) * (x - nMean)`), or the two-pass sum of squared deviations. A negative variance is always a numerical artifact — clamp and log, never take sqrt of it.

### Symptom: PDF integrates to 0.93 instead of 1
A truncated or one-sided branch was dropped. For Y = X² over X ~ Uniform(−1, 1) the missing half is the x = −√y branch: without it the integral is 0.5. Integrate numerically on a fine grid as a test; normalization must hold to 1e-12.

### Symptom: CDF is not monotone, or jumps backwards
Prefix sums were built from a PMF containing a tiny negative value (rounding or a subtraction in a recurrence). Enforce `cdf[i] = max(cdf[i], cdf[i-1])` *and* fix the PMF source; a monotone CDF with a wrong total hides the real bug.

### Symptom: samples appear outside the support
Inverse-transform draw used `u = nextDouble()` returning values in [0, 1). For a distribution on [0, ∞) with quantile q(u) = −log(1−u)/λ, u = 0 gives q = 0 (fine) but a closed form like q(u) = log(u)/(1−u) blows up at u = 0. Map uniforms to the open interval (0, 1): `u = (nextDouble() + 0.5 * ULP)` or use `1 − nextDouble()`.

### Symptom: mean of a lognormal sample is far above the median
Not a bug — E = e^{μ+σ²/2} while median = e^μ; with σ = 1 the mean is 1.65× the median. Verify against the analytic moments rather than against each other, and report median + IQR for skewed variables.

### Symptom: MGF or cumulant computation returns Infinity
M(t) for t large overflows double (M(t) = e^{t²/2} for N(0,1)). Work with log M(t) (cumulant generating function) or use the characteristic function φ(t) = E[e^{itX}], whose modulus never exceeds 1.

### Symptom: two samplers of "the same" variable disagree statistically
Compare with a two-sample KS test, not a t-test on means: means can agree while shapes differ. Also check the seed — two components initialized with the same default seed produce identical sequences and a spuriously perfect agreement.

## Debugging triage for distribution bugs

| Symptom | Most likely cause | Evidence to collect first |
|---|---|---|
| Simulated mean far from theoretical mean | Generator misconfigured (wrong scale/loc) or seed reuse across replicates | Print `data.mean()` vs `dist.mean()`; check whether two "independent" runs share a seed |
| Variance about half of theory | Averaging before measuring — you computed the distribution of the *sum* divided twice | Recompute variance of the raw draws, not of an already-averaged column |
| Histogram has spikes at 0 or 1 | Discrete distribution plotted with continuous bins, or rounding applied early | Plot with `bins=range(min,max+1)` and delay rounding until the final report |
| χ² test always rejects on large n | Trivial deviations become significant; expected counts below 5 in tail bins | Merge tail bins until every expected count ≥ 5, then re-test |
| CI coverage below nominal | Normal approximation used where n·p is small | Compare against the exact (Clopper–Pearson) interval on the same data |
| KS test rejects but QQ plot looks fine | Test sensitive to location shift at the mean; or parameters estimated from the same data | Use the Lilliefors correction when σ was estimated, not the tabled KS critical values |

## Two-minute checklist

- Verify one analytically known case (e.g. Uniform(0,1): mean 0.5, variance 1/12 ≈ 0.0833).
- Confirm the sample size you *think* you drew is the size actually in the array.
- Confirm no in-place transformation (`log`, standardization) was applied before computing the theoretical comparison.
