# Eigenvalues Advanced — Exercises

## 1. Characteristic polynomial

Q: Eigenvalues of [[4,1],[2,3]]?
A: t^2 - 7t + 10 = (t-5)(t-2): 5 and 2.

## 2. Eigenspaces

Q: Bases for both eigenspaces?
A: lambda=5: [[-1,1],[2,-2]], basis (1,1). lambda=2: [[2,1],[2,1]],
basis (1,-2). Each nullity 1; geometric = algebraic = 1.

## 3. Powers via D

Q: Compute A^2's trace without multiplying, then confirm.
A: 25+4 = 29. Direct product [[18,7],[14,11]] traces to 29.

## 4. Spectral decomposition

Q: Orthogonally diagonalize S = [[2,1],[1,2]].
A: Eigenvalues 3, 1 with orthonormal (1/sqrt2)(1,1), (1/sqrt2)(1,-1).
S = Q diag(3,1) Q^T; dot of the two vectors is 0.

## 5. Defective matrix

Q: Show J = [[2,1],[0,2]] is not diagonalizable.
A: Only eigenvalue 2 (double root). J-2I = [[0,1],[0,0]] has nullity
1 < 2, so no eigenbasis exists.

## 6. Cayley-Hamilton

Q: Verify p(A) = 0 for A above.
A: (A-5I)(A-2I) = [[0,0],[0,0]] entry by entry (Section 5).

## 7. Third power

Q: Trace of A^3, two ways?
A: 5^3+2^3 = 133; direct [[86,39],[78,47]] traces to 86+47 = 133.

## 8. Quick eigenvalue read

Q: Eigenvalues of triangular [[3,-1],[0,2]]?
A: Diagonal entries 3 and 2 — the characteristic polynomial splits
as (3-t)(2-t).

## 9. Constant term check

Q: Relate p(0) and p(1) to determinants for A = [[4,1],[2,3]].
A: p(0) = 10 = det A. p(1) = 4 = det(A-I) = 6-2. The polynomial
evaluated at shifts gives shifted determinants.
