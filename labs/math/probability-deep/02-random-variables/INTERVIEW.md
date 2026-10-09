# Interview: Random Variables

### Q1. Does Var(X + Y) = Var(X) + Var(Y)?
**A.** Only if Cov(X, Y) = 0 (independence is sufficient but stronger than needed). Expectation is linear without any condition because it is a sum of sums; variance squares the sum and produces the cross term 2Cov(X, Y). For n i.i.d. variables it collapses to nσ², which is why Var(X̄) = σ²/n — the result behind every standard error.

### Q2. A uniform distribution has f(x) = 1/8 on [0, 8]. How can a probability exceed 1?
**A.** It doesn't — 1/8 is a density, units of 1/x. P(X ∈ [0,1]) = ∫₀¹ (1/8) dx = 1/8 ≤ 1. A density can exceed 1 (Uniform(0, 0.4) has f = 2.5) as long as the total integral is 1. Only integrals over sets are probabilities; point densities are bookkeeping that changes when you change units.

### Q3. Y = X², X ~ Uniform(−1, 1). Find f_Y.
**A.** F_Y(y) = P(X² ≤ y) = P(−√y ≤ X ≤ √y) = (2√y)/2 = √y for y ∈ (0,1). Differentiate: f_Y(y) = 1/(2√y). Check: ∫₀¹ 1/(2√y) dy = [√y]₀¹ = 1 ✓. The factor 2 comes from both branches ±√y — dropping one branch leaves a density integrating to 1/2, the most common error in transformation problems.

### Q4. E[X] = 100, Var(X) = 400. Estimate P(X < 80) with no other information.
**A.** Chebyshev gives only a two-sided bound: P(|X − 100| ≥ 20) ≤ 400/400 = 1 — vacuous. Cantelli's one-sided inequality: P(X − μ ≤ −kσ) ≤ 1/(1 + k²); here k = 10/20 = 1, so P(X ≤ 80) ≤ 1/2. Without a distributional assumption, two moments barely constrain the tail — which is exactly why labs 03 and 07 need named families, and why sample-size formulas assume the CLT rather than moments alone.

### Q5. Why does the mean of a lognormal exceed its median?
**A.** X = e^{Z}, Z ~ N(μ, σ²): median = e^μ (the median of Z passes through the monotone map) while E[X] = e^{μ + σ²/2} (from the normal MGF). At σ = 1 the mean is e^{0.5} ≈ 1.65× the median because the right tail contributes mass with large leverage. Practical consequence: for latency, income or claim sizes, always report median/IQR — the mean is dominated by observations nobody experienced.

## Q7: How would you test whether a sample comes from a normal distribution?

Answer: Use three angles rather than one test. (1) A Q-Q plot — visual, and shows *where* a departure sits; (2) a formal test — Shapiro–Wilk for moderate n, Anderson–Darling if tail behavior matters, since it weights the tails more than the KS test; (3) a check of what the conclusion is *for* — if the sample feeds a t-test, the t-test is robust to moderate non-normality once n > 30, so a rejected normality test at n = 5000 need not change the analysis. Always mention that if parameters were estimated from the data, the standard critical values don't apply (Lilliefors correction).

## Q8: Mean and variance are given — when is that *not* enough?

Answer: When the distribution is not in a two-parameter family. Chebyshev's inequality gives bounds from mean and variance alone, but those bounds are often too loose to act on. Two distributions with identical mean and variance — a normal and a two-point distribution at μ ± σ — differ completely in tail probability: P(X ≥ μ + 3σ) is 0.0013 under the normal and exactly 1/9 under the symmetric two-point law. If the decision depends on extremes, ask for the full data or at least quantiles/skewness.

## Q9: What is the difference between the law of large numbers and the central limit theorem?

Answer: The LLN is about *where the average goes* — it converges to μ; it says nothing about the fluctuations around μ. The CLT is about *the distribution of the fluctuations* — √n(X̄ − μ) converges to N(0, σ²), giving the bell curve's width σ/√n. The LLN holds under far weaker conditions (finite mean suffices for the weak version); the CLT needs finite variance. You can have the LLN without the CLT (Pareto with 1 < α < 2 has finite mean, infinite variance): the average still converges, but too erratically for a normal approximation.

## Interview tips specific to this topic

- Quote the 68-95-99.7 rule *and* name its assumption in the same breath — it signals that you know it is conditional.
- When given mean and variance, immediately ask "and what shape?" before computing anything.
- Know one non-normal example cold (exponential waiting times or Poisson counts) so you can pivot from any "assume normality" prompt.
