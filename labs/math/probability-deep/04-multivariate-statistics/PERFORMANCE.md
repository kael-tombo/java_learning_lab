# Performance: Multivariate Statistics

## Costs that are cubic in the dimension p
- **Cholesky of Σ**: (1/3)p³ flops — required for every Mahalanobis distance batch, every multivariate-normal density evaluation and every Σ⁻¹ (never invert explicitly; solve ΣX = I, or better, solve per right-hand side).
- **Eigen-decomposition / SVD**: O(p³) for the p × p covariance; O(np² + p³) when computed directly from the n × p data matrix. PCA with randomized SVD (Halko et al. 2011) reduces to O(np·k) for k components — the practical route once p > 5 000.
- **Determinant of Σ** (for the MVN density): O(p³) via Cholesky, not the Leibniz expansion — det = ∏Lᵢᵢ².

## Costs that are quadratic in p
- **Sample covariance from data**: O(np²) time (each of the p(p+1)/2 entries scans n points) and O(p²) memory — 10⁵ × 500 features is 2.5×10¹⁰ multiply-adds before any analysis starts. Streaming/Welford-style accumulation keeps it O(p²) *memory* with O(np²) time and one pass.
- **Pairwise correlation matrix**: p(p−1)/2 distinct entries; 10 000 features → ~50 million pairs. Computation is a single BLAS-2 syrk call: memory, not flops, is usually the limit (400 MB for the float64 matrix).

## Regression and its condition number
OLS solves (XᵀX)β = Xᵀy: forming XᵀX is O(np²), the Cholesky solve O(p³). Condition number κ(XᵀX) = κ(X)² — squaring means a κ(X) = 10⁶ design already gives κ = 10¹², i.e. only ~4 correct digits left in float64 (ε = 2.2e-16, digits ≈ 16 − log₁₀κ). Remedies: center/scale first, ridge (λ > 0 caps κ at (κ_max + λ)/λ), or QR instead of the normal equations (κ(QR) = κ(X)).

## Dimensionality reduction pays for itself
Project to k components *before* the expensive step: distance computations drop from O(p) to O(k) per point; clustering from O(np²) to O(nk²); covariance estimation variance drops ~2p/n → 2k/n. The trade is explicit: reconstruction error = Σ_{j>k} λⱼ (the discarded eigenvalues) vs. estimation error roughly proportional to k/n.

## Rule of thumb, not a benchmark
For stable Σ⁻¹ (wells if the smallest eigenvalue is bounded away from 0 in expectation), classical guidance is n ≳ 5–10p; below that, shrinkage or a diagonal Σ is not an optimization but a requirement.

## Cost table: multivariate operations

| Operation | Time | Memory | Notes |
|---|---|---|---|
| Sample covariance from n × p | O(np²) | O(p²) | BLAS-3 syrk; one pass with Welford |
| Cholesky of Σ | p³/3 flops | O(p²) | Prerequisite for all Mahalanobis/MVN work |
| Mahalanobis for m points | O(p³ + mp²) | O(p²) | Factorize once, then forward-substitute per point |
| Full eigendecomposition of Σ | ~9p³–20p³ flops | O(p²) | Jacobi (accurate, p ≤ ~100) vs tridiagonal+QL |
| PCA of n × p without forming Σ | O(np² + p³) | O(np) | Streaming: never materialize p × p if p > 10⁴ |
| Randomized PCA, k components | O(npk) | O((n+p)k) | Halko et al. 2011; the route once p > 5 000 |
| OLS via QR | O(np²) | O(np) | κ(QR) = κ(X), vs κ² for normal equations |
| Pairwise correlation, all pairs | p(p−1)/2 entries | O(p²) | Memory-bound: 10⁴ features → 5×10⁷ pairs |

## Rules of thumb

- **Never invert Σ explicitly.** Solve ΣX = b (Cholesky) — 3× fewer flops and better conditioning.
- **Don't form XᵀX when p is large.** Its condition number is squared; QR or SVD of X directly costs more flops but keeps κ.
- **Cap p before the cubic step.** Project to k ≪ p features first: the p³ eigendecomposition becomes k³, and O(np²) becomes O(npk).
- **Streaming Σ is O(p²) memory regardless of n** — the observation matrix is never the constraint; p is.

## Sanity sizes (derived, not measured)

- p = 1 000: Σ has 500 500 unique entries (≈ 4 MB float64); Cholesky ≈ 3.3×10⁸ flops — milliseconds on any BLAS.
- p = 10 000: Cholesky ≈ 3.3×10¹¹ flops — seconds; Σ itself is 800 MB, which is why randomized/streaming PCA exists at all.
