# Code Deep Dive — Exact Probability Engineering

Three runnable Python programs (stdlib only) that carry the lab's
numbers; each output block is the real captured run, and fractions stay
exact end to end.

## 1. Axioms, Unions, and Conditionals in Rational Arithmetic

```python
from fractions import Fraction as F

omega = {1, 2, 3, 4, 5, 6}
A, B = {2, 4, 6}, {1, 2, 3}          # evens, and faces at most three

def P(S):
    return F(len(S), len(omega))     # uniform model: counting

print("P(A) =", P(A), " P(B) =", P(B), " P(A&B) =", P(A & B))
u = P(A) + P(B) - P(A & B)
print("inclusion-exclusion P(A|B) =", u, " direct =", P(A | B))
print("De Morgan: 1 - P(A|B) =", F(1) - u, " P(A^c & B^c) =", P(omega - (A | B)))
print("P(A|B) =", P(A & B) / P(B), " P(B|A) =", P(A & B) / P(A))
print("P(A)*P(B) =", P(A) * P(B), " equals P(A&B):", P(A) * P(B) == P(A & B))

C1, C2 = {1, 2, 3}, {4, 5, 6}
def AP(C):
    return P(A & C) / P(C) if C & A else F(0)
tot = P(C1) * AP(C1) + P(C2) * AP(C2)
print("total probability: P(A|C1) =", AP(C1), " P(A|C2) =", AP(C2),
      " sum =", tot, " direct P(A) =", P(A), " match:", tot == P(A))
print("Bayes: P(C1|A) =", AP(C1) * P(C1) / P(A))
```

Observed output:

```text
P(A) = 1/2  P(B) = 1/2  P(A&B) = 1/6
inclusion-exclusion P(A|B) = 5/6  direct = 5/6
De Morgan: 1 - P(A|B) = 1/6  P(A^c & B^c) = 1/6
P(A|B) = 1/3  P(B|A) = 1/3
P(A)*P(B) = 1/4  equals P(A&B): False
total probability: P(A|C1) = 1/3  P(A|C2) = 2/3  sum = 1/2  direct P(A) = 1/2  match: True
Bayes: P(C1|A) = 1/3
```

The test "equals P(A&B): False" is the dependence verdict from MATH_FOUNDATION.md,
now machine-checked; "match: True" certifies the reassembly.

## 2. Bayes With Counts: Test and Two-Boxes

```python
from fractions import Fraction as F

D = F(1, 100)        # disease prior
sens = F(99, 100)    # P(+|D)
spec = F(49, 50)     # P(-|no D), FPR = 1/50
pos = D * sens + (1 - D) * (1 - spec)
post = D * sens / pos
naive = sens / (sens + (1 - spec))
print("medical: P(+) =", pos, " P(D|+) =", post, " naive(no prior) =", naive)

BoxF, BoxB = F(1, 2), F(1, 2)
pHead = BoxF * F(1, 2) + BoxB * F(1)          # B holds 1 fair + 1 double-headed
print("boxes: P(head) =", pHead, " P(loaded box | head) =", BoxB * F(1) / pHead)
```

Observed output:

```text
medical: P(+) = 297/10000  P(D|+) = 1/3  naive(no prior) = 99/101
boxes: P(head) = 3/4  P(loaded box | head) = 2/3
```

Note the total-probability denominator `pos` being built before the
division: Bayes is one line once the partition work is done.

## 3. Frequencies Approach the Exact Values (seeded)

```python
import random
from fractions import Fraction as F

random.seed(12345)
n = 120000
A, B = {2, 4, 6}, {1, 2, 3}
hits_union = sum(1 for _ in range(n) if random.randrange(1, 7) in (A | B))
hits_even = sum(1 for _ in range(n) if random.randrange(1, 7) in A)
print("simulation n=%d: freq(exact union) = %.6f vs %.6f ;"
      " freq(even) = %.6f vs %.6f"
      % (n, hits_union / n, float(F(5, 6)), hits_even / n, float(F(1, 2))))
```

Observed output:

```text
simulation n=120000: freq(exact union) = 0.833467 vs 0.833333 ; freq(even) = 0.498600 vs 0.500000
```

Agreement to about three decimals at n = 120000 is what the axioms
promise about long-run behavior; the exact rationals remain the
reference the error shrinks toward.
