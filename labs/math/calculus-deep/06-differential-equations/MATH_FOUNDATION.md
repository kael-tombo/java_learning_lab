# Differential Equations -- Math Foundation

All values computed in Python; observed outputs pasted. Every closed
form is verified by substitution into its ODE.

## 1. Exponential Growth: y' = 2y, y(0) = 3

Solution y = 3 e^{2t}. Check: y' = 6 e^{2t} = 2y, and y(0) = 3.
Observed: y(1) = 22.16716829679195. Doubling time: y = 6 when
e^{2t} = 2, t = ln 2 / 2 = 0.34657359027997264 (observed). The same
equation with k = -2 would halve every 0.34657... time units.

## 2. Separable: dy/dx = x/y, y(0) = 2

Separate: y dy = x dx. Integrate: y^2/2 = x^2/2 + C. IC: 4/2 = C,
so C = 2 and y = sqrt(x^2 + 4) (positive branch, since y(0) = 2 > 0).
Verify at x = 3: y = sqrt(13) = 3.605551275463989 (observed);
y' = 3/sqrt(13), so y y' = 3 = x (observed 3.0 exactly in float:
sqrt(13)*(3/sqrt(13)) - 3 = 0.0). Solution curve confirmed on the ODE.

## 3. Linear: y' + 2y = 6, y(0) = 1

Integrating factor mu = e^{2x}. (e^{2x} y)' = 6 e^{2x}, so e^{2x} y
= 3 e^{2x} + C, y = 3 + C e^{-2x}. IC y(0) = 1 gives C = -2:
y = 3 - 2 e^{-2x}. Observed: y(0) = 1.0, y(1) = 2.7293294335267744,
approaching the equilibrium y = 3. Residual check: y' = 4 e^{-2x},
so y' + 2y - 6 = 4 e^{-2x} + 6 - 4 e^{-2x} - 6 = 0; observed 0.0 at
x = 0.5. Exact satisfaction, not a fit.

## 4. Euler Method on y' = y, y(0) = 1

h = 0.1, 10 steps: y_10 = 2.5937424601 (observed) vs e =
2.718281828459045 (observed). Error 0.124539368359045. The method
compounds (1 + h) each step: (1.1)^10 = 2.5937424601 exactly matches
the iteration, showing the error comes from the tangent-line
approximation, not implementation drift.

## 5. Logistic Sketch: y' = y(1 - y/10)

Equilibria at y = 0 (unstable: f'(0) = 1 > 0) and y = 10 (stable:
f'(10) = -1 < 0). Starting from y(0) = 2, Euler with h = 0.1 for 50
steps gives 9.761170243292469 (observed): monotone rise
toward 10, consistent with the stable equilibrium -- the trajectory
cannot cross y = 10 by uniqueness.
