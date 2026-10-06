# Principal Component Analysis

**Track:** ml  |  **Lab:** lab08  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. The Problem This Solves

You have more features than you can reason about, some of them correlated, and you need fewer dimensions without losing the variance that matters.

PCA is the preprocessing step that unblocks other algorithms: it regularises collinearity, decorrelates for neural networks, and compresses for serving.

## 2. Learning Objectives

- Derive PCA as the projection that maximises variance
- Implement PCA via eigendecomposition of the covariance matrix and via SVD of the centred data
- Compute explained variance ratio and choose k with a cumulative-variance target
- Interpret loadings correctly and distinguish them from feature importance
- Explain when PCA hurts: sparse data, categorical features, interpretability needs
- Use PCA as a preprocessing step and justify the fit on training data only

## 3. Core Concepts

### 3.1 PCA as maximum-variance projection

PCA finds the orthogonal direction along which the data varies most, then removes it and repeats. The directions are the eigenvectors of the covariance matrix, sorted by eigenvalue. No labels are used, so PCA is unsupervised — and can happily preserve variance you do not care about.

### 3.2 Two routes to the same answer

Eigendecomposition of the covariance matrix works for small p; SVD of the centred data matrix is numerically superior and works for large p, because you never form p×p. The singular values relate to eigenvalues by λᵢ = sᵢ²/(n−1). Both give identical components up to sign.

### 3.3 Explained variance and choosing k

Explained variance ratio is λᵢ/Σλ. Cumulative explained variance answers 'how many components to keep' — but the 95% threshold is a convention, not a law. Better: fit k components, then choose k by downstream validation error or reconstruction error.

### 3.4 Loadings, scores and interpretation

Loadings are the eigenvectors (the directions in feature space). Scores are the projected data. Loadings are not importance: a small-loading feature can be decisive in combination. With correlated features, individual loadings are unstable even when components are stable — the component is the interpretable unit, not the coefficient.

### 3.5 Standardise or not

Unscaled PCA finds directions of maximum total variance, so a feature in cents dominates. Standardised PCA finds directions of maximum correlation structure, which is usually what you want when features are on different scales. The choice must be stated, because it changes the answer.

### 3.6 When PCA is the wrong tool

Sparse text destroys variance-based structure — use truncated SVD on term counts instead. Categorical encodings have no meaningful variance. Interpretability-critical models should keep their features. And any supervised goal is better served by a supervised projection.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `Σ = (1/(n−1)) XᵀX (centred X)` | Sample covariance | the matrix whose eigenvectors we want |
| `Σvᵢ = λᵢvᵢ` | Eigenproblem | directions and their variance |
| `EV ratio = λᵢ / Σᵢλᵢ` | Explained variance ratio | share of variance per component |
| `zᵢ = (xᵢ − μ) Wₖ` | Projection | score in the new basis |
| `x̂ = μ + z Wₖᵀ` | Reconstruction | rank-k approximation of X |
| `λᵢ = sᵢ² / (n−1)` | Singular-value link | why SVD avoids forming Σ |
| `total variance = Σᵢ var(xᵢ)` | Trace relation | explained ratios must sum to 1 |

## 5. How the Pieces Fit Together

1. Decide whether to standardise: yes if units differ, no if they are comparable and total variance is meaningful.

2. Centre the data (mean subtract). PCA does not centre for you.

3. Decompose: eigendecomposition of the covariance matrix for small p, SVD of the centred matrix otherwise.

4. Sort components by descending eigenvalue; check the eigenvalue spectrum for a natural elbow.

5. Choose k from a cumulative-variance target or, better, from downstream validation error.

6. Store the scaler, the mean vector and the component matrix together — a transform is not just a matrix.

## 6. Assumptions and Invariants

- Variance is the structure worth preserving; if the target matters, PCA is unsupervised and blind to it
- Linear relationships — PCA finds linear subspace structure only
- Features are numeric and (after optional scaling) comparable
- Outliers have not been allowed to dominate the covariance
- The dominant variance directions are the directions you want to keep
- The transformation is fit on training data and applied unchanged to serving data

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| All the variance ends up in one component | features on wildly different scales | standardise before fitting |
| Test-time scores look nothing like training | PCA refit on the full dataset or on serving data | fit once on the training fold and serialise mean + components |
| k chosen by the 95% rule and downstream accuracy drops | retained variance is not the same as useful variance | choose k by validation error, not by cumulative variance |
| Loadings say feature 7 dominates | correlated features split the weight unpredictably | interpret the component, and use permutation importance for the model |
| Text classification gets worse after PCA | truncated SVD, not PCA, is right for sparse counts | use latent semantic indexing / TruncatedSVD on the sparse matrix |
| Components flip sign between runs | sign is arbitrary in eigendecomposition | fix the sign convention (largest-magnitude loading positive) and serialise it |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `Eigenvalue decomposition (QR iteration)` | the didactic route for small p, plus a symmetric-matrix solver |
| `Jacobi eigenvalue algorithm` | simple, stable for real symmetric matrices like covariance |
| `Arrays.sort on eigenvalues with paired index sort` | keeping eigenvalues and eigenvectors aligned is the classic bug |
| `DoubleSummaryStatistics` | streaming mean and variance for the centring step |
| `record PcaModel(double[] mean, double[][] components, double[] eigenvalues)` | the transform plus its metadata, in one serialisable unit |

## 9. Where This Sits in the Larger System

- **Lab 01** benefits directly: PCA removes the collinearity that inflates OLS standard errors.
- **Lab 05** benefits most: it mitigates the curse of dimensionality.
- **Lab 03** is a warning — PCA is rotation-sensitive in the wrong way for trees.
- **Lab 07** uses PCA as preprocessing when clusters are not spherical.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Derive PCA as the projection that maximises variance
- [ ] 0 — cannot yet — Implement PCA via eigendecomposition of the covariance matrix and via SVD of the centred data
- [ ] 0 — cannot yet — Compute explained variance ratio and choose k with a cumulative-variance target
- [ ] 0 — cannot yet — Interpret loadings correctly and distinguish them from feature importance
- [ ] 0 — cannot yet — Explain when PCA hurts: sparse data, categorical features, interpretability needs
- [ ] 0 — cannot yet — Use PCA as a preprocessing step and justify the fit on training data only

## 11. Summary Checklist

- [ ] I can derive PCA from the variance-maximisation constraint
- [ ] I know when to standardise and can justify the choice
- [ ] I choose k from validation error, not only from cumulative variance
- [ ] I can explain loadings versus importance
- [ ] I know PCA is blind to the target
- [ ] My transform artifact contains mean, scale and components together
