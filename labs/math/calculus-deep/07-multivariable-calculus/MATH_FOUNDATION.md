# Multivariable Calculus -- Math Foundation

All values computed in Python; observed outputs pasted.

## 1. Partials of f(x, y) = x^2 y + 3x y^2 at (2, 1)

fx = 2xy + 3y^2: termwise 2*2*1 = 4 and 3*1 = 3, so fx = 7 (observed). fy = x^2 + 6xy = 4 + 12 = 16 (observed).
Second order: fxx = 2y = 2, fyy = 6x = 12, fxy = 2x + 6y = 10,
fyx = 2x + 6y = 10 (all observed) -- Clairaut holds with equality
exhibited. Function value: f(2,1) = 4 + 6 = 10 (observed).

## 2. Gradient, Magnitude, Directional Derivative

grad f(2,1) = (7, 16). Magnitude sqrt(49 + 256) = sqrt(305) =
17.46424919657298 (observed). Steepest-ascent
unit vector: (7, 16)/17.46424919657298. Directional derivative along
u = (3/5, 4/5): D = 7*(3/5) + 16*(4/5) = 21/5 + 64/5 = 85/5 = 17
exactly (observed 17.0). Since 17 < 17.464..., u is steep but not
steepest, consistent with grad giving the maximum.

## 3. Tangent Plane Accuracy

Plane at (2, 1): z = 10 + 7(x-2) + 16(y-1). At (2.01, 1.02):
prediction 10 + 0.07 + 0.32 = 10.39; true f = 10.394513999999997
(observed). Remainder 0.004514: quadratic in the step (0.01, 0.02),
one order below the 0.39 linear move. Central-difference check of fx
at (2,1) with h = 1e-5: (f(2.00001,1) - f(1.99999,1))/0.00002 =
7.000000000... (observed 7.0000000000902665), confirming fx = 7.

## 4. Min of g(x, y) = x^2 + y^2 - 4x - 2y + 5

Complete the square: (x-2)^2 + (y-1)^2 = x^2 - 4x + 4 + y^2 - 2y + 1,
so g = (x-2)^2 + (y-1)^2 + 0. Minimum 0 at (2, 1) (observed g(2,1)
= 4 + 1 - 8 - 2 + 5 = 0). Hessian [[2, 0],[0, 2]], D = 4 > 0,
gxx = 2 > 0: the second-derivative test independently reports a local
min, and the sum-of-squares form upgrades it to global.

## 5. Iterated Integral Both Orders

int_0^1 int_0^2 (x + 2y) dx dy: inner = [x^2/2 + 2xy]_{x=0}^2 = 2 + 4y;
outer = [2y + 2y^2]_0^1 = 4 (observed). Swapped: inner over y =
[x + y^2... ]: int_0^1 (x+2y) dy = x + 1; outer int_0^2 (x+1) dx =
[x^2/2 + x]_0^2 = 2 + 2 = 4 (observed). Both orders give 4: Fubini
with equality exhibited.
