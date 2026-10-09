# Debugging: Estimation Theory

### Symptom: optimizer reports "converged" at a nonsense parameter
Check the gradient norm, not the status flag: a flat likelihood (over-parameterized model, or θ on the boundary) gives a tiny gradient at a meaningless point. Assert ‖score‖ < tol *and* that the observed information is positive definite; a negative eigenvalue means you found a saddle or the log-likelihood is being maximized as a minimization.

### Symptom: MLE for σ² doesn't match s²
It shouldn't: σ̂²_MLE = (n−1)/n · s². For n = 5 and s² = 2.5, MLE = 2.0 exactly. If you expected equality, you have the divisor mixed up — decide which one the downstream formula wants (t-tests and SEs want n−1; AIC/log-likelihood wants the MLE).

### Symptom: NaN standard errors
Causes in order: (1) information matrix singular — p ≥ n, collinear features, or a saturated model; (2) boundary estimate (variance → 0 in a mixture, weight → 0) so information → 0 and SE = 1/√I → ∞/NaN; (3) log(0) inside the log-likelihood for data at the support edge (lognormal evaluated at x = 0). Detect and report "SE undefined at boundary" instead of printing NaN.

### Symptom: CI coverage far below nominal in simulation
Run three diagnostics: does the estimator's bias ≈ 0 at this n (Wald intervals center on θ̂, so bias eats coverage)? is the sampling distribution skewed (skewness ≈ γ₁/√n; use BCa bootstrap or transform)? are the data independent (n_eff vs n — lab 05)? A Wald interval on a positive, right-skewed estimator (variance, rate) is systematically low on the upper side.

### Symptom: bootstrap interval equals the estimate at one endpoint
Percentile bootstrap on a boundary parameter (correlation → 1, variance → 0) piles mass at the boundary: many resamples give exactly the same extreme value. Use BCa or a transformation (Fisher z for correlations, log for variances) before resampling.

### Symptom: Newton's method oscillates or diverges
No line search. MLE surfaces are not globally quadratic — add step-halving (accept only if ℓ increases), or use BFGS with a Wolfe line search. Also rescale: parameters of magnitude 1e-6 and 1e6 in the same system make the Hessian's condition number catastrophic; work on log-parameters for constrained quantities.

### Symptom: two "equivalent" estimators disagree in the last digits
MLE via optimization vs closed form should agree to solver tolerance (1e-8 relative). Disagreement beyond that means the objective differs — often one code path drops a θ-independent term (fine for optimization) that the other includes (needed for AIC/log-likelihood reporting). Compare *log-likelihood values*, not just parameters.

## Debugging triage: estimation

| Symptom | Most likely cause | Evidence to collect first |
|---|---|---|
| θ̂ absurd / optimizer "converged" at nonsense | Flat or unbounded likelihood; no line search | ‖score‖, eigenvalues of observed information, likelihood trace per iteration |
| SE disagrees with bootstrap by >2× | Model-based SE on dependent/misspecified data | Sandwich ratio (J vs I); ACF of log-likelihood contributions |
| CI covers 91% instead of 95% in simulation | Bias at finite n, or sampling skew (γ₁/√n) | Bias vs n sweep; QQ of the θ̂'s across replications |
| Bootstrap CI collapses to a point | Boundary piling (r → 1, σ → 0) or shared RNG seed across resamples | Histogram of the B replicates; distinct seeds per resample |
| MLE ≠ closed form beyond 1e−8 | Objective omits θ-dependent terms, or maximizes a different quantity (conditional likelihood) | Compare *log-likelihood values*, not just parameters |
| Reported variance 10% low at n = 10 | MLE divisor (1/n) quoted as if unbiased (1/(n−1)) | Recompute both; check which one downstream formulas expect |
| Wald interval has a negative endpoint | Symmetric ±z·SE on a positive/skewed parameter (rate, variance, correlation) | Switch to profile LR or transform (log, Fisher z) and compare endpoints |

## Two-minute checklist

- Verify a closed form on a case that has one: normal μ̂ = x̄, binomial p̂ = k/n, exponential λ̂ = 1/x̄ — to solver tolerance.
- Print bias at your actual n on a simulated truth; if |bias| > 0.1·SE, no Wald interval will cover.
- Report SE three ways on the same data (observed information, sandwich, bootstrap) and record why any two differ.
