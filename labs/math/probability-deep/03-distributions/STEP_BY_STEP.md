# Step-by-Step Guide: Probability Distributions

## Worked example: Poisson arrival in a call center

λ = 4 calls per 15-minute window. Model X ~ Poisson(4): P(X = k) = e^{−4} 4ᵏ/k!.

### Step 1 — Compute the boundary term
P(X = 0) = e^{−4} = 0.018316 (verify: e^{−4} = 1/e⁴ = 1/54.598 = 0.018316 ✓)

### Step 2 — Recurse instead of factorials
P(X = k+1) = P(X = k) · λ/(k+1):
- P(1) = 0.018316 × 4 = 0.073263
- P(2) = 0.073263 × 4/2 = 0.146525
- P(3) = 0.146525 × 4/3 = 0.195367

### Step 3 — Answer a service question
P(X ≥ 4) = 1 − P(X ≤ 3) = 1 − (0.018316 + 0.073263 + 0.146525 + 0.195367)
= 1 − 0.433471 = **0.566529** — more often than not, 4+ calls per window.

### Step 4 — Check against mean and variance
E[X] = λ = 4 and Var(X) = λ = 4; our four terms must not exceed 1 total: 0.4335 < 1 ✓ (full pmf sums to 1).

## Worked example: normal difference

X ~ N(50, 100), Y ~ N(30, 64) independent (σₓ = 10, σᵧ = 8). D = X − Y:
- E[D] = 50 − 30 = **20**
- Var(D) = 100 + 64 = **164** (variances add for a difference!), σ_D = √164 ≈ **12.806**
- P(D > 0) = P(Z > (0 − 20)/12.806) = P(Z > −1.562) = Φ(1.562) ≈ **0.941**

## Verification checklist
- [ ] Support is correct: pmf = 0 off-support, density integrates to 1 over the declared interval
- [ ] Σ pmf or ∫ pdf = 1 to within 1e-10 (use the recurrence for Poisson/Binomial, quadrature for densities)
- [ ] Mean/variance from the pmf match the closed form (λ, np(1−p), σ², …)
- [ ] Tail queries use the right CDF boundary: P(X > k) = 1 − F(k), P(X ≥ k) = 1 − F(k−1)
- [ ] Parameterization confirmed by a sample mean within ~3σ/√n of the theoretical mean
