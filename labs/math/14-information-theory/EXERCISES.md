# Exercises — Information Theory, Worked

Five problems; numbers were produced by runs before the prose.

## Problem 1. Entropy Contributions, Cell by Cell

For p = (1/2, 1/4, 1/8, 1/8) list each pᵢ·(−log2 pᵢ) and sum them.

**Solution**: The run printed the contribution pairs
('1/2', '1/2'), ('1/4', '1/2'), ('1/8', '3/8'), ('1/8', '3/8');
the sum is 1/2 + 1/2 + 3/8 + 3/8 = 7/4 = 1.75 bits, exact in
fractions because every mass is a power of two.

## Problem 2. One Coin Tilted Off Dyadic Ground

Compute H(3/4, 1/4) and describe why it is no longer a clean fraction.

**Solution**: The float loop printed 0.8112781244591328 bits
(displayed as 0.811278 in convenience contexts). The exact value is
−(3/4)·log2(3/4) − (1/4)·log2(1/4): the mass 3/4 forces a term with
log2 3, which is irrational — H is irrational precisely when some
mass sits off the dyadic lattice. Contrast: 1.75 was exact.

## Problem 3. Huffman on a Fresh Alphabet, With a Gap

Build the Huffman code for weights (3/8, 3/8, 1/4) and compare the
average length against entropy.

**Solution**: The heap run merged 1/4 with a 3/8 (→ 5/8), then 5/8
with the other 3/8. Printed lengths [2, 1, 2] — one of the equally
heavy symbols got the short slot, a legitimate tie outcome — giving
average 3/8·2 + 3/8·1 + 1/4·2 = 13/8 = 1.625 bits against
H ≈ 1.561278; the printed gap was 0.06372187554086706. Huffman
cannot reach H here because no mass profile is fully binary-fitting.

## Problem 4. Direction-Dependent Prices in KL

For P = (1/2, 1/4, 1/8, 1/8) and Q = (1/4, 1/8, 1/2, 1/8), compute
KL(P||Q) and KL(Q||P) and prove asymmetry with exact values.

**Solution**: Ratios pᵢ/qᵢ are all powers of two, so the run
computed KL(P||Q) = 1/2·1 + 1/4·1 + 1/8·(−2) + 1/8·0 = 1/2 and
KL(Q||P) = 1/4·(−1) + 1/8·(−1) + 1/2·2 + 1/8·0 = 5/8, with the
asymmetry line `1/2 != 5/8 -> True`. Both are positive (KL is never
negative), and KL(P||P) printed 0.0 — zero exactly on equality, not
"approximately" zero.

## Problem 5. Programming: The XOR Independence Exhibit

Let X and Y be independent fair bits and Z = X ⊕ Y. Compute
MI(X, Y) and MI(X, Z) from the joint tables and report both.

**Solution**: The run built the (X, Y) table as four cells of 1/4
each and the (X, Z) table — Z = X ⊕ Y hits each pair once — also as
four cells of 1/4. Printed verdicts: H(X) = H(Y) = H(Z) = 1.0,
H(X,Y) = H(X,Z) = 2.0, hence MI(X, Y) = 1 + 1 − 2 = 0.0 EXACT and
MI(X, Z) = 1 + 1 − 2 = 0.0 EXACT. The lesson: Z is a function of X
and Y and carries a full bit of novelty about neither — XOR
correlation-annihilation is exact, not approximate, and any nonzero
"MI" from a buggy summation would be an artifact.
