# Architecture: Multivariate Statistics Implementation

## Package layout
```
com.mathlab.multivariate
├── data/        DataMatrix, ColumnSpec (scale/unit metadata), Centering
├── moments/     Covariance (Welford), Correlation, Scatter, RobustCov (MCD)
├── linalg/      Cholesky, EigenDecomposition, QR, SVD, Solve (never raw inverse)
├── distance/    Mahalanobis, Euclidean, DistanceMatrix
├── reduction/   PCA, KernelPCA?, ICA?           (feature-level)
├── models/      OLS, Ridge, LDA, HotellingT2    (inference-level)
├── cluster/     KMeans, WardHierarchical        (structure-level)
└── diag/        ConditionNumber, VIF, GoFChecks
```

## Invariants enforced at the boundary
1. DataMatrix validates finite values and reports (n, p) with `n > 1` before any moment is computed.
2. Covariance is built from centered columns only — centering is impossible to skip because `Covariance.of(X)` internally centers and refuses to accept pre-multiplied data.
3. Any method needing Σ⁻¹ requests `Cholesky` and fails with a typed `IllConditionedException` carrying the condition number, rather than returning garbage distances.
4. Correlation is *derived* from covariance (r = Σᵢⱼ/√(ΣᵢᵢΣⱼⱼ)), so |r| ≤ 1 holds by construction.

## Why decompositions are their own layer
PCA, OLS, Mahalanobis and Hotelling's T² all need the same three primitives — Cholesky, eigen, QR — with different preferences: T² wants log-det + triangular solves (Cholesky), PCA wants ordered eigenpairs, OLS wants QR (condition number κ(X) instead of κ(X)²). Sharing the layer means conditioning diagnostics are computed and logged once per model fit.

## Method → primitive map
| Method | Factorization | Failure mode caught centrally |
|---|---|---|
| Mahalanobis | Cholesky(Σ) | Σ not positive definite |
| PCA | eigen(Σ) or SVD(Xc) | zero eigenvalues (n ≤ p) |
| OLS | QR(X) | rank-deficient design |
| Ridge | eigen(XᵀX + λI) | λ not covering null space |
| Hotelling T² | Cholesky + F | n ≤ p |

## Test topology
Oracle cases computed by hand: Σ = [[2,1],[1,2]] → eigen 3, 1; r = 0.7746 on the 5-point sample; OLS line ŷ = 2.2 + 0.6x with residuals summing to 0; a deliberately duplicated column that must raise IllConditioned with κ reported.
