# Why It Exists: Multivariate Statistics

## The problem: one variable at a time lies
Galton and Pearson's bivariate tools (1889–1896) answered questions about *two* measurements, but real data arrive with many at once, and univariate analysis fails systematically:

- **Marginal associations contradict joint ones.** Yule (1897) showed that a strong association between pauperism and "outdoor relief" across unions disappeared — or reversed — once destitution was held constant. One variable at a time cannot see confounding; conditioning requires the joint model.
- **Units make cross-variable comparisons meaningless.** Covariance in cm·kg vs m·g differs by 1000×; correlation (Pearson, 1896) is the unit-free normalization that made meta-comparison possible.
- **Redundancy wastes data.** Five highly correlated measurements do not carry five independent pieces of information. Hotelling's (1933) principal components extract the effective dimension — the reason PCA predates modern ML by 70 years.

## What the framework adds over lab 01–03
1. **A geometry for data**: Σ defines distance (Mahalanobis, 1936), length (variance along a direction) and volume (ellipsoids of the MVN) — turning "similar?" into a computable question.
2. **Matrix inference**: Wishart's 1928 distribution of S gave sampling theory for covariance matrices; Hotelling's T² (1931) extended the t test to p response variables simultaneously.
3. **Dimensionality reduction with guarantees**: PCA's truncation error is exactly the sum of discarded eigenvalues (Eckart–Young), so the trade-off between compression and fidelity is measurable rather than guessed.
4. **Multivariate models as the default**: regression with several predictors (Yule 1907; Fisher's matrix formulation), LDA (Fisher, 1936), and every "control for X" analysis in the social and medical sciences.

## What it refuses to do
It does not infer causation from correlation structure — a point Fisher pressed repeatedly. Two Gaussian variables with ρ = 0.9 are equally consistent with X → Y, Y → X, or a common cause; the multivariate calculus constrains *association*, and the causal claim needs design or assumptions (Pearl's d-separation, 1988, is the later machinery for that gap).

## The alternative, and why it failed

**Analyze each variable separately, then average the conclusions.** Yule's 1897 pauperism data show why: outdoor relief correlates with pauperism across unions, but stratifying on destitution collapses the association — a marginal result that is simply false as a statement about any actual union. Separate univariate analyses cannot condition on anything; confounding control *requires* the joint model.

**Keep only pairwise correlations, skip the matrix.** Pairwise r's need not even form a valid distribution: ρ₁₂ = ρ₁₃ = 0.9 and ρ₂₃ = −0.9 are each legal pairwise, yet the 3×3 correlation matrix has a negative eigenvalue (det = −2.888), so no joint law realizes them. Any procedure that needs a draw, a density, or a distance (Mahalanobis) requires a coherent Σ, not a list of pairs.

**Fit one predictor at a time and select by significance.** With p predictors the selection itself overfits — testing p nulls at α = 0.05 yields 0.05p false selections on average — and the omitted-variable bias in each selected coefficient is exactly the partial-vs-marginal gap lab 04 measures.

## Why the matrix form specifically

Σ is simultaneously the covariance table, the metric tensor for distances, the spectrum for dimensionality reduction, and the sampling object of the Wishart — one p × p object serving four jobs is why multivariate statistics is organized around it rather than around a zoo of pairwise statistics.

## The test of the abstraction

Ask of any "multivariate method": can it be expressed as scalar operations on a covariance structure plus a projection? PCA (eigen of Σ), LDA (generalized eigen of S_W⁻¹S_B), Hotelling (quadratic form (x̄−μ₀)ᵀS⁻¹(x̄−μ₀)), Mahalanobis (same quadratic form per point), Gaussian likelihood (log-det + quadratic form) all answer yes — which is why they share one implementation layer, and why a defect in Cholesky surfaces in every one of them at once.
