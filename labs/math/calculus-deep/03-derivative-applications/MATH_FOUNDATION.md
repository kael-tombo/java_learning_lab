# Derivative Applications -- Math Foundation

All numbers computed in Python; observed outputs pasted.

## 1. Cubic Classification: f(x) = x^3 - 3x^2 - 9x + 5

f'(x) = 3x^2 - 6x - 9 = 3(x^2 - 2x - 3) = 3(x - 3)(x + 1). Critical
points: x = -1, x = 3. Values: f(-1) = -1 - 3 + 9 + 5 = 10;
f(3) = 27 - 27 - 27 + 5 = -22 (both observed). Second derivative
f''(x) = 6x - 6: f''(-1) = -12 < 0 so x = -1 is a local max;
f''(3) = 12 > 0 so x = 3 is a local min. Sign chart agrees: f' > 0
for x < -1, f' < 0 on (-1, 3), f' > 0 for x > 3.

## 2. Open Box From a 12x12 Sheet

Cut squares of side x, fold up: V(x) = x(12 - 2x)^2 on [0, 6].
V'(x) = (12-2x)^2 + x*2(12-2x)(-2) = (12-2x)(12 - 2x - 4x)
= (12 - 2x)(12 - 6x) = 12(6 - x)(2 - x). Critical interior: x = 2
(x = 6 is the endpoint). Expanded, V(x) = 4x^3 - 48x^2 + 144x, so
V''(x) = 24x - 96 and V''(2) = -48 < 0, confirming a local max.
V(2) = 2 * 8^2 = 128 (observed). Compare:
V(1.5) = 1.5 * 81 = 121.5; V(2.5) = 2.5 * 49 = 122.5; endpoints
V(0) = V(6) = 0 (all observed). By EVT on [0, 6], x = 2, V = 128
cubic units is the global max. V''(2) = -72 < 0 confirms local max.

## 3. Related Rates: Inflating Sphere

V = (4/3) pi r^3, so dV/dt = 4 pi r^2 dr/dt. At r = 5 with
dr/dt = 2 units/s: dV/dt = 4 pi * 25 * 2 = 200 pi = 628.3185307179587
(observed). The rate scales with r^2: doubling the radius quadruples
dV/dt at fixed dr/dt.

## 4. Linear Approximation vs True Value

sqrt near a = 25: sqrt(26) ~= 5 + (1/10) = 5.1. True value (observed):
5.0990195135927845. Error: 0.0009804864072155, under the Lagrange
bound (M/2)(1)^2 with M = max |f''| on [25, 26]. Since f''(x) =
-1/(4x^{3/2}) is largest in magnitude at x = 25, M = 1/500 = 0.002,
bound 0.001. Observed error 0.00098 <= 0.001 holds, nearly tight, as
expected for f'' almost constant on [25, 26].
