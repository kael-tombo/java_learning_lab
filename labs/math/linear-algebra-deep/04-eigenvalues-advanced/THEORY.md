# Eigenvalues Advanced — Theory

## 1. Definitions

lambda is an eigenvalue of A with eigenvector v != 0 iff Av = lambda v.
The characteristic polynomial p_A(t) = det(A - tI); its roots are the
eigenvalues. Trace = sum of eigenvalues, determinant = product
(counting algebraic multiplicity).

## 2. Running example

A = [[4,1],[2,3]]: A - tI = [[4-t,1],[2,3-t]],
p(t) = (4-t)(3-t) - 2 = t^2 - 7t + 10 = (t-5)(t-2).
Eigenvalues 5 and 2; eigenvectors (1,1) and (1,-2):

    A(1,1) = (5,5) = 5(1,1); A(1,-2) = (2,-4) = 2(1,-2).

Trace 7 = 5+2; det 10 = 5*2.

## 3. Diagonalization

A is diagonalizable iff it has n independent eigenvectors, iff the
geometric multiplicity of each eigenvalue equals its algebraic one.
Distinct eigenvalues always suffice. A = PDP^{-1} with
P = [[1,1],[1,-2]] (det -3), D = diag(5,2). Then A^k = PD^kP^{-1}.

## 4. Symmetric spectral theorem

Every real symmetric matrix is orthogonally diagonalizable with real
eigenvalues and orthonormal eigenvectors. Example S = [[2,1],[1,2]]:
eigenvalues 3 (vector (1,1)) and 1 (vector (1,-1)); normalized,
Q = (1/sqrt2)[[1,1],[1,-1]], S = Q diag(3,1) Q^T.

## 5. Non-diagonalizable case

J = [[2,1],[0,2]] has p(t) = (2-t)^2: eigenvalue 2 algebraic
multiplicity 2, but J - 2I = [[0,1],[0,0]] has rank 1, nullity 1 —
geometric multiplicity 1. Not diagonalizable. Cayley-Hamilton holds
regardless: (A-5I)(A-2I) = 0 for the A above.

## 6. Powers

A^3 = P diag(125,8) P^{-1}; trace 125+8 = 133. Direct product gives
[[86,39],[78,47]], trace 86+47 = 133. Powers stay inside the
eigenbasis: only the diagonal entries change.
