# Descriptive Statistics - Mathematical Foundations

**Track:** statistics  |  **Lab:** lab01  |  **Level:** Foundational

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## Notation

| Symbol | Meaning |
|---|---|
| `x̄ = (1/n)Σxᵢ` | Mean - uses every value, sensitive to outliers |
| `median = middle order statistic` | Median - robust to outliers and skew |
| `s² = Σ(xᵢ − x̄)² / (n−1)` | Sample variance - unbiased estimator of population variance |
| `σ² = Σ(xᵢ − μ)² / n` | Population variance - divisor n for a complete population |
| `IQR = Q3 − Q1` | Interquartile range - spread of the middle 50% |
| `outlier if x < Q1 − 1.5 IQR or x > Q3 + 1.5 IQR` | Fence rule - flag, do not delete automatically |
| `skew = m₃ / s³` | Sample skewness - sign and magnitude of asymmetry |
| `M2 update: M2 += (x−mean)(x−mean_new)` | Welford - stable single-pass variance |

## Why the Math Matters

The formulas below are not decoration: each one is the place where a wrong assumption silently produces a plausible number. Knowing which formula applies, and when it stops applying, is the skill this lab builds.


---

## 1. Sample versus population variance

```text
s^2 = sum(x_i - xbar)^2 / (n - 1)
sigma^2 = sum(x_i - mu)^2 / n
E[s^2] = sigma^2  (the n−1 divisor makes the estimator unbiased)
```

One degree of freedom is spent estimating the mean, so the residual sum of squares has expectation (n−1)σ², not nσ². Dividing by n gives a biased-low estimate of spread.

**Worked example.** Values [2,4,5,4,5]: mean 4. Deviations [-2,0,1,0,1], sum of squares 6. Population variance 1.2, sample variance 1.5, sample sd 1.2247. Reporting 1.2 as a sample variance is the common error.


---

## 2. Numerical stability: why naive variance fails

```text
naive: var = (sum x^2)/n - (mean)^2
stable (two-pass): var = sum(x_i - xbar)^2 / (n-1)
Welford: single pass, no cancellation
```

When the mean is large relative to the spread, sum of squares and the squared mean are nearly equal, and subtracting them loses most significant digits. Real data (latency in microseconds, money in cents) hits this constantly.

**Worked example.** Ten values around 1,000,000 with sd 100: sum x²/n is about 1e12, mean² is 1e12, and their difference is 1e4. Double precision keeps about 4 of 16 digits, so the naive variance can be off by tens of percent. Welford is exact to machine precision.


---

## 3. Quartiles and the IQR fence

```text
Q1 = quantile(0.25), Q3 = quantile(0.75)
IQR = Q3 - Q1
fences: [Q1 - 1.5 IQR, Q3 + 1.5 IQR]
values outside are flagged
```

The fence is scale-free and outlier-robust because it is built from order statistics. For roughly normal data it flags a small fraction; for heavy tails it flags more, which is a property of the shape, not a defect.

**Worked example.** Sorted [1..9] plus 100: Q1 = 3, Q3 = 8, IQR = 5, upper fence 15.5, so 100 is flagged. Sorted [1..100] uniformly: Q1 = 25.75, Q3 = 75.25, IQR = 49.5, upper fence 149.5, so nothing is flagged.


---

## 4. Percentiles versus mean plus standard deviation

```text
for right-skewed latency, report p50, p90, p99
mean + sd implies a symmetric distribution around the mean
skewness = m3 / s^3, kurtosis = m4 / s^4 - 3
```

A symmetric summary actively misdescribes a skewed distribution: the mean is not a typical observation, and the stated range is wrong. Percentiles describe what actually happens to a fraction of traffic.

**Worked example.** Latency [10, 10, 12, 14, 900]: mean 189.2, sd 400.1, median 12, p90 738. Quoting 189 ± 400 suggests typical values near 189; the median says a typical request takes 12 ms and the tail is the problem.


---

## 5. Skewness and kurtosis

```text
m3 = (1/n) sum(x_i - xbar)^3
skewness = m3 / s^3
kurtosis = m4 / s^4 - 3 (excess kurtosis)
```

Skewness gives the direction and strength of asymmetry; excess kurtosis gives tail weight relative to normal. Both decide which summary family and which tail analysis to use.

**Worked example.** Latency [10,10,12,14,900]: m3 dominated by 900, skewness about 2.5, so mean is unrepresentative. Log-transforming latency gives near-zero skew and makes a mean ± sd defensible on the log scale.


---

## Cheat Sheet

- `x̄ = (1/n)Σxᵢ` - Mean
- `median = middle order statistic` - Median
- `s² = Σ(xᵢ − x̄)² / (n−1)` - Sample variance
- `σ² = Σ(xᵢ − μ)² / n` - Population variance
- `IQR = Q3 − Q1` - Interquartile range
- `outlier if x < Q1 − 1.5 IQR or x > Q3 + 1.5 IQR` - Fence rule
- `skew = m₃ / s³` - Sample skewness
- `M2 update: M2 += (x−mean)(x−mean_new)` - Welford

## Numerical Traps

- Dividing by n for sample variance and calling it unbiased.
- Computing variance as sum of squares minus the squared mean.
- Quoting mean ± sd for a right-skewed variable such as latency or spend.
- Deleting flagged outliers before computing any summary.
- Reporting an aggregate that reverses inside every segment.

## Self-Check Problems

1. Compute mean, median, mode, population and sample variance for [2,4,5,4,5] and check unbiasedness by simulation.
2. Construct data where sum-of-squares variance is off by 20% while Welford is exact, and quantify the error.
3. Compute quartiles and the IQR fence for a dataset with a deliberate outlier, and explain the flag.
4. Compare mean ± sd reporting against percentiles for a lognormal sample.
5. Demonstrate Simpson's paradox with three segments and show the aggregate reversing.
