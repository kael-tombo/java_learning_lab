# Exercises — Estimation Theory

Solutions reuse figures and programs from CODE_DEEP_DIVE.md; derived
integers stay exact.

## Problem 1. Grid Proof of a Median's Territory
For the sample (1, 2, 4) compute the absolute-loss risk at every
half-integer candidate in {1, 3/2, 2, 5/2, 3} and locate the argmin.

**Solution**: Risks (mean absolute deviation, exact):
at 1: (0 + 1 + 3)/3 = 4/3; at 3/2: (1/2 + 1/2 + 5/2)/3 = 7/6; at 2:
(1 + 0 + 2)/3 = 1; at 5/2: (3/2 + 1/2 + 3/2)/3 = 7/6; at 3:
(2 + 1 + 1)/3 = 4/3. Minimum at 2 — the median — with symmetric
neighbors 7/6. The run had printed 1 at the median and 10/9 at the
mean; the fuller grid shows the flanks rising to 7/6 and 4/3.

## Problem 2. Decompose a Proportion's MSE
For p_hat = 7/10 from n = 10 Bernoulli-flip data with truth p = 1/2,
give Var, Bias, MSE exactly, then re-do at n = 40 scaled against a
new sample of 28 heads.

**Solution**: Run figures: Bias = 0 (E[p_hat] equals p for the fraction
estimator, always), Var = pq/n = 1/40, MSE = 1/40. At n = 40 with
p_hat = 28/40 = 7/10 the parts shrink fourfold: Var = 1/160, MSE = 1/160,
Bias still 0. Unbiasedness persists; only variance decays, exactly as
the MSE decomposition prescribes.

## Problem 3. Uniform Max, Bias Arithmetic
With θ = 12 and n = 3 samples, compute E[max], Bias, and the unbiased
rescaling; confirm each against the run.

**Solution**: E[max] = (3/4)·12 = 9 (printed). Bias = 9 − 12 = −3
(printed). Cure: (n+1)/n · max scales expectation to θ, since
E[(4/3) max] = (4/3)·(3/4)·12 = 12 — the run's corrected-estimator
line prints exactly 12 for the observed max of 9. One multiplier
moves an estimator from negatively biased to zero-bias.

## Problem 4. Poisson Critical Point, Done Twice
Data (1, 1, 3, 4, 1). Compute the log-likelihood derivative, solve for
the MLE, and state the concavity argument.

**Solution**: log L(λ) = −nλ + (Σ x_i) log λ − Σ log(x_i!). Derivative:
−n + (Σ x_i)/λ; zero at λ = Σx_i/n = 10/5 = 2 (run printed both
sum/n = 2 and the critical-point value 2). Concavity: (Σx_i) log λ
has second derivative −Σx_i/λ^2 < 0, so the critical point is a
maximum; the run's average matched every step of this read.

## Problem 5. Programming: Exact Risk Curve Over a Grid
Implement `sq_risk(data, a)` with fractions, scan a = 0..4 in steps of
1/12, and print the argmin/minimum pair; then scan the absolute-risk
version and print its minimum.

**Solution skeleton**:

```python
from fractions import Fraction as F

def sq_risk(data, a):
    return sum((x - a) ** 2 for x in data) / len(data)

def abs_risk(data, a):
    return sum(abs(x - a) for x in data) / len(data)

data = [F(1), F(2), F(4)]
print(min(((sq_risk(data, F(i, 12)), F(i, 12)) for i in range(49)),
          key=lambda t: t[0]))
print(min((abs_risk(data, F(i, 4)), F(i, 4)) for i in range(17)))
```

Executed pairs: (Fraction(14, 9), Fraction(7, 3)) for squared loss and
(1, 2) for absolute loss — matching the analysis runs; the half-integers
of Problem 1 sit on the same curve printed by the scanner.
