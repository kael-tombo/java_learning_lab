# Combinatorics — Flashcards (Verified Numbers)

Card numbers are pulled from the captured outputs of CODE_DEEP_DIVE.md.

### Card 1
**Front**: Stars-and-bars closed form, nonnegative case?
**Back**: C(n+k−1, k−1). Run-checked pairs: (10,3) → 66, (6,4) → 84,
(5,2) → 6, (12,5) → 1820, each brute-enumerated to equality.

### Card 2
**Front**: Strictly positive version, one shift?
**Back**: xᵢ ≥ 1 gives C(n−1, k−1): (10,3) → 36, (10,4) → 84, (7,2) → 6
(run matches). Same bars, one unit prepaid per coordinate.

### Card 3
**Front**: Without constraints, the bijection for (4,2,4)?
**Back**: The 12-slot string ★★★★|★★|★★★★: choosing 2 of 12 positions
as bars fixes the vector. Agreement at 66 = C(12,2) certifies the
correspondence is one-to-one.

### Card 4
**Front**: The xi ≤ 5 census for x₁+x₂+x₃ = 10?
**Back**: 66 − 3·15 + 3·0 = 21 (run: brute 21). Bad axes have
C(6,2) = 15 each; pairs impossible since 6+6 > 10, so the plus level
is dead.

### Card 5
**Front**: Inclusion–exclusion's net effect on one element?
**Back**: An element in exactly m sets has coefficient Σ_{j=1}^{m}
(−1)^{j+1} C(m,j) = 1 — odd levels subtract, even levels refund, and
the binomial telescoping pays each element exactly once.

### Card 6
**Front**: Derangement values by brute scan, n = 2..6?
**Back**: !2 = 1, !3 = 2, !4 = 9, !5 = 44, !6 = 265 — matched by
Σ(−1)^m C(n,m)(n−m)! on each n in the run.

### Card 7
**Front**: The n = 5 signed level terms?
**Back**: 120, −120, 60, −20, 5, −1 summing to 44 — i.e. C(5,0)5!,
−C(5,1)4!, +C(5,2)3!, −C(5,3)2!, +C(5,4)1!, −C(5,5)0!, observed
verbatim.

### Card 8
**Front**: Rate for !5 relative to all permutations?
**Back**: 44/120 ≈ 0.3667, approaching 1/e ≈ 0.368 as n grows — the
ratio, unlike the count, is a limit fact; the count itself is exact.

### Card 9
**Front**: Divisibility levels over 1..1000 for 2, 3, 5?
**Back**: Singles 500, 333, 200; pairs 166, 100, 66; triple 33 —
each a floor(1000/d) for d = 2, 3, 5, 6, 10, 15, 30 (run-printed
list).

### Card 10
**Front**: Union, survivors, identity — 2/3/5 census?
**Back**: Union 734 = 500+333+200−166−100−66+33; survivors 266 =
1000 − 734, printed equal True and matched by brute filtering.

### Card 11
**Front**: Residue structure of the survivors?
**Back**: 1, 7, 11, 13, 17, 19, 23, 29 mod 30 — the φ(30) = 8 coprime
classes; e.g. 1..60 holds exactly those doubled into 16 numbers
(run's list). 266 = 8·33 + 2.

### Card 12
**Front**: What counts as settled in this lab's method?
**Back**: Formula and brute census agreeing: every closed count (66,
84, 6, 1820, 36, 21, 44, 265, 734, 266) was double-run, formula side
and enumeration side, before use.
