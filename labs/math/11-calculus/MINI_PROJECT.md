# MINI_PROJECT — Calculus: Numerical Derivative & Integral Lab
> Implement + differentiate + integrate. ~3 hours.

## Goal
Build a CLI that numerically differentiates and integrates standard functions with
several methods, compares to analytic answers, and reports error vs step size.

## Build Steps
1. `Functions.java`: f, f', f'' for x², sin x, eˣ, 1/(1+x²).
2. `Deriv.java`: forward, backward, central differences; error table vs h=10⁻¹..10⁻⁶.
3. `Integrate.java`: left/right/trapezoid/Simpson; error table vs n.
4. `FTC.java`: ∫₀¹ 2x dx via F(b)-F(a) and via Simpson — assert agreement.
5. Driver: print tables, mark the best h/n, note central-difference stability.

## Sample Output
```
f=x² at x=2: forward(h=1e-4) 4.0001, central 4.0000000000
∫₀¹ x² dx: trap n=10 0.335, Simpson n=10 0.3333333, exact 1/3
```

## Benchmark Table (fill)
| method | h or n | value | abs error |
|--------|--------|-------|-----------|
| central diff (sin, x=π/4) | 1e-4 | | |
| trapezoid ∫₀¹ eˣ | n=100 | | |
| Simpson ∫₀¹ eˣ | n=100 | | |

## Acceptance
- [ ] Central difference beats forward at moderate h.
- [ ] Simpson error shrinks ~16× when n doubles (4th order).
- [ ] FTC cross-check passes within 1e-10 for polynomial.

## Extensions
- Richardson extrapolation to kill leading error term.
- Adaptive Simpson with tolerance.
