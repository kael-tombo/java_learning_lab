# Descriptive Statistics

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

## 1. The Problem This Solves

A dataset arrives with 400,000 rows and you have ten seconds to say something true about it before a meeting starts.

Every analytical claim downstream rests on knowing which summary to trust. The mean of a skewed distribution is a number nobody should quote without the median beside it.

## 2. Learning Objectives

- Compute mean, median and mode and know when each is the honest summary
- Distinguish population from sample variance and defend the divisor
- Compute quantiles, IQR and detect outliers with the 1.5 IQR rule
- Use Welford's algorithm for numerically stable streaming variance
- Report dispersion with a spread, not just a centre
- Recognise how shape, skew and outliers invalidate a single-number summary

## 3. Core Concepts

### 3.1 Mean, median, mode

The mean uses every value and is dragged by outliers. The median uses position and is robust. The mode is the most frequent value and the only one that works for categorical data. Reporting all three is the cheapest honesty available.

### 3.2 Population versus sample variance

Dividing by n gives the average squared deviation of the population you have. Dividing by n−1 gives an unbiased estimator of the population variance from a sample. Reporting the population variance of a sample as if it were the population variance understates spread.

### 3.3 Welford's algorithm

A single-pass update, mean ← mean + (x − mean)/n and M2 ← M2 + (x − mean)(x − mean_new), gives numerically stable variance. Naively summing squares and subtracting a large mean loses precision catastrophically on real data.

### 3.4 Quantiles and IQR

Q1, Q2, Q3 divide the ordered sample into quarters; IQR = Q3 − Q1 measures the middle 50% and is unaffected by outliers. The 1.5 IQR fence is a distributional rule of thumb for flagging points worth inspecting.

### 3.5 Shape is part of the summary

Skewness and kurtosis tell you whether a mean describes anything. Latency is right-skewed, so quote p50, p90 and p99 and describe the tail rather than pretending a mean plus a standard deviation characterises it.

### 3.6 Summaries are lossy

Mean and standard deviation destroy shape. Two datasets with identical mean and variance can have completely different distributions, which is why a distribution comparison and a two-number summary are different tools.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `x̄ = (1/n)Σxᵢ` | Mean | uses every value, sensitive to outliers |
| `median = middle order statistic` | Median | robust to outliers and skew |
| `s² = Σ(xᵢ − x̄)² / (n−1)` | Sample variance | unbiased estimator of population variance |
| `σ² = Σ(xᵢ − μ)² / n` | Population variance | divisor n for a complete population |
| `IQR = Q3 − Q1` | Interquartile range | spread of the middle 50% |
| `outlier if x < Q1 − 1.5 IQR or x > Q3 + 1.5 IQR` | Fence rule | flag, do not delete automatically |
| `skew = m₃ / s³` | Sample skewness | sign and magnitude of asymmetry |
| `M2 update: M2 += (x−mean)(x−mean_new)` | Welford | stable single-pass variance |

## 5. How the Pieces Fit Together

1. Load the data and check size, null count and type before summarising anything.

2. Compute the centre three ways: mean, median, mode, and compare them.

3. Compute dispersion with variance, standard deviation, IQR and range.

4. Inspect shape: histogram, quantiles, skewness and kurtosis.

5. Apply the 1.5 IQR fence and inspect every flagged row rather than deleting it.

6. Report a distribution-appropriate summary: p50/p90/p99 for skewed data, mean ± sd for symmetric.

## 6. Assumptions and Invariants

- Order statistics assume a defined ordering, which needs a real numeric scale
- Sample variance assumes an i.i.d. sample from a finite-variance population
- The mode is only meaningful for discrete or categorised data
- Quantile definitions differ between conventions; state which one you used
- The IQR fence assumes roughly unimodal data and is a screen, not a test
- Summaries computed on a sample describe that sample; population claims need inference

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Latency reported as mean 240 ms ± 60 ms | mean plus sd on a heavy right tail | report p50, p90, p99 and describe the tail |
| Variance computed by summing squares then subtracting | catastrophic cancellation | use Welford or a two-pass algorithm |
| Sample variance divided by n | biased-low spread quoted as the population value | use n−1 for sample variance and say which you used |
| Outliers silently removed before summarising | the interesting rows deleted by a fence rule | flag them, inspect them, report both with and without |
| Averaging across SKUs gives 3.4 but no SKU is 3.4 | Simpson's paradox across segments | report per-segment statistics alongside the aggregate |
| Mode reported for a continuous variable | binning choices invented the mode | use a density estimate or say the distribution is unimodal |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `DoubleSummaryStatistics` | streaming mean, variance and count without holding the data |
| `Arrays.sort for order statistics` | median and quartiles from a sorted copy |
| `Map<Double,Integer> for mode counts` | frequency counting with a single pass |
| `HashMap for quantile type frequencies` | detecting discrete distributions before choosing a summary |
| `record Summary(double mean, double median, double mode, double sd, double iqr, double p90)` | one immutable result so summaries travel together |

## 9. Where This Sits in the Larger System

- **lab02** turns these distributions into probabilities you can reason with.
- **lab03** uses the standard error from this lab as the denominator of a test statistic.
- **lab07** needs these summaries as the baseline for a trend line.
- **lab10** needs the effect size that starts from a mean difference and a pooled variance.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Compute mean, median and mode and know when each is the honest summary
- [ ] 0 — cannot yet — Distinguish population from sample variance and defend the divisor
- [ ] 0 — cannot yet — Compute quantiles, IQR and detect outliers with the 1.5 IQR rule
- [ ] 0 — cannot yet — Use Welford's algorithm for numerically stable streaming variance
- [ ] 0 — cannot yet — Report dispersion with a spread, not just a centre
- [ ] 0 — cannot yet — Recognise how shape, skew and outliers invalidate a single-number summary

## 11. Summary Checklist

- [ ] I report mean, median and mode together and explain any disagreement.
- [ ] I use n−1 for sample variance and state it.
- [ ] My variance is computed stably (Welford or two-pass).
- [ ] For skewed data I quote percentiles rather than mean ± sd.
- [ ] I flag outliers and inspect them rather than deleting them.
- [ ] I check per-segment statistics before quoting an aggregate.
