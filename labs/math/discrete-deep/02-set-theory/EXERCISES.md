# Exercises — Set Theory

Five problems with worked solutions; each number is quoted from the
captured runs in CODE_DEEP_DIVE.md or follows by one exact step on a
printed value.

## Problem 1. Exhaustive De Morgan

Over U = {1,2,3}, does (A∪B)ᶜ = Aᶜ∩Bᶜ hold for every pair of subsets?
How many pairs were checked?

**Solution**: Yes. The run enumerated all 8² = 64 pairs of subsets
(there are 2³ = 8 subsets) and reported 0 union failures and 0
intersection failures. Witness run also shown: A = {1,2}, B = {2,3}
gives (A∪B)ᶜ = ∅ = Aᶜ∩Bᶜ. Exhaustion at |U| = 3 is a proof for that
universe, since every case was individually evaluated.

## Problem 2. A Three-Set Census by Hand and Formula

A = {1,2,3,4}, B = {3,4,5}, C = {4,5,6}. Compute |A∪B∪C| directly and
by the six-term formula; identify which elements pay the triple
interaction.

**Solution**: Direct union is {1,2,3,4,5,6}, size 6. Formula:
4 + 5 + 3 − 1 − 2 − 2 + 1 = 6 (run printed both sides as 6). Element 4
lies in all three sets: it is counted three times by the plus terms,
cancelled by all three pair terms (it is in every pair), then restored
once by the triple term. Elements 3 and 5 sit in exactly two sets, on
the even level, and vanish.

## Problem 3. Size of the Power Set, and Its Bijection

State |P(S)| for |S| = 0, 1, 2, 3, 4, 10 and exhibit a bijection from
P({1,2,3}) to a 8-element standard set.

**Solution**: Sizes are 1, 2, 4, 8, 16, 1024 — each equal to 2ⁿ (run
verified all six). The bijection: subset ↦ membership bit string in
element order; e.g. {1,3} ↦ 101 ↦ integer 5. The run decoded all 8
subsets to integers forming exactly {0,...,7} (printed "each of 0..7
exactly once: True"), so the map is a two-sided correspondence.

## Problem 4. Count a Rational Slice Without Double-Counting

How many positive rationals have numerator ≤ 3 and denominator ≤ 4?
Why does the naïve 3 × 4 = 12 grid overcount?

**Solution**: Exactly 9 — the run's gcd-filtered list is 1/1, 1/2,
1/3, 1/4, 2/1, 2/3, 3/1, 3/2, 3/4. The 12-cell grid double-counts
equal values: 2/2 = 1/1 and 2/4 = 1/2 are duplicates of earlier cells;
each duplicate shows up wherever gcd(n,d) > 1; keeping only reduced
pairs (n,d) with gcd 1 removes them (3 cells are reducible — 2/2,
2/4, 3/3 — leaving 9).

## Problem 5. Cantor, Twice

(a) Given the 8-row list 00000000, 00100000, 01000000, 01100000,
10000000, 10100000, 11000000, 11100000, build the anti-diagonal and
show it escapes. (b) Compute π(1,1) for the Cantor pairing and explain
how diagonal walks make N×N countable.

**Solution**: (a) The machine printed anti-diagonal 11111111, absent
from the list, disagreeing with row i at position i for all 8 rows
(observed). Every row is beaten because position i only consults row
i. (b) π(1,1) = (1+1)(1+1+1)/2 + 1 = 3 + 1 = 4 (observed:
pair(1,1) = 4). Diagonal t carries t+1 pairs, so diagonals 0..5 hold
21 pairs (run printed 21) and diagonal 6 reaches 28 in total; every
pair eventually receives a natural number, giving a bijection N×N → N.
