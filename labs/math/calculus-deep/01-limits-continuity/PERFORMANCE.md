# Performance: Limits and Continuity

## Cost model
Numerical limit-taking is iteration counting. Bisection on a bracket
of width w needs O(log(w / tol)) function evaluations to reach
tolerance tol, gaining one binary digit per step. Fixed-point and
secant-type iterations converge linearly or superlinearly depending
on the local slope, so step counts depend on the function, not just
the tolerance: no honest table can list times without naming the
function. Each evaluation's cost dominates everything else.

## Series and squeeze costs
A partial sum with n terms costs O(n) evaluations of the general
term. For alternating series with shrinking terms, the Leibniz test
bounds the error by the first omitted term, which turns the error
analysis into counting how many terms reach the target. Squeeze
arguments cost two bounding evaluations per step plus the comparison.

## Discontinuity detection
Classifying a discontinuity needs one-sided limits: two sequences of
evaluations instead of one. Removable versus jump versus essential is
decided by comparing limits, each comparison costing its own
iteration budget. Interval methods (evaluating over ranges rather
than points) certify continuity at higher per-step cost.

## How to benchmark honestly
There are no timings in this file because none were measured. Real
measurements would warm up the runtime, then count evaluations to
reach a fixed tolerance across a suite of functions (smooth,
oscillatory, singular), reporting medians. Time is the wrong unit;
evaluations-to-tolerance is the right one, since one expensive
transcendental call dwarfs loop overhead. Python's timeit and the
JVM's JMH both work if warmup is honored. Never benchmark on a
single friendly function: a limit routine tuned on polynomials will
lie about functions with singularities.
