# Combinatorics — Lab 03 of Discrete Deep

Stars-and-bars closed forms matched against brute censuses, an
upper-bound case where the refund level stays dead, derangements by
two routes, and a thousand-integer divisibility census. All numbers
from captured runs.

## What each file contains

- THEORY.md: counting-as-bijection with the star-string witness (4,2,4)
  ↦ ★★★★|★★|★★★★; both stars-and-bars forms with four and three
  verified cases; the inclusion–exclusion principle with the level
  identity Σ(−1)^{j+1}C(m,j) = 1; derangements !2..!6; the 1..1000
  census with floors and complement identity.
- MATH_FOUNDATION.md: the same numbers shown as printed pairs —
  66/84/6/1820 nonnegative, 36/84/6 positive, the 21-census at xi ≤ 5
  with C(6,2) = 15 per bad axis, signed terms 120,−120,60,−20,5,−1,
  and the 734/266 union-survivor split.
- CODE_DEEP_DIVE.md: two executed Python programs — brute-vs-closed
  stars and bars; the bounded census, both derangement engines, and
  the divisibility census with floor list and complement identity.
- EXERCISES.md: five worked problems (candies three ways, five
  variables, capped coordinates, !5 by hand-level arithmetic, the
  thousand-case reassembly with residue classes).
- FLASHCARDS.md: twelve cards, all figures run-verified.

## Prerequisites within the track

Lab 01's induction supports the binomial artifact checks; Lab 02's
inclusion-exclusion view of set unions is the three-set census's
foundation (|A₂∩A₃| floors). Products of choices feed Lab 04's
Hamilton-path counting; the capped-dole census reappears in Lab 05's
generating-function coefficient extraction (x¹⁰ in (1+x+⋯+x⁵)³).

## Do this

Run program 1 twice: once trusting the closed form, once reading the
printed lex-order sample for x₁+x₂ = 5 — six solutions, C(6,1), oldest
tool confirmed. The upper-bound problem (21) is the one to redo by
hand: one subtraction and an empty refund level teaches more
inclusion–exclusion than a generic two-set example.
