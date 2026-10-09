# Reflection: Estimation Theory

## Rebuild the pipeline from scratch
Given five numbers (2, 5, 1, 3, 4): write the likelihood for N(μ, σ²), take the two derivatives, solve, and get μ̂ = 3 and σ̂²_MLE = 2.0. Then answer: why did the σ² equation give 2.0 and not 2.5, and which one feeds a t-interval? If you can't say which downstream formula needs which divisor, you've found your gap.

## Questions to work through
1. Uniform(0, θ): show L(θ) = θ⁻ⁿ for θ ≥ max(x), identify θ̂ = max(x), compute its bias at n = 10 (−θ/11) and its convergence rate. Which Cramér–Rao assumptions break, and what does that do to any "95% CI ± z·SE" you were about to write?
2. For the normal, derive I(μ) = n/σ² from the second derivative of ℓ and confirm Var(x̄) meets 1/I. Then do it for the exponential — does λ̂ = 1/x̄ meet its own bound?
3. You estimate a rate λ from m = 4 events in a window. Wald interval: λ̂ ± 1.96√m/T. Poisson is skewed — sketch why the Wald interval under-covers at m = 4 and name the fix (Garwood/exact, or a transformation).
4. James–Stein: for p ≥ 3, shrinkage beats x̄ uniformly under squared error. What does that imply about the default "one mean per metric" dashboards when you track p = 500 service metrics?
5. A colleague reports bootstrap CI [2.1, 2.1] for a correlation. Diagnose three plausible causes (boundary piling, resampling the wrong axis, statistic not varying because of a shared seed).

## Self-check table
| Concept | Can state it | Can compute it | Can break it |
|---|---|---|---|
| MLE via score equations | | | |
| bias vs variance vs MSE | | | |
| Fisher information / Cramér–Rao | | | |
| Wald vs LR vs score intervals | | | |
| sufficiency & Rao–Blackwell | | | |
| bootstrap mechanics (B·n) | | | |

## Milestones
- [ ] Reproduce μ̂, σ̂², s², SE, t-interval for (2,5,1,3,4) unaided
- [ ] Derive θ̂_MLE for Uniform(0,θ) and its n/(n+1) bias
- [ ] State CRB conditions and one family where it fails
- [ ] Explain why unbiased ≠ minimum MSE with a concrete pair
- [ ] Program a percentile bootstrap for the mean and check its width against s/√n

## Blind spots this lab exposes

- **Optimization output mistaken for inference.** A converged flag says nothing about identifiability, boundary proximity, or whether the information matrix is invertible — three separate assertions the fit must earn.
- **Quoting the model-based SE out of habit.** On clustered, serial, or contaminated data, I⁻¹ is optimistic by an unknown factor; the sandwich is cheap and the divergence between the two is itself a diagnostic worth reporting.
- **Choosing intervals by convenience.** Wald is the default because it's one line; profile LR or BCa is the same answer *with* the asymmetry that Wald throws away. The choice should follow the likelihood's shape, not the code's history.
- **Treating n as given after seeing the data.** Sample-size planning must run before collection — the SE law is one-way: once the data exist, the interval's width is fixed and no estimator narrows it.
- **Stopping at a point estimate.** "λ̂ = 4" without its interval (Garwood [1.09, 10.24] at m = 4) invites decisions the data cannot support — the interval is part of the estimate, not a bonus.
