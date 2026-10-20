# Combinatorics — Theory

## 1. Counting Is Bijection

The master tool of this lab is a bijection: |S| = |T| whenever S and T
correspond element-for-element. "How many" becomes "match to what". For
x₁+⋯+xₖ = n with xᵢ ≥ 0, the correspondence runs solution ↦ n stars
separated by k−1 bars: the string ★★★★|★★|★★★★ for (4,2,4) has 12
positions, and choosing 2 of the 12 as bars fixes the vector. Every
closed count in this lab was double-checked by brute enumeration in the
runs — the bijection and the census must agree digit-for-digit.

## 2. Stars and Bars, Exact

Nonnegative case: #solutions of x₁+⋯+xₖ = n is C(n+k−1, k−1). Verified
agreement in all four cases: n=10,k=3 gives 66 = C(12,2); n=6,k=4 gives
84 = C(9,3); n=5,k=2 gives 6 = C(6,1); n=12,k=5 gives 1820 = C(16,4).
Strictly positive xᵢ ≥ 1 shifts to C(n−1, k−1): with n=10,k=3 the count
drops to 36 = C(9,2), and the same total with k=4 gives 84 = C(9,3).
The shift is one memory-proof: hand one unit to each coordinate first,
then count the residual dole.

## 3. Upper Bounds Bring Inclusion–Exclusion

For x₁+x₂+x₃ = 10 with every xᵢ ≤ 5: the unbounded base is C(12,2) =
66; the bad set Aᵢ = {xᵢ ≥ 6} for one fixed axis has C(6,2) = 15
solutions — subtract 6 from the coordinate and count the leftover dole
of 4 across the same bars. Any two bad sets intersect emptily since
6+6 = 12 > 10, so the odd-level refund never fires and the run prints
66 − 45 + 0 = 21, agreeing with the brute enumerator at 21. The
census bookkeeping: |A₁∪A₂∪A₃| = 45 removed, pairwise terms identically
zero.

## 4. The Inclusion–Exclusion Principle, General Form

|A₁∪⋯∪Aₙ| = Σ|Aᵢ| − Σ|Aᵢ∩Aⱼ| + Σ|Aᵢ∩Aⱼ∩Aₖ| − ⋯. The coefficient of an
element belonging to exactly m of the sets is Σ_{j=1}^{m} (−1)^{j+1}·
C(m,j) = 1, whatever m is — odd levels subtract off the double-counts,
even levels refund the over-subtraction, and the telescoping binomial
identity resolves every element to exactly one membership. The run's
n=5 derangement expansion shows the levels as signed terms 120, −120,
60, −20, 5, −1, summing to 44.

## 5. Derangements: The Signature Census

Permutations with no fixed point. Direct enumeration of Sₙ gives
!2 = 1, !3 = 2, !4 = 9, !5 = 44, !6 = 265, and the inclusion–exclusion
formula Σ(−1)^m C(n,m)(n−m)! prints the same five values. The ratio
!n/n! falls toward 1/e ≈ 0.368 — !5/5! = 44/120 — but the counts
themselves are proved by the finite alternating sum, with no limit
argument required.

## 6. A Big Census Worked End-to-End

How many of 1..1000 are divisible by 2, 3, or 5? Floors do the level
counts: 500 + 333 + 200 − 166 − 100 − 66 + 33 = 734 (pairwise floors at
d = 6, 10, 15, triple at 30), and the run's complement identity is
exact: 1000 − 734 = 266 equals the brute count of integers free of the
three factors. First such candidates: 1, 7, 11, 13, 17, 19, 23, 29 —
coprime to 30, cyclic residue pattern repeats every 30 with 8 survivors
per window (266 = 8·33 + 2).

## 7. What the Programs Verify

Program 1 matches stars-and-bars closed forms against the brute grid
(all 4 + 3 cases); program 2 carries the upper-bound census, the
derangement counts, and the thousand-case divisibility census with the
floor identity printed digit-identically. Bijection first, formula
second, brute census as the referee in one file.
