# Derivative Applications -- Theory

## 1. Critical Points and Fermat

c is critical if f'(c) = 0 or f' is undefined at c (with c in the
domain). Fermat: a local extremum at an interior point forces f'(c)
= 0 (when differentiable). Endpoints and nondifferentiable points need
separate inspection -- they are critical without a zero derivative.

## 2. First and Second Derivative Tests

First derivative test: f' changes + to - at c gives a local max;
- to + gives a local min; no sign change gives neither (x^3 at 0).
Second derivative test: f'(c) = 0 and f''(c) < 0 gives a local max;
f''(c) > 0 gives a local min; f''(c) = 0 is inconclusive (x^4 vs x^3
both have f''(0) = 0; one is a min, the other is not an extremum).
Neither test replaces checking the sign chart or higher derivatives
when f''(c) = 0.

## 3. Extreme Value Theorem (EVT)

If f is continuous on a closed bounded [a, b], f attains a global max
and min there. Procedure: evaluate f at critical points inside (a, b)
and at a and b; the largest/smallest value wins. Open intervals and
discontinuities void the guarantee (e.g. 1/x on (0, 1] has no max).

## 4. Optimization Protocol

Model (single-variable function plus domain) -> differentiate ->
critical points -> classify (first/second derivative) -> compare with
endpoint behavior -> answer with units. MATH_FOUNDATION.md runs this
twice: a cubic interior classification and an open-box volume with
endpoint comparison.

## 5. Related Rates and Linear Approximation

Related rates: differentiate the governing relation implicitly with
respect to time, then substitute the instantaneous values (sphere
example in MATH_FOUNDATION.md). Linear approximation:
f(x) ~= f(a) + f'(a)(x - a) with error bounded by (M/2)(x-a)^2 where
M bounds |f''| nearby. Differentials dy = f'(x) dx package the same
idea; Newton iteration x_{n+1} = x_n - f/f' refines it.
