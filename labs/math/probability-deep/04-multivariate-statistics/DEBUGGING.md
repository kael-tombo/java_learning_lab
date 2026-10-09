# Debugging: Multivariate Statistics

### Symptom: SingularMatrixException when inverting Σ
n ≤ p, or two columns are perfectly collinear (duplicate feature, or one = 2× another). Print the eigenvalues: zero eigenvalues are exact linear dependencies. Fixes: increase n, drop collinear columns, or add ridge shrinkage (Σ + λI with λ > 0 guarantees positive definiteness).

### Symptom: Mahalanobis distance is negative (or NaN)
d² computed as (x−μ)ᵀΣ⁻¹(x−μ) should be ≥ 0; a negative value means Σ⁻¹ is not symmetric positive definite — typically because Σ was built as XᵀX/(n−1) with n < p, or accumulated with rounding error. Re-symmetrize (Σ + Σᵀ)/2, then Cholesky with a small jitter, or use the pseudo-inverse.

### Symptom: correlation matrix has entries outside [−1, 1]
The matrix was built from *unnormalized* cross-products (Sxy instead of Sxy/√(SxxSyy)) or Sxx/Syy were computed on uncentered data while Sxy was centered. Compute all three from centered data and divide by n−1 consistently; assert |rᵢⱼ| ≤ 1 + 1e-12.

### Symptom: PCA explains > 100% of variance
Components were ordered by eigenvalues of a *correlation* matrix (trace = p) but percentages were divided by the trace of Σ (or vice versa). Explained-variance ratio = λⱼ / Σλ — always divide by the trace of the very matrix you decomposed.

### Symptom: regression coefficients flip sign after adding a variable
Not a bug by itself — that is (near-)collinearity: two predictors sharing variance can each flip sign when the other enters (Simpson/Yule effect). Check the condition number of XᵀX and the variance inflation factor VIF = 1/(1−R²ⱼ): VIF > 10 means the coefficient's standard error is inflated √10 ≈ 3.2×.

### Symptom: r computed by hand differs from the library's
Mixing n and n−1: r is identical under both (the (n−1) cancels in Sxy/√(SxxSyy)), but *covariance* differs by n/(n−1). If r disagrees, one side centered differently or omitted a term — recompute Sxx, Syy, Sxy on centered data and compare each.

### Symptom: standardized regression and correlation disagree on sign
They shouldn't — the standardized slope equals r in simple regression. Divergence means a variable was standardized with population sd (÷n) in one place and sample sd (÷(n−1)) in another, or a weight was applied asymmetrically. Use one centering/scaling helper everywhere.

## Debugging triage for multivariate code

| Symptom | Most likely cause | Evidence to collect first |
|---|---|---|
| Mahalanobis distance negative or NaN | Σ not positive definite; built as XᵀX/(n−1) with n ≤ p, or rounding drift | Eigenvalues of (S + Sᵀ)/2 — any negative value confirms it |
| PCA results change run to run | Tied eigenvalues (components can rotate) or unsorted eigenpairs | Compare sorted eigenvalues, not component-by-component vectors |
| Explained variance ≠ 100% | Mixed Σ and correlation-matrix traces | Print trace of the exact matrix decomposed and the one used for percentages |
| Two implementations of r disagree | One centered, the other not; or n vs n−1 on covariance | Compare Sxx, Syy, Sxy separately — the error localizes in one of the three |
| Regression coefficients explode after adding a column | Collinearity: κ(XᵀX) = κ(X)² | κ(X), VIF per column; VIF > 10 flags the offender |
| Cluster assignment flips under tiny noise | Well-separated clusters assumed when silhouette is low | Silhouette score and the gap between the two largest eigenvalues |
| Correlation matrix not PSD after pairwise computation | Pairwise deletion: each r computed on a different subset | Recompute with listwise deletion; if it becomes PSD, the mismatch was the cause |

## Two-minute checklist before blaming the data

- Assert `S` is symmetric to 1e−12 and `eigvals ≥ −1e−10`.
- Assert `|rᵢⱼ| ≤ 1 + 1e−12` and `diag(S) > 0`.
- Recompute one known cell by hand (the 2×2 example in STEP_BY_STEP: Sxx = 10, Syy = 6, Sxy = 6 → r = 0.7746) as a regression test.
- Confirm the sample count used for Σ is n − 1, not n, and matches the n reported in output.
