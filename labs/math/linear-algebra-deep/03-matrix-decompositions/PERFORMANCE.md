# Performance: Matrix Decompositions

## Cost model
For square n-by-n work, LU without pivoting costs 2 n^3 / 3 flops and
Cholesky costs n^3 / 3, the symmetry saving exactly half. Householder
QR of an m-by-n matrix (m >= n) costs 2 n^2 (m - n / 3), which is
4 n^3 / 3 in the square case. Modified Gram-Schmidt on the same shape
costs about 2 m n^2 with worse constants and worse rounding behavior.
The Golub-Reinsch SVD costs O(m n^2). Triangular solves after the
fact are O(n^2) each and almost never dominate.

## Per-task costs in this lab
- LU product check with determinant 4 both ways: O(1) at this size,
  standing in for an O(n^3) factorization plus O(n^2) solve.
- QR residual with norm-squared 3 / 2: forming Q^T Q - I style checks
  costs O(n^3) naively, O(n^2) if only the residual vector is formed.
- SVD singular values 5 and 0 via A^T A: forming the Gram matrix is
  O(m n^2); its eigendecomposition is O(n^3). Production codes avoid
  forming A^T A (it squares the condition number) and bidiagonalize
  directly at the same asymptotic cost. Pivoted LU adds O(n^2)
  comparisons to the 2 n^3 / 3 flops and buys stability; the flop
  budget is unchanged, the error bounds are not.

## How to benchmark honestly
No measured figures appear here; anything resembling a timing table
would be fiction at these sizes. Measure instead: pick sizes spanning
at least a factor of 8, warm up until times stabilize, repeat and take
medians, and verify the exponent by log-log slope (3 for factorizations,
2 for the solves). Hardware details matter: pin threads, report flop
rate alongside time, and separate factorization from solve. JMH
handles the JVM side with warmup iterations; timeit covers Python.
Small hand-check sizes like this lab's exist to verify correctness,
never to demonstrate speed.
