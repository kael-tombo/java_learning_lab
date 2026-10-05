# Linear Algebra Mathematical Foundation

## 1. Vector Space Axioms
A vector space V over field F satisfies:
- **(V, +)** is an abelian group (closure, associativity, identity, inverses, commutativity)
- Scalar multiplication: F × V → V
- Distributivity: a(u+v) = au + av, (a+b)v = av + bv
- Compatibility: a(bv) = (ab)v
- Identity: 1·v = v

**Theorem:** The intersection of subspaces is a subspace.

**Theorem:** span(S) is the smallest subspace containing S.

## 2. Linear Independence and Bases
**Definition:** {v₁, ..., vₙ} is linearly independent if c₁v₁ + ... + cₙvₙ = 0 implies all cᵢ = 0.

**Replacement Theorem (Steinitz):** If {v₁, ..., vₙ} spans V and {w₁, ..., wₘ} is linearly independent, then m ≤ n.

**Corollary:** All bases of a finite-dimensional space have the same size (dimension).

**Theorem:** In an n-dimensional space, any n linearly independent vectors form a basis.

## 3. Matrix Algebra Theorems
**Theorem:** (AB)^T = B^T A^T. Proof: ((AB)^T)_ij = (AB)_ji = Σ A_jk B_ki = Σ B_ki A_jk = (B^T A^T)_ij.

**Theorem:** (AB)^(-1) = B^(-1)A^(-1). Proof: (AB)(B^(-1)A^(-1)) = A(BB^(-1))A^(-1) = AIA^(-1) = I.

**Theorem:** rank(A) = rank(A^T). Proof: row rank = column rank via pivot analysis.

**Rank-Nullity Theorem:** For A ∈ ℝ^(m×n): rank(A) + nullity(A) = n.
Proof: The null space has dimension n - rank(A); each free variable contributes one dimension.

## 4. Determinant Theorems
**Theorem:** det(AB) = det(A)det(B). Proof via elementary matrices: any A is a product of elementary matrices; det(E) for each type is known; multiplicativity follows.

**Theorem:** A is invertible iff det(A) ≠ 0. Proof: A invertible ⟺ rank(A) = n ⟺ n pivots ⟺ det ≠ 0.

**Cramer's Rule:** x_i = det(A_i)/det(A) where A_i replaces column i with b.

## 5. Eigenvalue Theorems
**Theorem:** A and A^T have the same eigenvalues. Proof: det(A - λI) = det((A - λI)^T) = det(A^T - λI).

**Theorem (Spectral):** Real symmetric matrices have real eigenvalues and orthogonal eigenvectors.
Proof: ⟨Av, w⟩ = ⟨v, A^Tw⟩ = ⟨v, Aw⟩; if Av = λv, Aw = μw, then λ⟨v,w⟩ = μ⟨v,w⟩, so (λ-μ)⟨v,w⟩ = 0.

**Theorem:** Similar matrices have the same eigenvalues. Proof: det(P^(-1)AP - λI) = det(P^(-1)(A-λI)P) = det(A-λI).

**Cayley-Hamilton:** Every matrix satisfies its own characteristic polynomial: p(A) = 0.

## 6. SVD Existence Proof
**Theorem:** Any A ∈ ℝ^(m×n) has an SVD A = UΣV^T.

**Proof sketch:**
1. A^T A is symmetric positive semi-definite → has orthonormal eigenvectors vᵢ with eigenvalues σᵢ² ≥ 0
2. Let σᵢ = √λᵢ, V = [v₁ ... vₙ]
3. Define uᵢ = Avᵢ/σᵢ for σᵢ > 0; extend to orthonormal basis for ℝ^m
4. Then AV = UΣ → A = UΣV^T

## 7. Orthogonality Theorems
**Theorem (Projection):** The closest point in subspace W to vector v is proj_W(v) = Σ⟨v, eᵢ⟩eᵢ for orthonormal basis {eᵢ}.

**Theorem (Pythagoras):** If u ⊥ v, then ||u + v||² = ||u||² + ||v||².

**Theorem (Cauchy-Schwarz):** |⟨u,v⟩| ≤ ||u||·||v||, equality iff u and v are linearly dependent.

**Theorem (Parseval):** For orthonormal basis {eᵢ}: ||v||² = Σ|⟨v,eᵢ⟩|².
