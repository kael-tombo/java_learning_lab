# Applied Linear Algebra

Micro-lab on least squares via the normal equations and power iteration
with the Rayleigh quotient, all on hand-checkable numbers.

## Contents

- THEORY.md: normal equations, the fit a = 3/2, b = 1/2 with residual
  norm-squared 3/2, power iteration toward eigenvalue 3, conditioning
  note (4 +- sqrt10).
- MATH_FOUNDATION.md: matrix assembly entry by entry, the 2x2 solve,
  the residual ledger, Rayleigh values 2, 14/5, 3.
- CODE_DEEP_DIVE.md: fractions snippets for the solve, the
  orthogonality sums, and the power step.
- EXERCISES.md: six problems with computed solutions.
- FLASHCARDS.md: twelve recall cards.

## How to use

Solve the 2x2 system by hand (det 6), then confirm the residual sums
are both zero before moving on.

## Worked anchors (all values executed)

- X^T X = [[3,3],[3,5]], X^T y = (6,7); a = 3/2, b = 1/2.
- Residual (-1/2,1,-1/2), |r|^2 = 3/2, X^T r = (0,0).
- Fitted (3/2,2,5/2); Pythagoras 14 = 50/4 + 6/4.
- Power: S(1,0) = (2,1); Rayleigh 2, 14/5, 3.
- X^T X eigenvalues 4 +- sqrt10.

## Study sequence

1. Assemble X^T X and X^T y entry by entry from the three points.
2. Solve the 2x2 system (det 6) for a = 3/2, b = 1/2.
3. List predictions and residuals; confirm X^T r = (0,0).
4. Close Pythagoras 14 = 50/4 + 6/4; compare the mean-only 2.
5. Run one power step on S; compute Rayleigh 14/5 by hand.

## Notes

- X column sums are (3,3): they seed the first row of X^T X.
- dof accounting: 3 points - 2 params = 1; variance scale 3/2.
