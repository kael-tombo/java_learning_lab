# Vector Spaces — Flashcards

## Q/A

1. Q: State the subspace test for W ⊆ V.
   A: 0 in W, and au + bv in W for all u,v in W and scalars a,b.

2. Q: Is the solution set of Ax = b (b != 0) a subspace?
   A: No — 0 is missing. It is the affine set x_p + N(A).

3. Q: Is (1,2,1) in span{(1,1,0),(0,1,1)}? Why?
   A: Yes: a=1, b=1 solves a(1,1,0)+b(0,1,1)=(1,2,1).

4. Q: Is (1,0,2) in the same span? Why?
   A: No: a=1 forces b=-1 from the second coordinate, but the third
   needs b=2. Contradiction.

5. Q: det of the matrix with rows (1,2,3),(4,5,6),(7,8,10)?
   A: -3, so the three vectors are independent.

6. Q: det with rows (1,2,3),(4,5,6),(7,8,9)?
   A: 0, so dependent. Relation: row3 = 2*row2 - row1.

7. Q: For rows (1,0,2,-1),(0,1,1,3),(2,1,5,1), what is the rank?
   A: 2, because row3 = 2*row1 + row2 exactly.

8. Q: Give a basis of that map's null space.
   A: {(-2,-1,1,0),(1,-3,0,1)}; each dots to 0 against both rows.

9. Q: State rank-nullity and the instance here.
   A: rank + nullity = dim(domain). Here 2 + 2 = 4.

10. Q: Coordinates of (3,7) in basis {(1,1),(1,-1)}?
    A: (5,-2), since 5(1,1)-2(1,-1)=(3,7).

11. Q: Union of two subspaces — subspace?
    A: Almost never. Intersection always is.

12. Q: dim of P_n and of M_{m x n}?
    A: n+1 and mn.

13. Q: det of the coordinate matrix [[1,1],[1,-1]]?
    A: -2, so {(1,1),(1,-1)} is a basis of R^2.

14. Q: dim of the solution set of a homogeneous 3x4 system of rank 2?
    A: Nullity 4-2 = 2.

15. Q: Why does one entry (9 to 10) flip dependence?
    A: det moves from 0 to -3; dependence in R^3 is the det = 0
    knife-edge.
