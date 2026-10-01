# Flashcards: Derivatives

## 1. Core definitions

### Card 1
**Q:** Define the derivative `f'(x)` via limits.
**A:** `f'(x) = lim_{h→0} (f(x+h) - f(x)) / h` — slope of the tangent line.

### Card 2
**Q:** Secant line vs. tangent line?
**A:** Secant = slope over an interval (average rate). Tangent = limit as the interval shrinks to zero (instantaneous rate = derivative).

### Card 3
**Q:** What is a partial derivative?
**A:** Rate of change w.r.t. one variable holding others constant. Uses `∂`, e.g. for `f(x,y) = x^2·y + y^3`: `∂f/∂x = 2xy`, `∂f/∂y = x^2 + 3y^2`.

## 2. Differentiation rules (theorems)

### Card 4
**Q:** State the Power Rule.
**A:** If `f(x) = x^n` then `f'(x) = n·x^(n-1)`. Example: `(x^2)' = 2x`.

### Card 5
**Q:** State the Product Rule.
**A:** `(u·v)' = u'·v + u·v'`.

### Card 6
**Q:** State the Quotient Rule.
**A:** `(u/v)' = (u'·v − u·v') / v^2`.

### Card 7
**Q:** State the Chain Rule (both notations).
**A:** If `y = f(g(x))`, then `dy/dx = f'(g(x))·g'(x)`, i.e. `dy/dx = dy/du · du/dx` with `u = g(x)`. Key to backpropagation.

### Card 8
**Q:** Derivatives of `sin(x)`, `cos(x)`, `e^x`, `ln(x)`?
**A:** `(sin x)' = cos x`; `(cos x)' = −sin x`; `(e^x)' = e^x`; `(ln x)' = 1/x`.

## 3. Intuition and ML links

### Card 9
**Q:** Why do derivatives matter for ML (gradient descent)?
**A:** The derivative of the cost w.r.t. each weight tells how much the error changes per unit weight change — hence which direction to step to reduce error.

### Card 10
**Q:** If `f'(a) > 0`, what does that say about `f` near `a`?
**A:** `f` is increasing through `a` (tangent slopes uphill). `f'(a) = 0` signals a stationary point (min/max/saddle candidate).

### Card 11
**Q:** Differentiable ⇒ continuous; is the converse true?
**A:** No. Counterexample: `f(x) = |x|` is continuous at 0 but not differentiable there (sharp corner, left/right slopes disagree).

### Card 12
**Q:** What is numerical differentiation (as in CODE_DEEP_DIVE)?
**A:** Approximating `f'(x) ≈ (f(x+h) − f(x−h)) / (2h)` (central difference) for small `h` — used when no closed form is available.
