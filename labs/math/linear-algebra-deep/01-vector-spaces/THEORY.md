# Vector Spaces — Theory

## 1. What a Vector Space Is

A vector space over a field F (think R or Q) is a set V with addition and
scalar multiplication satisfying eight axioms: closure under both
operations, associativity and commutativity of addition, a zero vector,
additive inverses, and distributivity/compatibility of scalars
(1·v = v, a(bv) = (ab)v, a(u+v) = au+av, (a+b)v = av+bv). Everything in
this lab is a consequence of those eight rules — subspaces, span,
independence, bases, and dimension all follow without further assumptions.

Standard examples: Rⁿ, the space Pₙ of polynomials of degree ≤ n
(dimension n+1), M_{m×n} matrices (dimension mn), and function spaces
(infinite-dimensional — the finite intuition needs care there).

## 2. Subspaces

A subset W ⊆ V is a subspace iff it is nonempty and closed under both
operations (equivalently: closed under linear combinations). Practical
test: 0 ∈ W, and au + bv ∈ W for all u, v ∈ W and scalars a, b.

- Solution sets of homogeneous systems Ax = 0 are subspaces (null spaces).
- Solution sets of Ax = b with b ≠ 0 are NOT subspaces (0 missing) — they
  are affine translates x_particular + N(A).
- Unions of subspaces are almost never subspaces (take vectors from each
  side; their sum escapes). Intersections always are.

## 3. Span, Independence, Basis, Dimension

- **Span** of {v₁, …, vₖ}: all linear combinations. Membership is a
  linear system: (1,2,1) ∈ span{(1,1,0),(0,1,1)} because a = 1, b = 1
  solves a(1,1,0) + b(0,1,1) = (1,2,1) — while (1,0,2) is outside it
  (a = 1 forces b = −1, but the third coordinate then reads −1 ≠ 2).
- **Independence**: the only relation c₁v₁ + … + cₖvₖ = 0 is the trivial
  one. {(1,2,3),(4,5,6),(7,8,10)} is independent (determinant −3 ≠ 0);
  note the near-miss classic {(1,2,3),(4,5,6),(7,8,9)} with determinant
  0 — one changed entry flips dependence to independence.
- **Basis**: independent + spanning. **Dimension** = size of any basis
  (well-defined: every basis of V has the same cardinality — the
  exchange theorem).
- **Coordinates**: relative to an ordered basis. v = (3,7) in the basis
  {(1,1),(1,−1)} has coordinates (5,−2), since 5(1,1) − 2(1,−1) = (3,7).

## 4. Rank–Nullity (Worked)

For T: R⁴ → R³ with rows r₁ = (1,0,2,−1), r₂ = (0,1,1,3),
r₃ = (2,1,5,1): r₃ = 2r₁ + r₂ exactly, so the row space has dimension 2
(rank 2). Free variables x₃, x₄ give null-space basis
{(−2,−1,1,0), (1,−3,0,1)} — each dot-verified against both rows —
so nullity 2, and 2 + 2 = 4 = dim(domain). Rank–nullity holds with
equality exhibited, not merely stated.
