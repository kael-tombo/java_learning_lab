# Architecture: Probability Distributions Implementation

## Package layout
```
com.mathlab.distributions
├── api/          Distribution, DiscreteDistribution, ContinuousDistribution
├── special/      LGamma, Gamma, Erf, IncompleteGammaP, BetaFn
├── discrete/     Poisson, Binomial, Geometric, NegativeBinomial, Hypergeometric
├── continuous/   Normal, Exponential, Gamma, Beta, Lognormal, Weibull, ChiSquared, StudentT, F
├── ecdf/         EmpiricalDistribution, OrderStatistics, QuantileSpec
├── sampling/     QuantileSampler, Ziggurat, PoissonSampler, UniformSource
└── fit/          MomentsFit, MLEFit, GoFTest (χ², KS)
```

## One contract for every family
```
interface ContinuousDistribution {
    double logPdf(double x);
    double cdf(double x);        // inclusive, P(X ≤ x)
    double sf(double x);         // P(X > x), accurate far into the tail
    double quantile(double p);   // inverse cdf
    double mean();  double variance();  Support support();
}
```
`logPdf` is primitive; `pdf` derives from it. `sf` is a first-class member (not `1 - cdf`) because tail probabilities are where the distributions actually get used — reliability, p-values, risk thresholds.

## Special functions are their own module
Gamma, log-gamma, erf/erfc, incomplete gamma P(a,x) and the beta function are implemented once, tested against published values (e.g. Γ(0.5) = √π, erfc(1) = 0.157299…), and shared by every family. Student-t cdf = incomplete-beta ratio; Poisson cdf = regularized incomplete gamma; χ² = gamma cdf — so a bug in `special/` is caught by *all* the families at once instead of by none.

## Fitting is a separate layer
`fit/` consumes a `Distribution` plus data (or moments) and returns parameters: method of moments first, MLE by Newton/IRLS when a closed form is missing. It never mutates the distribution — a fitted distribution is a new immutable instance, so the same data can be fit under Normal and Lognormal and compared by AIC/KS.

## Validation invariants
1. pdf ≥ 0 everywhere, ∫ = 1 (numeric quadrature check at construction for non-table families).
2. cdf monotone, cdf(−∞) = 0, cdf(+∞) = 1, quantile(cdf(x)) ≈ x.
3. mean/variance reported by the object match a 10⁶-draw Monte Carlo estimate within 4 standard errors (3σ/√n of the estimator).
4. Discrete support strictly integer; pmf = 0 off-support; Σ pmf = 1.

## Test topology
Analytic oracles: Poisson(4) terms (0.018316, 0.073263, 0.146525, 0.195367) computed by hand; Normal quantile(0.975) = 1.959964; Exponential mean 1/λ; Gamma(n,1) mean n for integer n vs (n−1)! check via log-gamma.
