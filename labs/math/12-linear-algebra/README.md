# Linear Algebra — Lab 12 of the Legacy Math Track

The lab works one 3x3 system through elimination in exact fractions,
certifies determinant and transpose/trace identities by direct
multiplication, solves two eigenproblems by hand, and then watches a
near-singular 2x2 amplify a 0.001 change in the right-hand side into
a 2-unit swing in the solution. Every number below was printed by a
run before being written.

## File inventory

- MATH_FOUNDATION.md: the elimination of
  [[2, 1, -1], [-3, -1, 3], [-2, 1, 2]] with multipliers -3/2, -1, 4,
  back-substitution to (13/5, 13/5, -1/5), the pivot-product identity
  2 · 1/2 · (-5) = -5 = det checked against a row-1 cofactor
  expansion, a derivation of (AB)^T = B^T A^T and trace(AB) =
  trace(BA) from the double sum, both eigenproblems (λ² - 4λ + 3 =
  0 and λ² - 4λ + 2 = 0) solved by hand, and the magnification factor
  κ₁ = 36012.001 = 6001²/1000 for the near-singular pair.
- CODE_DEEP_DIVE.md: two runnable stdlib-only programs — the 3x3
  elimination in exact fractions with residual and determinant
  checks, and one combined program verifying transpose/trace laws on
  a 2x3/3x2 pair, checking Av = λv exactly for the integer eigen pair and to 24 decimals for 2 ± √2, and solving the
  ill-conditioned system for three right-hand sides.
- EXERCISES.md: five worked problems — a 3x3 whose elimination
  produces a zero pivot and demands a row swap, the same transpose
  identity on fresh 2x2s, an eigenpair of [[4, 1], [1, 4]] verified
  in exact integers, and a run through the near-singular system with
  b₂ growing 6.001 → 6.002 → 6.004.
- FLASHCARDS.md: cards carrying the verified numbers: the multiplier
  triple, the pivot-product determinant, the eigenpair of
  [[2, 1], [1, 2]], the κ₁ = 36012.001 magnification, and the exact
  inverse [[4001, -2000], [-2000, 1000]].
- COMMON_MISTAKES.md: eliminating along the wrong axis (mixing up
  row multiplication with column operations), comparing matrix
  identities in floats instead of exact rationals, quoting
  trace/determinant as interchangeable eigenvalue statistics, and
  trusting a clean float residual from an ill-conditioned solve.

## Background you should carry in

Simultaneous-equation comfort from 02-algebra, function shape and
quadratics from 02-calculus, and the inner-product view that
03-geometry's coordinate sections develop. The eigen/conditioning
material feeds 15-numerical-methods; the fractional elimination
reappears in 13-mathematical-optimization's Hessian checks.

## Passing through the files

THEORY.md, then MATH_FOUNDATION.md with pencil, then run the deep
dive and confirm the residual lines on your own machine, then
EXERCISES.md; FLASHCARDS.md for review, COMMON_MISTAKES.md beside the
MINI_PROJECT.
