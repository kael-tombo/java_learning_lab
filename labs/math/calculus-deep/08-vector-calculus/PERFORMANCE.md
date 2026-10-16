# Performance: Vector Calculus

## Cost model
Pointwise field operators are cheap: analytic divergence and curl at
a point cost O(1) arithmetic, while finite-difference versions need
about 6 extra field evaluations for second-order accuracy. Line and
surface integrals multiply: quadrature nodes times field-evaluation
cost. The theorems are cost reductions: the divergence theorem trades
a surface quadrature for a volume quadrature when the interior is
simpler, and Green trades a boundary integral for an area integral.
Conservative fields are cheapest of all: one potential evaluation per
endpoint instead of a whole path quadrature.

## Pairwise interactions
Direct N-body field summation is O(N^2). Barnes-Hut treecodes lower
it to O(N log N) and the fast multipole method to O(N), both
textbook results with real implemented constants. These asymptotics
decide feasibility before any tuning begins.

## Accuracy pricing
Higher-order quadrature (Simpson-class O(1 / n^4)) beats refining
trapezoid rules whenever the field is smooth along the path. Near
singularities of the field, adaptive subdivision or singularity
removal wins over uniform refinement, mirroring the improper-integral
guidance of the techniques lab.

## How to benchmark honestly
This file offers analysis, not measurements. Anyone measuring should
warm up, then scale the node count and the field complexity
independently: node scaling tests the quadrature order, field scaling
tests evaluation cost, and conflating them proves nothing. Use
medians of repeats, timeit in Python, JMH on the JVM. Verify each
theorem numerically (both sides agreeing, as the lab's 2 pi and 4 pi
checks do) before timing either side; benchmarking code that has not
been cross-checked this way risks optimizing an incorrect integrand.
