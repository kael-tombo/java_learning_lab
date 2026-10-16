# Performance: Derivative Applications

## Cost model
Root-finding and optimization are priced in function evaluations per
correct digit. Bisection gains one bit per evaluation: linear
convergence, O(log(1 / tol)) steps, guaranteed with a bracket.
Newton's method near a simple root roughly doubles correct digits
per step (quadratic convergence) but needs the derivative and a good
start. The secant method needs no derivative and converges with order
about 1.6. Blind grid search over d variables at k points each costs
O(k^d): the curse of dimensionality in its purest form.

## Optimization rates
Gradient descent on smooth strongly convex functions converges
linearly, with the per-step factor set by the condition number: on
quadratics the error contracts like ((kappa - 1) / (kappa + 1))^2 per
step. Newton's method for optimization converges quadratically near
the minimum at O(d^3) per step for the Hessian solve. The lab's
Lagrange error bound converts a derivative bound into an evaluation
budget: smaller bound, fewer terms needed.

## Linear approximation cost
One linearization needs the function value plus n partials: n + 1
evaluations by finite differences, one AD pass by reverse mode. The
approximation itself is then O(n) per query.

## How to benchmark honestly
This file invents no timings. Fair benchmarks fix the tolerance and
count evaluations to reach it across a function suite, because wall
time confounds eval cost with iteration count. Warm up, repeat, and
report medians; state starting points, since Newton tuned on a kind
start humiliates bisection unfairly. timeit covers Python, JMH covers
the JVM. Include at least one ill-conditioned case: methods ranked on
easy quadratics reorder themselves on hard ones.
