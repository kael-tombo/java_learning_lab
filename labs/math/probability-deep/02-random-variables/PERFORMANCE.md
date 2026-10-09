# Performance: Random Variables Implementation

## Evaluating and sampling
- **PMF/CDF evaluation**: a PMF stored on k support points needs O(1) array access for indexed support (binomial, Poisson) and O(log k) binary search for arbitrary sorted support. The CDF is precomputed as prefix sums once — O(k) — so each query is one binary search, no rescanning.
- **Inverse-transform sampling**: build the CDF once (O(k)), then each draw is a binary search O(log k). For a continuous distribution the quantile function is analytic, so a draw costs one RNG uniform plus O(1) algebra.
- **Large-support convolutions**: the distribution of a sum of independent discrete variables is a convolution — naive O(k²), FFT-based O(k log k). Summing 10⁶ independent Bernoullis as a full PMF is infeasible either way; use the exact binomial recurrence or the normal approximation from the CLT instead.

## Computing expectations
Summation over a support of size k is O(k) with no closed form, but many expectations are closed-form: E[aX+b] = aE[X]+b, Var(aX+b) = a²Var(X). Always apply the affine shortcut before expanding — it is exact and avoids accumulating k rounding errors.

## Numerical traps with costs, not benchmarks
- **MGF overflow**: M(t) = E[e^{tX}] for X ~ N(0,1) is e^{t²/2}; at t = 26 that exceeds double range (t²/2 = 338, e³³⁸ ≈ 10¹⁴⁶ — fine; t = 40 → e⁸⁰⁰, overflow). Compute cumulants log M(t), or use the characteristic function (bounded by 1 in modulus) for any numeric work.
- **Variance cancellation**: E[X²] − μ² subtracts two ~10¹⁸ numbers to get ~10² for data near 10⁹. Welford's single pass is O(n), one division, error proportional to the variance itself rather than to the magnitudes.
- **Triangular (two-pass) summation**: Σ(x−x̄)² computed after a first pass for x̄ is backward stable; it costs two passes over memory but is the safest O(n) option for arrays that already fit in cache.

## Decision rule
| Need | Method | Cost |
|---|---|---|
| Moments of affine g | shortcuts | O(1) |
| Moments of general g on k points | weighted sum | O(k) |
| Sampling many draws | precomputed CDF + binary search | O(1) prep, O(log k)/draw |
| Sum of independent discrete RVs | FFT convolution | O(k log k) |

## Cost table: what each operation actually takes

| Operation | Cost | Notes |
|---|---|---|
| Draw n samples from a standard distribution | O(n) | Vectorized generators process ~10⁷ doubles/second/core |
| Compute mean / variance | O(n) | One pass for mean, Welford's algorithm one pass for variance |
| Sort n values (empirical quantile) | O(n log n) | Use `partition`/`nth_element`-style selection for a single quantile: O(n) |
| Rejection sampling for a custom density | O(n / acceptance rate) | Report the acceptance rate; a 2% rate means 50 draws per sample |
| Inverse-CDF sampling | O(n log n) if CDF must be numerically inverted per draw | Pretabulate the inverse on a grid and interpolate |
| Histogram with b bins | O(n + b log b) | Bin assignment is O(n); only the bin edges need sorting |
| Bootstrap with B resamples | O(B · n) | Dominates everything else in a typical analysis; B = 2000, n = 10⁵ → 2×10⁸ operations |
| Convolution of two PMFs of lengths a, b | O(a·b) direct, O((a+b) log(a+b)) via FFT | Matters for sums of independent discrete variables |

## Rules of thumb

- Generate at once (`size=1_000_000`), not in a Python loop — the loop costs 50–100× more than the draws.
- For repeated Monte Carlo, keep the random stream local; a shared global generator makes runs irreproducible when code is reordered.
- Profile before switching to a faster sampler: in most analyses the resampling loop, not the RNG, dominates.
