# Set Theory — Math Foundation

Every figure below is pasted from the captured runs of
CODE_DEEP_DIVE.md or is one exact step further from a printed value.

## 1. De Morgan, Exhausted Over a Universe

Over U = {1,2,3} the lab checks all subset pairs: 2³ = 8 subsets, 8² =
64 pairs. Observed: De Morgan union failures 0, intersection failures
0. Witness pair A = {1,2}, B = {2,3}: (A∪B)ᶜ = ∅ and Aᶜ∩Bᶜ = ∅ — U is
covered by the two sets, so only the empty set survives both complements.
The check is exhaustive at |U| = 3, so the law is proven for that
universe, not merely sampled.

## 2. Inclusion–Exclusion Census, Both Sizes

A = {1,2,3,4}, B = {3,4,5}, C = {4,5,6}; the three pairwise overlaps
are A∩B = {3,4}, A∩C = {4}, B∩C = {4,5}, and the triple is A∩B∩C = {4}.
Observed: |A∪B∪C| = 6 and the six-term sum
4 + 5 + 3 − 1 − 2 − 2 + 1 = 6 — the pair runs agree to the digit. The
element 4 appears once in each pair-term (3 penalties) and once in the
triple (1 refund), which is the net bookkeeping of belonging everywhere.

## 3. Power-Set Size and the Bit Bijection

Observed values of |P(S)|: 1, 2, 4, 8, 16, 1024 for n = 0, 1, 2, 3, 4,
10 — exactly 2ⁿ at every step. For S = {1,2,3} the run lists all
subsets (8 of them) and their membership bit strings 000 through 111,
then decodes each to its integer and recovers every subset on
round-trip (run: identity True on all 8). The decoded integers came out
a permutation of 0..7, so the run exhibits P(S) of size 8 = 2³ and a
two-sided bijection, both machine-verified.

## 4. Pairing Function, Valued

Cantor pairing π(i,j) = (i+j)(i+j+1)/2 + j. Observed: π(0,0) = 0,
π(1,0) = 1, π(0,1) = 2, π(2,0) = 3, π(1,1) = 4, π(0,2) = 5, π(3,0) = 6,
π(2,1) = 7, π(1,2) = 8, π(0,3) = 9 — the first ten outputs walk the
diagonals, each diagonal t = i+j contributing t+1 fresh pairs. The
shell i+j ≤ 6 therefore holds 28 = 1+2+⋯+7 pairs. Injectivity is
structural: t is a strictly increasing function of i+j, and j breaks
ties inside a diagonal, so (i,j) is recoverable from π.

## 5. Rationals After Lowest-Term Filtering

Numerator ≤ 3, denominator ≤ 4, gcd(n,d) = 1 gives exactly 9 fractions:
1/1, 1/2, 1/3, 1/4, 2/1, 2/3, 3/1, 3/2, 3/4 (run-verified list). Cases
2/2 and 2/4 are excluded by the gcd filter because 2/2 = 1/1 and
2/4 = 1/2 already sit in the list — filtering reduced pairs is what
turns the naïve double-count into an honest enumeration of Q⁺.

## 6. The Anti-Diagonal Refutes Any List

Handed the 8-row list 00000000, 00100000, 01000000, 01100000,
10000000, 10100000, 11000000, 11100000, the machine built d = 11111111
and found it absent from the claimed list, with d[i] ≠ sᵢ[i] confirmed
at all 8 diagonal positions. The construction is list-universal:
whatever rows appear, position i is read from row i alone. This finite
mirror is the entire proof structure; the infinite version just never
runs out of positions to disagree at.

## 7. Finite Jump vs Infinite Strata

The doubling 2ⁿ is exact on finite witnesses (8 subsets for n = 3,
1024 for n = 10); at infinity it breaks the ceiling — P(N) cannot line
up with N, by the diagonal argument above, so |P(N)| = 2^ℵ₀ > ℵ₀.
Schröder–Bernstein closes the sandwich for countable products:
|N×N| = ℵ₀ via pairing, and Q ⊆ N×N (reduced pairs) with N ⊆ Q (n ↦ n),
both injections, hence |Q| = ℵ₀.
