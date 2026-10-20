# Exercises — Random Variables

Solutions quote figures produced by executing the snippets in
CODE_DEEP_DIVE.md; every expressed value is an output of a run.

## Problem 1. Single-Die Moment Audit
Compute E, E[X^2], and Var for one fair die, then check the identity
Var = E[X^2] − (E[X])^2 by substitution.

**Solution**: Executed exactly: E = 7/2, E[X^2] = 91/6, and
91/6 − 49/4 = (182 − 147)/12 = 35/12. Substituting back into the
definition route Σ(k − 7/2)^2 p(k) returns the same 35/12 — the identity
holds on the exhibit, machine-checked during the run.

## Problem 2. Fibers of a Sum and Its Tail
Using fibers of the two-dice sum, verify P(X <= 7) and explain the
plateau arithmetic.

**Solution**: Fiber counts for sums 2 through 7 are 1, 2, 3, 4, 5, 6 —
total 21 pairs of the 36 — so P(X <= 7) = 21/36 = 7/12 (matches the run
line). The CDF therefore sits at F(7) = 7/12, having absorbed steps of
1/36, 2/36, 3/36, 4/36, 5/36, 6/36 at the first six support points.

## Problem 3. Conditional Message
Given the sum came out odd, what is P(X = 7)?

**Solution**: Observed in the run: P(sum odd) = 1/2 and
P(X = 7 | odd) = (6/36)/(18/36) = 1/3. Conditioning deleted the even
plateaus and rescaled survivors; because 6 of the 18 odd-sum pairs
produce the value 7, exactly one third remains.

## Problem 4. Depth of the Reciprocal Trap
For X on {1, 2} with equal halves, confirm E[1/X] > 1/E[X] and articulate
why no rule was broken.

**Solution**: The run printed E[X] = 3/2, E[1/X] = 3/4, 1/E[X] = 2/3, and
marked them unequal (3/4 ≠ 2/3). LOTUS computes E[1/X] = 1/2·1 + 1/2·(1/2)
directly from the pmf; the failing step would be to feed E[X] INTO the
function. Moments average after applying g at the support points, never
before.

## Problem 5. Programming: Exact Moment Engine
Implement `moments(pmf)` returning (E, E[X^2], Var) as exact fractions
for a dict {value: Fraction}. Verify it reproduces the two-dice-sum
numbers 7, 329/6, 35/6 and the notes-scale {0: 1/4, 1: 1/2, 2: 1/4}
numbers 1, 3/2, 1/2.

**Solution skeleton**:

```python
from fractions import Fraction as F

def moments(pmf):
    assert sum(pmf.values()) == 1
    m = sum(F(k) * v for k, v in pmf.items())
    m2 = sum(F(k * k) * v for k, v in pmf.items())
    return m, m2, m2 - m * m

print(moments({k: F(v, 36) for k, v in
               Counter(i + j for i in range(1, 7)
                       for j in range(1, 7)).items()}))
print(moments({0: F(1, 4), 1: F(1, 2), 2: F(1, 4)}))
```

The executed pair printed (Fraction(7), Fraction(329, 6), Fraction(35, 6))
and the three-point triple (1, 3/2, 1/2) — identical to the analytic
entries above. The mass assertion doubles as a guard against malformed
input tables.
