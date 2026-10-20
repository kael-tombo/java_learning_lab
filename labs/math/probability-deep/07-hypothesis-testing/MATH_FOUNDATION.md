# Hypothesis Testing — Math Foundation

All numbers are run outputs from the exact-arithmetic programs in
CODE_DEEP_DIVE.md (fractions module; enumeration where feasible).

## 1. Price the Rejection Region Exactly
Model: n = 10 fair-coin flips, two-sided region
R = {k <= 1} ∪ {k >= 9}. Observed exact size:
alpha = 11/512 (the run printed both shapes: 11/512 = 22/1024).
Coefficient book: the extremes contribute (1 + 10) + (10 + 1) = 22 of
the 1024 equiprobable sequences. A hypothesis test with alpha ≈ 0.0215
is a machine-engineered false-alarm rate, not a convention imported
from outside the data.

## 2. What the Test Misses — Type II Exactly
True p = 3/10: beta = P(2 <= k <= 8 | p = 3/10) = 1 − P(k <= 1) −
P(k >= 9), executed as the exact fraction 4252739841/5000000000 =
0.8505479682; power = 1 − beta = 0.1494520318. Read that number as a
design budget: a 30% coin survives a 10-flip audit about 85% of the
time. The mirror value at p = 7/10 printed identically — the
reflection symmetry about the null coin is exact, not approximate.

## 3. One-Sided Region Cheaper Tail by Tail
Region {k >= 8} at p = 1/2: observed exact alpha = 7/128
(= 56/1024; coefficients 45 + 10 + 1 at the top three heads-counts).
Comparing with the two-sided 11/512: the one-sided test costs under
three times the false-alarm budget (0.0547 vs 0.0215) while guarding
only one direction.

## 4. Permutation Reality Check, 3 vs 3
Groups A = (1, 2, 3), B = (4, 5, 6); observed difference of means 3.
Enumeration over all C(6,3) = 20 labelings: exactly one achieves a
difference >= 3 (identity), so the one-sided p-value is 1/20 =
0.05; two-sided |d| >= 3 occurs twice → p = 2/20 = 1/10 (both
printed). No normality was assumed anywhere in this paragraph — only
counting.

## 5. Permutation at 4 vs 4 — Money Changes
Separation grows with balanced sizes: for A = (1, 2, 3, 4) vs
B = (5, 6, 7, 8), observed mean difference 4 over C(8,4) = 70
labelings, only the two extremes (identity and its full swap) reach
|d| >= 4. Two-sided exact p = 2/70 = 1/35 ≈ 0.0286 (run line).
Doubling group sizes multiplied the denominator 3.5× and left the
extreme count at two: exact small-sample inference in one jump.

## 6. Cross-Check Between Sections
The binomial region's arithmetic and the permutation counts
independently produce p-values near 0.02–0.05 on different
mechanisms; seeing 1/20, 1/10, 7/128, 11/512, 1/35 all reduce to
coefficient counting keeps the whole lab auditable by hand when the
power goes off — each figure has a term-by-term breakdown above.
