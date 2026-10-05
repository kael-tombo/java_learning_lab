# MINI_PROJECT — Derivative Applications: Max/Min & Related-Rates CLI
> Implement + optimize + solve. ~2 hours.

## Goal
Build a CLI that finds critical points of polynomials, classifies them via first/second
derivative tests, solves related-rates for circle/cone, and prints a verification table.

## Build Steps
1. `Poly.java`: value, derivative, second derivative at a point.
2. `Critical.java`: scan for roots of f', bisect to refine, classify.
3. `Related.java`: dr/dt given, compute dA/dt and dV/dt.
4. Driver: 10 cases; print value/classification/verification.

## Acceptance
- [ ] All roots of f' reported; classification matches second-derivative sign.
- [ ] Related-rates answers double-checked by finite difference.

## Extensions
- Newton refinement to 1e-12.
