# Step-by-Step Guide: Estimation Theory

## Worked example: MLE, SE and CI for five observations

Data: x = (2, 5, 1, 3, 4), i.i.d. from N(μ, σ²) with σ unknown.

### Step 1 — MLE by maximizing the log-likelihood
ℓ(μ, σ²) = −(n/2)log(2πσ²) − Σ(xᵢ − μ)²/(2σ²). ∂ℓ/∂μ = Σ(xᵢ − μ)/(2σ²) = 0 → **μ̂ = x̄ = 3**.
∂ℓ/∂σ² = 0 → **σ̂² = (1/n)Σ(xᵢ − x̄)² = 10/5 = 2.0** (note the n divisor).

### Step 2 — Unbiased variance for inference
Σ(xᵢ − 3)² = 1 + 4 + 4 + 1 + 0 = 10 → s² = 10/(5−1) = **2.5**, s = 1.5811.

### Step 3 — Standard error of the estimator
SE(x̄) = s/√n = 1.5811/√5 = 1.5811/2.2361 = **0.7071**

### Step 4 — 95% interval with unknown σ (Student t, n−1 = 4 df)
t₀.₀₂₅,₄ = 2.776 → x̄ ± t·SE = 3 ± 2.776 × 0.7071 = 3 ± 1.963 → **(1.04, 4.96)**

### Step 5 — Cross-check with the Cramér–Rao bound
For N(μ, σ²): Fisher information for μ is I(μ) = n/σ², so any unbiased estimator has Var ≥ σ²/n. With s² = 2.5: bound ≈ 2.5/5 = 0.5, and Var(x̄) = 2.5/5 = 0.5 — **x̄ attains the bound**: it is efficient (and UMVU by Lehmann–Scheffé).

## Worked example: Uniform(0, θ), the non-regular case
L(θ) = θ⁻ⁿ for θ ≥ max(x), else 0 → **θ̂_MLE = max(x)**.
E[max] = nθ/(n+1) ⇒ biased; corrected **θ̂ = (n+1)/n · max** is unbiased.
Rate: Var(max) = nθ²/((n+1)²(n+2)) ~ θ²/n² — the estimator converges at rate **n, not √n**, and Cramér–Rao does not apply (support depends on θ). This is the standard example that "MLE is √n-normal" is a *regular-family* theorem.

## Verification checklist
- [ ] Score equations solved exactly (gradient ≈ 0 at the optimum, checked numerically)
- [ ] σ̂² labeled with its divisor: n (MLE) or n−1 (unbiased)
- [ ] SE derived from information/sandwich, not from the raw spread
- [ ] Interval method matched to n and to σ known/unknown (z vs t)
- [ ] Family checked for regularity before quoting CRB or √n-normality
