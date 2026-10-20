# Exercises — Bayesian Statistics

Worked solutions; figures come from the captured runs in
CODE_DEEP_DIVE.md or exact one-step arithmetic on its printed
fractions.

## Problem 1. A Fresh Dataset Through the Same Engine
Prior Beta(2, 2) meets data HHT. Give the posterior, its mean, and the
predictive for the next flip.

**Solution**: Add counts: posterior Beta(2+2, 2+1) = Beta(4, 3)
(run printed exactly this). Mean = 4/7 ≈ 0.571429; because the
Bernoulli predictive equals the posterior mean, P(next head) = 4/7
(run printed it twice, as mean and as predictive). Prior contributed
half a coin against the data's two heads; the mean 4/7 sits between
the raw 2/3 and the prior 1/2.

## Problem 2. All Tails, Flat Prior
Data TTT under Beta(1, 1). Posterior, mean, and one commentary line.

**Solution**: Posterior Beta(1, 4) (printed on the run). Mean = 1/5
= 0.2 exactly. Flatness is why the mean sits at 1/(3+1+1)... at
a/(a+b) = 1/5 rather than zero — the flat prior holds one
pseudo-observation per endpoint? Beta(1,1) acts like one prior
pseudo-success and one prior pseudo-failure, tempering zero heads
into a fifth-odds estimate instead of certainty at zero.

## Problem 3. Jeffreys Prior, Half-Observation Structure
Data H, H, H, T with prior Beta(1/2, 1/2). Posterior and mean?

**Solution**: Adding counts to 1/2: posterior Beta(7/2, 3/2)
(exact printed). Mean = (7/2)/(7/2 + 3/2) = (7/2)/5 = 7/10 = 0.7.
The Jeffreys prior behaves like half a pseudo-head and half a
pseudo-tail — the lightest possible prior weight, and its footprint
shows in the posterior's parameters being half-integers.

## Problem 4. Order Invariance, Run It Both Ways
With Beta(2, 2) and data 7 heads then 3 tails, verify the posterior is
the same when the data arrive in reverse order.

**Solution**: The update is modular addition: parameters start at
(2, 2) and each observation adds 1 to one of them; addition is
commutative, so ANY order — reversed, or one-at-a-time, or whole-batch
— prints Beta(9, 5). The run's `identical: True` line executed the
batch-vs-stream check; order-invariance is the same statement viewed
from the reverse direction.

## Problem 5. Programming: A Predictive Calculator
Implement `bayes_coin(prior_pair, flips)` returning (posterior pair,
predictive mean) as exact fractions; run it on (2,2) with the 10-flip
dataset and confirm the printed (9, 5), 9/14, gap 2/35 against the
plug-in 7/10.

**Solution skeleton**:

```python
from fractions import Fraction as F

def bayes_coin(pa, pb, flips):
    a, b = F(pa), F(pb)
    for x in flips:
        a, b = a + x, b + (1 - x)
    return (a, b), a / (a + b)

(post, pred) = bayes_coin(2, 2, [1, 1, 1, 1, 1, 1, 1, 0, 0, 0])
print(post, pred, F(7, 10) - pred)
```

Executed: (Fraction(9), Fraction(5)), Fraction(9, 14), Fraction(2, 35)
— matching the analysis-run triple (posterior parameters, predictive
mean, plug-in gap) verbatim.
