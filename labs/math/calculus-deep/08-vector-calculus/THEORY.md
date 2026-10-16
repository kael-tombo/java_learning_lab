# Vector Calculus -- Theory

## 1. Gradient, Divergence, Curl

For scalar f(x,y,z): grad f = (fx, fy, fz). For F = (P, Q, R):
div F = Px + Qy + Rz (scalar: net outflow per volume);
curl F = (Ry - Qz, Pz - Rx, Qx - Py) (vector: local rotation axis).
For F(x,y,z) = (x^2, y^2, z^2): div F = 2x + 2y + 2z (12 at (1,2,3),
observed) and curl F = (0, 0, 0) (observed componentwise). For
G(x,y,z) = (-y, x, 0): div G = 0 and curl G = (0, 0, 2) (observed).

## 2. Conservative Fields and Potentials

F = grad phi on an open simply connected domain iff curl F = 0 there
(and in general path-independence is equivalent to zero loop integrals
iff the domain has no holes). Then int_C F . dr = phi(end) - phi(start).
Example: F(x,y) = (2x, 2y) = grad(x^2 + y^2), so the integral from
(0,0) to (1,1) is 2 - 0 = 2 along every path (observed for two paths
in MATH_FOUNDATION.md).

## 3. Line and Surface Integrals

int_C F . dr = int_a^b F(r(t)) . r'(t) dt for parametrized C.
Flux across S: int_S F . n dS. For F(x,y) = (y, x) along r(t) =
(t, t^2), 0 <= t <= 1: F(r) . r' = (t^2)(1) + (t)(2t) = 3t^2, integral
[t^3]_0^1 = 1 (observed; midpoint sum gives 0.9999999999750026).

## 4. Green, Stokes, Divergence Theorems

Green (circulation): for positively oriented simple closed C bounding
D with P, Q continuously differentiable on D: int_C P dx + Q dy =
int_D (Qx - Py) dA. Check: F = (-y, x) on the unit circle gives
circulation 2 pi = 6.283185307179586 (observed): integrand Qx - Py =
1 + 1 = 2, area pi, product 2 pi.
Stokes: int_S (curl F) . n dS = int_{boundary} F . dr under matching
orientation, for piecewise smooth S with C^1 field.
Divergence (Gauss): int_{closed S} F . n dS = int_V div F dV.
Each needs the stated smoothness on the full region, not just the
boundary -- the hypotheses are load-bearing.

## 5. Which Theorem Applies

Loop integral in the plane: Green. Surface flux from interior
divergence: Gauss. Surface integral of curl from boundary data:
Stokes. Line integral of a gradient: potential difference, no theorem
needed. Checking curl = 0 first saves work whenever it vanishes.
