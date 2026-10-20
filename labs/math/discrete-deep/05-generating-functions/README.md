# Generating Functions — Lab 05 of Discrete Deep

Coefficient extraction as exact integer arithmetic: binomial and
trinomial expansions, a dice product read row by row, the partition
GF to degree 12, Euler's distinct = odd collapse on five rows, and a
change-making table certified by brute triples. All numbers from
captured runs.

## What each file contains

- THEORY.md: the formal-series stance (no convergence); product rule
  semantics at i + j = n; the x = 1 evaluation ledger (2·3 = 6, 3³ =
  27, 2⁴ = 16 all printed); dice D(x)²; the partition recurrence as
  1/∏(1−xᵏ); Euler's product identity realised as a DP.
- MATH_FOUNDATION.md: the printed arrays with one-step derivations —
  1, 4, 6, 4, 1; 1, 3, 6, 7, 6, 3, 1; dice 1..6..1; partitions to
  p(12) = 77; the 4·5·6·8·10 identity rows; the ten paying triples.
- CODE_DEEP_DIVE.md: two executed Python programs — exact polynomial
  multiplication with the x = 1 ledger; dice/coin product semantics,
  the partition GF with brute and Euler cross-checks, and the coin
  table.
- EXERCISES.md: five worked problems (extraction by hand, the x = 1
  homomorphism, dice coefficients, the 10-paying census, partitions
  and Euler).
- FLASHCARDS.md: twelve cards, run-verified figures only.

## Prerequisites within the track

Lab 03's stars-and-bars is this lab's [x³] = 7 case in disguise, and
the xi ≤ 5 census is [x¹⁰] of (1+x+⋯+x⁵)³. Lab 02's product/bijection
frame underlies the pairing semantics of multiplication here. The
integer recurrence carries into Lab 06's modular-exponentiation DP,
and Euler's distinct = odd collapse is the lab's deepest result: five
checked equalities falling out of one telescoping product.

## Do this

Type the dice row (1..6 apex) from memory, then compare: six at total
7 is the convolution's center-of-mass signature. Then re-derive the
10-pay table by hand through amount 6 and check against the printed
1, 1, 2, 2, 3, 4, 5, 6, ... — the first disagreement anywhere means
your coin loop got the order of coins wrong.
