# Internals: Random Variables Implementation

## Core representation
A discrete random variable stores `double[] support` and `double[] pmf`, plus a `double[] cdf` built once as a running sum. The invariant checked at construction: `Σ pmf = 1` within 1e-12, every pmf ≥ 0, cdf monotone with last entry 1. Sampling uses `Arrays.binarySearch(cdf, u)` — O(log k) per draw.

A continuous random variable stores an analytic `pdf(x)`, `cdf(x)` and `quantile(p)`. Only the quantile is used for sampling; pdf/cdf serve evaluation and testing (via numeric integration).

## The expectation operator
`E[g(X)]` is one method: for discrete it is `Σ g(support[i])·pmf[i]`; for continuous, Gauss–Legendre quadrature over the support (fixed nodes, exact for polynomials up to 2n−1 points). Both paths return `double` and are exercised against hand-computed values — the 3-flip binomial (1.5, 0.75) and Uniform(0,2) (1, 1/3).

## Transformations: push-forward
Y = g(X) computes the induced distribution rather than sampling-then-histogram:
- Discrete: push each support point through g, merge duplicate outputs, renormalize (merge step is O(k log k) for sorting).
- Continuous: change of variables f_Y(y) = f_X(h(y))·|h′(y)| over each inverse branch; branches are enumerated explicitly (Y = X² over (−1,1) registers two: ±√y).

## Moment bookkeeping
Moments are cached as `double[] raw` (E[Xⁿ]) and `double[] cumulants` (κ₂ = Var, κ₃ related to skewness). Affine transforms update them in O(1): raw moments through the binomial expansion, cumulants of order ≥ 2 scaled by aⁿ. This is what makes `5X+1` cost one arithmetic op instead of a full resummation.

## Welford's online moments
Streaming state is (count n, mean, M2) — three doubles for *any* n. Adding x: δ = x − mean; mean += δ/n; M2 += δ·(x − mean). This is the variance path used everywhere a sample accumulates; the E[X²] − μ² identity is retained only for symbolic/analytic work where exactness holds.

## Layering
`DiscreteRV / ContinuousRV → Transform → Moments → Sampler`. Samplers depend on quantiles only, so a new distribution needs three functions (pdf, cdf, quantile) and inherits expectation, transformation and testing for free.

## Internal representations compared

| Representation | Stored | Best for | Inversion cost |
|---|---|---|---|
| PMF array | value → probability | Small finite support (dice, categories) | O(1) after O(m) prefix sums |
| CDF array on a grid | grid → cumulative probability | Arbitrary 1-D distributions; monotone by construction | O(log m) binary search + interpolation |
| Piecewise-exponential CDF | breakpoints + rates | Fast high-precision sampling (used in modern RNG libraries) | O(log m) + closed-form piece |
| Sufficient statistics | counts, sums, sumsq | Conjugate families: Beta keeps (successes, failures), Normal keeps (n, Σx, Σx²) | Not a sampler — an update rule |
| Quantile function (closed form) | formula | Normal, Exponential, Logistic | O(1) per draw via inverse erf / log |
| Mixture components | weights + component parameters | Multimodal or hierarchical data | O(k) per draw to pick a component |

The sufficient-statistics row matters more than it looks: because Beta(a, b) is conjugate to Binomial, updating after new data is two additions — you never revisit the raw data. That is an *architectural* property of the exponential family, not an optimization someone applied.
