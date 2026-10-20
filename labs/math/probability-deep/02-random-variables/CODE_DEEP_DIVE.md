# Code Deep Dive — Exact Random-Variable Machinery

Three runnable Python programs (stdlib only) holding the lab's table,
moments, and counterexample; each output block is the genuine captured
run.

## 1. The Two-Dice Sum: PMF, Expectation, Two Variances

```python
from fractions import Fraction as F
from collections import Counter

counts = Counter(i + j for i in range(1, 7) for j in range(1, 7))
pmf = {k: F(v, 36) for k, v in sorted(counts.items())}
print("P(2),P(7),P(12):", pmf[2], pmf[7], pmf[12], " total mass:", sum(pmf.values()))

E = sum(F(k) * p for k, p in pmf.items())
EX2 = sum(F(k * k) * p for k, p in pmf.items())
Var = EX2 - E * E
Var2 = sum(((F(k) - E) ** 2) * p for k, p in pmf.items())
print("E[X] =", E, " E[X^2] =", EX2)
print("Var route2 =", Var2, " route1 E[X^2]-E^2 =", Var, " equal:", Var2 == Var)
```

Observed output:

```text
P(2),P(7),P(12): 1/36 1/6 1/36  total mass: 1
E[X] = 7  E[X^2] = 329/6
Var route2 = 35/6  route1 E[X^2]-E^2 = 35/6  equal: True
```

The `total mass: 1` line is the PMF axioms enforced by construction;
`equal: True` certifies the variance identity on this distribution
rather than as a slogan.

## 2. CDF Jumps and Moments of a Three-Point PMF

```python
from fractions import Fraction as F

q = {0: F(1, 4), 1: F(1, 2), 2: F(1, 4)}
print("tiny PMF: F(x<0)=0, F(0) =", q[0], " F(1) =", q[0] + q[1],
      " F(x>=2) =", sum(q.values()))
m = sum(F(k) * v for k, v in q.items())
m2 = sum(F(k * k) * v for k, v in q.items())
print("tiny PMF: E =", m, " Var =", m2 - m * m)
```

Observed output:

```text
tiny PMF: F(x<0)=0, F(0) = 1/4  F(1) = 3/4  F(x>=2) = 1
tiny PMF: E = 1  Var = 1/2
```

Each printed F value is a partial SUM of pmf entries; the last one is
the whole table, i.e., property F → 1 realized at the right end of the
support.

## 3. LOTUS Breaks Nonlinear Substitution — Plus Die-Moment Audit

```python
from fractions import Fraction as F
from collections import Counter

r = {1: F(1, 2), 2: F(1, 2)}
e = sum(F(k) * v for k, v in r.items())
eg = sum(F(1, k) * v for k, v in r.items())
print("X on {1,2}: E[X] =", e, " E[1/X] =", eg, " 1/E[X] =", F(1) / e,
      " unequal:", eg != F(1) / e)

sd = {k: F(1, 6) for k in range(1, 7)}
Es = sum(F(k) * v for k, v in sd.items())
Es2 = sum(F(k * k) * v for k, v in sd.items())
print("single die: E =", Es, " E[X^2] =", Es2, " Var =", Es2 - Es * Es)

EXY = sum(F(k) * F(k) * v for k, v in sd.items())
print("two independent dice: E[XY] =", EXY, " E[X]E[Y] =", Es * Es,
      " Cov =", EXY - Es * Es)

odd = Counter(i + j for i in range(1, 7) for j in range(1, 7) if (i + j) % 2)
tot = sum(odd.values())
print("P(sum odd) =", F(tot, 36), " P(X=7 | odd) =", F(odd[7], tot))
print("P(X<=7) =", F(21, 36))
```

Observed output:

```text
X on {1,2}: E[X] = 3/2  E[1/X] = 3/4  1/E[X] = 2/3  unequal: True
single die: E = 7/2  E[X^2] = 91/6  Var = 35/12
two independent dice: E[XY] = 91/6  E[X]E[Y] = 49/4  Cov = 35/12
P(sum odd) = 1/2  P(X=7 | odd) = 1/3
P(X<=7) = 7/12
```
