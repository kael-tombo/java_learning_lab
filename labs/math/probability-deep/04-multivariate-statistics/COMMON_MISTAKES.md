# Common Mistakes: Multivariate Statistics

### 1. Covariance instead of correlation when comparing pairs
Cov(X, Y) scales with units: heights in cm vs m change the covariance by 100×, correlation unchanged. r = Cov/(σₓσᵧ) ∈ [−1, 1] is the comparable quantity; report covariance only for the same-scale joint quantities (it feeds Σ).

### 2. Inverting an ill-conditioned covariance matrix
With n = 10 observations of p = 15 features, the sample Σ is singular (rank ≤ n − 1) and Σ⁻¹ does not exist or explodes. Mahalanobis distance then produces distances dominated by noise. Fix: shrinkage (Ledoit–Wolf 2004), drop features, or n ≥ 5–10× p before inverting.

### 3. Component-wise regressions instead of partial regression
Two variables both correlated with a third (ice cream sales and drowning both track temperature) produce a strong marginal correlation with the wrong sign or magnitude once temperature is controlled — Yule's 1897 demonstration and Simpson's paradox (1951). Fit the joint model; the marginal association answers a different question.

### 4. PCA on unscaled data
PCA maximizes variance; variables measured in bigger units dominate the leading components. Height in mm vs weight in kg: the first PC is basically the mm column. Standardize (correlation matrix) when units differ — and know that using Σ vs the correlation matrix is a modeling choice, not a formatting one.

### 5. Interpreting the sample correlation as strong evidence with small n
r = 0.7 with n = 5: Fisher's z transform gives atanh(0.7) = 0.867, SE = 1/√(5−3) = 0.707, so the 95% CI is 0.867 ± 1.96×0.707 = [−0.52, 2.25] → r ∈ [−0.48, 0.98]. Almost anything is compatible with n = 5; using t = r√(n−2)/√(1−r²), r = 0.7 needs n ≥ 9 before the two-sided test clears p < 0.05 (t = 2.59, df = 7).

### 6. Assuming Σ diagonal because variables were "measured separately"
Marginal models ignore correlation: portfolio risk Σᵢwᵢ²σᵢ² vs true Var(ΣwᵢXᵢ) = ΣᵢΣⱼwᵢwⱼCovᵢⱼ. With ρ = 0.6 between two assets, the two-asset variance is σ₁² + σ₂² + 1.2σ₁σ₂, not the sum of variances — 20–60% error in σ for typical ρ.

### 7. Reading PCs as "the most important features"
PC1 maximizes *sample* variance, not predictive power and not causal relevance; a low-variance direction can carry the class signal entirely (heteroscedastic data). Always check PC–target association separately before discarding low-variance components.

### 8. Confusing the correlation matrix's determinant with independence
det(R) = 1 only when all |rᵢⱼ| = 0... exactly: R = I iff uncorrelated. But det(R) near 1 does not rule out a single strong pair offset elsewhere — inspect the eigenvalues (condition number) and the matrix, not just its determinant.

## Self-check: could you defend these answers?

1. *"Two variables, covariance 450, so they're strongly related."* — Strong by what scale? Covariance 450 means nothing until you divide by σₓσᵧ. Heights in cm × weights in kg routinely give covariances in the hundreds for r ≈ 0.6.
2. *"The correlation matrix is fine — all entries are between −1 and 1."* — Necessary, not sufficient. The matrix must also be positive semi-definite: for ρ₁₂ = 0.9, ρ₁₃ = 0.9, ρ₂₃ = −0.9 the entries all pass, but det = 1 + 2(0.9)(0.9)(−0.9) − 0.81 − 0.81 − 0.81 = −2.888 < 0, so no such joint distribution exists. Check eigenvalues ≥ 0, not just bounds.
3. *"PCA found the most important directions."* — The most *variable* ones, in the sample you gave it. If PC1 is a batch-effect axis or a unit artifact, "most important" is backwards for your goal.
4. *"n = 40, p = 35, so Σ is estimable."* — It is invertible but useless: rank ≤ 39 is not the issue, the condition number is. At n ≈ p the smallest eigenvalue of S is near zero by Marchenko–Pastur, and Σ⁻¹ amplifies noise ~1/λ_min. Shrink or reduce before any inverse.
5. *"Both variables are significant, so the pair is informative."* — Univariate significance says nothing about the *joint* structure: two marginally strong variables can be redundant (r = 0.95, one effective dimension) or complementary (partial r ≈ 0, two independent signals). Test the pair's contribution, not the marginals.
