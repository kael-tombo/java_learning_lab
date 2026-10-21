# Matrix Decompositions — Flashcards

## Q/A

1. Q: LU of [[2,1,1],[4,3,3],[8,7,9]]?
   A: L=[[1,0,0],[2,1,0],[4,3,1]], U=[[2,1,1],[0,1,1],[0,0,2]].

2. Q: det from that LU?
   A: 2*1*2 = 4; expansion gives 12-12+4 = 4.

3. Q: Elimination multipliers?
   A: 2, 4, then 3.

4. Q: When does no-pivot LU exist (square)?
   A: All leading principal minors nonzero.

5. Q: Thin QR shapes for m x n independent columns?
   A: Q m x n orthonormal columns, R n x n upper-triangular.

6. Q: R for columns (1,1,0),(0,1,1)?
   A: [[sqrt2,1/sqrt2],[0,sqrt(3/2)]].

7. Q: u2 and |u2|^2 in that Gram-Schmidt step?
   A: (-1/2,1/2,1), norm-squared 3/2.

8. Q: SVD of [[3,0],[4,0]]?
   A: Singular values 5, 0; u1=(3/5,4/5), v1=(1,0).

9. Q: A^T A there?
   A: [[25,0],[0,0]].

10. Q: Rank from SVD?
    A: Count of nonzero singular values.

11. Q: Full SVD shapes for 5x3?
    A: U 5x5, Sigma 5x3, V 3x3.

12. Q: Fix for zero pivot?
    A: Partial pivoting: PA = LU.

13. Q: Solution of Ax=(3,7,18) via the LU factors?
    A: Forward gives y=(3,1,3); back gives x=(1,-1/2,3/2).

14. Q: R_11 meaning?
    A: Norm of the first column: sqrt2 = |a1|.
