# Interview: Probability Distributions

### Q1. Which distribution for "number of events in an interval"? When does Poisson fail?
**A.** Poisson(λ) when events are rare, independent, and at a constant rate. It fails on three counts: (a) overdispersion — real counts often have Var > mean (negative binomial is the first fallback); (b) clustering/autocorrelation (Hawkes processes); (c) a finite-capacity denominator — with n trials and small p it's Binomial(n, p) with λ = np, and the Poisson approximation's P(X = 0) error at n = 10, p = 0.4 is e^{−4} = 0.0183 vs 0.6¹⁰ = 0.0060, a 3× miss in the tail.

### Q2. Normal or lognormal for latency data?
**A.** Latency is positive and typically right-skewed with a heavy tail; normal puts mass at negative values and underweights the tail. Lognormal (or gamma/Weibull) matches the shape: mean = e^{μ+σ²/2}, median = e^μ. Verify empirically: log-transform then QQ-plot against normal, or compare AIC/KS between the two fits. The CLT justifies normality of the *mean* of many latencies, not of a single latency.

### Q3. P(X > 40) returns 0 in code. Why and fix?
**A.** Computed as 1 − cdf(40), which cancels: Φ(40) = 1 to double precision (~10⁻³⁵⁰ tail). Fix: use the survival function `sf(x)` / erfc, or compute the log tail directly. Same failure mode appears in likelihood products (use logPdf sums) and in p-values reported as exactly 0 (report p < 1e-300 or compute via the complementary routine).

### Q4. Two distributions with identical mean and variance — how do you tell them apart?
**A.** Higher-order shape: skewness (lognormal > 0), kurtosis (Pareto infinite for α ≤ 4), tail plots (log survival vs log x: straight line ⇒ Pareto), QQ-plot against the candidate family, and formal tests (χ² with binned counts, KS/Cramér–von Mises on the fitted family — with parameters estimated on held-out data, since in-sample fitting invalidates the standard null distribution). Moments identify neither the family nor the tail.

### Q5. Sum of two independent Poissons? Sum of two gammas?
**A.** Poisson(λ₁) + Poisson(λ₂) = Poisson(λ₁ + λ₂) — closed form, because their pgfs multiply into another Poisson. Gamma(α₁, θ) + Gamma(α₂, θ) with a *shared scale* = Gamma(α₁ + α₂, θ); different scales ⇒ no closed form, use convolution/FFT or the CLT. Normals always close (means and variances add). These closure properties are exactly why those families recur in queueing and reliability models.

## Q7: Which distribution for "how many trials until the first success," and why is its mean 1/p?

Answer: Geometric on {1, 2, 3, …} with P(X = k) = (1−p)^{k−1} p. The mean is 1/p by the memoryless argument: E = p·1 + (1−p)(1 + E), solve E = 1/(p) — each trial is a fresh copy of the same problem, so the expected remaining wait never changes. Mention the variant: if you count failures before success (support {0, 1, …}), the mean is (1−p)/p; always state which convention you use, because interviewers' follow-ups depend on it.

## Q8: Poisson or binomial for this situation — how do you decide?

Answer: Ask what is fixed. Binomial: known number of trials n, each with success probability p — you *know* the denominator. Poisson: events occur independently at a rate per unit of time/space, and the count of events in a window is what you observe — the denominator (n) is not defined, only the rate. The Poisson(λ) is the limit of Binomial(n, p) with λ = np as n → ∞, p → 0; so "rare event, large exposure" justifies Poisson from a binomial, and I'd verify the approximation by checking np is not large enough to make the binomial visibly finite (P(X = n) non-negligible).

## Q9: What breaks if you fit a normal to bounded, skewed data?

Answer: Two failures. (1) Support: the fitted density assigns positive probability to impossible values — for a 0–100 scale it quietly leaks mass beyond the bounds, and any simulation using it produces invalid records. (2) Tail asymmetry: for right-skewed data the normal's symmetric tails understate the upper tail and overstate the lower; downstream risk metrics (95th percentile cost, VaR-style summaries) come out biased low. The standard fix is to model on the transformed scale (log, logit) with the corresponding transformed distribution, or use a bounded family (beta for [0,1], scaled beta) — and to report which you chose and why.

## Tips

- Quote one memorized identity per family (Poisson mean = variance; binomial variance = np(1−p); exponential memoryless) — it signals fluency faster than prose.
- When asked "which distribution," answer with the *data-generating mechanism* first, family second.
