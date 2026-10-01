# Quiz: Derivatives

10 questions. Worked answers with derivations are in the Answer Key.

## Questions

**Q1.** Use the limit definition to find the derivative of `f(x) = x^2` at a general point `x`.
- A) `2x`
- B) `x`
- C) `2`
- D) `x^2 / 2`

**Q2.** Differentiate `f(x) = 3x^4 - 5x^3 + 2x - 7`.
- A) `12x^3 - 15x^2 + 2`
- B) `12x^3 - 15x^2 - 7`
- C) `3x^3 - 5x^2 + 2`
- D) `12x^4 - 15x^3 + 2x`

**Q3.** Differentiate `f(x) = x^2 · sin(x)` (product rule).
- A) `2x·sin(x) + x^2·cos(x)`
- B) `2x·cos(x)`
- C) `x^2·cos(x)`
- D) `2x·sin(x) - x^2·cos(x)`

**Q4.** Differentiate `f(x) = (x^2 + 1) / (x - 1)` at `x = 2` (quotient rule).
- A) `-1`
- B) `1`
- C) `3`
- D) `5`

**Q5.** Differentiate `f(x) = (3x^2 + 1)^4` (chain rule).
- A) `24x(3x^2 + 1)^3`
- B) `4(3x^2 + 1)^3`
- C) `6x(3x^2 + 1)^3`
- D) `12(3x^2 + 1)^3`

**Q6.** If `f(x, y) = x^2·y + y^3`, what is `∂f/∂x`?
- A) `2xy`
- B) `x^2 + 3y^2`
- C) `2xy + 3y^2`
- D) `2x + y^3`

**Q7.** If `f(x, y) = x^2·y + y^3`, what is `∂f/∂y` at `(x, y) = (2, 1)`?
- A) `7`
- B) `4`
- C) `5`
- D) `11`

**Q8.** True/False with reason: if `f` is differentiable at `x = a`, then `f` is continuous at `x = a`.
- A) True
- B) False

**Q9.** A car's position is `s(t) = 4t^2 + 2t` (metres, seconds). What is its instantaneous velocity at `t = 3`?
- A) `26 m/s`
- B) `24 m/s`
- C) `42 m/s`
- D) `14 m/s`

**Q10.** For `f(x) = e^(2x)`, what is `f'(x)`? (Chain rule with exponential.)
- A) `2e^(2x)`
- B) `e^(2x)`
- C) `2x·e^(2x)`
- D) `e^(2x) / 2`

## Answer Key (worked derivations)

**A1 → A.** `[x^2]': lim_{h→0} ((x+h)^2 - x^2)/h = lim_{h→0} (2xh + h^2)/h = lim_{h→0} (2x + h) = 2x.`

**A2 → A.** Term by term: `d/dx[3x^4] = 12x^3` (power rule), `d/dx[-5x^3] = -15x^2`, `d/dx[2x] = 2`, `d/dx[-7] = 0`. Sum: `12x^3 - 15x^2 + 2`.

**A3 → A.** Product rule `(uv)' = u'v + uv'` with `u = x^2`, `v = sin(x)`: `u' = 2x`, `v' = cos(x)`. So `f' = 2x·sin(x) + x^2·cos(x)`.

**A4 → A.** Quotient rule `(u/v)' = (u'v - uv')/v^2`, `u = x^2+1`, `v = x-1`: `u' = 2x`, `v' = 1`. `f' = (2x(x-1) - (x^2+1)·1)/(x-1)^2`. At `x=2`: numerator `= 2·2·1 - 5 = -1`, denominator `= 1`. So `f'(2) = -1`.

**A5 → A.** Outer `u^4 → 4u^3`, inner `u = 3x^2+1 → u' = 6x`. Chain: `f' = 4(3x^2+1)^3 · 6x = 24x(3x^2+1)^3`.

**A6 → A.** Hold `y` constant: `∂/∂x[x^2·y] = 2xy`, `∂/∂x[y^3] = 0`. So `∂f/∂x = 2xy`.

**A7 → A.** `∂f/∂y = x^2 + 3y^2` (derivative of `x^2·y` w.r.t. `y` is `x^2`; of `y^3` is `3y^2`). At `(2,1)`: `4 + 3 = 7`.

**A8 → A (True).** Differentiability means the limit `lim_{h→0} (f(a+h)-f(a))/h` exists, so `f(a+h) - f(a) = h · (→f'(a)) → 0`. Hence `lim_{h→0} f(a+h) = f(a)`: continuity. Converse is false (`|x|` at 0).

**A9 → A.** `v(t) = s'(t) = 8t + 2`. At `t = 3`: `24 + 2 = 26 m/s`.

**A10 → A.** Let `u = 2x`, `f = e^u`. `df/dx = e^u · du/dx = e^(2x) · 2 = 2e^(2x)`.
