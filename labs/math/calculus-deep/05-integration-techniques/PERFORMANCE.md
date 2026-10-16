# Performance: Integration Techniques

## Cost model
Substitution and parts cost O(expression size): each step rewrites
the integrand, and success means reaching the table. Partial
fractions add algebra: after factoring, the coefficient solve is
O(k^3) in the number of poles, while factoring itself dominates
symbolically. Numeric fallback has fixed prices: an m-point
Gauss-Legendre rule integrates polynomials through degree 2m - 1
exactly, and adaptive Simpson subdivides only where the local error
estimate demands it.

## Improper integrals
Truncate the domain or isolate the singularity, then bound the tail.
Exponential tails need O(log(1 / tol)) extra panels; algebraic tails
x^-p need O(tol^(-1 / (p - 1))) by direct truncation, which is why
the p-test is a cost estimate as well as a convergence test.
Substitution that removes the singularity usually beats brute-force
refinement near it.

## Symbolic versus numeric
A closed-form antiderivative evaluates in O(1); quadrature pays per
digit by its order. The rational strategy is symbolic first, numeric
on the remainder, which is exactly the lab's workflow of
differentiate-back checks plus numerical confirmation.

## How to benchmark honestly
This file fabricates no numbers. Real comparisons warm up, then time
each technique on shared integrands at matched accuracies, counting
evaluations alongside seconds. Medians over repeats, never bests;
log-log error-versus-evaluations plots, never single-point claims.
Python timings belong in timeit, JVM timings in JMH. Separate the
easy cases (table hits) from the hard ones (oscillatory, singular,
high-dimensional): averaging them produces a number that describes
no actual integral.
