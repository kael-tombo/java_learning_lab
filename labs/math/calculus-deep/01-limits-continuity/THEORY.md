# Limits and Continuity -- Theory

## 1. Epsilon-Delta Definition

lim_{x -> a} f(x) = L means: for every epsilon > 0 there exists
delta > 0 such that 0 < |x - a| < delta implies |f(x) - L| < epsilon.
The point x = a itself is excluded; the limit depends only on nearby
values. One-sided limits restrict to x > a (right, x -> a+) or x < a
(left, x -> a-). The two-sided limit exists iff both one-sided limits
exist and agree.

## 2. Limit Laws

If lim f(x) = F and lim g(x) = G (both finite), then:
sum/difference: lim (f +- g) = F +- G; product: lim fg = FG;
quotient: lim f/g = F/G provided G != 0; power/root and composition
pass through wherever the outer function is continuous.
Direct substitution works for polynomials, rationals (denominator
nonzero), roots, exponentials, logs, and trig at interior points --
every other technique here exists for the cases where substitution
gives 0/0 or another indeterminate form.

## 3. Continuity

f is continuous at a iff three things hold: f(a) is defined,
lim_{x -> a} f(x) exists, and the limit equals f(a). Continuity on an
interval means continuity at each point (one-sided at endpoints).
Sums, products, quotients (nonzero denominator), and compositions of
continuous functions are continuous. Polynomials are continuous
everywhere; rational functions wherever defined.

## 4. Squeeze Theorem

If g(x) <= f(x) <= h(x) near a (except possibly at a) and
lim g = lim h = L, then lim f = L. Standard use:
-|x| <= x sin(1/x) <= |x| forces lim_{x -> 0} x sin(1/x) = 0,
and the geometric squeeze gives lim_{x -> 0} sin(x)/x = 1, from which
lim (1 - cos x)/x^2 = 1/2 follows (see MATH_FOUNDATION.md).

## 5. Intermediate Value Theorem (IVT)

If f is continuous on [a, b] and N is between f(a) and f(b), then some
c in (a, b) has f(c) = N. Hypotheses matter: continuity on the whole
closed interval is required. Consequence: a continuous f with f(a) and
f(b) of opposite signs has a zero in (a, b).

## 6. Removable vs Jump vs Infinite Discontinuities

(x^2 - 4)/(x - 2) has a removable discontinuity at x = 2 (limit 4,
function undefined); redefining f(2) = 4 makes it continuous. A jump
(step function) has distinct finite one-sided limits and cannot be
fixed by one point. A vertical asymptote (1/x at 0) is an infinite
discontinuity: at least one one-sided limit is unbounded.
