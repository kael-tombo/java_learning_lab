# Integral Fundamentals -- Math Foundation

All values computed in Python (exact Fraction arithmetic for the
Riemann sums, float spot-checks elsewhere); observed outputs pasted.

## 1. Riemann Sums for x^2 on [0, 2], n = 4

dx = 0.5. Left endpoints {0, 0.5, 1, 1.5}: squares 0, 1/4, 1, 9/4,
sum 14/4, L4 = 14/4 * 1/2 = 7/4 = 1.75. Right endpoints
{0.5, 1, 1.5, 2}: squares 1/4, 1, 9/4, 4, sum 30/4,
R4 = 30/4 * 1/2 = 15/4 = 3.75. Midpoints {0.25, 0.75, 1.25, 1.75}:
squares 1/16, 9/16, 25/16, 49/16, sum 84/16 = 21/4,
M4 = 21/4 * 1/2 = 21/8 = 2.625 (all observed via fractions).
True value: int_0^2 x^2 dx = 8/3 = 2.6666... (observed). Ordering
L4 < M4 < exact < R4 holds as theory predicts for increasing convex
f: left underestimates, right overestimates, midpoint is closest.

## 2. FTC Part 2 Evaluations

int_1^3 (2x + 1) dx: antiderivative x^2 + x, so (9 + 3) - (1 + 1)
= 10. Check by geometry: trapezoid with heights 3 and 7 over width
2 gives (3+7)/2 * 2 = 10. int_0^1 e^x dx = e - 1 = 1.718281828459045
(observed). Differentiation-back: d/dx (x^2 + x) = 2x + 1,
d/dx e^x = e^x, both confirmed.

## 3. Net vs Total Area

int_{-1}^1 x^3 dx = [x^4/4]_{-1}^1 = 1/4 - 1/4 = 0: odd symmetry
cancels. Total geometric area = 2 * int_0^1 x^3 dx = 2 * 1/4 = 1/2.
Observed numerically: Simpson with n = 1000 on [-1, 1] gives
-8.881784197001253e-19, zero to machine precision.

## 4. Accumulation Function (FTC Part 1)

F(x) = int_0^x t^2 dt = x^3/3; F'(x) = x^2 = f(x) verified.
Numeric: F(2) = 8/3 = 2.6666666666666665 (observed); difference
quotient (F(2.00001) - F(1.99999))/0.00002 = 4.000000000070614
(observed), matching f(2) = 4. Accumulation differentiates back to
the integrand at the point.
