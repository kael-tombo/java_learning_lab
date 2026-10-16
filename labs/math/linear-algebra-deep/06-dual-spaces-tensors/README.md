# Dual Spaces and Tensors

Micro-lab on dual bases computed explicitly, annihilators, Kronecker
products with the mixed-product identity, and rank-one matrices.

## Contents

- THEORY.md: dual basis phi1=(x+y)/2, phi2=(x-y)/2 with the identity
  duality table, annihilator dimension, Kronecker (3,-1,6,-2) and the
  mixed product (18,6,12,4), rank-one form.
- MATH_FOUNDATION.md: the duality checks, functional expansion giving
  14 at (5,1), the mixed product both ways, det 0 rank argument.
- CODE_DEEP_DIVE.md: fractions snippets printing 1 0 0 1, the two
  Kronecker lists, and the zero determinant.
- EXERCISES.md: six problems with computed solutions.
- FLASHCARDS.md: twelve recall cards.

## How to use

Verify the duality table by hand first; everything else is arithmetic
built on phi1 and phi2.

## Worked anchors (all values executed)

- Duality table [[1,0],[0,1]] from phi1=(x+y)/2, phi2=(x-y)/2.
- 3x-y = 2 phi1 + 4 phi2; value 14 at (5,1), 3 at (1,0).
- Kronecker (3,-1,6,-2); mixed product (18,6,12,4) both orders.
- Rank-one det 0; annihilator dim 1 with 1+1 = 2.

## Study sequence

1. Fill the duality table by evaluating phi1, phi2 on e1, e2.
2. Expand 3x-y as 2 phi1 + 4 phi2; test at (5,1) and (1,0).
3. Form the Kronecker product (3,-1,6,-2) and the mixed product
   (18,6,12,4); run snippet 2.
4. Read rank 1 off the outer-product columns; confirm det 0.
5. Do EXERCISES.md 1-9; cards 7-9 test the product identities.

## Notes

- Outer-product columns (3,6) and (-1,-2) are 3(1,2) and -1(1,2).
- Pairing: (2 phi1 + 4 phi2)(5,1) = 2*3 + 4*2 = 14.
