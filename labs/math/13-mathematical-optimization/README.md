# Mathematical Optimization — Lab 13 of the Legacy Math Track

The lab tracks gradient descent step by step in exact fractions,
watches learning rates flip from convergence to oscillation to
divergence, tests convexity through the Hessian rather than by eye,
enumerates an LP's five vertices to find the optimum, and lands two
different starts of a tilted quartic in two different basins. All
numbers were printed by captured runs.

## What is inside each file

- MATH_FOUNDATION.md: the update x ← x − η·2x as a geometric series
  with exact factor (1 − 2η) — ratios 3/5, 1/5, −1/10, −1, −11/10 for
  η = 1/5, 2/5, 11/20, 1, 21/20 — plus the anisotropic quadratic
  x² + 10y² whose two direction-factors 41/50 and −4/5 explain
  zigzag, the Hessian minor test on five quadratics (including
  x² + 6xy + y² = (x+3y)² − 8y², whose −4 eigenvalue makes
  a "bowl-looking" formula nonconvex), the LP problem
  max 2x + 3y over {x+y ≤ 4, x+3y ≤ 6, x, y ≥ 0} whose true optimum
  sits at the interior vertex (3, 1), and the tilted quartic
  f = x⁴/4 − 2x² + x/4 whose exact critical values −9/2 and −7/2 at
  ∓2 are not equal.
- CODE_DEEP_DIVE.md: three runnable stdlib-only programs — five
  learning rates on f(x) = x² pasted six steps each, two rates on the
  2D anisotropic bowl, the monotonicity table for convexity by
  Hessian, and the vertex-enumeration LP plus the floating descent
  from five starts of the quartic.
- EXERCISES.md: five worked problems — a by-hand GD run at η = 1/5,
  a Hessian conviction table for f = x² + 4xy + y², an LP whose
  vertex optimum is a corner the interior vertex loses to, and a
  basin-prediction program for the quartic.
- FLASHCARDS.md: cards carrying run values — the divergence table's
  121/20 by 21/20, the zigzag y 1 → −4/5 → 16/25, minors 2, −32 for
  the mixed quartic, LP z values 0, 6, 8, 9, and the two basin
  endpoints −4.5038 and −3.5040.
- COMMON_MISTAKES.md: fixed-rate steps that overshoot (on x² rates past
  η = 1/2 bounce and past η = 1 they orbit or diverge), judging convexity
  from plot shape instead of
  the Hessian, "gradient zero means minimum" (the quartic's local max
  has f'(0) = 0 too — here the tilt moves it so basins, not maxima,
  catch starts), and trusting an LP found by projection rather than
  vertex enumeration.

## Where the prerequisites live

Single-variable derivatives from 02-calculus, quadratic forms and
matrices from 12-linear-algebra, and convex-geometry language from
05-optimization. The LP section pairs well with 08-probability's
expectation-as-linear-weight reading; conditioning of Hessians
echoes 12-linear-algebra's κ₁ exhibit.

## Order of attack

THEORY.md, MATH_FOUNDATION.md with pencil, deep-dive programs run at
PYTHONHASHSEED=0, then EXERCISES.md; keep COMMON_MISTAKES.md beside
the MINI_PROJECT to catch η slips and nonconvex verdicts early.
