# Matrix Calculus

Micro-lab on derivatives of Ax, quadratic forms, and trace identities,
each with a hand-checkable numeric instance.

## Contents

- THEORY.md: d(Ax)/dx = A, d(x^T A x)/dx = (A+A^T)x giving (12,21)
  at (1,2) with f = 27, trace cyclic 21 = 21, identity table, layout
  note.
- MATH_FOUNDATION.md: Ax = (5,11), expansion 1+4+6+16 = 27, partials
  12 and 21, the ABC/CAB products entry by entry.
- CODE_DEEP_DIVE.md: fractions snippets printing [5,11] 27,
  [12,21], and 21 21.
- EXERCISES.md: six problems with computed solutions.
- FLASHCARDS.md: twelve recall cards.

## How to use

Expand x^T A x by hand once (four terms, total 27); the gradient
formula then reads as bookkeeping rather than magic.

## Worked anchors (all values executed)

- Ax = (5,11); x^T A x = 27 = 1+4+6+16.
- Gradient (12,21) via [[2,5],[5,8]]; finite difference 13 = 12 + h.
- Trace cyclic: ABC and CAB traces both 21, entry by entry.
- Hessian [[2,5],[5,8]], det -9: saddle, not minimum.
- Linear form x1+2x2: gradient (1,2), value 5 at (1,2).

## Study sequence

1. Expand x^T A x into four terms summing to 27 at (1,2).
2. Differentiate term by term; assemble (12,21) = (A+A^T)x.
3. Confirm the x1 finite difference 13 = 12 + h.
4. Multiply out ABC and CAB; check both traces equal 21.
5. Note the Hessian det -9: explain why x = 0 is not a minimum.

## Notes

- d(a^T x)/dx = a: row 1 of A is (1,2), matching df1/dx exactly.
- Chain shapes: scalar-of-Ax gradients compose as (1x2)(2x2) = 1x2.
