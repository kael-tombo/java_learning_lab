# MINI_PROJECT — Multivariable Calculus: Gradient & Contour CLI
> Implement + differentiate + scan. ~2 hours.

## Goal
Build a CLI computing partials numerically, plotting ASCII contour maps, locating
critical points by gradient-zero scans, and classifying them via Hessian approx.

## Build Steps
1. `Field.java`: f(x,y) for a few surfaces.
2. `Partials.java`: central differences for f_x, f_y, f_xx, f_yy, f_xy.
3. `Contour.java`: ASCII heatmap over a grid.
4. `Critical.java`: |∇f|<tol scan, classify via determinant of Hessian.
5. Driver: 3 surfaces; print critical points + ASCII contour.

## Acceptance
- [ ] Partials within 1e-4 of analytic on a test point.
- [ ] Saddle point distinguished from min/max by Hessian determinant.

## Extensions
- Directional derivative along an arbitrary unit vector.
