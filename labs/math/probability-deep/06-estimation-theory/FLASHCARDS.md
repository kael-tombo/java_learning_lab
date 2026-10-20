# Flashcards — Estimation Theory

## Definition Cards

### Card 1
**Front**: Define bias of an estimator.
**Back**: Bias(θ_hat) = E[θ_hat] − θ; measuring the distance between
the replication-average of the estimator and the true parameter.

### Card 2
**Front**: State the MSE decomposition exactly.
**Back**: E[(θ_hat − θ)^2] = Var(θ_hat) + (Bias)^2, from inserting
plus-minus E[θ_hat] and watching the cross term die.

### Card 3
**Front**: Define consistency of a sequence of estimators.
**Back**: θ_hat_n → θ in probability: P(|θ_hat_n − θ| >= ε) → 0 for all
ε > 0 as n → ∞; shown by MSE_n → 0 plus Chebyshev.

### Card 4
**Front**: MVUE — definition?
**Back**: Minimum-variance unbiased estimator: unbiased, and no other
unbiased estimator beats its variance.

### Card 5
**Front**: Define the likelihood function and the MLE.
**Back**: L(θ) = Π f(x_i | θ) viewed as a function of θ with data
fixed; MLE = argmax_θ L(θ), usually through d/dθ log L = 0.

### Card 6
**Front**: Factorization theorem — exact statement of sufficiency?
**Back**: T is sufficient iff L(θ) = h(x) · g(T(x); θ) — a data-only
factor times a statistic-only factor; conditionally, given T, θ drops
out of the data's law.

## Property Cards

### Card 7
**Front**: Cramer–Rao bound to recite?
**Back**: Var(θ_hat) >= 1/(n I(θ)) with I(θ) = E[(∂ log f/∂θ)^2]; an
estimator attaining it (unbiased) is called efficient.

### Card 8
**Front**: MLE invariance — statement?
**Back**: If θ_hat is the MLE of θ, then g(θ_hat) is the MLE of g(θ)
for any function g; reparameterizations need no re-optimization.

### Card 9
**Front**: Which loss picks the mean, which the median?
**Back**: Squared loss → mean (executed: minimizer 7/3 on the three-
point sample); absolute loss → median (executed minimizer 2).

### Card 10
**Front**: Sufficient statistic for Bernoulli(p), and why?
**Back**: T = Σ x_i: L(p) = p^T (1−p)^{n−T}, factoring as
h(x)·g(T; p) with h(x) = 1 — counts of successes exhaust θ's reach.

## Judge-the-Number Cards

### Card 11
**Front**: Bernoulli n = 10, p = 1/2: Var and MSE of p_hat?
**Back**: Both 1/40 (bias zero); scaled at n = 40 both become 1/160.

### Card 12
**Front**: U(0, 12), n = 3: E[max], bias, and the cure multiplier?
**Back**: E[max] = 9, bias = −3, cure (n+1)/n = 4/3 — simulated mean
8.997715881500072 confirms the exact 9.
