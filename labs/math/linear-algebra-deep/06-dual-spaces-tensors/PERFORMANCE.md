# Performance: Dual Spaces and Tensors

## Cost model
Computing a dual basis for R^n is one n-by-n solve: O(n^3) once, then
O(n) per functional evaluation. The Kronecker product of an m-by-n
matrix with a p-by-q matrix is an mp-by-nq array, so forming it
explicitly costs O(m n p q) time and storage: quartic in the side
length for square factors. The escape hatch is the vec identity,
(B x A) vec(X) = vec(A X B^T), which applies the product with ordinary
multiplications at cubic cost and never forms the big matrix.

## Per-task costs in this lab
- Duality table checks: dot products, O(n) each.
- Functional expansion evaluated at (5, 1) giving 14: O(n).
- Explicit Kronecker vector (3, -1, 6, -2): O(m n p q) in general,
  constant here.
- Mixed-product verification (18, 6, 12, 4) both ways: the whole
  point is that the factored side stays cheap while the expanded
  side blows up.
- Rank-one form: applying u v^T costs O(m + n) via v^T x first,
  against O(m n) for a dense matrix; the Sherman-Morrison update
  solves the rank-one-modified system in O(n^2). General tensor
  contractions are priced per index summed; the Kronecker-vec identity
  is the case where structure removes a whole factor from the bill.

## How to benchmark honestly
No measured numbers live in this file. A real comparison would time
three implementations across growing sizes after warmup: naive formed
Kronecker action, vec-trick action, and rank-one factored action, each
repeated and summarized by medians. Expect the formed version to pull
away quartically on a log-log plot. JVM experimenters should use JMH;
Python experimenters timeit; both should isolate allocation from
arithmetic, since at these expression sizes memory traffic can swamp
flops. State every shape: Kronecker costs depend on four dimensions.
