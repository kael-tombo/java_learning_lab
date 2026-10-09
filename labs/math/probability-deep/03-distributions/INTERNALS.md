# Internals: Probability Distributions

## Three shapes of distribution object
1. **Index family** (Poisson, Binomial): support is integers in a computed range; pmf from a recurrence; cdf = prefix sums, built lazily on first query.
2. **Closed-form continuous** (Normal, Exponential, Gamma): pdf and cdf as analytic functions with published approximations; quantile either closed-form (normal via inverse-erf) or by Newton on the cdf.
3. **Empirical** (ECDF from data): support = sorted sample, cdf = i/n step function; pmf = counts/n. Everything downstream accepts it as if it were parametric.

All three implement the same `pdf/cdf/quantile/mean/variance` contract, so tests, plotting and sampling never branch on family.

## Log-space is the default
`logPdf(x)` is the primitive; `pdf(x) = exp(logPdf(x))` when in range. Products of densities become sums of log-densities, comparisons become sums of logs, and underflow disappears until the exponentiation step — which is only done for display.

## CDF construction and boundary discipline
Discrete CDFs are built inclusive: F(k) = Σ_{i ≤ k} p(i). Every public API exposes both `cdf(k)` = P(X ≤ k) and `sf(k)` = P(X > k) = 1 − F(k), with sf implemented via the complementary routine (not 1 − F) in the far tail. Internally, tail queries never compute `1 - x` when x is within 1e-15 of 1.

## Quantile inversion
- Normal: Acklam/Wichura AS241 rational initial guess + one Halley refinement step on erfc — full double precision, no bisection.
- General continuous: bisection on cdf as a guaranteed fallback (monotone, bracketed), accelerated by Newton when the derivative (pdf) is available and positive.
- Discrete: binary search for the smallest k with F(k) ≥ p — this is why P(X = k) can be recovered as a jump and why `quantile(cdf(k)) ≤ k`.

## Sampling
`UniformSource → quantile(u)` for closed-form families; rejection samplers (ziggurat for Normal/Gamma) sit behind the same `Sampler` interface and hold their table as a static final. The Poisson sampler dispatches: Knuth loop for λ < 30, transformed rejection above.

## Special functions
One `SpecialFunctions` class owns lgamma, gamma, erf, erfc and the incomplete gamma P(a,x) — used by every continuous family (Gamma, Poisson cdf, χ², t). A single tested implementation prevents the classic inconsistency where a library's gamma and its Poisson cdf disagree in the 7th digit.

## Test vectors every implementation should assert

| Check | Exact value | Source of truth |
|---|---|---|
| Poisson(4) pmf at k = 0..3 | 0.018316, 0.073263, 0.146525, 0.195367 | e^{−4}4^k/k! |
| Exponential(1) quantile at 0.5 | 0.693147 | −ln(1 − 0.5) |
| Normal quantile at 0.975 | 1.959964 | Φ⁻¹(3/4 + ...) — cross-check against a published table |
| Binomial(10, 0.5) pmf at 5 | 0.246094 | 252/1024 |
| Gamma(2, scale=3): mean, variance | 6, 18 | αβ, αβ² |
| Uniform(0, 1) mean, variance | 0.5, 0.083333 | 1/2, 1/12 |

Each row pins a different code path: recurrence, log-gamma, inverse-CDF, closed-form moments. A change that breaks a row is a behavior change, not a rounding wobble — that is what makes these worth keeping next to the sampler rather than in a separate document nobody opens.
