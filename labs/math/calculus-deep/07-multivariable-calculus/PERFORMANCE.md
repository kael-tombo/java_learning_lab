# Performance: Multivariable Calculus

## Cost model
Dimension d is the budget. A finite-difference gradient needs d + 1
function evaluations; a full Hessian needs O(d^2). One Newton
optimization step solves a d-by-d system at O(d^3). Grid search at k
points per axis costs O(k^d), exponential in dimension, while gradient
descent pays O(d) per step and converges linearly with a rate set by
the Hessian's condition number. Tensor-product quadrature with m
points per axis needs m^d evaluations: the same exponential wall as
grid search.

## Monte Carlo escapes the wall
Sampling-based integration converges as O(1 / sqrt(N)) with no d in
the exponent, which is why dimensions above single digits belong to
Monte Carlo and its quasi-random refinements. The lab's small exact
cases (gradients at a point, 2-D iterated integrals) sit far below
the crossover where sampling wins.

## Second-order tests
The Hessian second-derivative test needs all second partials plus an
eigenvalue sign check: O(d^2) evaluations plus O(d^3) linear algebra.
Finite-difference Hessians amplify rounding error, so analytic or AD
partials change the achievable accuracy, not just the speed.

## How to benchmark honestly
Nothing here was timed, so nothing here quotes time. Real studies
sweep d, not just tolerance: fix the accuracy, grow the dimension,
and watch grid and tensor methods explode while gradient and sampling
methods climb gently. Discard warmup runs, repeat, and summarize with
medians; timeit for Python harnesses, JMH for JVM ones. Report
evaluations and seconds side by side, because a method with cheap
steps and many iterations can beat one with costly steps and few, or
lose, depending on the function. State d in every result line.
