# Debugging: Probability Distributions

### Symptom: density evaluates to 0.0 (or Infinity) at valid x
For x deep in a normal tail, exp(−x²/2) underflows (x = 40 → e^{−800} = 0). Compute log-density directly (−0.5x² − log(σ√(2π))) and exponentiate only when the result is within range. Symptom of the same bug: log-likelihood is NaN because one term was already 0 before taking log(0).

### Symptom: pmf sums to 1.04
The recurrence ran one term too far or used an un-updated k. Recurrence invariant: after computing p(k), verify p(k+1) = p(k)·λ/(k+1) with the *incremented* index; then renormalize (p(k) /= Σ) and assert |Σ − 1| < 1e-12.

### Symptom: tail probability is exactly 0 or 1
`1 - CDF(40)` cancels to 0 because Φ(40) equals 1 to within ~10⁻³⁵⁰ — the complement's precision is gone before subtraction. Use the survival function (erfc) or compute P(X > x) directly from the complementary CDF the library exposes.

### Symptom: samples don't match the requested mean/variance
Check the parameterization first: `Normal(mean, sd)` vs `Normal(mean, variance)` (Apache Commons takes sd; some libraries take variance); Exponential(rate) vs Exponential(scale). Print sample mean and compare against 1/λ or λ before suspecting the RNG.

### Symptom: KS test rejects against the distribution the data "clearly" follows
Two causes: (a) parameters were estimated from the same sample — the null distribution of the KS statistic no longer applies (Lilliefors correction needed); (b) discrete data fed to a continuous KS reference — ties inflate the statistic. Fit parameters on a training split, test on held-out data, or use the χ² test with estimated-parameter df correction.

### Symptom: binomial overflows for n > 170
Computing C(n,k) as `factorial(n)/(factorial(k)*factorial(n-k))` overflows at 171! ≈ 1.2×10³⁰⁹ (170! ≈ 7.3×10³⁰⁶ still fits; double max ≈ 1.8×10³⁰⁸) even when the final pmf is perfectly representable. Never form factorials separately: use log-gamma (log C(n,k) = lgamma(n+1) − lgamma(k+1) − lgamma(n−k+1)) plus k·log(p) + (n−k)·log(1−p), then exponentiate.

### Symptom: Poisson sampler takes seconds
Knuth's multiplicative loop iterates λ times — fine at λ = 5, unusable at λ = 10⁶. Switch to the normal approximation (with continuity correction) or transformed rejection (Hörmann 1993); both are O(1) per draw.

## Distribution-debugging triage

| Symptom | Likely cause | Fast check |
|---|---|---|
| Draws contain 0 or negatives from a "positive" distribution | Wrong parameterization: rate (1/β) passed where scale β expected, or vice versa | Exponential(mean=2) vs Exponential(scale=2): check `data.mean()` equals what you intended, not 1/what you intended |
| Chi-square test always rejects | Bins with expected count < 5, or parameters estimated from the same data but df not reduced | df = bins − 1 − (#estimated parameters); merge tail bins |
| Generated multinomial counts don't sum to n | Independent binomials per category instead of one multinomial draw | Sum row-wise; must equal n exactly |
| Gamma vs Erlang confusion produces non-integer shape | Erlang requires integer shape = Poisson arrival counting | Assert `shape == int(shape)` when modeling arrival batches |
| QQ plot fine in the center, diverges in tails | Wrong tail family (normal vs t vs lognormal) — center is nearly family-free | Compare only the outer 5% of points; use Anderson–Darling, which weights tails |

## One-line sanity identities to assert in tests

- Binomial(n, p): mean = np, variance = np(1−p) — variance must be strictly less than the mean.
- Poisson(λ): mean = variance = λ exactly.
- Exponential(λ): mean = 1/λ, P(X > t) = e^{−λt} — check P(X > 1/λ) ≈ 0.368.
- Geometric(p) (trials-until-first-success): mean = 1/p.
