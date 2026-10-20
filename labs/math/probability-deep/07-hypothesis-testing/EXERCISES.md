# Exercises — Hypothesis Testing

Worked solutions; each quoted value either appears in the captured
outputs of CODE_DEEP_DIVE.md or follows from two such values by exact
fraction arithmetic.

## Problem 1. Region Price Tag
For n = 10 flips under H0: p = 1/2, price the region
R = {k <= 1} ∪ {k >= 9} term by term and confirm the machine fraction.

**Solution**: Terms: head-counts 0 and 10 (1 sequence each), 1 and 9
(10 each): total 22 of 1024 equiprobable sequences, so
alpha = 22/1024 = 11/512 — matching the run's double-printed pair.
Decimal: about 0.0215.

## Problem 2. Mirror Symmetry of beta
At true p = 3/10 the run reported beta = 4252739841/5000000000.
Predict the beta at p = 7/10 before checking, then check.

**Solution**: The region is symmetric under head-count flips (k →
10 − k maps {k <= 1} ∪ {k >= 9} onto itself), and p → 1 − p mirrors
the binomial pmf the same way. Prediction: identical. Run line:
`beta at p=7/10 = 4252739841/5000000000  equal to 3/10 case: True`.

## Problem 3. One-Sided Arithmetic
Price the one-sided region {k >= 8} at n = 10, p = 1/2 and compare to
the two-sided region's 11/512.

**Solution**: Coefficients at 8, 9, 10: 45 + 10 + 1 = 56; alpha =
56/1024 = 7/128 ≈ 0.0547 (run value). Ratio to two-sided: (7/128) ÷
(11/512) = (28/512) ÷ (11/512) = 28/11 ≈ 2.55. Guarding one tail costs
about 2.5 false-alarm budgets; that is the honest cost line between
sided designs.

## Problem 4. Permutation Exactness With Four-Point Groups
For A = (1, 2, 3, 4), B = (5, 6, 7, 8), enumerate conceptually and
give both one-sided and two-sided exact p-values for the observed mean
difference of 4.

**Solution**: Label space is C(8,4) = 70. The observed arrangement has
meanA − meanB = 2.5 − 6.5 = −4; a labeling achieves a difference of
magnitude >= 4 ONLY at the two fully separated labelings (identity and
its complement at +4). Recorded from the run: two-sided count 2 →
p = 2/70 = 1/35 ≈ 0.0286 (printed line); the same enumeration gives
one-sided count 1 → p = 1/70.

## Problem 5. Programming: Exact Tail Function
Implement `btail(n, k, p)` returning the exact two-sided binomial
p-value by summing pmf terms at distance >= |k − n/2| from the center,
using fractions; run it for n = 10, k = 9, p = 1/2 and compare with
the region-size fraction from Problem 1.

**Solution skeleton**:

```python
from fractions import Fraction as F
from math import comb

def btail(n, k, p):
    center = abs(k - n / 2)
    terms = [F(comb(n, j)) * p**j * (1 - p)**(n - j)
             for j in range(n + 1) if abs(j - n / 2) >= center]
    return sum(terms)

print(btail(10, 9, F(1, 2)))
```

Executed: 11/512 — identical to Problem 1's region price, as it must
be since the function is summing the same extreme sequences.
