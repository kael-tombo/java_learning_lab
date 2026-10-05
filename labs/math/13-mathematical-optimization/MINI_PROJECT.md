# MINI_PROJECT — Optimization: Gradient Descent Playground
> Implement + descend + report. ~3 hours.

## Goal
Build a CLI minimizing classic objectives (quadratic bowl, Rosenbrock, rastrigin 2D)
with vanilla GD, momentum, and Adam, logging loss per step and final point.

## Build Steps
1. `Objective.java`: f(x,y) and analytic ∇f for bowl/rosenbrock/rastrigin.
2. `GD.java`: vanilla, fixed LR, max steps, early stop on ||∇f||<1e-6.
3. `Momentum.java`: v=βv−η∇f, x+=v.
4. `Adam.java`: standard β1=0.9, β2=0.999, ε=1e-8.
5. Driver: LR sweep {1e-3,1e-2,1e-1,1e0} per objective; CSV of loss curves.

## Sample Output
```
bowl η=0.1: x→[0.0001] steps=38
rosenbrock η=0.001 GD: stuck at [−0.7,0.5] (saddle-ish)
rastrigin Adam η=0.05: found global min at [0.002,−0.001]
```

## Benchmark Table (fill)
| objective | method | η | steps to tol | final f |
|-----------|--------|---|--------------|---------|
| bowl | GD | 0.1 | | |
| bowl | Adam | 0.05 | | |
| rosenbrock | momentum | 0.01 | | |
| rastrigin | Adam | 0.05 | | |

## Acceptance
- [ ] Divergence at too-large LR is detected and reported.
- [ ] Adam reaches bowl minimum within 200 steps.
- [ ] Loss curves exported to CSV.

## Extensions
- Nesterov variant; Nesterov vs momentum on Rosenbrock.
- Plot contour map ASCII for 2D objectives.
