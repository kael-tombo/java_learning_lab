# Code Deep Dive — Bayesian Bookkeeping, Executed

Three runnable Python programs (stdlib only). Output blocks are
captured runs; the conjugate updating stays in exact fractions.

## 1. Sequential vs Batch — One Invariance, One Engine

```python
import math
from fractions import Fraction as F

a0, b0 = F(2), F(2)                     # Prior Beta(2,2)
data = [1, 1, 1, 1, 1, 1, 1, 0, 0, 0]   # 7 heads, 3 tails
a_s, b_s = a0, b0
for x in data:
    a_s, b_s = a_s + x, b_s + (1 - x)
a_b, b_b = a0 + 7, b0 + 3
print("sequential posterior: Beta(%s, %s)" % (a_s, b_s))
print("batch posterior:      Beta(%s, %s)" % (a_b, b_b),
      " identical:", (a_s, b_s) == (a_b, b_b))
mean = a_s / (a_s + b_s)
mode = (a_s - 1) / (a_s + b_s - 2)
print("posterior mean =", mean, " (%.6f)" % float(mean),
      " posterior mode =", mode)
print("prior mean =", a0 / (a0 + b0), " prior mode =",
      (a0 - 1) / (a0 + b0 - 2))
print("posterior predictive P(next head) =", mean, " plug-in 7/10 =",
      F(7, 10), " gap =", F(7, 10) - mean)
print("normalization: B(9,5) via factorial identity 8!*4!/13! =",
      F(math.factorial(8) * math.factorial(4), math.factorial(13)))
```

Observed output:

```text
sequential posterior: Beta(9, 5)
batch posterior:      Beta(9, 5)  identical: True
posterior mean = 9/14  (0.642857)  posterior mode = 2/3
prior mean = 1/2  prior mode = 1/2
posterior predictive P(next head) = 9/14  plug-in 7/10 = 7/10  gap = 2/35
normalization: B(9,5) via factorial identity 8!*4!/13! = 1/6435
```

One loop is the entire Bayesian machinery: counting evidence into the
two parameters.

## 2. Three Priors Hear the Same Data Differently

```python
from fractions import Fraction as F

a2, b2 = F(1) + 0, F(1) + 0                # flat prior Beta(1,1)
for x in [0, 0, 0]:
    a2, b2 = a2 + x, b2 + (1 - x)
print("flat prior + TTT -> Beta(%s, %s): mean =" % (a2, b2), a2 / (a2 + b2))

aj, bj = F(1, 2), F(1, 2)                  # Jeffreys Beta(1/2,1/2)
for x in [1, 1, 1, 0]:
    aj, bj = aj + x, bj + (1 - x)
print("Jeffreys + H,H,H,T -> Beta(%s, %s): mean =" % (aj, bj), aj / (aj + bj))

a3, b3 = F(2), F(2)                        # Beta(2,2)
for x in [1, 1, 0]:
    a3, b3 = a3 + x, b3 + (1 - x)
print("data HHT with Beta(2,2) -> Beta(%s, %s): mean =" % (a3, b3),
      a3 / (a3 + b3), " predictive =", a3 / (a3 + b3))
print("predictive equals posterior mean here: yes, both a/(a+b)")
```

Observed output:

```text
flat prior + TTT -> Beta(1, 4): mean = 1/5
Jeffreys + H,H,H,T -> Beta(7/2, 3/2): mean = 7/10
data HHT with Beta(2,2) -> Beta(4, 3): mean = 4/7  predictive = 4/7
predictive equals posterior mean here: yes, both a/(a+b)
```

(For Bernoulli trials the posterior predictive IS the posterior mean:
the integration collapses to one fraction — no extra formula to
remember.)

## 3. What the Update Never Does

The engine above never integrates a likelihood, requires no sampler,
and never touches floating point until the final decimal display
(%.6f on 9/14 for readability). Conjugacy is the arithmetic
simplification: everything before that is rationals.
