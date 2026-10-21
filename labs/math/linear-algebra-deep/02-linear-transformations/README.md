# Linear Transformations

Micro-lab on the matrix of a linear map, kernel/image with rank-nullity,
composition as matrix product, and change of basis via similarity.

## Contents

- THEORY.md: linearity, the running matrix [[1,2,3],[0,1,4]],
  kernel span{(5,-4,1)}, rank-nullity 1+2=3, similarity
  A_P = [[3,-1],[0,2]] with trace 5 and det 6 preserved.
- MATH_FOUNDATION.md: the kernel solved coordinate by coordinate, the
  2x2 minor equal to 1, the similarity product P^{-1}AP step by step,
  a composition check giving (6,3).
- CODE_DEEP_DIVE.md: fractions snippets reproducing the kernel zero,
  the minor, the similarity, and the composition order.
- EXERCISES.md: six problems with computed solutions.
- FLASHCARDS.md: twelve recall cards.

## How to use

Work the kernel computation by hand first, then confirm with the code
snippets. Keep track of product order in every composition.

## Worked anchors (all values executed)

- ker of [[1,2,3],[0,1,4]] is span{(5,-4,1)}; rank 2 via minor 1.
- Rank-nullity: 1 + 2 = 3.
- Similarity: P^{-1}AP = [[3,-1],[0,2]]; trace 5, det 6 preserved.
- A_P eigenvalues 3 (vector (1,0)) and 2 (vector (1,1)).
- Composition check: BA(1,1) = (6,3).

## Study sequence

1. Solve the kernel system in MATH_FOUNDATION.md section 1 by hand.
2. Confirm the image minor equals 1 with the snippet in section 2.
3. Multiply out P^{-1}AP row by row; check trace 5 and det 6.
4. Read off A_P's eigenvalues from its triangular form; verify both
   eigenvectors by multiplication.
5. Do EXERCISES.md 1-8; cards 2, 8, and 13 carry the key numbers.
