# Architecture: Random Variables Implementation

## Package layout
```
com.mathlab.randomvars
├── core/       RandomVariable (interface), Support, Validation
├── discrete/   BinomialRV, PoissonRV, GeometricRV, EmpiricalRV
├── continuous/ UniformRV, NormalRV, ExponentialRV, LognormalRV
├── ops/        Expectation, AffineTransform, PushForward, Convolution
├── moments/    Welford, RawMoments, Cumulants, SkewnessKurtosis
├── sampling/   InverseTransform, BoxMuller, UniformSource
└── tests/      NormalizationOracle, AnalyticMomentCases
```

## The single interface everything implements
```
interface RandomVariable {
    double pdf(double x);        // PMF for discrete (0 off-support)
    double cdf(double x);
    double quantile(double p);   // inverse CDF — drives sampling
    double mean();  double variance();
    Support support();
}
```
One contract for discrete and continuous variables is possible because F(x) = P(X ≤ x) is defined identically for both (Stieltjes 1894). Discrete implementations return staircase cdf values; continuous ones return smooth ones.

## Operations are separate from distributions
Expectation, affine transforms and push-forwards live in `ops/`, taking two RVs or a function — never as subclasses. Adding LognormalRV therefore costs no new expectation code: `E[exp(X)]` routes through the closed-form cache, falling back to quadrature only when no closed form is registered.

## Layered dependencies
```
sampling ──→ quantile only
ops       ──→ pdf/cdf + moments
discrete/continuous ──→ core
moments   ──→ core (no knowledge of specific distributions)
```
`moments` never imports a concrete distribution, so Welford is unit-tested against a pure LCG-generated stream without any distribution logic in the loop.

## Validation at construction (fail fast)
1. Σ pmf = 1 within 1e-12 (discrete); numeric ∫ pdf = 1 within 1e-9 (continuous).
2. pmf[i] ≥ 0 and support sorted strictly increasing.
3. quantile monotone with quantile(0) = inf, quantile(1) = sup of support.
4. variance ≥ 0 — negative values raise, exposing cancellation bugs at the source rather than downstream as sqrt(NaN).

## Test strategy
Analytic oracle cases: binomial(3, 0.5) → mean 1.5, var 0.75; Uniform(0,2) → 1, 1/3; Y = 5X+1 → 8.5, 18.75; Y = X² over Uniform(−1,1) → density 1/(2√y). Each sampled variant is checked with a KS statistic against its own analytic CDF rather than against another implementation.

## From axioms to a usable distribution: the build order

1. **Specify the probability space.** Sample space Ω, events, P. For simulation, Ω is the output space of your RNG in [0,1)^k.
2. **Define the random variable X: Ω → ℝ** as a measurable function. In code this is exactly `X = f(uniform_draws)`.
3. **Push the measure forward** to get the distribution of X on ℝ: P(X ≤ x) = P({ω : X(ω) ≤ x}). This pushforward is why a single uniform generator can produce *any* distribution.
4. **Choose a representation:** PMF (countable support), PDF (absolutely continuous), or CDF (always exists, always right-continuous, sufficient for all probability statements).
5. **Attach parameters** (μ, σ, λ, p …) and check identifiability: each parameter must move the distribution in a distinguishable way.
6. **Derive summaries** (mean, variance, quantiles) from the representation, not from simulation — simulation is for quantities that have no closed form.

Every bug in a distribution implementation is a break in one of these six steps: wrong space (support), wrong function (transformation), wrong pushforward (inversion method), wrong parameterization (scale vs. rate).
