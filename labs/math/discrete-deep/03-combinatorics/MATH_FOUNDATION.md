# Combinatorics — Math Foundation

Every figure below appears in the captured runs of CODE_DEEP_DIVE.md;
enumeration and closed formulas had to agree digit-for-digit.

## 1. Stars and Bars, Brute Force Committee

Nonnegative solutions of x₁+⋯+xₖ = n. Brute counts vs closed C(n+k−1,
k−1), printed as pairs: (10,3): 66 = 66; (6,4): 84 = 84; (5,2): 6 = 6;
(12,5): 1820 = 1820 — four matches, no exceptions. Positive case
xᵢ ≥ 1 refits to C(n−1, k−1): (10,3): 36; (10,4): 84; (7,2): 6 —
observed matches again. The run also showed the lexicographic start of
x₁+x₂ = 5: (0,5), (1,4), (2,3), (3,2), with 6 total = C(6,1).

## 2. Upper-Bound Census: xi ≤ 5 With Triple Overlap Empty

Target x₁+x₂+x₃ = 10, all coordinates ≤ 5. Levels, as printed:
unbounded base C(12,2) = 66; a fixed axis violating xi ≥ 6 leaves
C(6,2) = 15; three such bad sets → union 45; pairs of bad sets empty
because 6+6 > 10. Inclusion–exclusion: 66 − 45 + 0 = 21, and the brute
enumerator printed 21. One changed bound moves the whole count: the
do-not-care ceiling is doing all the work here.

## 3. Derangements Both Ways

Brute permutation scans of Sₙ print !2 = 1, !3 = 2, !4 = 9, !5 = 44,
!6 = 265, matched by Σ(−1)^m C(n,m)(n−m)!. For n = 5 the signed level
terms printed: 120, −120, 60, −20, 5, −1, partial sum 44. Level data:
|S₅| = 120 is the 0-level; subtracting permutations with at least one
fixed point at level 1 = C(5,1)·4! = 120 undoes everything, and the
deeper levels rebuild — the alternating machinery subtracts its way to
exactly the no-fixed-point residue.

## 4. Thousand-Case Divisibility Census

Over 1..1000, observed memberships: divisible by 2 → 500; by 3 → 333;
by 5 → 200; pairs by floor(1000/6) = 166, /10 = 100, /15 = 66; triple
/30 = 33. Inclusion–exclusion union: 500+333+200−166−100−66+33 = 734.
Complement identity, both printed on the run: 1000 − 734 = 266 equals
the brute count of integers with no factor in {2,3,5}. Survivors come
in residue classes coprime to 30 — the printed first candidates in
1..60 are 1, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 49, 53, 59
(8 per full 30-window since φ(30) = 8, and 266 = 8·33 + 2).

## 5. Sanity Bijection for the Bar-Counting

A solution to x₁+⋯+x₃ = 10 corresponds to a 12-slot binary string with
exactly 2 bars: for example (4,2,4) is ★★★★|★★|★★★★. Brute/C(12,2)
agreement at 66 IS the statement that this correspondence is a
bijection and not a many-to-one projection. The sampler printed the
2-variable case's page-one solutions as a smell test before trusting
the formula's authority.
