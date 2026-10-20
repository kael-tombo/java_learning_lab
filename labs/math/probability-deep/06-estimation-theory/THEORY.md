# Estimation Theory — Theory

## 1. Estimators Are Statistics With a Job
An estimator θ_hat = g(X1, ..., Xn) is any function of the sample
proposing a value for a population parameter θ. Evaluation is
statistical: the same formula applied across hypothetical data
replications should land close to θ, and closer as n grows.

## 2. Bias and Variance — Exact Definitions
- Bias: Bias(θ_hat) = E[θ_hat] − θ. Zero means the estimator's
  averaging center sits exactly on the target; no statement yet about
  spread.
- Variance: Var(θ_hat) — the replication spread.
- MSE: E[(θ_hat − θ)^2]. The fundamental decomposition, exact:
  MSE = Var(θ_hat) + (Bias(θ_hat))^2,
  obtained by inserting (θ_hat − E[θ_hat]) + (E[θ_hat] − θ) and
  expanding — the cross term vanishes because deviations from their
  own mean average to zero.

## 3. Consistency — Exact Statement
θ_hat_n is consistent for θ if θ_hat_n → θ in probability as
n → ∞, i.e., P(|θ_hat_n − θ| >= ε) → 0 for all ε > 0. A sufficient
route (used constantly): show MSE_n → 0, then Markov/Chebyshev
delivers the convergence. Consistency is an asymptotic property of
the SEQUENCE, not of any single estimator drawing.

## 4. Unbiasedness Is Not Efficiency — The Hierarchy
- MVUE: among unbiased estimators, the one with minimum variance.
- Efficiency: an estimator achieves the Cramer–Rao lower bound
  Var(θ_hat) >= 1 / (n I(θ)), with I(θ) the Fisher information
  I(θ) = E[(∂/∂θ log f(X | θ))^2]. Unbiased and bound-attaining
  halves the story; asymptotically efficient estimators reach the
  bound as n → ∞.

## 5. Likelihood and Maximum Likelihood Estimation
Given iid data x1, ..., xn from a family f(· | θ), the likelihood is
L(θ) = Π_i f(x_i | θ) — a function of θ with the data fixed. The MLE
is θ_higher = argmax_θ L(θ), usually located by setting
d/dθ log L(θ) = 0. Properties (statements, conceptually): MLEs are
consistent, asymptotically normal with variance approaching the
Cramer–Rao bound, and invariant: if θ_higher = t then g(θ_higher) is
the MLE of g(θ) for any function g.

## 6. Sufficiency — Factorization, Exact Statement
A statistic T(X1, ..., Xn) is sufficient for θ when the conditional
law of the data given T does not depend on θ. The
Neyman–Fisher factorization theorem: T is sufficient iff the joint
likelihood factors as
  L(θ) = h(x) · g(T(x); θ),
a data-only piece times a T-only piece. Exploitation checklist: for
Bernoulli data, Σ x_i is the sufficient statistic (counts of successes
freeze what θ can hear the sample say); for normal (θ, σ^2) pairs,
(Σx_i, Σx_i^2) jointly suffice.

## 7. Loss Governs the Central Value
Squared loss E[(θ − a)^2] is minimized by a = mean of the distribution;
absolute loss E[|θ − a|] by a median. These are distributional facts;
their sample versions (sample mean, sample median) are the plug-in
estimators, and the two loss functions force different robustness
behavior — executed side by side in MATH_FOUNDATION.md.
