# Code Deep Dive — Convergence, Executed

Three runnable Python programs (stdlib only). Captured outputs are the
pasted blocks; the fractions stay exact, the simulations are seeded for
reproducibility.

## 1. The 1/n Variance Clock and the Exact-Bound Pair

```python
from fractions import Fraction as F

var_mean = lambda n: F(1) / (4 * n)
for n in (1, 4, 16, 64, 256):
    print("Bernoulli(1/2): n=%3d  Var(mean) = %s" % (n, var_mean(n)))

n, var = 4, F(1, 16)
exact_half = F(2, 16)  # mean = 0 or mean = 1
print("c=1/2: bound =", var / (F(1, 2) * F(1, 2)), " exact =", exact_half,
      " valid bound:", exact_half <= var / (F(1, 2) * F(1, 2)))
print("c=3/4: bound =", var / (F(3, 4) * F(3, 4)), " exact =",
      F(0) if True else None)
```

Observed output:

```text
Bernoulli(1/2): n=  1  Var(mean) = 1/4
Bernoulli(1/2): n=  4  Var(mean) = 1/16
Bernoulli(1/2): n= 16  Var(mean) = 1/64
Bernoulli(1/2): n= 64  Var(mean) = 1/256
Bernoulli(1/2): n=256  Var(mean) = 1/1024
c=1/2: bound = 1/4  exact = 1/8  valid bound: True
c=3/4: bound = 1/9  exact = 0
```

The empty-event line is deliberate: a bound still holds when its
probability target is 0, which is what makes universal envelopes
usable.

## 2. Seeded Means March Toward 1/2

```python
import random

random.seed(2024)
for nn in (10, 100, 10000, 1000000):
    m = sum(random.random() < 0.5 for _ in range(nn)) / nn
    print("seeded run: n=%7d  mean=%.6f  |dev|=%.6f" % (nn, m, abs(m - 0.5)))
```

Observed output:

```text
seeded run: n=     10  mean=0.600000  |dev|=0.100000
seeded run: n=    100  mean=0.580000  |dev|=0.080000
seeded run: n=  10000  mean=0.494700  |dev|=0.005300
seeded run: n=1000000  mean=0.500447  |dev|=0.000447
```

Rerunning the script reproduces all four lines digit for digit — the
seed is part of the exhibit.

## 3. Heavy Tails Slow the Clock; Bounds vs True Tails

```python
import random
import math

random.seed(99)
xs = [random.choices((1, 2, 3, 10**6), weights=(45, 30, 20, 5))[0]
      for _ in range(200000)]
for i in (199, 1999, 19999, 199999):
    print("heavy tail: first %6d sample mean = %.4f"
          % (i + 1, sum(xs[:i + 1]) / (i + 1)))

print("Markov P(X>=3) <= 1/3; exact P(X>=3) =", math.exp(-3.0))
print("Chebyshev P(|X-1|>=2) <= 1/4; exact =", math.exp(-3.0))
```

Observed output:

```text
heavy tail: first    200 sample mean = 45001.6350
heavy tail: first   2000 sample mean = 45001.6325
heavy tail: first  20000 sample mean = 49151.6488
heavy tail: first 200000 sample mean = 49736.6496
Markov P(X>=3) <= 1/3; exact P(X>=3) = 0.049787068367863944
Chebyshev P(|X-1|>=2) <= 1/4; exact = 0.049787068367863944
```

The prefix means crawl because individual 10^6 jumps move the running
total more than all small draws combined — weight by magnitude, not
frequency.
