# Number Theory — Lab 10 of the Legacy Math Track

Integers, divisibility, and clocks: the lab rebuilds the division
algorithm, runs extended Euclid to a full Bezout certificate, cracks
Sun Tzu's congruence system with CRT, and checks Fermat and Euler
against exact integer powers — every number below is pasted from a
captured Python run, not asserted.

## What the six files hold

- MATH_FOUNDATION.md: the division algorithm with a uniqueness proof
  for q and r, the Euclid descent for (240, 46) finished by exhaustive
  back-substitution into the identity 2 = -9·240 + 47·46, the inverse
  7⁻¹ ≡ 15 (mod 26) plus nonexistence for 6 (mod 14), CRT applied
  term-by-term to x ≡ 2, 3, 2 against moduli 3, 5, 7 yielding x = 23,
  Fermat/Euler verifications (2¹⁰ ≡ 1 mod 11; 3⁴⁰ ≡ 1 mod 100; the
  composite-modulus contrast 2⁸ ≡ 1 but 2¹⁴ ≡ 4 mod 15), a census of
  φ(n) for n = 1..24 computed two ways, and the Carmichael number 561
  shown passing Fermat a^560 ≡ 1 while its λ = 80.
- CODE_DEEP_DIVE.md: three runnable stdlib-only programs —
  divmod across all four sign cases of (a, b) normalized to the
  canonical remainder, extended Euclid printing one Bezout line per
  quotient, and the CRT construction cross-checked against a brute
  sweep of all 105 residues, then Euler/Fermat probes plus a φ table
  from both brute count and factorization formula (asserted equal).
- EXERCISES.md: five worked problems — the canonical division of
  -29 by 7, a Bezout certificate for gcd(99, 78) = -11·99 + 14·78,
  the modular inverse of 11 mod 37 (27), a fresh three-moduli CRT
  system (x ≡ 1, 2, 3 mod 4, 7, 13 resolving to x = 289 = 17²), and a
  CRT-solver program that detects the inconsistent pair x ≡ 1 (mod 4),
  x ≡ 3 (mod 8).
- FLASHCARDS.md: front-back cards carrying the run numbers: the
  Bezout identity for (240, 46), inverse 15 mod 26, the four CRT
  terms 140, 63, 30 summing to 233 ≡ 23, Fermat's composite-modulus
  failure, and the sum Σφ(n) for n ≤ 24 equal to 180.
- COMMON_MISTAKES.md: sign slips in back-substitution (the wrong
  identity 2 = 2·46 + 9·240 evaluates to 2252, not 2), inverses
  demanded where gcd ≠ 1, Fermat quoted at composite moduli, CRT
  applied to non-coprime moduli, and Python's divisor-sign convention
  for divmod versus the canonical remainder.

## Assumed background

Modular intuition from 01-arithmetic, factorization and induction from
02-algebra, and the remainder/quotient view of division that
03-probability's uniform counting also uses. Lab 15-numerical-methods
takes the inverse-existence question into the floating-point world;
06-combinatorics uses φ-like coprime counting for reduced residues.

## A reading order that works

THEORY.md, then MATH_FOUNDATION.md with pencil, then run the deep
dive, then EXERCISES.md; keep FLASHCARDS.md for spaced review and
COMMON_MISTAKES.md open while writing the MINI_PROJECT.
