# Step-by-Step Guide: Bayesian Statistics

## Worked example: Beta–Binomial updating (conjugate)

Prior: p ~ Beta(α = 2, β = 2) (mean 0.5 — "weak belief that the coin is fair"). Data: 9 heads and 1 tail in 10 flips.

### Step 1 — Prior × likelihood
p(θ | D) ∝ L(θ)·π(θ) ∝ θ⁹(1−θ)¹ · θ¹(1−θ)¹ = θ¹⁰(1−θ)²

### Step 2 — Recognize the kernel
θ^α′−1(1−θ)^β′−1 with α′ = 11, β′ = 3 → **posterior = Beta(11, 3)** (the normalizing constant is B(11,3), the marginal likelihood ratio).

### Step 3 — Posterior summaries
- mean = α′/(α′+β′) = 11/14 = **0.786**
- variance = α′β′/((α′+β′)²(α′+β′+1)) = 33/(196 × 15) = 33/2940 = **0.01122**, sd = **0.106**
- MLE would be 0.900; the prior pulls the estimate down — that is *regularization*, not bias.

### Step 4 — Posterior probability of a statement (the Bayesian answer)
P(p > 0.5 | D) = 1 − I₀.₅(11, 3) = P(Y ≤ 10) where Y ~ Binomial(13, 0.5)
= 1 − [C(13,11) + C(13,12) + C(13,13)]/2¹³ = 1 − (78 + 13 + 1)/8192 = 1 − 92/8192 = **0.9888**

### Step 5 — Sanity checks
- Prior Beta(2,2) → posterior mean 0.786 sits between prior mean 0.5 and data mean 0.9, closer to data because 10 observations outweigh 2 pseudo-observations of each kind (total prior strength α+β = 4 "prior flips").
- Normalization: the Beta(11,3) density integrates to 1 by construction (kernel matched to a known family).

## Worked example: the medical-test posterior in odds form
Prior odds = 0.01/0.99 = 0.0101; likelihood ratio = 0.99/0.05 = 19.8; posterior odds = 0.0101 × 19.8 = **0.2** → posterior probability = 0.2/1.2 = **1/6 ≈ 16.7%** — matching lab 01 by a different route.

## Verification checklist
- [ ] Posterior integrates to 1 (numeric check, or conjugate kernel matched)
- [ ] Data used exactly once (prior not already fit on the same sample)
- [ ] Prior sensitivity reported for small n (vary α, β; compare conclusions)
- [ ] MCMC (if used): split-R̂ < 1.01, ESS > 400, trace plots clean
- [ ] Interval labeled *credible* (posterior probability) or *confidence* (long-run coverage) — never both
