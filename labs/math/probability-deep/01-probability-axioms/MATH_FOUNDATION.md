# Probability Axioms — Math Foundation

All figures below were produced by running the snippets in
CODE_DEEP_DIVE.md; every fraction is an exact Python `fractions` result,
pasted from actual output rather than derived by hand.

## 1. One Die, Two Events, Everything Exact
Sample space Ω = {1,...,6}; A = even faces {2,4,6}; B = {1,2,3}.
Observed exactly: P(A) = 1/2, P(B) = 1/2, P(A ∩ B) = P({2}) = 1/6,
P(A ∪ B) = 5/6 by inclusion–exclusion (and by direct set union), and
P(A^c ∩ B^c) = 1/6, which equals 1 − 5/6: De Morgan checked from both
sides on the same numbers.

## 2. Conditioning Rescales the Survivors
To condition on B, delete the faces outside it and divide by P(B) = 1/2,
so each of {1,2,3} doubles to 1/3 and faces 4,5,6 drop to 0. The
conditional weights then sum to 1 (1/3 + 1/3 + 1/3 = 1). Observed
conditionals: P(A | B) = P({2}) / P(B) = (1/6)/(1/2) = 1/3 and
P(B | A) = 1/3 as well — equal here only because P(A) = P(B); the
symmetry of the two conditionals is a coincidence of this sample, not a
rule.

## 3. The Independence Test Fails, Numerically
Independence requires P(A ∩ B) = P(A) P(B). Observed:
P(A) P(B) = 1/4 against P(A ∩ B) = 1/6. Since 1/4 ≠ 1/6 the events are
dependent — meeting an even face raises the chance that the face is at
most 3, because face 2 lives in both sets. The failing product is the
entire diagnostic; no further machinery is needed.

## 4. Law of Total Probability, Executed Over a Partition
Partition C1 = {1,2,3}, C2 = {4,5,6}, each of weight 1/2. Observed exact
conditionals: P(A | C1) = 1/3 (only face 2 qualifies inside C1), P(A | C2) =
2/3 (faces 4 and 6 qualify inside C2). Reassembly:
P(A) = 1/2 · 1/3 + 1/2 · 2/3 = 1/2, matching the direct value P(A) = 1/2.
The bookkeeping recomposes the event from disjoint slices, with zero room
for double-counting.

## 5. Bayes Flips the Direction
After observing A, Bayes prices each partition member at
P(Ci | A) = P(Ci) P(A | Ci) / P(A). Observed:
P(C1 | A) = (1/2 · 1/3)/(1/2) = 1/3. Seeing an even face demotes C1
(credibility 1/2 → 1/3) because C1 contains a single even face while C2
contains two.

## 6. Medical Test — Why Base Rates Dominate
Prior P(D) = 1/100, sensitivity P(+ | D) = 99/100, false positive rate
P(+ | no D) = 1/50. Observed exactly:
P(+) = 297/10000 and P(D | +) = 99/297 = 1/3.
A test that misses only 1 in 100 sick people, administered once, still
leaves most positives healthy: the prior 1/100 is outweighed by 99/50
odds of false alarm across the healthy population. The p-substituting
intuition — sensitivity over (sensitivity plus false positive rate) —
yields 99/101 ≈ 0.98 (observed: 99/101), which is off by a factor near
three; dividing by the true denominator 297/10000 burns the base rate
into the answer.

## 7. Two Coins in Boxes (Bayes, Cleanly)
Box F holds two fair coins; box L holds one fair coin and one
double-headed coin. A box is drawn uniformly, a coin uniformly, and one
flip shows heads. Observed: P(heads) = 1/2·1/2 + 1/2·1 = 3/4, and
P(box L | heads) = (1/2 · 1)/(3/4) = 2/3. The direction of the update
follows the data: only the loaded coin was certain to produce the
observed heads.
