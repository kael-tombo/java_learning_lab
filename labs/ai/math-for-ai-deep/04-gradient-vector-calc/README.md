# 04-gradient-vector-calc - Gradients and Jacobians
## Overview
Gradient points along steepest ascent; central differences (f(x+h)-f(x-h))/2h approximate it to O(h^2). The Jacobian generalizes to vector outputs: rows = outputs, columns = inputs.
## Key formulas
- grad f = (df/dx_1, ..., df/dx_n); chain rule: dL/dx = J^T dL/dy.
- Jacobian of f:R^n->R^m is m x n.
## What the snippets show
- Mt04A: analytic/numeric agreement to 1e-4.
- Mt04B: 2x3 Jacobian with matrix-vector product.
## Try it
Shrink h to 1e-8 and watch roundoff degrade the match (floating-point lesson).
## Formula reference
- Partial df/dx_i; gradient column vector; Hessian matrix of second partials.
- Forward diff O(h), central O(h^2); complex-step avoids cancellation.
- Chain: dz/dx = dz/dy dy/dx; backprop is reverse-mode accumulation.
## Worked example
- f = a^2 b^2: df/da = 2a b^2 = 2*2*9 = 36; df/db = 2a^2 b = 24.
- Central h = 1e-6 matches to 4 decimals as printed.
- Jv = [0.2, 0.3]: f([1.1,2.1,3.1]) - f([1,2,3]) ~= [0.21, 0.3] (first-order).
## Pitfalls
- h too small: catastrophic cancellation; too large: truncation error.
- Jacobian storage m*n explodes; use vector products instead.
- Non-smooth points (ReLU 0): subgradients, pick a convention.
## Connections
- Backprop applies this chain rule per layer.
- Optimizers descend along these gradients.
## Exercises
1. Shrink h to 1e-8; observe roundoff damage.
2. Differentiate x^3 at x = 2 both ways.
3. Build J for f = [a+b, a-b] and apply to v.
