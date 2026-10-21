# Dual Spaces and Tensors — Exercises

## 1. Dual basis

Q: Dual basis to {(1,1),(1,-1)}?
A: phi1(x,y) = (x+y)/2, phi2(x,y) = (x-y)/2; table is identity.

## 2. Expansion

Q: Write f(x,y) = 3x - y in the dual basis; test at (5,1).
A: 2 phi1 + 4 phi2; 2*3+4*2 = 14 = 3*5-1.

## 3. Annihilator

Q: Annihilator of span{(1,1)} in R^2?
A: Multiples of phi2: (x,y) -> a(x-y)/2. Dimension 1; 1+1 = 2.

## 4. Kronecker

Q: (1,2) (x) (3,-1)?
A: (3,-1,6,-2).

## 5. Mixed product

Q: Verify (A (x) B)(u (x) v) = (Au) (x) (Bv) for the lab's matrices.
A: Au = (3,2), Bv = (6,2), product (18,6,12,4) — matches the direct
application.

## 6. Rank

Q: Rank of u v^T for nonzero u,v?
A: At most 1 (columns all multiples of u); exactly 1 here since
det [[3,-1],[6,-2]] = 0 with the matrix nonzero.

## 7. Second expansion

Q: Expand g(x,y) = 3x-y in the dual basis; test at (1,0).
A: g(e1) = 2, g(e2) = 4, so g = 2 phi1 + 4 phi2. At (1,0):
2*(1/2)+4*(1/2) = 3 = g(1,0). Exact.

## 8. Kronecker dimensions

Q: (A (x) B) shape for A 2x2, B 2x2? Input/output sizes?
A: 4x4 on 4-vectors: (2*2) x (2*2). Here it sends (3,-1,6,-2) to
(18,6,12,4).

## 9. Annihilator values

Q: Evaluate z(x,y) = (x-y)/2 on (1,1) and (1,-1). Conclusion?
A: 0 and 1. Zero on W = span{(1,1)}, nonzero overall: spans W^0,
which is 1-dimensional since 2-1 = 1.
