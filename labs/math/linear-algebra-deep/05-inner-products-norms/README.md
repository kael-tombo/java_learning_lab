# Inner Products and Norms

Micro-lab on Cauchy-Schwarz, Gram-Schmidt with exact fractions, the
projection formula, and orthogonal matrices.

## Contents

- THEORY.md: inner product axioms, Cauchy-Schwarz (9 <= 28 instance),
  the full Gram-Schmidt triple with norms 2, 3/2, 4/3, projection
  (1/3,8/3,7/3), orthogonal matrices.
- MATH_FOUNDATION.md: every coefficient derived: 1/2, 1/2, 1/3; all
  three orthogonality dots; the residual check; det 2.
- CODE_DEEP_DIVE.md: fractions snippets printing the norms, the zero
  dots, and the projection.
- EXERCISES.md: six problems with computed solutions.
- FLASHCARDS.md: twelve recall cards.

## How to use

Reproduce u2 by hand (one subtraction), then let the snippets carry
the heavier u3 arithmetic.

## Worked anchors (all values executed)

- u2 = (-1/2,1/2,1) with |u2|^2 = 3/2; u3 = (2/3,-2/3,2/3).
- All three pairwise dots are 0; det of the triple is 2.
- Projection of (1,2,3): (1/3,8/3,7/3) via 3/2 and 7/3.
- Cauchy-Schwarz: 9 <= 28; cos = 3/sqrt28.
- Orthonormal: e3 = (1/sqrt3)(1,-1,1).

## Study sequence

1. Compute u2 by hand; confirm coefficients 1/2, 1/2, 1/3 in order.
2. Check all three orthogonality dots with snippet 1.
3. Derive the projection coefficients 3/2 and 7/3 before reading.
4. Close the Pythagoras ledger 38/3 + 4/3 = 14 yourself.
5. Do EXERCISES.md 1-7; cards 4-7 hold the Gram-Schmidt numbers.

## Notes

- The residual (2/3,-2/3,2/3) equals u3 exactly: projection missed
  only the u3 direction.
- Triangle spot-check: |x+y|^2 = 22 sits inside (|x|+|y|)^2.
