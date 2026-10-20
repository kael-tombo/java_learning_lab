# Set Theory — Theory

## 1. Sets as Pure Constructions

A set has only membership: x ∈ x is banned (foundation), extensionality
says A = B iff they share members, and everything else — pairs, unions,
products, power sets — is built by construction schemata. From the empty
set ∅ alone: 0 := ∅, 1 := {∅}, 2 := {∅,{∅}}, and n+1 := n ∪ {n}. This
is not decoration; it realizes every natural number as a set with n
elements' worth of predecessors, so arithmetic becomes a consequence of
membership alone.

## 2. Algebra of Operations, Machine-Checked

Complement is relative: Aᶜ = U − A. Idempotence A∪A = A, commutativity,
associativity, absorption A∪(A∩B) = A, distributivity, and both De
Morgan laws (A∪B)ᶜ = Aᶜ∩Bᶜ, (A∩B)ᶜ = Aᶜ∪Bᶜ. The lab enumerates all
64 pairs of subsets of a 3-element universe and counts zero failures
for either De Morgan law. The witness pair A = {1,2}, B = {2,3} reads
(A∪B)ᶜ = ∅ on both sides, since everything lies in A or in B. Exhaustion
over |U| = 3 is a proof of the law for that universe — a finite fact
no inspection shortcut can replace.

## 3. Counting Sets: Inclusion–Exclusion

|A∪B| = |A| + |B| − |A∩B|: membership paid twice deserves one bill.
Three-set census (run-checked): |A∪B∪C| for A = {1,2,3,4},
B = {3,4,5}, C = {4,5,6} equals 6, and the six-term formula
4+5+3 −1−2−2 +1 collapses to the same 6. The lampshade is the triple
intersection 4 counted three times, removed twice, restored once —
the odd level reappears, the even level vanishes.

## 4. Power Set Cardinality

|P(S)| = 2ⁿ for |S| = n: each of n elements is in or out, so membership
vectors in {0,1}ⁿ classify subsets. Run numerics: n = 0,1,2,3,4,10 give
1, 2, 4, 8, 16, 1024. The finite bijection is concrete: subsets of
{1,2,3} map to integers 0..7 via the read-ordered bit string, and the
run showed the decoded list is a permutation of 0..7 — map and inverse
both verified, not asserted. Consequently |P(S)| > |S| always in the
finite world (8 > 3, 1024 > 10).

## 5. Countability: Hiding Nothing in the Enumeration

A set is countable when a surjection N → S exists. Pairs: N××N is
countable via the Cantor pairing π(i,j) = (i+j)(i+j+1)/2 + j, whose run
values are π(0,0) = 0, π(1,0) = 1, π(0,1) = 2, π(2,0) = 3, π(1,1) = 4,
π(0,2) = 5, π(3,0) = 6, π(2,1) = 7 — diagonal anti-walks, and the
(i+j) ≤ 6 shell holds 28 = 1+2+⋯+7 pairs. Rationals: filtering pairs by
lowest terms is the trick — gcd(n,d) = 1 kills duplicates — so the
positive rationals with numerator ≤ 3, denominator ≤ 4 number exactly
9: 1/1, 1/2, 1/3, 1/4, 2/1, 2/3, 3/1, 3/2, 3/4.

## 6. Cantor Diagonalization, Done Properly

Claim: no surjection N → {0,1}^∞ exists. Suppose f lists binary
sequences s₀, s₁, .... Build d by d[i] := 1 − sᵢ[i]. Then d differs
from sᵢ at position i for every i, so d ∉ ran(f): contradiction. The
finite mirror executed: on the 8-row list 00000000, 00100000, 01000000,
01100000, 10000000, 10100000, 11000000, 11100000 the machine prints the
anti-diagonal 11111111, absent from the list, differing from row i at
column i for all 8 rows. The subtlety carried by "done properly":
d[i] is computed ONLY from row i's own i-th entry, so no row can dodge.

## 7. What It Means: Strata of Infinity

|N| = ℵ₀ and |{0,1}^∞| = 2^ℵ₀ sit in different strata: the run does not
list reals, but the same doubling operator gives |P(S)| = 2^|S| on
finite witness sizes and jumps in cardinality as soon as the set is
infinite: P(N) ≅ binary sequences ≅ R. Schroeder-Bernstein (injections
both ways imply a bijection) then licenses |Q × Q| = ℵ₀ without
hand-waving — Q injects into N×N as reduced pairs; N injects into Q via
n ↦ n/1.
