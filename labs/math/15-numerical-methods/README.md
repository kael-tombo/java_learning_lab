# Numerical Methods - Lab 15 of the Legacy Math Track

Every number in this lab was either captured from a real Python run
or derived in exact fraction arithmetic; none is quoted from memory.

## What the six files contain

- **README.md** (this file) - the honest map and the prerequisites.
- **MATH_FOUNDATION.md** - full derivations: the bisection bound for
  x^3 - x - 2 on [1, 2] with the exact sign table f(3/2) = -1/8,
  f(7/4) = 103/64, f(13/8) = 341/512, f(25/16) = 1033/4096; Newton's
  step pulled out of Taylor's theorem, then the iterate chain
  18/11 -> 14326/9361 worked in exact fractions; the 0 <-> 1 Newton
  cycle of x^3 - 2x + 2 proved in plain integers; fixed point rates
  |g'(r)| for three candidate maps; the Euler-Maclaurin edge term
  (f'(1) - f'(0))*h^2/12 that predicts the trapezoid and Simpson
  error columns to 3-4 digits; and the cancellation pathology of
  (10^16 + 1) - 10^16.
- **CODE_DEEP_DIVE.md** - three stdlib-only programs (bisection
  rows plus Newton error columns plus a failure cycle; fixed point
  versus Newton on x <- exp(-x); quadrature ratios plus
  integer-versus-float subtraction), each followed by an "Observed
  output:" block pasted from verbatim stdout.
- **EXERCISES.md** - five problems (two hand Newton iterates, a
  halving count for a 1e-6 guarantee, the arctan divergence, two
  slope-at-the-root verdicts, and a quadrature cross-examination of
  pi/4), each with a complete worked solution.
- **FLASHCARDS.md** - twelve prompt/reply cards covering bounds,
  exact fraction tables, rate constants, error orders, and failure
  modes; every numeric claim is run-backed or exactly derived.
- **COMMON_MISTAKES.md** - seven ways this topic bites: reading a
  bisection bound as the error itself, trusting one good-looking
  Newton iterate, assuming convergence is automatic, pushing big
  integers through doubles, subtracting nearly equal numbers to
  form small roots, quoting h^2/h^4 without their edge constants,
  and judging an iteration by how it looks rather than its ratio.

## Prerequisites, honestly

- Single-variable calculus: derivatives f', f'' and the Taylor
  picture behind Newton's step; nothing needs multivariable tools.
- Python floats and the fractions module. The exact-arithmetic
  habit is cultivated in labs/math/10-number-theory; lab 12
  examines ill-conditioning from the algebra side while this lab
  views the same disease from the rounding side; lab 13's descent
  machinery is fixed point iteration in different clothes.
- No numerical-analysis vocabulary assumed: contraction,
  cancellation, and order of accuracy are defined on first use.

## What the lab deliberately omits

ODE solvers, eigensolvers, matrix decompositions, random numbers.
The scope is one cubic (x^3 - x - 2), one map (x <- exp(-x)), two
integrand sets (e^x and 1/(1 + x^2)), and the double-precision
arithmetic underneath them - measured, not asserted.
