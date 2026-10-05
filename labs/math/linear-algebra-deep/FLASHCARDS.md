# Linear Algebra Flashcards

## Vectors & Spaces
| Front | Back |
|-------|------|
| Vector space | Set closed under addition and scalar multiplication |
| Span | All linear combinations of a set |
| Linearly independent | Only trivial combination gives zero |
| Basis | Linearly independent spanning set |
| Dimension | Number of vectors in a basis |
| Subspace | Subset that is itself a vector space |
| Rank | Dimension of column space |
| Null space | {x : Ax = 0} |
| Column space | Span of columns of A |

## Matrices
| Front | Back |
|-------|------|
| Identity matrix I | Diagonal of 1s; AI = A |
| Symmetric matrix | A = A^T |
| Orthogonal matrix | A^T = A^(-1) |
| Upper triangular | Zeros below diagonal |
| Diagonal matrix | Non-zeros only on main diagonal |
| Transpose A^T | (A^T)_ij = A_ji |
| Matrix multiplication | (AB)_ij = Σ A_ik·B_kj |
| Inverse A^(-1) | AA^(-1) = I |
| Determinant | Volume scaling factor |

## Linear Systems
| Front | Back |
|-------|------|
| Gaussian elimination | Row operations to REF |
| Row echelon form | Staircase pattern of pivots |
| Reduced REF | Pivots are 1, zeros above and below |
| Consistent system | At least one solution |
| Unique solution | rank(A) = n |
| Homogeneous system | Ax = 0; always has trivial solution |
| Particular solution | Any single solution to Ax = b |

## Eigenvalues & Eigenvectors
| Front | Back |
|-------|------|
| Eigenvalue λ | det(A - λI) = 0 |
| Eigenvector v | Av = λv, v ≠ 0 |
| Characteristic polynomial | det(A - λI) |
| Diagonalization | A = PDP^(-1) |
| Trace | Sum of eigenvalues |
| Spectral theorem | Symmetric → real eigenvalues, orthogonal eigenvectors |
| Algebraic multiplicity | Power of factor in characteristic polynomial |
| Geometric multiplicity | Dimension of eigenspace |

## Inner Products & Orthogonality
| Front | Back |
|-------|------|
| Dot product | ⟨u,v⟩ = u^T v |
| Norm ||v|| | √⟨v,v⟩ |
| Orthogonal | ⟨u,v⟩ = 0 |
| Orthonormal | Orthogonal + unit length |
| Gram-Schmidt | Convert basis to orthonormal |
| QR decomposition | A = QR, Q orthogonal, R upper triangular |
| Projection of v onto u | (⟨v,u⟩/⟨u,u⟩)·u |

## SVD & Decompositions
| Front | Back |
|-------|------|
| SVD | A = UΣV^T |
| Singular values | σ_i = √λ_i(A^T A) |
| Rank-k approximation | Keep top k singular values |
| Eckart-Young | Truncated SVD is best rank-k approx |
| PCA | SVD of centered data matrix |
| Pseudoinverse | A⁺ = VΣ⁺U^T |
| LU decomposition | A = LU, L lower, U upper |
| Cholesky | A = LL^T for positive definite A |
