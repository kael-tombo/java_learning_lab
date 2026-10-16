# Multivariable Calculus -- Theory

## 1. Partial Derivatives

fx = lim_{h -> 0} (f(x+h, y) - f(x, y))/h treats y as constant; fy
symmetrically. Clairaut: if fxy and fyx are continuous near a point,
they are equal there -- mixed partials commute under that hypothesis.
For f(x, y) = x^2 y + 3x y^2: fx = 2xy + 3y^2, fy = x^2 + 6xy,
fxx = 2y, fyy = 6x, fxy = fyx = 2x + 6y (verified at (2,1) in
MATH_FOUNDATION.md).

## 2. Gradient and Directional Derivatives

grad f = (fx, fy) points in the steepest-ascent direction with
magnitude equal to the steepest slope. The directional derivative in
unit direction u is D_u f = grad f . u. At (2, 1) for the f above,
grad = (7, 16), |grad| = sqrt(305) = 17.46424919657298 (observed),
and along u = (3/5, 4/5): D = (21 + 64)/5 = 17 exactly (observed).

## 3. Tangent Planes and Linear Approximation

z = f(a, b) + fx(a,b)(x - a) + fy(a,b)(y - b) is the tangent plane;
it is the first-order Taylor polynomial. For the f above at (2, 1):
z = 10 + 7(x - 2) + 16(y - 1). At (2.01, 1.02) the plane predicts
10.39 while the true value is 10.394513999999997 (observed) --
quadratic remainder ~0.0045, as expected one order smaller than the
0.03 linear correction.

## 4. Critical Points and the Second-Derivative Test

Critical: fx = fy = 0. With D = fxx fyy - fxy^2: D > 0 and fxx > 0
gives a local min; D > 0 and fxx < 0 a local max; D < 0 a saddle;
D = 0 inconclusive. For g(x, y) = x^2 + y^2 - 4x - 2y + 5:
gx = 2x - 4, gy = 2y - 2, critical (2, 1), D = 4 > 0 with gxx = 2
> 0: local min, value g(2,1) = 0 (observed).

## 5. Chain Rule and Double Integrals

Multivariable chain rule: dz/dt = fx dx/dt + fy dy/dt along a path.
Fubini: iterated integrals equal the double integral for continuous f
on a rectangle. Example: int_0^1 int_0^2 (x + 2y) dx dy = int_0^1
(2 + 4y) dy = [2y + 2y^2]_0^1 = 4 (observed); swapping the order gives
int_0^2 int_0^1 (x + 2y) dy dx = int_0^2 (x + 1) dx = 4 (observed).
