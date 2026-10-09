# Internals: Multivariate Statistics

## Data layout
Observations are stored row-major as `double[n][p]` for access by observation (regression, kNN) with a column-major cache (or BLAS `syrk`) for covariance. Centering is done once: Xc = X − 1μᵀ, then every statistic reads from Xc. One centering pass, no repeated mean recomputation inside Sxx loops.

## Covariance accumulation
Single-pass Welford over p dimensions: for each observation x, δ = x − mean; mean += δ/n; M2 += δ ⊗ (x − newMean) — the outer product form keeps the O(np²) time but accumulates error proportional to the variance, not the magnitudes. Final Σ = M2/(n−1), then explicitly symmetrized (Σ + Σᵀ)/2.

## Solving, never inverting
Mahalanobis and MVN densities call `Cholesky.decompose(Σ)` once (L with Σ = LLᵀ) and then solve per point: d² = ‖L⁻¹(x−μ)‖² by forward substitution, O(p²) per point after the O(p³) factorization. log-det = 2Σ log Lᵢᵢ comes free from the same factor. Explicit Σ⁻¹ is only formed for display.

## PCA pipeline
1. Center (and optionally scale) — a flag, because Σ vs correlation matrix changes the answer.
2. Eigen-decompose the p × p Σ (Jacobi rotation for p ≤ ~100; tridiagonal + QL for larger; randomized SVD on the raw Xc for p > 5000).
3. Sort eigenvalues descending, project Xc·V_k, accumulate explained-variance ratios against the *decomposed matrix's* trace.

## Correlation
rᵢⱼ = Σᵢⱼ / √(Σᵢᵢ Σⱼⱼ) — derived from the covariance matrix, never accumulated separately (that's how r > 1 bugs happen). Zero-variance column → r undefined (NaN), flagged at build time rather than propagating.

## Regression solve
QR decomposition of X (Householder) then triangular solve — chosen over the normal equations because κ(QR) = κ(X) instead of κ(X)². Cholesky on XᵀX is retained only for the closed-form covariance of coefficients, (XᵀX)⁻¹σ², where the factorization is reused.

## Layering
`data → center → moments(Σ, μ) → decompositions(Cholesky/eig/QR) → methods(Mahalanobis, PCA, OLS, Hotelling)`. Each method consumes only decomposed primitives, so an ill-conditioned Σ is detected once, at factorization, instead of failing differently in every method.

## Symmetry, definiteness, and defensive copying

Every routine that accepts a Σ copies into a symmetric buffer: S ← (S + Sᵀ)/2. Rationale: covariance is symmetric by construction, but callers pass XᵀX/(n−1) results whose two halves differ in the last bits, and Cholesky on a non-symmetric matrix silently reads only one triangle — producing an L that does not reproduce the other. Symmetrizing once makes the failure mode visible instead of biased.

Eigen routines sort descending by construction and clamp λ < −ε·λ_max to zero (ε ≈ 1e−10) before any inverse: negative eigenvalues are rounding noise unless they exceed that scale, in which case the error is raised rather than smoothed over.

## Which decomposition, which accuracy

| Path | Algorithm | Accuracy | Used for |
|---|---|---|---|
| p ≤ 100 | Cyclic Jacobi rotations | High (orthogonal by construction) | General Σ, small problems |
| p up to ~5 000 | Householder tridiagonalization + implicit QL | High | Full spectrum |
| p > 5 000 or n × p only | Randomized SVD (range finder, q = 2–4 power iterations) | Approximate, tunable | Top-k components only |
| Need only k = 1–2 | Lanczos / power iteration | Good for extreme λs | Largest eigenvalue checks |

The randomized path never forms Σ: it multiplies Xᵀ(XΩ) for a p × (k + 10) Gaussian Ω — memory drops from O(p²) to O(p·k), which is the difference between runnable and not when p = 10⁵.
