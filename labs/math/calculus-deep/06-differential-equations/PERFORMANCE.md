# Performance: Differential Equations

## Cost model
With step h over an interval of length T, any one-step method takes
T / h steps at O(d) work per step in dimension d. Global error is
O(h) for Euler and O(h^4) for classical RK4 on smooth problems, so
halving RK4's error costs about 20 percent more steps while halving
Euler's costs double. Implicit Euler pays a nonlinear solve per step,
O(d^3) dense with Newton's method, in exchange for stability.

## Stability limits
Explicit methods have bounded stability regions: for decaying modes
with rate |lambda|, the step must stay below a constant over |lambda|
or the computation blows up regardless of accuracy. Stiff problems,
where fast and slow modes coexist, therefore force implicit methods:
the per-step solve is cheaper than the millions of tiny explicit
steps stability would demand. The lab's logistic sketch shows the
mild end of this phenomenon.

## Adaptivity
Embedded pairs (two orders from shared stages) estimate the local
error almost for free and resize h automatically. Step counts then
track solution roughness instead of worst-case curvature.

## How to benchmark honestly
No timings are manufactured for this file. Credible ODE benchmarks
fix the tolerance and record steps plus function evaluations to reach
it, since eval counts transfer across machines and seconds do not.
Warm up, repeat, take medians; sweep tolerances to trace the
work-precision curve on log-log axes, where Euler shows slope 1 and
RK4 slope 4. timeit fits Python, JMH fits JVM code. Benchmark stiff
and non-stiff problems separately: a method comparison on one class
says nothing about the other. Always verify the solution residual;
fast integration of the wrong equation is not performance.
