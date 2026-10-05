# MINI_PROJECT — Numerical Methods: Solver & Integrator Lab
> Implement + solve + tabulate. ~3 hours.

## Goal
Build a CLI with bisection/Newton/secant root-finders, trapezoid/Simpson integrators,
and Euler/RK4 ODE solvers, each printing an error-vs-step table.

## Build Steps
1. `Roots.java`: bisection, Newton, secant; iteration counts; divergence detection.
2. `Integrators.java`: left/trap/Simpson with exact for comparison; error vs n=10..100000.
3. `ODEs.java`: Euler vs RK4 on y'=y, y(0)=1; error at t=1 vs h.
4. `StopWhen.java`: |f(x)|<tol OR |Δx|<tol OR maxIter — whichever first.
5. Driver: tables for f(x)=x²−2; y'=y; ∫₀¹ sin x dx; analysis at bottom.

## Sample Output
```
bisection: root 1.4142135 in 20 iters
Newton: root 1.41421356 in 5 iters (quadratic)
Simpson vs exact ∫₀¹ sin x = 0.45969769… err 1.5e-7 at n=16
RK4 y(1)=2.71828182 vs Euler 2.5937 (h=0.1)
```

## Benchmark Table (fill)
| method | param | value | error |
|--------|-------|-------|-------|
| bisection | iters | | |
| Newton | iters | | |
| Simpson | n=16 | | |
| RK4 | h=0.1 | | |
| Euler | h=0.1 | | |

## Acceptance
- [ ] Newton diverges (reported) for a deliberately bad start.
- [ ] Simpson error shrinks 16× per n doubling.
- [ ] RK4 beats Euler by >3 decimal digits at same h.

## Extensions
- Secant with Brent fallback.
- Adaptive step RK45.
