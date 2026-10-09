# Why It Matters: Random Variables

## Everything downstream is a function of them
- **Distributions (lab 03)** are the named laws of specific random variables: Binomial counts successes, Exponential times the wait, Normal summarizes averages.
- **LLN/CLT (lab 05)** are statements about the sequence of partial sums Sₙ = X₁ + … + Xₙ — random variables in their own right.
- **Estimation (lab 06)**: X̄ = (1/n)ΣXᵢ is a random variable *before* you see data; its sampling distribution is what "Var(θ̂) = σ²/n" refers to.
- **Testing (lab 07)**: the test statistic (t, χ², F) is a random variable whose distribution under H₀ gives the p-value.
- **Bayesian (lab 08)**: θ itself is treated as a random variable with a posterior distribution.

## The two numbers that run the world
Expectation and variance are the operating parameters of applied work:
- **E[X] prices things.** An insurance premium for n policyholders with claims Xᵢ is n·E[X] plus a risk margin; a portfolio's expected return is ΣwᵢE[Xᵢ].
- **Var(X) prices uncertainty.** The standard deviation of the *average* of n observations is σ/√n — this single expression is the sample-size rule behind every poll, clinical trial and A/B test.

Drop the covariance term in Var(ΣwᵢXᵢ) and you misprice correlated risk — the exact mistake that made 2008-era CDO models report portfolio σ far below realized.

## Where means mislead
For lognormal, Pareto and other right-skewed variables — income, file sizes, claim severities, request latencies — the mean sits far above the median. Any dashboard showing "average latency 900 ms" over a bimodal or heavy-tailed service distribution hides both the median and the tail; the distribution (lab 03) must be reported alongside the two moments.

## The hand-off
This lab ends where modeling begins: you can compute E, Var, and transformations of a given X. Labs 03–08 ask the harder question — *which* X, and what do you do when its parameters are unknown?

## Where the choice of distribution changes a real decision

**Clinical trial sizing.** Assuming a normal outcome with σ = 10 to detect a 3-point difference needs about n = 2 × (1.96 + 0.84)² × 100 / 9 ≈ 173 per arm. If the outcome is actually right-skewed (tumor counts, turnaround times) with the same mean and SD, the normal-based sample size undercovers and the trial is underpowered — the distributional assumption, not the budget, decides the outcome.

**Insurance and risk.** Pricing a policy from the mean loss is safe only if the tail is thin. Claim severity is heavy-tailed: replacing a lognormal assumption with a Pareto tail can multiply the 99.9th-percentile reserve by an order of magnitude while leaving the mean nearly unchanged. The mean is the same number; the decision it supports is not.

**Anomaly detection.** A threshold set at μ + 3σ flags "anomalies" at the expected rate only under normality. For Poisson(4) arrivals, P(X ≥ 12) ≈ 0.0058 — 4× more often than the normal tail would suggest (which is why rare-event counting needs the exact distribution).

**Machine learning.** Loss functions implicitly assume an outcome distribution: squared loss is the maximum-likelihood estimator under normal errors, absolute loss under double-exponential errors. Choosing squared loss on heavy-tailed targets lets a handful of outliers set the model — the same data with a different likelihood assumption yields a different fitted model.

## Reading checklist

- Is the outcome bounded? (Then a normal model is an approximation whose quality depends on how far the mean sits from the bounds.)
- Is the variance stable across the range of the predictor? (If it grows with the mean, model log Y instead.)
- Which tail quantity will be used — mean, quantile, or exceedance probability? Normal approximation is safest near the center and least safe exactly where risk decisions live.
