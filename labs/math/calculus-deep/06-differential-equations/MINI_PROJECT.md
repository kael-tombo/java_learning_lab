# MINI_PROJECT — Differential Equations: Growth/Decay Solver
> Implement + solve + simulate. ~2 hours.

## Goal
Build a CLI solving separable first-order ODEs symbolically where elementary, and
numerically (Euler/RK4) otherwise, comparing both on solvable cases.

## Build Steps
1. `Separable.java`: pattern match dy/dx = f(x)g(y); integrate both sides.
2. `Growth.java`: analytic for dy/dx = ky.
3. `Euler.java`, `Rk4.java`: numeric paths with h sweep.
4. Driver: population (logistic via Euler), decay, verify y' = ky to 1e-4.

## Acceptance
- [ ] Numeric matches analytic for y' = −y within 1e-4 at h=0.01.
- [ ] RK4 outperforms Euler by >2 digits at same h.

## Extensions
- Adaptive step on the numeric path.
