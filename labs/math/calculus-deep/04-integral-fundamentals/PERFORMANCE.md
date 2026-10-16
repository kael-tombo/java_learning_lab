# Performance: Integral Fundamentals

## Cost model
Quadrature error orders are textbook results in the panel count n.
Left and right Riemann sums converge as O(1 / n); midpoint and
trapezoid rules as O(1 / n^2) for twice-differentiable integrands;
Simpson's rule as O(1 / n^4) for four-times-differentiable ones. Each
halving of the error therefore costs 2x more panels for Simpson but
16x more for left endpoints: order dominates budget. The Fundamental
Theorem route costs one antiderivative lookup plus O(1) evaluations,
which is why symbolic antidifferentiation wins whenever it applies.

## Monte Carlo scaling
Random sampling converges as O(1 / sqrt(N)) in the sample count N,
independent of dimension. Below about four dimensions deterministic
rules win; far above, Monte Carlo is the only game in town. Halving
Monte Carlo error always costs 4x the samples. Quasi-random
(low-discrepancy) sequences improve the rate toward O(1 / N) up to
logarithmic factors, a standard refinement of the same idea.

## Signed versus total area
Total area needs root locations first: root-finding cost plus one
quadrature per subinterval. Signed area is a single quadrature. The
extra solves are priced like the previous lab's root-finding.

## How to benchmark honestly
No timings appear below because none were taken. Honest quadrature
benchmarks fix the integrand and the tolerance, then record
evaluations-to-tolerance for each rule, with medians over repeats
after warmup. Plot error against evaluation count on log-log axes and
read the slope: -1, -2, -4 reveal the rule more reliably than any
stopwatch. Use timeit for Python and JMH for JVM ports. Test smooth,
kinked, and singular integrands separately; Simpson's O(1 / n^4) only
holds where the smoothness hypotheses hold.
