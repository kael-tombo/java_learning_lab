# MINI_PROJECT — Algebra: Equation Solver CLI
> Implement + verify + visualize. ~3 hours.

## Goal
Build a CLI that solves linear equations, quadratic equations, and 2x2 linear systems,
shows the step-by-step algebra, and pretty-prints results including discriminant analysis.

## Build Steps
1. `LinearSolver.java`: parse `ax + b = cx + d`, normalize, solve, verify by substitution.
2. `QuadraticSolver.java`: standard form, discriminant Δ, one/two/complex root handling.
3. `System2x2.java`: substitution and elimination paths; determinant check for singularity.
4. `StepTracer.java`: record each transformation as a human-readable line.
5. Driver: run 12 problems, print steps + verification, count correct-by-substitution.

## Sample Run
```
3x - 7 = 2x + 5 → x = 12 (check: 29 = 29 OK)
x² - 5x + 6 = 0 → Δ=1 → x=3, x=2
2x+3y=7; x-y=1 → det=-5 → x=2, y=1
```

## Benchmark Table (fill)
| problem type | count | solved | verified | avg ms |
|--------------|-------|--------|----------|--------|
| linear       | 20    | | | |
| quadratic    | 20    | | | |
| system 2x2   | 20    | | | |

## Acceptance
- [ ] Every printed solution passes substitution check.
- [ ] Singular systems reported, not NaN.
- [ ] Complex roots printed as `a ± bi`.

## Extensions
- Add completing-the-square "derive roots" mode.
- Export steps as Markdown for study notes.
