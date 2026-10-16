# Performance: Derivatives and Rules

## Cost model
Symbolic differentiation costs scale with expression size: each rule
(product, quotient, chain) replaces one node of the expression tree
with a few nodes, so a single derivative pass is linear in the tree
size, though repeated differentiation can grow expressions
exponentially. Numerical differentiation is priced in function
evaluations: forward differences need 2 evaluations with truncation
error O(h); centered differences need 2 evaluations with error
O(h^2). Rounding error grows as the step shrinks, so the best
attainable error sits near h of order sqrt(eps) for forward and order
eps^(1/3) for centered differences, where eps is machine epsilon.

## Automatic differentiation
Dual-number forward mode differentiates exactly (to roundoff) in one
pass per input direction: a gradient in n variables costs about n
forward evaluations. Reverse mode returns the full gradient for a
small constant multiple of one evaluation, at the cost of recording
the computation trace. Symbolic rules, finite differences, and AD
thus span the full triangle of exactness, speed, and memory.

## Rolle and MVT as algorithms
Locating a guaranteed stationary point by bisection on the derivative
costs O(log(1 / tol)) derivative evaluations. Verifying MVT
hypotheses is continuity plus differentiability checking, priced like
the limit routines of the previous lab.

## How to benchmark honestly
No measured numbers are quoted here. A genuine study warms up, then
compares the three approaches (symbolic, finite-difference, AD) on
the same functions at several input sizes, reporting medians of many
repeats. Vary both the expression size and the dimension: symbolic
methods degrade with the former, finite differences with the latter.
Use timeit in Python and JMH on the JVM, and always report the step
size alongside finite-difference timings, since h selects the point
on the truncation-versus-rounding tradeoff being measured.
