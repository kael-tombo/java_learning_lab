# Data Validation & Quality - Mathematical Foundations

**Track:** mlops  |  **Lab:** lab09  |  **Level:** Intermediate

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
| `expectation: violation_count = |{r : predicate(r) false}|` | Expectation - the atomic unit of validation |
| `null_ratio = nulls / rows` | Null ratio - with a threshold and an owner |
| `rate_diff = |p_current - p_reference|` | Rate comparison - for binary and categorical checks |
| `KS = max|F_cur(x) - F_ref(x)|` | Rank statistic - shape comparison without assuming a form |
| `freshness = now - max(event_ts)` | Freshness - the most common real failure |
| `suite_score = 1 - weighted_violations` | Suite result - comparable over time |

## Why the Math Matters

Data quality is hypothesis testing applied to pipelines: rate comparisons with a noise floor, sampling detection probability, and rank statistics for shape.


---

## 1. Rate differences and their noise floor

```text
p_hat = violations / n
SE(p_hat) = sqrt(p(1-p)/n)
significant if |p_cur - p_ref| > z * sqrt(SE_ref^2 + SE_cur^2)
```

Comparing two rates without accounting for sampling noise turns normal variation into alerts. This is the same two-proportion test from statistics applied to data quality, and it is what makes thresholds defensible.

**Worked example.** Null rate 0.5% on n=1M vs 0.52% on n=1M: difference 0.02 points, SE_each = 0.00022, pooled SE = 0.00031, z = 0.64. Not a change. At 0.9% the z is 25 and the alert is unambiguous.


---

## 2. Sampling and the failure granularity

```text
P(miss a failure affecting fraction f) = (1 - f)^n_sample
to detect f=0.01 with 95% probability needs n_sample >= 299
```

The detection probability compounds with sample size. Validating a 1% sample detects a 50% corruption almost surely and a 0.5% corruption essentially never, which is why sampling hides exactly the subtle failures you were hoping to catch.

**Worked example.** n=10,000 of 10M (0.1% sample): misses a 1% corruption with probability 0.99^10000 = 4.3e-44, essentially always caught. Misses a 0.01% corruption with probability 0.99^10000 ~ 0, so 10M rows slip through.


---

## 3. Rank-based shape comparison

```text
F_ref, F_cur empirical CDFs
KS = sup_x |F_cur(x) - F_ref(x)|
null distribution: KS ~ sqrt(n_eff * alpha * (1 - alpha))
```

A rank statistic needs no distributional assumption, which is why it works on skewed business data where a mean-and-variance check is meaningless. The null distribution gives a threshold rather than a vibe.

**Worked example.** With effective n = 10,000 at alpha = 0.5: critical KS at 5% is 1.36/sqrt(10000) = 0.0136. A KS of 0.08 is far beyond chance, indicating genuine shape change.


---

## 4. Suite score as a trend

```text
score = 1 - (sum_v w_v * violations_v) / (sum_v w_v * rows)
blocked if any blocking expectation violates
```

A weighted score gives a single comparable number across time, while the blocking rule preserves the property people actually need: the pipeline must not proceed on broken data. The score informs, the rule decides.

**Worked example.** 10 expectations, 1M rows, 3 violations in one non-blocking expectation with weight 0.5: score = 1 - 0.5*3/1e6 = 0.9999985, a flat trend. The same 3 violations in a blocking expectation stop the pipeline regardless of score.


---

## Cheat Sheet

- `expectation: violation_count = |{r : predicate(r) false}|` - Expectation
- `null_ratio = nulls / rows` - Null ratio
- `rate_diff = |p_current - p_reference|` - Rate comparison
- `KS = max|F_cur(x) - F_ref(x)|` - Rank statistic
- `freshness = now - max(event_ts)` - Freshness
- `suite_score = 1 - weighted_violations` - Suite result

## Numerical Traps

- Comparing rates without a sampling-noise floor, so normal variation alerts.
- Sampling below the granularity of the failures you expect.
- Using a flat volume expectation that fires every seasonality peak.
- Treating validation score as the gate instead of the blocking rule.
- Setting thresholds from round numbers with no reference history.

## Self-Check Problems

1. Compute the sample size needed to detect a 0.5% null-rate regression at 95% power.
2. Test whether a null rate moved from 0.4% to 0.55% on two samples of 500k.
3. Compute the critical KS value for two samples of 50k and evaluate a KS of 0.02.
4. Design a window-aware volume expectation that survives a weekly cycle.
5. Build a suite of 10 expectations with weights and compute the trend score for two weeks.
