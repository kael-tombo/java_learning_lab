# MINI_PROJECT — Integral Fundmentals: Area & Accumulation Lab
> Implement + integrate + verify. ~2 hours.

## Goal
Build a CLI computing areas between curves, accumulation functions, and average
values, cross-checked between FTC and Simpson integration.

## Build Steps
1. `Integrand.java`: polynomial/trig lambdas.
2. `Ftc.java`: F(b)−F(a) via symbolic antiderivative for polynomials.
3. `Simpson.java`: numeric integral with error vs n table.
4. Driver: 6 integrals; print both values and relative difference.

## Acceptance
- [ ] FTC and Simpson agree within 1e-8 for polynomials.
- [ ] Area between two curves non-negative and correct on a fixture.

## Extensions
- Trapezoid comparison showing lower accuracy.
