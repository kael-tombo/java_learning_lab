# Lab 04 — Multivariate Statistics

Extends single-variable probability to joint structure: two-way tables,
covariance algebra, correlation, and the honest limits of each.

## What This Lab Actually Teaches
- Joint PMFs, marginalization as axis collapse, conditional rows as
  rescaled table slices (THEORY.md).
- Independence as a per-cell product condition, and why it fails on
  whole grids rather than in one spot.
- Covariance: computational identity, bilinearity, Cov(X, X) = Var(X),
  and the general variance law of sums.
- Correlation's scale-freeness and the exact range −1 <= ρ <= 1.
- The covariance matrix as a positive-semidefinite object.
- Zero covariance without independence, embodied by a quadratic trap
  that a single violated cell convicts.

## The Worked Material
MATH_FOUNDATION.md reads one four-cell table exhaustively: mass 1,
marginals (1/2, 1/2), E[XY] = 1/8, Cov = −1/8, ρ = −1/2 certified via
its normalization identity, conditional rows (3/4, 1/4) vs (1/4, 3/4),
and a direct/formula double on Var(2X + 3Y) = 7/4. The quadratic trap
(X uniform on {−1,0,1}, Y = X^2) shows Cov = 0 executed exactly, cell
(−1, 1) at 1/3 vs product 2/9, and Var(X + X^2) = 8/9 by both routes.
CODE_DEEP_DIVE.md holds the three programs with captured output.

## Files (core six)
| File | Contents |
|------|----------|
| THEORY.md | Joint laws, covariance algebra, correlation, PSD matrix |
| MATH_FOUNDATION.md | The four-cell table worked to the last fraction |
| CODE_DEEP_DIVE.md | Three runnable programs, outputs pasted |
| EXERCISES.md | Five problems with computed solutions |
| FLASHCARDS.md | 11 cards including theorem statement cards |
| README.md | This overview |

Companion files in this directory (QUIZ, HISTORY, the Java sources,
projects, and the rest) were not modified.

## Suggested Sequence
1. THEORY.md, then the table section of MATH_FOUNDATION.md with a
   fractions session open.
2. Run all three CODE_DEEP_DIVE.md programs; watches: `joint sums to: 1`,
   `match: True`, `Cov = 0` with the dependence conviction.
3. EXERCISES.md with attempts before solutions.
4. FLASHCARDS.md until the sums law and the trap are automatic.
