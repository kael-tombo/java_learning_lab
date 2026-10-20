# Number Theory — Lab 06 of Discrete Deep

Extended Euclid printing its own division steps, inverses sold with
multiply-to-1 certificates, CRT assembled tile by tile from photogenic
terms (140, 63, 30 → 23 mod 105), and Fermat/Euler checked on typed
powers. All numbers from captured runs.

## What each file contains

- THEORY.md: Bezout as the smallest positive {ax+by}; extended Euclid
  recursion; inverse existence criterion with the 6-mod-15 rejection;
  CRT triple construction term-by-term; the non-coprime consistency
  gate; Fermat with typed powers and the mod-4 counter-case; φ
  census-vs-formula and Euler's theorem.
- MATH_FOUNDATION.md: the same data with substitution checks —
  −2160 + 2162 = 2, 646 = 15·43 + 1, raw 233 → 23, difference-gate
  rows, 1024 mod 11 = 1, (4−2)(9−3) = 12.
- CODE_DEEP_DIVE.md: two executed Python programs — Euclid/Bezout with
  inverse certificates; the CRT consistency gate with printed Mi and
  inverse terms, two dead pairs, and the Fermat/Euler battery with the
  composite counter-case.
- EXERCISES.md: five worked problems (gcd 2 from (−9, 47), inverting
  17 mod 43, rebuilding 23 from tiles, the consistency gate, and
  Fermat/Euler with the counter-case).
- FLASHCARDS.md: twelve cards, every figure run-verified.

## Prerequisites within the track

Lab 01's induction justifies the Euclid descent's termination; Lab
03's census and quotient bookkeeping here become floor counts
(a mod m) in κ-CRT; Lab 05's exact-integer stance is why no modular
computation uses floating point. The tile method generalizes at once:
every CRT system with pairwise coprime moduli assembles the same way,
with the difference gate refusing the non-coprime ones.

## Do this

Redo the CRT triple with the printed inverses (2, 1, 1) and recompute
140 + 63 + 30 = 233 → 23 by hand before comparing against the checks:
the tiles are small enough that the whole theorem becomes one
arithmetic line, and the two dead pairs teach the gate the way no
positive example can.
