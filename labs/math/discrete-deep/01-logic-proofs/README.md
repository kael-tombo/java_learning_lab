# Logic and Proofs — Lab 01 of Discrete Deep

Truth tables that actually decide, induction executed to n = 1000, and
a counterexample finder that shows why forty cases prove nothing. All
numbers pasted from captured runs.

## What each file contains

- THEORY.md: the connectives as truth functions; natural deduction
  rules and the central sequent (p→q)∧(q→r) ⊢ p→r; weak/strong/
  structural induction; contraposition vs contradiction as two
  machines; a soundness/completeness sketch with the Kalmár route and
  compactness; the decidability boundary (2ⁿ enumeration vs
  semi-decidable first-order validity).
- MATH_FOUNDATION.md: the 8-valuation enumeration of the central
  sequent (hypotheses hold on 4 of 8), the reversed chain's failure at
  p=false,q=false,r=true, ¬(p→q) ≡ p∧¬q checked on 4 rows, the
  contradiction templates, the induction step n²+(2n+1) = (n+1)²
  verified on 0..999, and the Euler near-miss n²−n+41 dying at n = 41.
- CODE_DEEP_DIVE.md: two executed Python programs — a truth-table
  engine with counterexample extraction; the negation/contradiction/
  contraposition battery followed by induction to n = 1000 and the
  checkerbreaker.
- EXERCISES.md: five problems with solutions quoting the runs
  (validity by counting, the falsifying valuation, correct negation,
  vacuous truth behind reductio, induction-vs-checking).
- FLASHCARDS.md: twelve front-back cards; every figure (8 rows, 4 of
  8, 0 of 8 satisfying ⊥, 0 mismatches to 1000, first failure 41)
  carried from verified output.

## Prerequisites within the track

None — this is the entry lab. It supplies the proof patterns used by
set theory (Lab 02) and combinatorics (Lab 03): counting assignments,
constructing bijections of valuations, and induction for sum/product
identities.

## Do this

Run both programs first with the outputs in view; then re-do
Problem 2 by hand to feel one counterexample defeating a candidate
proof — the cheapest skill in this lab and the one most often missing.
