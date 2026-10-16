# Matrix Calculus — Exercises

## 1. Jacobian of Ax

Q: d(Ax)/dx for A = [[1,2],[3,4]]? Verify on row 1 at x = (1,2).
A: The Jacobian is A itself. Row 1 gives f1 = x1+2x2 = 5 with
gradient (1,2), the matrix's first row.

## 2. Quadratic gradient

Q: Gradient of x^T A x at (1,2) for the same A?
A: (A+A^T)x = [[2,5],[5,8]](1,2) = (12,21). Partial check:
2*1+5*2 = 12; 5*1+8*2 = 21.

## 3. Finite difference

Q: Confirm the first gradient entry by finite differencing in x1.
A: f(2,2) = 40, f(1,2) = 27; (40-27)/1 = 13 = 12 + h with h = 1,
so the linear term is 12.

## 4. Trace cyclic

Q: Verify tr(ABC) = tr(CAB) for A=[[1,2],[0,1]], B=[[2,1],[1,2]],
C=[[1,0],[3,1]].
A: ABC = [[19,5],[7,2]], trace 21; CAB = [[4,5],[13,17]], trace 21.

## 5. Symmetric shortcut

Q: Gradient of x^T S x with S symmetric? Apply to S=[[2,1],[1,2]]
at (1,1).
A: 2Sx = 2(3,3) = (6,6). Also (S+S^T)x = 2Sx. Consistent.

## 6. d tr(AXB)/dX

Q: State and check against A = B = I.
A: A^T B^T = I, and indeed d tr(X)/dX puts 1 on the diagonal, 0
elsewhere.

## 7. Hessian definiteness

Q: Hessian of x^T A x for A = [[1,2],[3,4]]? Definite?
A: [[2,5],[5,8]], det -9: indefinite saddle. Gradient zero at x = 0
is not a minimum.

## 8. Linear form

Q: Gradient of g(x) = x1 + 2x2? Value at (1,2)?
A: (1,2) everywhere; value 5 — row 1 of Ax.
