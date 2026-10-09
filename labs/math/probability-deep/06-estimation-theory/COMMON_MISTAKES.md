# Common Mistakes: Estimation Theory

### 1. Reporting the MLE variance with 1/n
σ̂²_MLE = (1/n)Σ(xᵢ − x̄)² estimates (n−1)/n·σ² — biased low. At n = 10 the estimate is 90% of the truth (10% bias in variance, 5% in sd). The unbiased s² = Σ(xᵢ − x̄)²/(n−1) is what standard errors and t-tests expect. Both are consistent; the mistake is quoting the MLE while *labeling* it σ̂² without noting the divisor.

### 2. Ignoring the bias–variance tradeoff
MSE(θ̂) = bias² + variance. Shrinking an estimator toward 0 adds bias and removes variance; whether MSE improves depends on the truth. For Uniform(0, θ): MLE is max(x) with E = nθ/(n+1) — biased; the unbiased correction (n+1)/n·max increases MSE at every n. "Unbiased" is not "better," only a different point on the tradeoff.

### 3. Treating a biased estimator as asymptotically consistent anyway
Bias that vanishes with n (n/(n+1) factor) is harmless asymptotically; bias that *doesn't* (squaring a noisy measurement: E[X²] = μ² + σ² — the estimator of μ² is biased by σ² forever) is not. Check whether bias → 0 before trusting large-n theory.

### 4. Assuming the Cramér–Rao bound applies
CRB needs a *regular* family: support not parameter-dependent, twice-differentiable log-likelihood, I(θ) > 0. For Uniform(0, θ), Pareto's scale, or a mixture's weight, those fail — the bound is infinite or undefined and the MLE's asymptotics are *not* normal (max-based estimators converge at rate n, not √n).

### 5. Confusing the standard error with the sample spread
s = 15.8 describes individuals; SE = s/√n = 15.8/√50 = 2.24 (n = 50) describes the estimator. Quoting "mean 3 ± 15.8" as if it were an estimate of μ uses the wrong quantity — the interval is √50 ≈ 7.1× too wide.

### 6. Ignoring dependence when computing SE
Wald SE from the observed information assumes i.i.d. contributions. Clustered/serially dependent data inflate true variance by 1 + 2Σρₖ; the sandwich (White, 1980) or cluster-robust variance is required, or the interval under-covers (see lab 05's n_eff).

### 7. Selecting models on training likelihood only
MLEs of larger models always fit at least as well (likelihood monotone in parameters). Model choice needs penalty or held-out data: AIC = −2logL + 2k, BIC = −2logL + k·log n. Reporting the best training fit without penalty conflates estimation with selection.

### 8. Forgetting that MLE ≠ plug-in of moments
For Binomial(n, p), MLE(p̂) = k/n equals the moment estimator; for Lognormal(μ, σ²) MLE of σ² uses 1/n and *log* data — while the moment estimator on raw data has much larger variance. Which estimator you use changes the answer; state which and why.

## Self-check: can you defend these answers?

1. *"The optimizer converged, so θ̂ is the MLE."* — Convergence is a statement about the algorithm, not the objective: for a flat likelihood (saturated model, p ≥ n) every point is a stationary point. Show ‖score‖ small **and** information positive definite **and** compare against a known closed form when one exists (normal μ: θ̂ must equal x̄ to machine precision).
2. *"My SE from the model is 0.2, the bootstrap says 0.6 — the bootstrap must be wrong."* — The opposite conclusion is likelier: model-based SE assumes the family is right and data independent; the bootstrap's job is exactly to catch that. Diagnose with the sandwich (White 1980): if I⁻¹JI⁻¹ >> I⁻¹, your data are dependent or misspecified and the honest SE is the bigger one.
3. *"Unbiased means it's the estimator to report."* — Uniform(0, θ): unbiased θ̂ = (n+1)/n·max(x) has *higher* MSE than the biased MLE at every n (the correction inflates variance more than it removes bias). Unbiasedness is one constraint in a tradeoff, not a ranking.
4. *"n = 20, so 1.96 is my critical value."* — t₁₉ = 2.093: with s estimated from 20 points the interval is 6.8% wider than z. For n = 4 the gap is 62% (t₃ = 3.182 vs 1.96): using z there produces an interval that under-covers badly — the classic small-sample Wald failure.
5. *"The MLE is efficient, so the Cramér–Rao bound is achieved."* — Asymptotically, in regular families only. At n = 10 the MLE of σ² is 10% biased, and for Uniform(0, θ) the bound does not exist at all. Efficiency is a limit statement — always say "as n → ∞" out loud.
