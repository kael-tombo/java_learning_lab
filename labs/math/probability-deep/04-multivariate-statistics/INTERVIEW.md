# Interview: Multivariate Statistics

### Q1. PCA or correlation: what's the difference, and when does scaling change PCA?
**A.** PCA decomposes Σ and finds directions of maximal *sample variance*; correlation analysis reads rᵢⱼ off the standardized matrix. PCA on raw data weights variables by their units — a variable measured in mm dominates PC1. Standardizing (using the correlation matrix) makes each variable contribute equally. Rule: same comparable units → covariance matrix; mixed units/scales → correlation matrix. Both preserve total variance (trace), but they rotate to different axes.

### Q2. Your covariance matrix is singular. What happened and how do you fix it?
**A.** rank(Σ) ≤ min(p, n−1), so p ≥ n makes it singular; perfect collinearity does too. Consequences: Mahalanobis distances NaN, MVN density undefined, LDA collapses. Fixes in order of preference: (1) reduce p (drop collinear/irrelevant features or PCA to k < n−1); (2) shrinkage Σ_λ = (1−λ)S + λ·diag(S) (Ledoit–Wolf); (3) ridge jitter Σ + εI as a stopgap. Increasing n is the structural fix.

### Q3. Two variables, ρ = 0.8. Portfolio of equal weight: compute the variance reduction.
**A.** Equal weights, equal σ: Var = σ²(1 + ρ)/2 = 0.9σ² for ρ = 0.8 (vs σ² in one asset) — only 10% variance reduction; for ρ = 0 it would be 0.5σ². The general lesson: diversification scales with (1 − ρ̄); correlated books don't diversify. Also note the *off-diagonal* term 2w₁w₂ρσ₁σ₂ is what a factor model estimates — getting ρ right matters more than refining σᵢ.

### Q4. PCA says 80% of variance is in two components. What does that NOT tell you?
**A.** It doesn't tell you those components predict anything: variance ≠ signal. A low-variance PC can carry class separation (heteroscedastic data), and high-variance PCs often capture nuisance variation (batch effects, measurement scale, subject ID). It also doesn't validate the linearity assumption — nonlinear structure (Swiss roll) is invisible to PCA and needs kernels/t-SNE/UMAP. Finally, "80%" is relative to the matrix you decomposed (Σ vs correlation) and to the sample: components estimated from n = 50 p = 100 data are themselves noisy (see Anderson's adequacy: n should exceed p for stable eigenvalues).

### Q5. How would you detect account takeover using this lab's tools?
**A.** Build a per-user feature vector (login hour, geo-distance-from-last, request rate, bytes, failure count), estimate μ and Σ from a robust estimator (MCD) over each user's own history, and score new sessions by Mahalanobis d². Threshold at a chi-square quantile with p df (d² ~ χ²_p for MVN data) — say χ²₅,0.999 = 20.5. Watch two failure modes: covariate drift (re-fit; refit windows or the baseline absorbs the attacker) and masking (attackers included in the baseline inflate Σ and hide themselves) — hence robust covariance and short, pre-attack training windows.

## Q6: You get a 10 000 × 500 dataset. What's your first move and why?

**A.** Compute n/p = 500/10 000 = 0.05 — p is 20× n, so the sample Σ is exactly singular and *any* method needing Σ⁻¹ or a full spectrum is off the table as-is. First move: (1) sanity — missingness, constant columns, units; (2) variance screen — drop near-zero-variance features (they are noise dimensions in PCA); (3) unsupervised reduction: randomized PCA on the centered matrix to k ≈ 50 components (O(npk), no p × p ever formed); (4) only then model, with the pipeline fit *inside* the cross-validation fold to avoid leakage. I'd report the scree plot and how much variance k components carry, and treat 10 000 features as an asset for later selection, not as input to a covariance inverse.

## Q7: Two analysts report r = 0.6 (n = 50) and r = 0.3 (n = 50) for the same variables in two studies. Significantly different?

**A.** Use Fisher's z transform, which is approximately normal with SE = 1/√(n − 3): atanh(0.6) = 0.6931, atanh(0.3) = 0.3095, SE = √(1/47 + 1/47) = 0.2063, so z = 0.3836/0.2063 = 1.86, two-sided p ≈ 0.063. Not significant at 0.05 — and that is the right lesson: correlation differences need *much* larger n than correlations themselves. If I were designing the second study, n ≈ 110 per group is what "detect Δz = 0.38 at 80% power" would require.

## Q8: PCA, factor analysis, and ICA — what problem does each actually solve?

**A.** PCA: an exact rotation maximizing retained variance — a *dimensionality reduction* tool, no noise model, deterministic. Factor analysis: a probabilistic latent-variable model x = Λf + ε distinguishing shared variance (communalities) from unique noise — an *inference* tool; it needs assumptions (uncorrelated factors, diagonal uniquenesses) and gives loadings whose rotation is not identified without constraints. ICA: assumes the sources are statistically *independent*, not merely uncorrelated — solves blind source separation (the cocktail-party problem), where PCA's uncorrelated-but-mixed outputs are still entangled. Choose by goal: compress → PCA; explain covariance → FA; unmix → ICA.

## Interview tips

- Have one number memorized from your own work: "our Σ had κ = 10⁸ until we dropped two collinear columns."
- When handed p ≈ n data, say "shrinkage or PCA before any inverse" *before* you're asked.
- Correlation differences go through Fisher z, not through comparing the two r's directly.
