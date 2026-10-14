# Descriptive Statistics - Interview Questions

## Q1. n or n - 1 - decide and defend.

A: Describing these seven numbers: n (30.82). Estimating population
variance for inference: n - 1 (35.95), because E[ss] = (n-1) sigma^2. The
interview answer names the question first, then the divisor - the divisor
follows the estimand.

## Q2. Mean 10.57, median 9.0 - which do you report to executives?

A: Both, led by the median with IQR for operations (half the cases are at
most 9), mean second for totals (sums need the mean). One sentence explains
the gap: a right tail pulls the mean up.

## Q3. Skew is +0.58. What action does that drive?

A: Prefer median/IQR summaries, check log or rank transforms before
mean-based models, and inspect the tail (the 21) before choosing.
Shape numbers route to methods, not to decoration.

## Q4. r = 0.99 - can we drop one variable?

A: For linear purposes nearly yes - but plot first: 0.99 also arises from
curves and single-lever outliers. Check the scatter, then drop or combine
with the redundancy documented.

## Q5. Your variance routine returns NaN on a new feed. Diagnose live.

A: Suspects in order: NaN in input poisoning sums, constant column giving
0/0 downstream, overflow in one-pass sum-of-squares. Fix: NaN pre-scan with
counts, zero-spread branch, two-pass deviations.

## Q6. Explain kurtosis -0.62 without jargon.

A: "Tails milder than a bell curve with the same spread - surprises beyond
two sd are rarer than normal would predict. Our extremes stay close, so
normal-based alarms would over-fire."

## Q7. How do you summarize a column with missing values?

A: Report n, missing count, and mechanism judgment first; compute summaries
on observed with the mechanism stated; never let NaN silently shrink n.
Summaries without missingness accounting describe whoever answered.

## Q8. Build these summaries for 100M rows on plain JDK?

A: Single streaming pass for count/sum/min/max plus Welford-style
accumulators for variance; exact median/quartiles need selection or
sorting (partition the data); moments accumulate in higher precision.
Report which summaries are exact vs approximate.
