# Linear Algebra Exercises

## Vectors and Vector Spaces (Problems 1-4)

**1.** Determine if v = (2, 3) is in the span of {(1, 1), (1, -1)}.
*Hint: Solve c₁(1,1) + c₂(1,-1) = (2,3).*

**2.** Are the vectors (1,2,3), (4,5,6), (7,8,9) linearly independent?
*Hint: Form a matrix and compute its rank.*

**3.** Find a basis for the subspace of ℝ³ defined by x + y + z = 0.

**4.** What is the dimension of the space of all 2×2 symmetric matrices?

## Matrix Operations (Problems 5-8)

**5.** Compute AB where A = [1 2; 3 4] and B = [5 6; 7 8].

**6.** Find the transpose and determinant of A = [2 1; 3 4].

**7.** Compute the inverse of A = [1 2; 3 4] using Gauss-Jordan elimination.

**8.** Verify that (AB)^T = B^T A^T for the matrices in Problem 5.

## Linear Systems (Problems 9-11)

**9.** Solve using Gaussian elimination: 2x + y = 5, x - y = 1.

**10.** Find all solutions to: x + 2y - z = 3, 2x + 4y - 2z = 6.

**11.** For what value of k does the system x + y = 2, 2x + ky = 4 have (a) unique solution, (b) no solution, (c) infinitely many?

## Determinants (Problems 12-13)

**12.** Compute det([1 2 3; 0 1 4; 5 6 0]) using cofactor expansion.

**13.** Prove: If A is 3×3 and det(A) = 5, find det(2A).

## Eigenvalues and Eigenvectors (Problems 14-17)

**14.** Find eigenvalues of A = [2 1; 1 2].
*Hint: Solve det(A - λI) = 0.*

**15.** Find eigenvectors for each eigenvalue in Problem 14.

**16.** Diagonalize A = [4 1; 2 3]: find P and D such that A = PDP^(-1).

**17.** Find the eigenvalues of A = [0 -1; 1 0]. What do you notice?

## Inner Products and Orthogonality (Problems 18-20)

**18.** Compute the dot product and angle between u = (1, 2) and v = (3, 4).

**19.** Apply Gram-Schmidt to {(1,1,0), (1,0,1)} to get an orthonormal basis.

**20.** Find the projection of v = (3, 4) onto u = (1, 0).

## SVD and Applications (Problems 21-25)

**21.** Compute A^T A for A = [1 0; 0 1; 1 1] and find its eigenvalues.

**22.** Find the singular values of A = [3 0; 0 -2].

**23.** Explain why the SVD always exists for any matrix A.

**24.** Given A = UΣV^T with Σ = [5 0; 0 2], what is the rank of A?

**25.** How does truncating SVD to k singular values give the best rank-k approximation?
*Hint: Eckart-Young theorem.*
