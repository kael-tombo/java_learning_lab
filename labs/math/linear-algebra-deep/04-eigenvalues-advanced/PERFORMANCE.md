# Performance: Eigenvalues, Advanced

## Cost model
Dense nonsymmetric eigensolving is O(n^3) end to end: reduction to
Hessenberg form dominates, then QR iteration at O(n^2) per sweep over
a modest number of sweeps. Symmetric tridiagonal QR is far cheaper per
step, which is why reduction to tridiagonal form comes first. Power
iteration costs one matvec, O(n^2) dense, per step, with the number of
steps set by the eigenvalue gap: error shrinks like |lambda2/lambda1|
per step, so clustered leading eigenvalues mean slow convergence.

## Per-task costs in this lab
- Characteristic polynomial of a 2-by-2: O(1); never a general
  strategy, since polynomial root-finding is ill-conditioned and the
  coefficients alone cost O(n^3) for large n.
- Diagonalization check and the A^2 trace identity: matrix
  multiplication, O(n^3) naive, O(1) at n = 2.
- Cayley-Hamilton verification entry by entry: one squaring plus
  additions, O(n^3) in general.
- Defective-block experiment: QR iteration converges slowly or stalls
  near a nontrivial Jordan block, a qualitative fact worth observing
  rather than timing.

## How to benchmark honestly
This file contains no timings because none were taken. For real data,
warm up, fix the matrix ensemble (random symmetric vs. Jordan-like
behave nothing alike), and report iterations-to-tolerance alongside
seconds, since eigensolvers stop on criteria, not clocks. Confirm
cubic scaling across sizes before quoting any single size. JMH is the
right harness for JVM code, timeit for Python. Never benchmark only
diagonal or only 2-by-2 inputs: the former converges instantly and the
latter measures call overhead, not arithmetic. Shift strategies
(Wilkinson shift for symmetric tridiagonal QR) cut sweep counts
sharply; they change the constant, not the O(n^3) envelope.
