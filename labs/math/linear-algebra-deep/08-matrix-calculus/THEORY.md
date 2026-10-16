# Matrix Calculus — Theory

## 1. Derivative of Ax

For fixed A, f(x) = Ax has Jacobian A: d(Ax)/dx = A. Row-wise:
f1 = x1 + 2x2 has gradient (1,2), the first row of A = [[1,2],[3,4]].

## 2. Quadratic form gradient

For f(x) = x^T A x: df/dx = (A + A^T) x; if A is symmetric, 2Ax.
Instance: A = [[1,2],[3,4]], x = (1,2). Ax = (5,11),
f = 1*5 + 2*11 = 27. A + A^T = [[2,5],[5,8]],
grad = (2+10, 5+16) = (12,21).
Finite-difference check on x1: f(1+h,2) - f(1,2) = 2h + h^2 + 10h
over h -> 12 as h -> 0. Matches.

## 3. Trace cyclic property

tr(ABC) = tr(CAB) = tr(BCA). Instance: A = [[1,2],[0,1]],
B = [[2,1],[1,2]], C = [[1,0],[3,1]]; tr(ABC) = 21 = tr(CAB),
computed entry by entry in MATH_FOUNDATION.md.

## 4. Standard identities used here

- d(a^T x)/dx = a.
- d(x^T A x)/dx = (A + A^T) x.
- d tr(AXB)/dX = A^T B^T.
- d det(X)/dX = det(X) X^{-T} (X invertible).
- Chain: dL/dx = (dL/dy)(dy/dx) with shapes (1 x m)(m x n).

## 5. Layout note

This lab uses numerator layout: df/dx for scalar f is a column of
partial derivatives. Denominator layout transposes everything;
pick one and hold it through each derivation.

## 6. Hessian of the quadratic

d2f/dx2 = A + A^T = [[2,5],[5,8]]: constant, since f is quadratic.
Symmetric with det 16-25 = -9: this f is indefinite (a saddle, not a
bowl) — gradient descent on x^T A x with this A does not converge to
a minimum. The sign of the Hessian, not just the gradient, decides.
