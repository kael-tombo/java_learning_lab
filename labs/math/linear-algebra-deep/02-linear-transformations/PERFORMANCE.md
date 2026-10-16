# Performance: Linear Transformations

## Cost model
A map from R^n to R^m applied to one vector (matvec) costs O(m n):
one dot product per output row. Composing maps is matrix
multiplication: naive product of m-by-n by n-by-p costs O(m n p),
while Strassen's 1969 algorithm lowers square multiplication to
about O(n^2.81). Kernel computation is elimination at
O(m n min(m,n)); reading the trace is O(n).

## Per-task costs in this lab
- Applying the running 2-by-3 matrix: 6 multiplications, O(1).
- Kernel solve: elimination on a 2-by-3 system, constant work here,
  O(m n min(m,n)) in general.
- Composition as product: naive cost scales with the triple of the
  three dimensions; Strassen-class methods only pay off at sizes far
  beyond this lab.
- Similarity transform P^-1 A P: two square multiplications plus one
  small solve, O(n^3) overall, O(1) at n = 2.
- Trace/determinant invariance check: O(n) against an O(n^3) setup,
  which is why invariants are cheap monitors of expensive code.

## How to benchmark honestly
This file reports no measured times. A credible benchmark warms up
first (throwaway calls so caches and the JIT settle), then repeats
each size many times and keeps the median. Plot time against n on a
log-log scale and read off the slope: matvec should show slope 2,
naive multiplication slope 3. If a slope disagrees, suspect the
measurement (allocation, GC, tiny-size noise) before suspecting the
theory. Java users should reach for JMH; Python users for timeit.
Always benchmark the kernel solve separately from a bare matvec, and
state the shapes, since rectangular costs depend on all three sizes.
Sparse structure changes the picture: a sparse matvec costs O(nnz),
the nonzero count, not O(m n).
