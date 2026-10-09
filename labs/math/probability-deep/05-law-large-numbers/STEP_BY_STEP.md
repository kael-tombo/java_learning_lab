# Step-by-Step Guide: Law of Large Numbers and CLT

## Worked example: how likely is |X̄ − μ| ≥ 1 for n = 36 fair dice?

### Step 1 — Single-draw moments
μ = 3.5, σ² = (1/6)Σ(k − 3.5)² = 35/12 ≈ 2.9167, σ ≈ 1.7078.

### Step 2 — Sampling distribution of the mean
E[X̄] = 3.5, Var(X̄) = σ²/n = 2.9167/36 = 0.08102, SE = 1.7078/6 ≈ 0.2846.

### Step 3 — Chebyshev bound (no distribution assumed)
P(|X̄ − 3.5| ≥ 1) ≤ Var(X̄)/1² = **0.0810** — an 8.1% worst case.

### Step 4 — CLT approximation (n = 36 is moderate)
P(|X̄ − 3.5| ≥ 1) = P(|Z| ≥ 1/0.2846) = P(|Z| ≥ 3.514) ≈ 2 × 0.00022 = **0.00044**
The Chebyshev bound is ~180× the actual — a guarantee, not an estimate.

### Step 5 — Verify the 1/√n law numerically
Rerun with n = 144: SE = 1.7078/12 = 0.1423 — exactly half of 0.2846. Quadruple n ⇒ halve the SE. If your simulation shows otherwise, n is not what you think (or the draws aren't independent).

## Worked example: a poll
n = 1000 respondents, p̂ = 0.50 (worst case for variance):
SE = √(0.25/1000) = 0.01581 → 95% CI = 0.50 ± 1.96 × 0.01581 = 0.50 ± 0.031 → **(0.469, 0.531)**
This "±3 points" number is entirely 1.96 × 0.5/√n; for 90% precision (±1.5%) you need n = (1.96 × 0.5/0.015)² ≈ **4269** respondents.

## Worked example: CLT from a non-normal shape
Sum of 12 i.i.d. Uniform(0,1): mean 6, variance 12 × (1/12) = 1. The exact sum is Irwin–Hall, already very close to N(6, 1) — with k = 2 uniforms the sum is triangular (definitely not normal), k = 6 is visibly bell-shaped. Normality is a property of the *sum*, improving with the number of moderate-sized terms (or one dominant term: Lindeberg condition).

## Verification checklist
- [ ] SE reported as σ/√n and *measured* SE matches within Monte Carlo error (rerun with 4n to see it halve)
- [ ] Tail claims checked against k: Chebyshev bound (1/k²) stated as an upper bound, CLT value as an approximation
- [ ] Independence of draws asserted (or ESS used) before quoting σ²/n
- [ ] Moments verified to exist (finite mean, finite variance) before either theorem is invoked
