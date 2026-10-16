# Performance: Inner Products and Norms

## Cost model
A dot product or squared norm on vectors of length n costs O(n): one
multiply-add per entry. Classical Gram-Schmidt over m vectors of
length n costs O(m^2 n): vector k is orthogonalized against all k - 1
predecessors at O(n) each. The projection formula and residual checks
are single dots, O(n); applying an orthogonal matrix is O(n^2).

## Per-task costs in this lab
- Cauchy-Schwarz instance 9 <= 28: two dots plus a comparison, O(n).
- Full Gram-Schmidt triple: O(m^2 n) with m = 3, trivial in absolute
  terms and exactly the asymptotic regime in miniature.
- Projection (1/3, 8/3, 7/3): coefficient dots plus a linear
  combination, O(n) per projected vector.
- Orthogonality dots and the determinant-2 check: O(n) and O(1).

## Stability is not complexity
Modified Gram-Schmidt has the same O(m^2 n) cost as the classical
variant but far better rounding behavior; Householder QR at
2 n^2 (m - n / 3) is the production choice for the same reason. This
lab's exact fractions sidestep rounding entirely, trading speed for
bit-for-bit reproducibility. Reorthogonalization doubles the constant
to about 4 m^2 n and is the standard cure when one pass loses
orthogonality.

## How to benchmark honestly
No timings are printed here; none were collected. If you collect your
own, warm up, sweep the vector length over at least two orders of
magnitude, and confirm linear scaling for dots before believing any
single figure. Report medians of many repeats, plus the memory layout
(row- vs column-major changes constants, never exponents). JMH with
warmup iterations is the JVM standard; timeit is its Python cousin.
Benchmark norms, full orthogonalization, and residual checks as three
separate series so the O(m^2 n) term does not masquerade as O(n).
