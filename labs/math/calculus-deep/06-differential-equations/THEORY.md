# Differential Equations -- Theory

## 1. What a Solution Means

An ODE relates y, y', and x; a solution is a differentiable function
satisfying the equation on an interval, verified by substitution.
General solutions carry one constant per order; initial conditions
pin them down. Existence-uniqueness: if f and df/dy are continuous
near (x0, y0), y' = f(x, y), y(x0) = y0 has exactly one local solution.
Without the df/dy hypothesis uniqueness can fail (y' = sqrt|y|).

## 2. Separable Equations

dy/dx = g(x) h(y) separates to dy/h(y) = g(x) dx (where h != 0);
integrate both sides. MATH_FOUNDATION.md solves dy/dx = x/y with
y(0) = 2: y dy = x dx gives y^2/2 = x^2/2 + 2, i.e. y = sqrt(x^2+4)
(positive branch through (0,2)), verified by substitution at x = 3.

## 3. First-Order Linear and Integrating Factors

y' + P(x) y = Q(x) is solved by mu(x) = exp(int P dx): then
(mu y)' = mu Q, so y = (int mu Q + C)/mu. MATH_FOUNDATION.md solves
y' + 2y = 6, y(0) = 1: mu = e^{2x}, (e^{2x} y)' = 6 e^{2x},
y = 3 - 2 e^{-2x}, with residual exactly 0 at the checked point.

## 4. Growth, Decay, and Equilibria

y' = k y gives y = C e^{kx}: k > 0 growth, k < 0 decay, verified by
y' - k y = 0 on substitution. Equilibria of y' = f(y) sit at zeros of
f; f' < 0 there means stable (returns after perturbation), f' > 0
means unstable. For y' + 2y = 6, y = 3 is the stable equilibrium the
solution approaches (y(1) = 2.7293294335267744, observed).

## 5. Euler Approximation

y_{n+1} = y_n + h f(x_n, y_n) follows the tangent line. For y' = y,
y(0) = 1, h = 0.1, ten steps give 2.5937424601 (observed) against
exact e = 2.718281828459045: first-order global error O(h), here
0.1245 with h = 0.1. Halving h roughly halves the error; the method
is a baseline that higher-order schemes improve on.
