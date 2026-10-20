# Code Deep Dive — Tests You Can Reproduce Digit-for-Digit

Three runnable Python programs (stdlib only). Output blocks are the
captured runs; the binomial work is fractionally exact and the
permutation work is exhaustive.

## 1. Exact Binomial Engine: Region Size, Type II, One-Sided

```python
from fractions import Fraction as F
from math import comb

def binpmf(n, k, p):
    return F(comb(n, k)) * p**k * (1 - p)**(n - k)

n, p0 = 10, F(1, 2)
print("size of region {k<=1 or k>=9} at p=1/2:", sum(binpmf(10, k, p0)
      for k in list(range(2)) + list(range(9, 11))),
      " = 22/1024 =", F(22, 1024))

p1 = F(3, 10)
beta = 1 - sum(binpmf(10, k, p1) for k in [0, 1, 9, 10])
print("power at p=3/10 = 1 - beta; beta =", beta)
print("beta decimal:", float(beta), " power decimal:", float(1 - beta))
p2 = F(7, 10)
beta2 = 1 - sum(binpmf(10, k, p2) for k in [0, 1, 9, 10])
print("beta at p=7/10 =", beta2, " equal to 3/10 case:", beta2 == beta)

region = sum(binpmf(10, k, p0) for k in (8, 9, 10))
print("one-sided alpha for {k>=8} =", region, " =", F(56, 1024))
```

Observed output:

```text
size of region {k<=1 or k>=9} at p=1/2: 11/512  = 22/1024 = 11/512
power at p=3/10 = 1 - beta; beta = 4252739841/5000000000
beta decimal: 0.8505479682  power decimal: 0.1494520318
beta at p=7/10 = 4252739841/5000000000  equal to 3/10 case: True
one-sided alpha for {k>=8} = 7/128  = 7/128
```

The `equal ... True` line certifies the p = 1/2 mirror symmetry of
beta from within the same engine.

## 2. Exact Permutation Test, 3 vs 3

```python
from fractions import Fraction as F
import itertools

vals = [1, 2, 3, 4, 5, 6]
mean = lambda xs: F(sum(xs), len(xs))
diffs = []
for idx in itertools.combinations(range(6), 3):
    a = [vals[i] for i in idx]
    b = [vals[i] for i in range(6) if i not in idx]
    diffs.append(mean(a) - mean(b))
print("permutation: arrangements =", len(diffs))
print("one-sided count d>=3 =", sum(1 for d in diffs if d >= 3),
      " p =", F(sum(1 for d in diffs if d >= 3), len(diffs)))
print("two-sided count |d|>=3 =", sum(1 for d in diffs if abs(d) >= 3),
      " p =", F(sum(1 for d in diffs if abs(d) >= 3), len(diffs)))
```

Observed output:

```text
permutation: arrangements = 20
one-sided count d>=3 = 1  p = 1/20
two-sided count |d|>=3 = 2  p = 1/10
```

Every label is visited; the p-values are label counts over 20, exact.

## 3. Permutation at 4 vs 4

```python
from fractions import Fraction as F
import itertools

vals4 = [1, 2, 3, 4, 5, 6, 7, 8]
mean = lambda xs: F(sum(xs), len(xs))
diffs4 = []
for idx in itertools.combinations(range(8), 4):
    a = [vals4[i] for i in idx]
    b = [vals4[i] for i in range(8) if i not in idx]
    diffs4.append(mean(a) - mean(b))
print("4v4: arrangements =", len(diffs4), " two-sided |d|>=4 count =",
      sum(1 for d in diffs4 if abs(d) >= 4),
      " p =", F(sum(1 for d in diffs4 if abs(d) >= 4), len(diffs4)))
```

Observed output:

```text
4v4: arrangements = 70  two-sided |d|>=4 count = 2  p = 1/35
```

Two extremes out of 70: denser samples buy smaller exact p-values
without any parametric machinery entering the door.
