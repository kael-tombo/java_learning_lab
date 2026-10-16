# Matrix Calculus — Math Foundation

All values computed in exact rational arithmetic (Python `fractions`).

## 1. Ax and the quadratic value

A = [[1,2],[3,4]], x = (1,2). Row 1: 1+4 = 5. Row 2: 3+8 = 11.
f = x^T A x = (1,2).(5,11) = 5 + 22 = 27. Direct expansion agrees:
1 + 4 + 6 + 16 = 27 (x1^2 + 2 x1x2 + 3 x2x1 + 4 x2^2 at (1,2)).

## 2. Gradient entries

A + A^T = [[2,5],[5,8]]. Times (1,2): (2+10, 5+16) = (12,21).
Partial check: df/dx1 = 2x1 + 5x2 = 2+10 = 12; df/dx2 = 5x1 + 8x2 =
5+16 = 21. Finite difference in x1 with h = 1: f(2,2) = 4+8+12+16 =
40; (40-27)/1 = 13 = 12 + h. Linear term 12 confirmed.

## 3. Trace cyclic, exhibited

AB: row 1 = (1*2+2*1, 1*1+2*2) = (4,5); row 2 = (0+1, 0+2) = (1,2).
ABC: row 1 = (4*1+5*3, 5) = (19,5); row 2 = (1+6, 2) = (7,2);
trace 19+2 = 21.
CA: row 1 = (1,2); row 2 = 3*(1,2)+(0,1) = (3,7).
CAB: row 1 = (4,5); row 2 = 3*(4,5)+(1,2) = (13,17);
trace 4+17 = 21. So tr(ABC) = 21 = tr(CAB).

## 4. d tr(AXB)/dX check

With A = I, B = I: tr(X) derivative is the ones-on-diagonal matrix;
entry (i,j) derivative of sum_k X_kk is delta_ij. Consistent with
A^T B^T = I.

## 5. Linear form and Hessian entries

g(x) = a^T x with a = (1,2): dg/dx = (1,2) = a. At x = (1,2),
g = 5 — the first entry of Ax, as expected since row 1 of A is a^T.
Hessian of f: d/dx1 of (2x1+5x2) = 2; d/dx2 of (5x1+8x2) = 8;
cross partials 5, 5 — symmetric, matching [[2,5],[5,8]].
det = 16-25 = -9.

## 6. Row-gradient correspondence

f1 = x1+2x2 has gradient (1,2) = row 1 of A; f2 = 3x1+4x2 has
gradient (3,4) = row 2. d(Ax)/dx = A stacks one row-gradient per
output row. At (1,2): f = (5,11), as in Section 1.
