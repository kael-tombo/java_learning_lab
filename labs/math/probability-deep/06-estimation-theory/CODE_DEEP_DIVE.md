# Code Deep Dive — Estimators You Can Reproduce

Three runnable Python programs (stdlib only). Output blocks are
captured runs; fractions stay exact where the model is discrete.

## 1. Two Losses Argue Over One Sample

```python
from fractions import Fraction as F

data = [F(1), F(2), F(4)]
mean = sum(data) / 3
med = sorted(data)[1]
print("sample:", [str(x) for x in data], " mean =", mean, " median =", med)

risks = {}
for i in range(0, 49):
    a = F(i, 12)  # grid 0, 1/12, ..., 4
    risks[a] = sum((x - a) ** 2 for x in data) / 3
best = min(risks, key=risks.get)
print("squared-loss argmin over grid =", best, " min risk =", risks[best],
      " risk at 9/4 =", risks[F(9, 4)], " risk at 29/12 =", risks[F(29, 12)])
abs_risk = lambda a: sum(abs(x - a) for x in data) / 3
print("abs risk at median 2 =", abs_risk(med), " at mean 7/3 =",
      abs_risk(mean))
```

Observed output:

```text
sample: ['1', '2', '4']  mean = 7/3  median = 2
squared-loss argmin over grid = 7/3  min risk = 14/9  risk at 9/4 = 25/16  risk at 29/12 = 25/16
abs risk at median 2 = 1  at mean 7/3 = 10/9
```

The symmetric 25/16 flanks prove the middle is the breaker; the
absolute-loss column prices robustness at exactly 10/9 − 1 = 1/9.

## 2. Bernoulli Proportion: MLE and Its Moments

```python
from fractions import Fraction as F

s, n = 7, 10
phat = F(s, n)
print("Bernoulli MLE p_hat =", phat, " bias at p=1/2 :", 0)
print("true p=1/2: Var(p_hat) = pq/n =", F(1, 4) / n, " MSE = Var + bias^2 =",
      F(1, 4) / n)
lam_data = [F(1), F(1), F(3), F(4), F(1)]
print("Poisson data sum/n =", sum(lam_data) / len(lam_data))
print("Poisson d log L: sample mean IS the MLE; mean =", F(10, 5))
```

Observed output:

```text
Bernoulli MLE p_hat = 7/10  bias at p=1/2 : 0
true p=1/2: Var(p_hat) = pq/n = 1/40  MSE = Var + bias^2 = 1/40
Poisson data sum/n = 2
Poisson d log L: sample mean IS the MLE; mean = 2
```

Both discrete MLEs reduce to counting: heads-over-flips and
sum-over-points.

## 3. The Uniform Max: Biased, Measured, Cured

```python
from fractions import Fraction as F
import random

theta = F(12)
sample = [F(3), F(8), F(9)]
print("U(0,12) data max =", max(sample), " expected max = n/(n+1)*theta =",
      F(3, 4) * theta, " bias =", F(3, 4) * theta - theta)
print("bias-corrected (n+1)/n * max =", F(4, 3) * max(sample))
random.seed(777)
reps = 200000
tot = 0.0
for _ in range(reps):
    tot += max(random.uniform(0, 12) for _ in range(3))
print("simulated E[max] over", reps, " trials =", tot / reps,
      " theory 9 =", float(F(3, 4) * theta))
```

Observed output:

```text
U(0,12) data max = 9  expected max = n/(n+1)*theta = 9  bias = -3
bias-corrected (n+1)/n * max = 12
simulated E[max] over 200000  trials = 8.997715881500072  theory 9 = 9.0
```

The simulation recovers n/(n+1)·θ = 9 within 0.03%: theory and random
search meet at the same number.
