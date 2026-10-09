# Step-by-Step Guide: Hypothesis Testing

## Worked example: one-sample t test

H₀: μ = 100; H₁: μ ≠ 100. Data: n = 25, x̄ = 102, s = 8 (σ unknown).

### Step 1 — Statistic
t = (x̄ − μ₀)/(s/√n) = (102 − 100)/(8/5) = 2/1.6 = **1.25**, df = n − 1 = 24.

### Step 2 — p-value (two-sided)
p = 2·P(T₂₄ > 1.25) ≈ 2 × 0.1115 = **0.223** — with t₀.₀₂₅,₂₄ = 2.064 > 1.25, do not reject.

### Step 3 — The interval says the same thing
95% CI = 102 ± 2.064 × 1.6 = 102 ± 3.30 → **(98.70, 105.30)**; it contains 100, consistent with p > 0.05 (they are the same inversion).

### Step 4 — Power: was this test capable of seeing anything?
For a standardized effect δ = (μ₁ − μ₀)/σ = 0.5 at α = 0.05 (two-sided), 80% power:
n per group = 2(z₀.₀₂₅ + z₀.₂₀)²/δ² = 2(1.96 + 0.84)²/0.25 = 2 × 7.84/0.25 = **62.7 → 63 per group**.
n = 25 with δ = 0.5 gives power ≈ Φ(δ√n − 1.96) − Φ(−δ√n − 1.96) = Φ(2.5 − 1.96) ≈ Φ(0.54) ≈ **0.71** — a 29% chance of missing a real half-sigma effect.

## Worked example: multiple comparisons
20 tests, α = 0.05 each, independent:
P(≥ 1 false positive) = 1 − (1 − 0.05)²⁰ = 1 − 0.95²⁰ = 1 − 0.3585 = **0.6415**
Bonferroni α' = 0.05/20 = 0.0025 per test restores FWER ≤ 0.05 at the cost of power; Benjamini–Hochberg instead controls the expected *proportion* of false discoveries among rejections.

## Verification checklist
- [ ] Hypotheses, α, tails and primary endpoint fixed before looking at data
- [ ] Reference distribution matches design (t vs z, Welch df, χ² expected counts ≥ 5)
- [ ] p-value stated as P(data | H₀), never P(H₀ | data)
- [ ] Interval and effect size reported alongside p
- [ ] Power/minimum detectable effect computed *before* the study; family-wise correction named for m > 1 tests
