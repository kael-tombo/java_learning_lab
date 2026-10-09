# How It Works: Law of Large Numbers and CLT

## 1. Where Var(X̄) = σ²/n comes from
Independence kills the cross terms: Var(X₁ + … + Xₙ) = ΣVar(Xᵢ) + 2Σᵢ<ⱼCov = nσ² (covariances are 0). Divide by n²: Var(X̄) = nσ²/n² = σ²/n. Every standard error in labs 06–07 is this one line; drop independence and the 2ΣCov terms survive, inflating the SE.

## 2. Chebyshev on the mean is the weak law
Apply Markov's inequality to the non-negative variable (X̄ − μ)²: P(|X̄ − μ| ≥ ε) ≤ E[(X̄ − μ)²]/ε² = σ²/(nε²) → 0 as n → ∞. That *is* the WLLN — the entire proof is variance of the average plus one inequality. It explains why finite variance was assumed from 1867 until Khinchin's (1929) theorem removed it (via truncation, for i.i.d. with E|X| < ∞).

## 3. The CLT is a fourth-moment (or transform) argument
Lyapunov's proof: expand the characteristic function φ(t) of (X − μ)/σ near t = 0: log φ(t) = −t²/2 + o(t²). The n-fold product φ(t/√n)ⁿ → e^{−t²/2} — the normal characteristic function. Non-identical summands work when no single term dominates (Lindeberg's condition: for every ε, maxᵢ Var of terms beyond ε√n total → 0).

## 4. Why the shape emerges from shapeless pieces
Convolution smooths: uniform ⊛ uniform = triangle; ⊛ uniform = cubic B-spline; after 12 convolutions the density is visually Gaussian. Algebraically, each convolution multiplies characteristic functions, and a product of many bounded factors converges to the Gaussian's — normality is the fixed point of convolution with a *finite-variance* kernel.

## 5. The speed: Berry–Esseen
supₓ |Fₙ(x) − Φ(x)| ≤ C·ρ/(σ³√n) with ρ = E|X − μ|³ (the *absolute* third moment) and best-known universal C ≤ 0.4748. The ratio ρ/σ³ is scale-free: Uniform(0,1) gives 0.03125/0.02406 ≈ **1.30**, Exponential(1) gives 12/e ≈ **4.42** — so a skewed input converges to normality about 3.4× slower at the same n. The bound is distribution-sensitive: symmetric light tails finish first.

## 6. What failure looks like
Infinite variance (Pareto α = 1.8): ρ = ∞, Berry–Esseen void, and sums converge to an α = 1.8 stable law with jumps — sample means overestimate and then snap. The corrective: verify moments exist (lab 03 diagnostics), then choose Gaussian (CLT), stable (Lévy), or trimmed estimators (robust statistics).

## 7. Turning Berry–Esseen into a sample size

Invert the bound for a target normal-approximation error ε: need C·(ρ/σ³)/√n ≤ ε, so n ≥ (C·(ρ/σ³)/ε)². With C = 0.4748:
- Uniform(0,1), ρ/σ³ = 1.30, ε = 0.01 → n ≥ (0.4748 × 1.30 / 0.01)² = **3 810**.
- Exponential(1), ρ/σ³ = 4.42, ε = 0.02 → n ≥ (0.4748 × 4.42 / 0.02)² = **11 011**.

Same target accuracy, 2.9× the data for the skewed input — the bound prices skewness directly into n. (It is a worst-case guarantee: the true error is usually far below it, so treat these as ceilings, not predictions.)

## 8. Effective sample size from the variance of a correlated mean

Var(X̄) = (σ²/n)(1 + 2Σₖρₖ) comes from expanding the n² covariance terms and grouping by lag: each lag k contributes 2(n−k)/n ≈ 2ρₖ of cross terms. Setting Var(X̄) = σ²/n_eff identifies n_eff = n/(1 + 2Σρₖ). For AR(1) the sum is geometric: Σρₖ = ρ/(1−ρ), giving n_eff = n(1−ρ)/(1+ρ) — ρ = 0.5 → n/3, ρ = 0.9 → n/19. Same formula as in MENTAL_MODELS #6 and INTERVIEW Q3; here it is derived rather than quoted, which is why it can be trusted for ρ < 0 too (n_eff > n).
