# Eigenvalues Advanced — Math Foundation

All values computed in exact rational arithmetic (Python `fractions`).

## 1. Characteristic polynomial of [[4,1],[2,3]]

det(A - tI) = (4-t)(3-t) - 2 = 12 - 7t + t^2 - 2 = t^2 - 7t + 10.
Roots: t = (7 +- 3)/2 = 5, 2.

## 2. Eigenvector verification

A(1,1) = (4+1, 2+3) = (5,5) = 5(1,1).
A(1,-2) = (4-2, 2-6) = (2,-4) = 2(1,-2).
Eigenspaces: for lambda = 5, A - 5I = [[-1,1],[2,-2]], rows dependent
(second = -2 first), nullity 1, basis (1,1). For lambda = 2,
A - 2I = [[2,1],[2,1]], basis (1,-2).

## 3. Diagonalizer determinant

P = [[1,1],[1,-2]]: det = -2 - 1 = -3, nonzero, so diagonalizable.
A^2 check via D: A^2 = P diag(25,4) P^{-1}; trace = 25+4 = 29.
Direct: A^2 = [[18,7],[14,11]], trace 18+11 = 29. Agreement.

## 4. Symmetric case

S = [[2,1],[1,2]]: p(t) = (2-t)^2 - 1 = t^2 - 4t + 3 = (t-3)(t-1).
S(1,1) = (3,3); S(1,-1) = (1,-1). Orthonormal: (1/sqrt2)(1,1) dot
(1/sqrt2)(1,-1) = (1-1)/2 = 0.

## 5. Cayley-Hamilton on A

(A - 5I)(A - 2I) = [[-1,1],[2,-2]] [[2,1],[2,1]] = [[0,0],[0,0]]:
entry (1,1): -2+2 = 0; (1,2): -1+1 = 0; (2,1): 4-4 = 0;
(2,2): 2-2 = 0.

## 6. Third power trace

A^2 = [[18,7],[14,11]]. A^3 = A^2 A: (1,1): 72+14 = 86;
(1,2): 18+21 = 39; (2,1): 56+22 = 78; (2,2): 14+33 = 47.
Trace 86+47 = 133 = 125+8 = 5^3+2^3.

## 7. Polynomial values at 0 and 1

p(0) = 10 = det A: the constant term of the characteristic polynomial
is the determinant (up to sign; exact here since degree 2).
p(1) = 1-7+10 = 4 = det(A-I): A-I = [[3,1],[2,2]], det 6-2 = 4.
Consistent both ways.
