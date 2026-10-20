# Information Theory — Flashcards, Run-Backed

Twelve cards; numbers were printed by captured runs or derived in
exact fractions that the runs verified.

### Card I1
**Q:** Entropy of (1/2, 1/4, 1/8, 1/8), and why the sum stays a fraction.
**A:** 7/4 bits. Every −log2 pᵢ is an integer (1, 2, 3, 3), so
H = 1/2 + 1/2 + 3/8 + 3/8 exactly; the float loop agreed bit-for-bit
(`equal: True`).

### Card I2
**Q:** The cap on four-symbol entropy and the near-miss below it.
**A:** H ≤ log2 4 = 2 (uniform), printed `exceeds 7/4: True`. The
(2/3, 1/3) pair scores log2 3 − 2/3 ≈ 0.9182958340544896 —
irrational because of log2 3.

### Card I3
**Q:** Huffman's exact verdicts on the two run alphabets.
**A:** (1/2, 1/4, 1/8, 1/8) → lengths [1, 2, 3, 3], avg 7/4, gap 0.
(2/5, 1/5, 1/5, 1/10, 1/10) → lengths [2, 2, 2, 3, 3], avg 11/5 = 2.2
vs H ≈ 2.121928, gap 0.07807190511263773.

### Card I4
**Q:** What did Kraft's inequality audit print for both codes?
**A:** Exactly 1 both times — the full-tree condition. A partial
tree (Kraft < 1) would mean wasted codeword slots; Kraft > 1 is
impossible for any prefix code.

### Card I5
**Q:** The exact KL pair from the swapped dyadic distributions.
**A:** KL(P||Q) = 1/2, KL(Q||P) = 5/8 for P = (1/2, 1/4, 1/8, 1/8),
Q = (1/4, 1/8, 1/2, 1/8). Computed mass-times-integer-exponent, no
logarithms touched: 1/2 + 1/4 − 1/4 + 0 versus −1/4 − 1/8 + 1 + 0.

### Card I6
**Q:** KL's two structural facts the run asserted.
**A:** Strictly positive both directions (`True and True`) and zero
if and only if the distributions coincide (KL(P||P) printed 0.0).
No dyadic shortcut's absence — positivity holds universally.

### Card I7
**Q:** The float KL pair that broke symmetry again.
**A:** P = (1/2, 1/4, 1/4) vs R = (3/4, 1/8, 1/8): 0.188722 one way,
0.207519 the other. Close, unequal — a trap for anyone who assumes
symmetry from similar magnitudes.

### Card I8
**Q:** The joint table that defined the MI exhibit and its marginals.
**A:** p(0,0) = 1/2, p(0,1) = 0, p(1,0) = 1/4, p(1,1) = 1/4; marginals
pX = (1/2, 1/2), pY = (3/4, 1/4). H(X) printed 1.0 exactly, H(Y)
0.811278, H(X,Y) 3/2.

### Card I9
**Q:** Two independent routes to the same MI, and the value.
**A:** H(X) + H(Y) − H(X,Y) = 0.311278 AND the direct double sum
0.311278 — printed `equal: True` at 1e−12 tolerance. Two different
summation paths agreeing is the audit that matters.

### Card I10
**Q:** The chain-rule piece inside the MI exhibit.
**A:** H(Y|X) = H(X,Y) − H(X) = 3/2 − 1 = 1/2 exactly (half the time
Y is a fixed echo of X, half the time a fresh fair bit), and
MI = H(Y) − H(Y|X) = 0.811278 − 0.5 = 0.311278.

### Card I11
**Q:** XOR's exact spoiler outcome from the exercises run.
**A:** With X, Y independent fair bits and Z = X ⊕ Y, both
MI(X, Y) and MI(X, Z) computed EXACTLY 0 — each joint table is four
1/4 cells. Correlation is destroyed, though Z is a function of X,Y.

### Card I12
**Q:** Why is "bits" load-bearing in this lab?
**A:** Every logarithm is base 2. Switching to nats multiplies all
entropies by ln 2 ≈ 0.6931 and makes Kraft's Σ2^(−ℓ) bookkeeping
incoherent; the base is part of each definition, not a switch to
flip mid-computation.
