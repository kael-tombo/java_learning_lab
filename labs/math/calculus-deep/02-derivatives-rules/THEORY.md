# Derivatives and Rules -- Theory

## 1. Definition

f'(a) = lim_{h -> 0} (f(a+h) - f(a))/h when the limit exists. Then f
is differentiable at a. Differentiability implies continuity: write
f(a+h) - f(a) = h * (f(a+h)-f(a))/h -> 0 * f'(a) = 0, so
lim_{h -> 0} f(a+h) = f(a). The converse is false: |x| is continuous
at 0 but not differentiable there (left quotient -1, right +1).

## 2. Core Rules

Power: d/dx x^n = n x^{n-1}. Linearity: (af + bg)' = af' + bg'.
Product: (fg)' = f'g + fg'. Quotient: (f/g)' = (f'g - fg')/g^2
(g != 0). Chain: d/dx f(g(x)) = f'(g(x)) g'(x). These five derive every
computation in MATH_FOUNDATION.md; the quotient rule is the product
rule applied to f * (1/g), and the chain rule follows from the linear
approximation of f at g(a) composed with that of g at a.

## 3. Standard Derivatives

d/dx e^x = e^x; d/dx a^x = a^x ln a; d/dx ln x = 1/x (x > 0);
d/dx sin x = cos x; d/dx cos x = -sin x; d/dx tan x = sec^2 x.
Inverse trig, e.g. d/dx arctan x = 1/(1+x^2), follows from implicit
differentiation of tan(y) = x. Logarithmic differentiation handles
x^x and products of many factors: ln y then differentiate implicitly.

## 4. Higher Derivatives and Notation

f'', f''', f^{(n)} or d^2y/dx^2: differentiate repeatedly. Leibniz
notation tracks the variable; prime notation tracks the function.
Mixed partials (lab 07) commute under the same smoothness that makes
the second derivative symmetric here.

## 5. Mean Value Theorem and Rolle

Rolle: if f is continuous on [a,b], differentiable on (a,b), and
f(a) = f(b), then some c in (a,b) has f'(c) = 0. MVT: under the same
hypotheses minus f(a) = f(b), some c has f'(c) = (f(b)-f(a))/(b-a).
Proof sketch: tilt f by the secant line to reduce MVT to Rolle; Rolle
follows from EVT (an extremum in (a,b) has zero derivative). Failure
without differentiability inside: f(x) = |x| on [-1,1] has no c with
f'(c) = 0 despite f(-1) = f(1).
