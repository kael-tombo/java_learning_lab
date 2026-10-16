# Vector Spaces

Micro-lab on subspaces, span, independence, bases, dimension, and
rank-nullity, worked with exact rational arithmetic throughout.

## Contents

- THEORY.md: eight axioms, subspace test, span/independence/basis,
  coordinates in the basis {(1,1),(1,-1)}, rank-nullity on the
  rows (1,0,2,-1), (0,1,1,3), (2,1,5,1) with rank 2 and nullity 2.
- MATH_FOUNDATION.md: span membership as a solved linear system,
  determinant test (-3 vs 0 on the near-miss triples), exhibited
  null-space basis {(-2,-1,1,0),(1,-3,0,1)}, coordinates (5,-2).
- CODE_DEEP_DIVE.md: stdlib-only Python (fractions) that recomputes
  the determinant, the row dependence, the null-space check, and the
  coordinates, with observed outputs.
- EXERCISES.md: six problems with worked solutions, including the
  dependence relation 2*(4,5,6)-(1,2,3)=(7,8,9).
- FLASHCARDS.md: twelve recall cards keyed to the same numbers.

## How to use

Read THEORY.md, then MATH_FOUNDATION.md with a REPL open; rerun every
CODE_DEEP_DIVE.md snippet before attempting EXERCISES.md.

## Prerequisites

High-school algebra and solving 2x2 linear systems. No prior abstract
algebra assumed.

## Worked anchors (all values executed, not hand-waved)

- det {(1,2,3),(4,5,6),(7,8,10)} = -3; with 9 instead of 10, 0.
- Row dependence 2*row1 + row2 = row3 pins rank at 2.
- Null-space basis {(-2,-1,1,0),(1,-3,0,1)}; rank + nullity = 2+2 = 4.
- Coordinates of (3,7) in {(1,1),(1,-1)} are (5,-2); the coordinate
  matrix has det -2.

## Study sequence

1. Read THEORY.md sections 1-2; test {(1,0),(0,1)} vs {(1,1),(1,-1)}
   for the subspace rules by hand.
2. Solve both span systems in MATH_FOUNDATION.md section 1 on paper.
3. Run the determinant snippet; flip 10 to 9 and rerun.
4. Verify each null-basis dot product without looking, then check.
5. Do EXERCISES.md 1-6 in order; cards 3-10 cover the same ground.
