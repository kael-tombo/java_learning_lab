# Architecture: Estimation Theory Implementation

## Package layout
```
com.mathlab.estimation
├── api/         Estimator, Estimate, Interval, StandardError
├── closedform/  SampleMean, SampleVariance (n / n−1), Proportion, Rate, UniformEndpoint
├── mle/         NewtonRaphson, Score, ObservedInfo, ProfileLikelihood
├── bounds/      CramerRao, FisherInfo, Bhattacharyya (where CRB fails)
├── interval/    Wald, LikelihoodRatio, Score, TInterval, ClopperPearson
├── bootstrap/   Percentile, BCa, Jackknife, Influence
├── model/       AIC, BIC, LRTest, ResidualDiagnostics
└── stream/      WelfordMoments, RecursiveLeastSquares, Forgetting
```

## Design decisions
1. **`Estimate` carries method + uncertainty.** `new Estimate(3.0, se, METHOD.MLE_WALD, n)` — printing a bare double is not possible through the API; "3.0" without provenance cannot leak into a report.
2. **Variance divisor is explicit.** `SampleVariance` takes a `Divisor` enum; the default for *inference* is n−1, the default for *likelihood* is n. One field, checked at construction — killing the classic MLE/unbiased mix-up at compile time.
3. **Regular-family checks gate √n theory.** `CramerRao.of(model, θ)` throws `IrregularFamily` when the support depends on θ or information is singular, instead of returning a meaningless bound.

## Data flow
```
DataView → closedform? → Estimator.point / .interval
                    └→ mle.NewtonRaphson → Wald | LR | Score intervals
                                            ↘ bootstrap (optional, simulation-based)
Interval → model.AIC/BIC compare → diagnostics (coverage studies)
```

## Failure handling (typed, never silent)
- `NonConvergence` — optimizer step-halving exhausted; carries final gradient norm.
- `SingularInformation` — p ≥ n or collinear design; message includes condition number.
- `IrregularFamily` — CRB/√n-normality requested on a non-regular model.
- `BoundaryEstimate` — θ̂ at parameter space edge; Wald SE replaced by one-sided bound flag.

## Test topology
Analytic oracles: normal sample (2,5,1,3,4) → μ̂ = 3, σ̂²_MLE = 2.0, s² = 2.5, SE = 0.7071, t-interval (1.04, 4.96); Uniform(0,θ) MLE = max and its E = nθ/(n+1) bias verified by simulation; coverage of the Wald interval over 10 000 replications ∈ [0.945, 0.955]; bootstrap percentile interval width matching the analytic one within 10% at n = 50 (not a benchmark — a sanity band).
