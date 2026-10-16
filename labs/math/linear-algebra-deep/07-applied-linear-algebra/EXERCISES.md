# Applied Linear Algebra — Exercises

## 1. Normal equations

Q: Fit y = a + bx to (0,1),(1,3),(2,2).
A: X^T X = [[3,3],[3,5]], X^T y = (6,7), det 6; a = 3/2, b = 1/2.

## 2. Residual

Q: Residual vector and squared error?
A: r = (-1/2,1,-1/2); |r|^2 = 3/2. X^T r = (0,0): sums 0 and 0.

## 3. Projection view

Q: What geometric object is the fitted vector (3/2,2,5/2)?
A: The orthogonal projection of y onto col(X); y minus it is
orthogonal to both columns.

## 4. Power iteration

Q: One power step on S = [[2,1],[1,2]] from (1,0); Rayleigh at (2,1)?
A: S(1,0) = (2,1). Rayleigh at (2,1): 14/5 = 2.8, moving from 2
toward the dominant eigenvalue 3.

## 5. Conditioning

Q: Eigenvalues of X^T X and what they say?
A: 4 +- sqrt10 (product 6, sum 8). Positive, so invertible; the
spread ~7.16/0.84 warns that forming X^T X squares sensitivity.

## 6. Rank deficiency

Q: What breaks if X's columns are dependent?
A: X^T X singular (det 0); infinitely many minimizers — the normal
equations still hold but no unique b_hat.

## 7. Pythagoras check

Q: Verify |y|^2 = |X b_hat|^2 + |r|^2.
A: 14 = 50/4 + 6/4: (9/4+4+25/4) + (1/4+1+1/4) = 56/4 = 14.

## 8. Inverse check

Q: Verify the inverse (1/6)[[5,-3],[-3,3]] of X^T X.
A: Product row 1: ((15-9)/6, (-9+15)/6) = (1,0); row 2: (0,1).

## 9. Mean-only baseline

Q: Compare against fitting just the mean.
A: y-bar = 2, residuals (-1,1,0), norm-squared 2 > 3/2. The slope
reduces squared error from 2 to 3/2.
