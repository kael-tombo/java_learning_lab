# Exercises — Combinatorics

Five problems with worked solutions; every number is quoted from the
captured runs in CODE_DEEP_DIVE.md.

## Problem 1. Count a Dole Three Ways

In how many ways can 10 identical candies go to 3 children, with no
constraint? With each child getting at least one?

**Solution**: Unconstrained: C(12,2) = 66 — the run's brute census
printed 66 and match True. Positive version: C(9,2) = 36, brute print
36. The shift of 3 units off the target is the entire difference
between bars without and with a guaranteed unit per child.

## Problem 2. Five Variables, Twelve Units

How many nonnegative solutions has x₁+⋯+x₅ = 12?

**Solution**: 1820. The run printed brute 1820 and C(16,4) = 1820 —
12 stars with 4 bars among 16 slots. The scale compounds quadratically
in n and to the fourth power in k's binomial coefficient; the brute
grid would have scanned all C(16,4)-worth of candidates.

## Problem 3. Cap the Coordinates

Count solutions of x₁+x₂+x₃ = 10 with 0 ≤ xᵢ ≤ 5.

**Solution**: 21. Levels from the run: unbounded C(12,2) = 66;
each bad-axis condition xᵢ ≥ 6 contributes C(6,2) = 15; three such
axes give 45; pairs of violations are impossible (6+6 > 10), so plus
level is 0. Inclusion–exclusion: 66 − 45 + 0 = 21 = brute print. The
parity here is one subtraction and nothing else, since the refund
never activates.

## Problem 4. Derangements: Verify !5 by Hand-Level Arithmetic

Compute !5 with the alternating-sum formula and reconcile with brute.

**Solution**: Signed terms (run-printed): 120, −120, 60, −20, 5, −1,
total 44 = !5. Reconciliation: brute permutation scan of S₅ also
printed 44. Term provenance: 120 = C(5,0)5!; −120 = −C(5,1)4!;
+60 = +C(5,2)3!; −20 = −C(5,3)2!; +5; −1. !5/5! = 44/120 ≈ 0.3667.

## Problem 5. The Thousand-Case Census, Reassembled

Of integers 1..1000, how many are divisible by 2, 3, or 5? How many
survivors? Check the complement identity and the 30-residue structure.

**Solution**: Levels (run-printed floors): 500, 333, 200 for single
divisibility; 166, 100, 66 pairwise; 33 for /30. Union:
500+333+200−166−100−66+33 = 734. Survivors: 1000 − 734 = 266, equal
True on the run, matching the brute count of integers surviving both
filters. Structure: survivors in 1..60 are 1, 7, 11, 13, 17, 19, 23,
29, 31, 37, 41, 43, 47, 49, 53, 59 — eight residues per 30-block,
namely 1, 7, 11, 13, 17, 19, 23, 29 (mod 30), and φ(30) = 8 counts
them; 266 = 8·33 + 2 accounts for the two extra survivors 31·30's
remainder classes in the final window.
