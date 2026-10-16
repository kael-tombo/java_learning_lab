# Integral Fundamentals -- Theory

## 1. Riemann Sums and the Definite Integral

Partition [a, b], sample x_i* in each subinterval, form
sum f(x_i*) dx. The definite integral int_a^b f is the limit as mesh
-> 0, when it exists (continuous functions are integrable). Left,
right, midpoint, and trapezoidal choices differ for finite n but share
the limit. MATH_FOUNDATION.md computes L4, R4, M4 for x^2 on [0, 2]
exactly: 7/4, 15/4, 21/8 against the true 8/3.

## 2. Fundamental Theorem, Part 1

If f is continuous on [a, b], then F(x) = int_a^x f(t) dt satisfies
F'(x) = f(x): accumulation functions differentiate back to the
integrand. Corollary: every continuous function has an antiderivative,
even when no elementary formula exists (e.g. e^{-x^2}).

## 3. Fundamental Theorem, Part 2

If f is continuous on [a, b] and F' = f there, then
int_a^b f(x) dx = F(b) - F(a). Hypotheses: continuity of f on the
whole closed interval and F an antiderivative on it. Net area follows:
the integral counts signed area, so int_{-1}^1 x^3 dx = 0 while the
total geometric area is 1/2.

## 4. Properties and Standard Antiderivatives

Linearity, interval additivity (int_a^b + int_b^c = int_a^c),
comparison (f <= g gives int f <= int g), and |int f| <= int |f|.
Power rule: int x^n dx = x^{n+1}/(n+1) + C (n != -1);
int 1/x dx = ln|x| + C; int e^x dx = e^x + C;
int sin x dx = -cos x + C; int cos x dx = sin x + C;
int sec^2 x dx = tan x + C; int 1/sqrt(1-x^2) dx = arcsin x + C
(|x| < 1); int 1/(1+x^2) dx = arctan x + C. Each is verified by
differentiating back -- the check used for every antiderivative in
this track. The + C matters: antiderivatives form a one-parameter
family, and initial conditions select the member.
