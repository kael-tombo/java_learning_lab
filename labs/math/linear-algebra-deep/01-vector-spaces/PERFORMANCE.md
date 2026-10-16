# Performance: Vector Spaces (exact rational arithmetic)

## Cost model
Count field operations as a function of matrix shape. For an m-by-n
matrix with m <= n, reduction to row-echelon form costs about
2 m^2 n - 2 m^3 / 3 flops; square n-by-n is the familiar 2 n^3 / 3.
Rank, the null-space basis, and the determinant test in this lab all
ride on that one elimination, so they share its cubic cost.

## Per-task costs in this lab
- Determinant of a 3-by-3 triple: O(1) work, six products either way.
- Row reduction of the 3-by-4 running example: a small constant
  number of flops; the point is the method, not the size.
- Null-space basis extraction: back-substitution over the free
  variables, O(n^2) once elimination is finished.
- Coordinate solve in a 2-by-2 basis: O(1); the 2-by-2 inverse is
  four multiplications and one division.

## Exact arithmetic surcharge
This lab uses fractions, not floats. Results are exact, but numerators
and denominators grow during elimination (intermediate coefficient
swell), so wall-clock cost rises faster than the flop count suggests.
Fraction-free elimination (Bareiss, 1960s) keeps intermediates integral
at the same O(n^3) flop budget. Rank by SVD costs O(m n^2) and is
the stable choice in floating point; elimination is exact here only
because fractions allow it.

## How to benchmark honestly
No timings are quoted here because none were measured. To get real
numbers: warm the interpreter with throwaway runs, then time many
repetitions with timeit and report the median, never the best single
run. Vary the matrix size and confirm cubic growth; one size proves
nothing. On the JVM the equivalent harness is JMH with warmup
iterations. Time elimination alone, then the full null-space
extraction, so the O(n^2) tail is not hidden inside the O(n^3) head.
