# Exercises - Numerical Methods, Worked

Five problems; the numbers came out of capture runs and exact
fraction work before any prose existed.

## Problem 1. Newton, Two Exact Iterates Deep

Starting from x0 = 2 on f(x) = x^3 - x - 2, produce the first two
iterates entirely in exact fractions, then match them against the
float run.

**Solution**: f(2) = 4 and f'(2) = 11, so
x1 = 2 - 4/11 = 18/11 = 1.63636363..., and the run's first Newton
line prints 1.6363636363636. Continue exactly:
f(18/11) = (5832 - 2178 - 2662)/1331 = 992/1331,
f'(18/11) = (972 - 121)/121 = 851/121, step = 992/9361, and
x2 = 18/11 - 992/9361 = 14326/9361 = 1.5303920521311825. The run's
k=2 line prints 1.5303920521312, so fraction and float agree
through every digit displayed.

## Problem 2. How Many Halvings for 1e-6, and Where Does Newton Stand?

Guarantee |x - r| <= 1e-6 for the root in [1, 2] by bisection, and
compare the evaluation budget with Newton's three-step standing
from the run.

**Solution**: The bisection bound after n halvings is
(b - a)/2^(n+1); the demand is 2^(n+1) >= 10^6. Since 2^19 = 524288
falls short and 2^20 = 1048576 clears it, n = 19 halvings and 20
evaluations suffice. The deep dive's ten halvings reached the bound
2^-11 = 0.0004883, about 500 times short of the target. Newton at
k = 3 stands at e = 6.167e-05, and the Taylor constant prices the
next step: 0.7679*(6.167e-05)^2 = 2.92e-09, roughly 7 orders of
magnitude past the bisection target, for 4 evaluations instead of
20.

## Problem 3. The Arctan Newton That Never Comes Back

Run Newton on f(x) = (1 + x^2)*atan(x) from x0 = 2, list the
iterates, and explain the flight.

**Solution**: The capture printed -3.5357, 13.9510, -279.3441,
122016.9989, with the |x| growth flag True at all four steps. The
correction x - f(x)/f'(x) here moves the iterate by
-(1 + x^2)*atan(x); once |x| is out of the basin, atan(x) sits near
+-pi/2 while (1 + x^2) keeps growing, so each step flings the
iterate to the opposite side with roughly the square of its current
size. Nothing about the method announces this: textbook Newton,
innocent starting point one unit from the root, permanent
departure.

## Problem 4. Rate Shopping for the Cubic's Root

Let r be the root of x^3 - x - 2. Judge three iteration maps by
their slope at r, then check each verdict against 12-iteration
runs: g1(x) = (x^3 - 2)^(1/3), g2(x) = 2/(x^2 - 1),
g3(x) = sqrt(1 + 2/x).

**Solution**: At r, r^3 = r + 2. For g2, g2'(x) = -4x/(x^2 - 1)^2
with x^2 - 1 = 2/x at r, so |g2'(r)| = 4r*r^2/4 = r^3 = 3.5214: over
1, so divergent, and the run shows |x - r| = 1.258e+00 after 12
iters. For g3, g3'(x) = -1/(x^2*sqrt(1 + 2/x)) and sqrt(1 + 2/r) = r
at r, so |g3'(r)| = 1/r^3 = 0.2840: convergent at that linear rate,
and the run shows 9.594e-08 after 12 iters. g1 is the trap with a
twist: its fixed point equation x = (x^3 - 2)^(1/3) cubes to
x^3 = x^3 - 2, which no x satisfies, so it has no fixed point at all
(run: |x - r| = 2.380e+00 after 12 iters). Even its slope evaluated
at r, r^(4/3) = 1.7497..., sits above 1, so no rate argument could
have rescued it anyway.

## Problem 5. A Quadrature Cross-Examination of pi/4

On I = the integral of 1/(1 + x^2) over [0, 1] = pi/4 exactly, the
capture recorded trapezoid errors 0.002604046, 0.000651040,
0.000162760 (n = 4, 8, 16) and Simpson errors 0.000006007,
0.000000038, 0.000000001, with Simpson ratios 158.98 then 63.90.
State each rule's order and explain why Simpson's ratios are not 16.

**Solution**: Trapezoid halving divides the error by 4.00 both
times: order h^2, and the constant checks -
(f'(1) - f'(0))*h^2/12 with f'(x) = -2x/(1 + x^2)^2 gives
|f'(1) - f'(0)| = 1/2, forecasting 0.5/12/16 = 0.00260417 for n = 4
against the measured 0.002604046. Simpson's ratios fly past 16
because this integrand annihilates Simpson's edge term:
f'''(x) = 24x(1 - x^2)/(1 + x^2)^4 satisfies f'''(0) = f'''(1) = 0,
so the sharp h^4 piece (f'''(1) - f'''(0))*h^4/180 is exactly zero
and the decay drops to the next Euler-Maclaurin level, which the
observed 158.98 and 63.90 reflect. The generic ratio 16 is what
e^x shows (15.91 -> 15.99 in the deep dive); on this integrand it
would have been a false prediction.
