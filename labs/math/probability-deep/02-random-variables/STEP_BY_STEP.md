# Step-by-Step Guide: Random Variables

## Part A — Discrete: heads in 3 fair flips

### Step 1 — List the support and PMF
k = 0,1,2,3 with P(X = k) = C(3,k)(1/2)³: 1/8, 3/8, 3/8, 1/8. Check Σp = 1 ✓

### Step 2 — Expectation (each term k·p)
E[X] = 0·(1/8) + 1·(3/8) + 2·(3/8) + 3·(1/8) = (0 + 3 + 6 + 3)/8 = 12/8 = **1.5**
Matches np = 3 × 0.5 ✓

### Step 3 — Second moment and variance
E[X²] = 0·(1/8) + 1·(3/8) + 4·(3/8) + 9·(1/8) = 24/8 = 3
Var(X) = 3 − 1.5² = 3 − 2.25 = **0.75**, σ = √0.75 ≈ 0.866
Check np(1−p) = 3 × 0.5 × 0.5 = 0.75 ✓

### Step 4 — Affine transformation Y = 5X + 1
E[Y] = 5(1.5) + 1 = **8.5**; Var(Y) = 5² × 0.75 = **18.75**; sd(Y) = 5 × 0.866 = **4.33**.

## Part B — Continuous: X ~ Uniform(0, 2)

### Step 1 — Density and normalization
f(x) = 1/2 on [0, 2]; ∫₀² ½ dx = 1 ✓

### Step 2 — Expectation as center of mass
E[X] = ∫₀² x·½ dx = ½ · [x²/2]₀² = ½ · 2 = **1**

### Step 3 — Variance as average squared deviation
Var(X) = ∫₀² (x − 1)² · ½ dx. Substitute u = x − 1: ½ ∫₋₁¹ u² du = ½ · (2/3) = **1/3 ≈ 0.3333**.

### Step 4 — Non-linear transform breaks averages
Z = X²: E[Z] = ∫₀² x²·½ dx = ½ · (8/3) = 4/3 ≈ 1.333, while (E[X])² = 1. The gap 1.333 − 1 = 0.333 is exactly Var(X) — this *is* the identity E[X²] = Var(X) + (E[X])².

## Verification checklist
- [ ] Σp = 1 (discrete) and ∫f = 1 (continuous), each to 1e-12
- [ ] σ ≥ 0 and Var(X) = E[X²] − μ² ≥ 0
- [ ] Var(aX + b) = a²Var(X) — the constant b never enters
- [ ] E[g(X)] computed by summing/integrating g, not by plugging in g(E[X])

## Extension: the full chi-square goodness-of-fit procedure

Step 12. State hypotheses: H₀ "the data follow the claimed distribution F", H₁ "they do not".
Step 13. Estimate any free parameters of F from the data itself, and reduce the degrees of freedom accordingly: df = (number of bins) − 1 − (number of estimated parameters).
Step 14. Choose bin boundaries so every expected count is ≥ 5 (merge tail bins if needed).
Step 15. Compute χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ over all bins.
Step 16. Compare with the χ² critical value at the chosen α; reject if the statistic exceeds it.
Step 17. If rejected, inspect the standardized residuals (Oᵢ − Eᵢ)/√Eᵢ per bin to see *where* the model fails — a significant test alone does not say which tail is wrong.

Example: 120 observations in 6 equiprobable categories, observed (15, 18, 25, 20, 22, 20), expected 20 each:
χ² = (25+4+25+0+4+0)/20 = 58/20 = 2.9, df = 5, p ≈ 0.72 → no reason to reject.
