# Dual Spaces and Tensors — Theory

## 1. Dual space

V* is the space of linear functionals f: V -> F. dim V* = dim V.
Given a basis {e1,e2} of R^2 with e1 = (1,1), e2 = (1,-1), the dual
basis {phi1,phi2} satisfies phi_i(e_j) = delta_ij:

    phi1(x,y) = (x+y)/2, phi2(x,y) = (x-y)/2.

Check: phi1(e1) = 1, phi1(e2) = 0; phi2(e1) = 0, phi2(e2) = 1.
Every functional is a combination: f = f(e1) phi1 + f(e2) phi2.

## 2. Annihilator

For W ⊆ V, W^0 = {f : f(w) = 0 for all w in W}; dim W + dim W^0 = dim V.
Example: W = span{(1,1)} in R^2; W^0 = span{phi2}-direction, i.e.
functionals (x,y) -> a(x-y)/2, dimension 1. 1 + 1 = 2.

## 3. Tensor/Kronecker product

For u in R^m, v in R^n, u (x) v lists all pairwise products u_i v_j.
Example: (1,2) (x) (3,-1) = (3,-1,6,-2). Mixed-product identity:

    (A (x) B)(u (x) v) = (Au) (x) (Bv).

Instance: A = [[1,1],[0,1]], B = [[2,0],[1,1]] give Au = (3,2),
Bv = (6,2), and (Au) (x) (Bv) = (18,6,12,4).

## 4. Rank one

u (x) v as a matrix is u v^T, rank <= 1. Here [[1],[2]] [3,-1] =
[[3,-1],[6,-2]]: row 2 = 2 row 1, rank exactly 1.

## 5. Double dual

Evaluation v -> (f -> f(v)) identifies finite-dimensional V with V**.
A bilinear form B(x,y) = x^T M y is a (0,2)-tensor with matrix M.

## 6. How functionals change basis

If vectors change by P, coordinates change by P^{-1}, and dual
functionals change by P^{-T} (contragredient). Here P = [[1,1],[1,-1]]
has symmetric inverse [[1/2,1/2],[1/2,-1/2]], so old-coordinate
functional (a,b) reads ((a+b)/2, (a-b)/2) in the new dual basis —
the same halves as phi1, phi2. Consistency, not coincidence.
