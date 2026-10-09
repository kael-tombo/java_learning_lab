# Common Mistakes: Probability Distributions

### 1. Using the wrong support
Exponential and Poisson are on [0, ∞) and the integers ≥ 0 — placing an exponential density on (−∞, ∞) integrates to 2. A Poisson pmf evaluated at k = 2.5 must return 0, not Γ(3.5)/2.5!… — support checks belong in the implementation, not in the caller's head.

### 2. Confusing parameters between reparameterizations
The normal density has σ as the *standard deviation* in exp(−x²/(2σ²)) but many libraries (scipy, Apache Commons) take `sigma` as sd while the exponential takes rate λ (pdf λe^{−λx}) not scale 1/λ. `exponential(2)` has mean 0.5 if λ = 2, mean 2 if it is a scale. Check the mean against the formula before trusting any draw.

### 3. Wrong discrete limit: Poisson vs Binomial
Binomial(n, p) and Poisson(λ = np) agree only when n is large and p small (rule of thumb n ≥ 20, p ≤ 0.05). Using Poisson(λ = np) for n = 10, p = 0.4 (λ = 4) instead of Binomial(10, 0.4): P(X = 0) is 0.6^10 = 0.00605 vs e^{−4} = 0.0183 — a 3× error in the far tail, exactly where decisions are made.

### 4. Gaussian applied past its domain
Fitting a normal to latencies or incomes (strictly positive, right-skewed) produces negative predictions at >50% of draws for a mean near zero in σ units. Lognormal, gamma or a mixture is the correct shape; the CLT justifies normality of *averages*, not of the underlying variable.

### 5. Forgetting that adding normals scales variances
X ~ N(1, 4), Y ~ N(2, 9) independent → X + Y ~ N(3, 13), not N(3, 25) (σ² are added, σ are not: √13 ≈ 3.61 ≠ 2 + 3). Same error in reverse when standardizing: (X − μ)/σ for a difference of means uses √(σ₁²/n₁ + σ₂²/n₂).

### 6. Discrete CDF overshoot at the boundary
P(Poisson(4) ≤ 3) uses the *inclusive* CDF; P(X ≥ 3) = 1 − F(2), not 1 − F(3). Off-by-one at the CDF boundary flips the inequality and is the most frequent bug in tail-probability code.

### 7. Treating a fitted distribution as exact
An empirical distribution of 1 000 request latencies cannot support claims about the 99.99th percentile (10⁵-scale events): the largest observed order statistic has expectation well below the true 1 − 1/(n+1) quantile. Tail statements need a parametric assumption (Pareto/GPD) plus justification, not an ECDF extrapolation.

### 8. Ignoring that many distributions share only two moments
Matching mean and variance does not identify a family: lognormal(μ, σ) and a two-point mixture can share both. Selection must use shape evidence (skewness, tail plots, goodness-of-fit) — χ² or KS — not just the first two moments.

## Self-check on distribution choice

1. *"n = 40, so I'll use a normal for this count data."* — Large n does not make a Poisson mean normal-shaped when λ is small. With λ = 2, P(X ≥ 8) = 0.0058; the normal with the same mean and variance gives 0.0067 — close, but at λ = 0.5 the normal approximation is qualitatively wrong (it puts probability below 0).
2. *"Variance equals mean, therefore Poisson."* — Necessary, not sufficient. Check the tail: for Poisson(9), P(X ≥ 15) ≈ 0.066. Overdispersed count data (variance 3× the mean) fails this and needs negative binomial instead — check the upper tail too: Poisson(9) gives P(X ≥ 15) ≈ 0.041, and data far above that at mean 9 are overdispersed.
3. *"Uniform is the safe default for an unknown bounded quantity."* — Only if you genuinely know nothing about location within the bounds. Uniform(0, 100) for a reaction time that clusters near 40 throws away information every later step needed.
4. *"Log-normal and normal are interchangeable after taking logs."* — True only if the raw data are strictly positive and the log histogram is symmetric. If zeros appear, the log transform is undefined and the model choice was wrong before you transformed.
5. *"Exponential waiting time means the process is memoryless — so past failures don't matter."* — Applies only to a homogeneous Poisson process. If arrivals rate changes by hour (call centers, traffic), the exponential inter-arrival with a single rate is misspecified; use a non-homogeneous or mixture model.
