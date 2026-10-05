# MINI_PROJECT — Vector Calculus: Field Visualizer CLI
> Implement + visualize + integrate. ~2 hours.

## Goal
Build a CLI computing divergence/curl of 2D fields, plotting vector fields as ASCII,
and evaluating line integrals along polylines; check Green's theorem on one fixture.

## Build Steps
1. `Field.java`: F(x,y) lambdas; divergence; curl (z-component).
2. `Plot.java`: ASCII arrows on a grid.
3. `LineIntegral.java`: sum over segments.
4. `GreenCheck.java`: work around a unit square vs ∬ curl dA numerically.
5. Driver: 3 fields; print divergences, curls, line integrals, Green check.

## Acceptance
- [ ] Green's theorem matches within 1e-3 on the fixture.
- [ ] Conservative field gives path-independent work (two paths match).

## Extensions
- Stokes on a hemisphere (statement-level).
