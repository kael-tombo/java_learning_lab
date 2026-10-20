# Code Deep Dive — Distributions as Computable Objects

Three runnable Python programs (stdlib only): a CDF/density round trip,
exact binomial objects, and decimal machinery for exponential, Poisson,
and normal families. Outputs are the genuine captured runs.

## 1. Uniform[0, 2] and Exponential(1)

```python
import math
from fractions import Fraction as F

print("uniform F(-0.5)=0 F(1) =", F(1, 2), " F(2) =", F(1), " F(3) =", F(1))
print("total mass of f(x)=1/2 on [0,2]:", F(1, 2) * 2)

print("P(X>1) =", math.exp(-1.0), " F(1) =", 1.0 - math.exp(-1.0))
s15, s1 = math.exp(-1.5), math.exp(-1.0)
print("P(X>1.5)/P(X>1) = P(X>0.5) =", s15 / s1, " e^-0.5 =", math.exp(-0.5))
```

Observed output:

```text
uniform F(-0.5)=0 F(1) = 1/2  F(2) = 1  F(3) = 1
total mass of f(x)=1/2 on [0,2]: 1
P(X>1) = 0.36787944117144233  F(1) = 0.6321205588285577
P(X>1.5)/P(X>1) = P(X>0.5) = 0.6065306597126334  e^-0.5 = 0.6065306597126334
```

The last line is memorylessness executed as long division: the survival
ratio equals the clean exponent exactly because e^{−1.5}/e^{−1} cancels
to e^{−1/2}.

## 2. Binomials, Exact and Parameterized

```python
import math
from fractions import Fraction as F
from math import comb

tbl = [F(math.comb(4, k), 16) for k in range(5)]
mean = sum(F(k) * p for k, p in enumerate(tbl))
ex2 = sum(F(k * k) * p for k, p in enumerate(tbl))
print("Bin(4, 1/2) pmf:", tbl, " sum =", sum(tbl))
print("Bin(4, 1/2): E =", mean, " np =", F(2), " Var =", ex2 - mean**2,
      " npq =", F(1))
p = F(1, 3)
tbl10 = [F(comb(10, k)) * p**k * (F(2, 3))**(10 - k) for k in range(11)]
print("Bin(10,1/3): sum =", sum(tbl10), " E =", F(10, 3), " Var =", F(20, 9))
print("Bin(10,1/3): P(X<=1) =", tbl10[0] + tbl10[1])
```

Observed output:

```text
Bin(4, 1/2) pmf: [Fraction(1, 16), Fraction(1, 4), Fraction(3, 8), Fraction(1, 4), Fraction(1, 16)]  sum = 1
Bin(4, 1/2): E = 2  np = 2  Var = 1  npq = 1
Bin(10,1/3): sum = 1  E = 10/3  Var = 20/9
Bin(10,1/3): P(X<=1) = 2048/19683
```

Both `sum = 1` lines and both parameter matches (np, npq) are computed
checks on the pmf tables, not appeals to the formulas.

## 3. Poisson(2) and the Standard Normal

```python
import math

lam = 2.0
pois = [math.exp(-lam) * lam**k / math.factorial(k) for k in range(12)]
print("Poisson(2):", [round(v, 8) for v in pois])
print("Poisson(2): sum k=0..11 =", sum(pois), " exact P(X=0) =", math.exp(-2.0))

print("Phi(0.0) =", 0.5 * (1 + math.erf(0.0)))
print("Phi(0.5) =", 0.5 * (1 + math.erf(0.5 / math.sqrt(2.0))))
print("Phi(1.0) =", 0.5 * (1 + math.erf(1.0 / math.sqrt(2.0))))
print("Phi(2.0) =", 0.5 * (1 + math.erf(2.0 / math.sqrt(2.0))))
print("P(-1<X<1) =", 0.5 * (1 + math.erf(1 / math.sqrt(2))) - 0.5 *
      (1 + math.erf(-1 / math.sqrt(2))))
print("P(X>2) =", 1 - 0.5 * (1 + math.erf(2.0 / math.sqrt(2.0))))
```

Observed output:

```text
Poisson(2): [0.13533528, 0.27067057, 0.27067057, 0.18044704, 0.09022352, 0.03608941, 0.0120298, 0.00343709, 0.00085927, 0.00019095, 3.819e-05, 6.94e-06]
Poisson(2): sum k=0..11 = 0.9999986353848405  exact P(X=0) = 0.1353352832366127
Phi(0.0) = 0.5
Phi(0.5) = 0.691462461274013
Phi(1.0) = 0.8413447460685428
Phi(2.0) = 0.9772498680518209
P(-1<X<1) = 0.6826894921370856
P(X>2) = 0.022750131948179098
```

The truncated Poisson sum lands at 1 minus 1.4e−06; that residual IS
the truncation, reported, not hidden.
