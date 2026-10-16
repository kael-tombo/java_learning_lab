# Integration Techniques -- Theory

## 1. Substitution

If u = g(x) is differentiable with continuous g' and f continuous,
int f(g(x)) g'(x) dx = int f(u) du. For definite integrals change the
limits: x = a maps to u = g(a). The method inverts the chain rule, so
its check is differentiating back. Example: int 2x e^{x^2} dx with
u = x^2 gives e^{x^2} + C, verified since d/dx e^{x^2} = 2x e^{x^2}.

## 2. Integration by Parts

int u dv = uv - int v du, from the product rule. Choice of u follows
LIATE priority (log, inverse trig, algebraic, trig, exponential):
for int x e^x dx take u = x, dv = e^x dx, giving (x-1)e^x + C, and
d/dx [(x-1)e^x] = e^x + (x-1)e^x = x e^x confirms it. Definite form:
int_a^b u dv = [uv]_a^b - int_a^b v du.

## 3. Partial Fractions

A proper rational P/Q with factored denominator splits into A/(linear)
and (Bx+C)/(quadratic) terms. Example: 1/((x+1)(x+2)) = 1/(x+1) -
1/(x+2) (check: ((x+2)-(x+1))/((x+1)(x+2)) = 1/((x+1)(x+2))). Then
int_0^1 = [ln|x+1| - ln|x+2|]_0^1 = (ln 2 - ln 3) - (0 - ln 2)
= 2 ln 2 - ln 3 = 0.2876820724517808 (observed). Repeated and
irreducible-quadratic factors add standard terms.

## 4. Trigonometric Integrals and Substitution

sin^2 x = (1 - cos 2x)/2 and sin^2 + cos^2 = 1 reduce powers; e.g.
int sin^2 x dx = x/2 - sin(2x)/4 + C, checked by differentiating back
(1/2 - cos(2x)/2 = sin^2 x). For sqrt(a^2 - x^2) use x = a sin theta;
for sqrt(a^2 + x^2) use x = a tan theta; for sqrt(x^2 - a^2) use
x = a sec theta. Each converts the radical to a trig factor whose
antiderivative is elementary.

## 5. Improper Integrals

int_a^infty f = lim_{R -> infty} int_a^R f when the limit exists.
int_1^infty 1/x^2 dx = lim_{R} (1 - 1/R) = 1 converges; int_1^infty
1/x dx = lim ln R diverges. Comparison and p-test (int_1^infty
1/x^p converges iff p > 1) decide the rest.
