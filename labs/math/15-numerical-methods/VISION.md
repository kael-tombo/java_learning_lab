# VISION — Numerical Methods Mastery Path
> Where this lab takes you: from exact ideals to floating-point reality.

## The Arc
1. **Foundations** — float representation, rounding, machine epsilon.
2. **Fluency** — root-finding (bisection/Newton), numerical integration, interpolation.
3. **Discrimination** — convergence vs divergence; stability vs conditioning.
4. **Scale** — ODE stepping (Euler/RK4), error propagation, iterative linear solvers.
5. **Production** — pick the method, quantify the error, never trust a raw double.

## Milestones (checkable)
- [ ] M1: print eps/2 and show 1.0 + eps/2 == 1.0.
- [ ] M2: bisection on x²−2 in [1,2] to 1e-6 — count iterations.
- [ ] M3: Newton on x²−2 from x=2 — observe quadratic convergence.
- [ ] M4: trapezoid vs Simpson for ∫₀¹ eˣ dx, error vs n.
- [ ] M5: Euler vs RK4 on y'=y, y(0)=1 to t=1 — error vs h.

## Anti-Goals
- `for(i=0;i<1.0;i+=0.1)` as a loop idiom; assuming Newton always converges.

## Interview Lens
- "Why is catastrophic cancellation bad?" "Iterations for bisection to tol t?" log₂((b−a)/t).

## 30-Day Plan
- Wk1 THEORY+HOW_IT_WORKS. Wk2 EXERCISES→QUIZ 90%+. Wk3 MINI_PROJECT.
- Wk4 REAL_WORLD_PROJECT war-story + teach-back.

## Done = You Can
- Choose a numerical method, predict its error, and verify empirically.
