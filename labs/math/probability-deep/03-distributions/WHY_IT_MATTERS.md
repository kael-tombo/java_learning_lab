# Why It Matters: Probability Distributions

## They are the vocabulary of everything downstream
- **Lab 05 (LLN/CLT)**: "X̄ ≈ N(μ, σ²/n)" only means something once Normal(μ, σ²) is a defined object with a known shape.
- **Lab 06 (estimation)**: an MLE is distribution-specific — λ̂ = n/Σxᵢ for Exponential, p̂ = k/n for Binomial, x̄ for Normal. Choose the family, get a different estimator with different bias.
- **Lab 07 (testing)**: the null distribution of the test statistic (t, χ², F) is a *named* distribution; the p-value is its tail area. Without named families there are no p-values.
- **Lab 08 (Bayes)**: conjugate families (Beta–Binomial, Gamma–Poisson) make posterior updating arithmetic instead of integration.

## Decisions are tail areas, not averages
The engineering and financial questions live in the tails:
- Reliability: P(component survives 10 000 h) = e^{−λ·10000} under exponential; Weibull shape > 1 signals aging.
- Queueing: P(wait > t) for M/M/1 = ρ·e^{−(μ−λ)t} — the tail decides staffing, not the mean wait.
- Finance: VaR is the 95th/99th percentile of the loss distribution — a quantile, invisible to mean and variance.

## Choosing wrong changes the answer by orders of magnitude
For lognormal(μ = 0, σ = 2): P(X > 1000) = P(Z > ln(1000)/2) = P(Z > 3.454) ≈ 2.7×10⁻⁴; the same data fit by a normal gives essentially zero. In the other direction, fitting a normal to Pareto-distributed claim sizes understates a 1-in-100-year loss by orders of magnitude — a documented cause of 2008-era risk-model failures.

## The practical discipline
Report the family, the fitted parameters, *and* a goodness-of-fit check. A mean without a distribution is half a statement; a percentile without one is a guess.

## Concrete decisions that change with the family

**Insurance reserve.** Claim sizes with variance 4× the mean are not Poisson-gamma; fitting a light-tailed family underestimates the 99.9th percentile that solvency rules require. Same expected loss, very different capital requirement.

**A/B test duration.** Binomial conversions with p ≈ 0.02: a normal approximation on the difference wastes or misallocates samples because the variance is p(1−p) and the distribution is visibly discrete at low counts — using the exact binomial test can cut the required sample size by avoiding the conservative normal padding, or reveal that a "significant" win rests on 40 vs 31 conversions.

**Capacity planning.** Poisson(λ = 90/min) peak-hour arrivals are ≈ normal (λ large), so ±2σ staffing works: 90 ± 2·9.5 ≈ 71–109. Poisson(λ = 4) is not: P(X ≥ 10) = 0.0081 exactly, while the normal with mean 4 and SD 2 gives only 0.0014 — a 6× underestimate of the busy-hour probability, so a site staffed to the normal tail is under-provisioned regularly.

**Quality control.** Defects per unit: Poisson with a *c-chart* triggers when counts exceed λ + 3√λ; using a binomial p-chart with the same data changes the control limits and therefore which day gets flagged. The family determines the alarm.

## What to ask when someone hands you a distribution

- What was counted/timed, and what fixes the denominator?
- Which tail decision does this feed (risk, staffing, threshold)?
- Which alternative family did you rule out, and with what evidence?
