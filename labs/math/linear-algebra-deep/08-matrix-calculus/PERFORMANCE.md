# Performance: Matrix Calculus

## Cost model
For A n-by-n and x length n: evaluating A x costs O(n^2), and so does
the quadratic form x^T A x with its gradient (A + A^T) x. Trace
identities are not just algebra, they are algorithm selection: using
the cyclic property to parenthesize a product chain cheapest-first
can change an O(n^3) evaluation into an O(n^2) one. This lab's trace
check 21 = 21 is the constant-size shadow of that choice.

## Differentiation modes
Finite differences need n + 1 function evaluations for a gradient,
with truncation error fighting rounding error as the step shrinks.
Forward-mode automatic differentiation costs roughly n times one
function evaluation for a full gradient; reverse mode costs a small
constant multiple of one evaluation regardless of n, at the price of
storing the forward pass. For scalar-valued functions of many
variables, reverse mode wins; for few inputs and many outputs,
forward mode does.

## Per-task costs in this lab
- A x = (5, 11): one matvec, O(n^2).
- Expansion 1 + 4 + 6 + 16 = 27: the double sum, O(n^2).
- Partials 12 and 21: one more matvec with the symmetrized matrix.
- ABC versus CAB trace products: same trace, different flop counts
  in general, identical here by smallness.

## How to benchmark honestly
No timings are given here since none were measured. To compare modes
fairly: warm up, fix n across a wide sweep, and time full gradient
evaluations (not one partial) with medians over repeats. Confirm the
expected slopes on a log-log plot: quadratic for matvec-based
gradients, linear-times-n for forward mode. Use JMH on the JVM and
timeit in Python. Count memory traffic for reverse mode alongside
time, because its tape storage is the real budget at scale. State the
layout convention in every report; timings for transposed-convention
code are not comparable.
