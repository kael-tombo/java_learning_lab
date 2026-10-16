# Performance: Applied Linear Algebra

## Cost model
Least squares on an m-by-n matrix (m >= n) has three standard prices.
Normal equations: form A^T A at O(m n^2), Cholesky at n^3 / 3, solve
at O(n^2). Householder QR without forming A^T A: about 2 m n^2
flops. SVD-based solution: O(m n^2) with the largest constant but the
best behavior on rank-deficient data. Power iteration is one O(n^2)
matvec per step for dense matrices; the Rayleigh quotient adds one
more matvec per evaluation.

## Convergence, not just flops
Power iteration error shrinks per step by |lambda2 / lambda1|, so the
lab's march 2, 14/5, 3 toward eigenvalue 3 is linear convergence made
visible. Normal equations square the condition number, so Cholesky on
A^T A can fail where QR on A succeeds: same answers in exact
arithmetic, different answers in floating point.

## Per-task costs in this lab
- 2-by-2 normal-equation assembly and solve: O(1) here, O(m n^2)
  plus O(n^3) in general.
- Residual ledger with norm-squared 3 / 2: O(m n) to form residuals.
- Three Rayleigh values: O(n^2) each dense.

## How to benchmark honestly
This document quotes no timings. Honest numbers need: warmup runs
discarded, medians over repeats, sizes spanning a wide range, and the
three solvers (normal, QR, SVD) timed on identical inputs, since data
shape decides the winner. Track residual norms next to seconds: the
fastest wrong answer is not a result. JMH serves JVM measurements,
timeit serves Python ones. Report the condition estimate too, because
a benchmark on well-conditioned matrices flatters normal equations.
Randomized sketching reduces m before solving, trading a small
accuracy loss for large speedups on tall systems; the flop counts
above then apply to the sketch, not the original.
