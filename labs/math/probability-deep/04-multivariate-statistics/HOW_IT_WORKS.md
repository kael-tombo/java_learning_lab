# How It Works: Multivariate Statistics

## 1. Everything starts from centered cross-products
Collect Sxx, Syy, Sxy (two variables) or the full S = (1/(n−1))XcᵀXc (p variables). Centering makes S depend only on *co-variation*; without it, means leak into the matrix and r stops being bounded by 1.

## 2. Correlation standardizes; covariance doesn't
r = Sxy/√(SxxSyy) divides out the units — Cauchy–Schwarz guarantees |r| ≤ 1, with equality iff one variable is a perfect linear function of the other. This is the same operation as z-scoring both columns first: r is the covariance of standardized data, always.

## 3. Least squares is orthogonal projection
β̂ = (XᵀX)⁻¹Xᵀy is the projection of y onto the column space of X; residuals are orthogonal to that space (Xᵀe = 0), which is why the fitted line must pass through (x̄, ȳ). In two dimensions β₁ = Sxy/Sxx — the slope *is* the regression of y-deviations on x-deviations.

## 4. PCA diagonalizes the covariance
Find V where VᵀΣV = Λ (diagonal): rotate so the new axes are uncorrelated, variances = eigenvalues. Ordering λ₁ ≥ λ₂ ≥ … and keeping k axes is the best k-dimension approximation in squared error (Eckart–Young). Trace is invariant: Σλⱼ = tr(Σ) = total variance, so "75% explained" is literally 3/(3+1) in our example.

## 5. Mahalanobis whitens first
Cholesky Σ = LLᵀ; then z = L⁻¹(x−μ) transforms the cloud into a sphere where Euclidean distance equals Mahalanobis. Anisotropic scales become isotropic, correlated directions decorrelate — the 4.47σ joint event at (2, −2) emerges only after whitening.

## 6. Partial correlation conditions out
Regress x on z and y on z, take r of the residuals: what remains of the association not explained by z. Repeated conditioning gives the r(x, y | z₁, …, z_k) sequence that separates confounded from direct association — Yule's 1897 point, made mechanical.

## 7. Where multivariate meets inference
With multivariate-normal data, x̄ is MVN(μ, Σ/n); Hotelling's T² = n(x̄ − μ₀)ᵀS⁻¹(x̄ − μ₀) is (n−p)/(p(n−1))·F_{p, n−p} — the exact multivariate analogue of the one-sample t², and the reason every test in lab 07 has a multivariate sibling here.

## 8. Between- and within-class scatter is the same calculus twice

LDA's generalization of PCA in one line: PCA diagonalizes S_T = S_W + S_B (total scatter) and takes the top eigenvectors; LDA instead solves S_W⁻¹S_B v = λ v — directions with large *between-class* scatter relative to *within-class* scatter. Because S_W must be inverted, LDA needs n > p (or shrinkage), while PCA never does. Same eigenvalue machinery, different numerator: variance *of* the labels, not variance *of* the data.

## 9. Why the trace is the bookkeeping device

Every rotation preserves tr(Σ): eigenvalues, explained-variance ratios and "percent of variance kept" are all allocations of one conserved quantity. That is why percentages must be computed against the trace of the matrix you actually decomposed (see DEBUGGING's >100% symptom), and why adding a feature with variance v raises total variance by exactly v — a check you can run on any pipeline in one line of code.
