# Linear Algebra Theory

## 1. Vectors and Vector Spaces
A **vector** is an element of a vector space — a set closed under addition and scalar multiplication.

**Vector space axioms (over ℝ):**
- Addition is commutative and associative
- Zero vector exists: v + 0 = v
- Additive inverses exist: v + (-v) = 0
- Scalar multiplication distributes over vector and scalar addition
- 1·v = v (multiplicative identity)

**Key concepts:**
- **Span:** All linear combinations of a set of vectors
- **Linear independence:** No vector in a set is a linear combination of the others
- **Basis:** A linearly independent spanning set
- **Dimension:** Number of vectors in a basis

**Subspaces:** A subset W ⊆ V that is itself a vector space (closed under + and scalar ×).

## 2. Matrices and Matrix Operations
A **matrix** is a rectangular array of numbers representing linear transformations.

**Operations:**
- **Addition:** (A + B)_ij = A_ij + B_ij (same dimensions)
- **Scalar multiplication:** (cA)_ij = c·A_ij
- **Matrix multiplication:** (AB)_ij = Σ_k A_ik·B_kj (inner dimensions must match)
- **Transpose:** (A^T)_ij = A_ji

**Special matrices:**
- **Identity I:** Diagonal of 1s; AI = IA = A
- **Diagonal:** Non-zero entries only on main diagonal
- **Symmetric:** A = A^T
- **Orthogonal:** A^T = A^(-1); columns are orthonormal
- **Upper/Lower triangular:** Entries below/above diagonal are zero

**Rank:** Dimension of the column space (or row space); equals number of pivots in REF.

## 3. Systems of Linear Equations
A system Ax = b can have:
- **Unique solution:** rank(A) = n (number of variables)
- **Infinitely many solutions:** rank(A) < n, consistent
- **No solution:** Inconsistent (b not in column space of A)

**Gaussian elimination:** Use row operations to reach row echelon form (REF) or reduced row echelon form (RREF).

**Row operations:**
1. Swap two rows
2. Multiply a row by a non-zero scalar
3. Add a multiple of one row to another

**Inverse:** A^(-1) exists iff det(A) ≠ 0; solve [A | I] → [I | A^(-1)] via Gauss-Jordan.

## 4. Determinants
**Definition (2×2):** det([a b; c d]) = ad - bc

**Properties:**
- det(AB) = det(A)·det(B)
- det(A^T) = det(A)
- det(A^(-1)) = 1/det(A)
- det(cA) = c^n·det(A) for n×n matrix
- Swapping rows changes sign
- Adding a multiple of one row to another preserves det

**Geometric meaning:** |det(A)| is the volume scaling factor of the linear transformation.

**Cofactor expansion:** det(A) = Σ_j (-1)^(i+j)·A_ij·M_ij (Laplace expansion along row i).

## 5. Eigenvalues and Eigenvectors
**Definition:** Av = λv for non-zero v; λ is an eigenvalue, v is an eigenvector.

**Characteristic polynomial:** det(A - λI) = 0

**Properties:**
- Trace = sum of eigenvalues
- det(A) = product of Eigenvalues
- A and A^T have the same eigenvalues
- Similar matrices (B = P^(-1)AP) have the same eigenvalues

**Diagonalization:** A = PDP^(-1) where D is diagonal (eigenvalues) and P has eigenvectors as columns. Possible iff A has n linearly independent eigenvectors.

**Spectral theorem:** Symmetric matrices have real eigenvalues and orthogonal eigenvectors.

## 6. Inner Products and Orthogonality
**Dot product:** ⟨u, v⟩ = u^T v = Σ u_i v_i

**Norm:** ||v|| = √⟨v, v⟩

**Orthogonality:** u ⊥ v iff ⟨u, v⟩ = 0

**Orthonormal set:** Vectors are pairwise orthogonal and unit length.

**Gram-Schmidt process:** Convert any basis to an orthonormal basis:
- v₁ = u₁/||u₁||
- v₂ = (u₂ - ⟨u₂,v₁⟩v₁)/||u₂ - ⟨u₂,v₁⟩v₁||
- Continue subtracting projections

**QR decomposition:** A = QR where Q is orthogonal and R is upper triangular.

## 7. Singular Value Decomposition (SVD)
**Theorem:** Any m×n matrix A can be factored as A = UΣV^T where:
- U is m×m orthogonal (left singular vectors)
- Σ is m×n diagonal with non-negative singular values σ₁ ≥ σ₂ ≥ ... ≥ 0
- V is n×n orthogonal (right singular vectors)

**Relationship to eigenvalues:** σ_i = √(λ_i(A^T A))

**Applications:**
- Low-rank approximation (Eckart-Young theorem)
- Principal Component Analysis (PCA)
- Pseudoinverse: A^(-1) = VΣ^(-1)U^T
- Image compression, recommender systems, latent semantic analysis
