# Descriptive Statistics - Debugging Guide

## Symptom: mean prints NaN

Cause: a NaN element in the sum loop, or 0/0 from an empty array. Fix:
pre-scan with `Double.isNaN` counting, reject empty input with an exception,
and assert finite output.

## Symptom: variance negative (tiny, like -1e-12)

Cause: one-pass formula cancellation on large-mean data. Fix: switch to
two-pass deviations; clamp only after confirming the magnitude is rounding
noise, and log when clamping fires.

## Symptom: median off by one position

Cause: even-n averaging skipped, or sorting the wrong array. Fix: unit-test
odd n = 7 (expect 9.0) and an even-n case (expect middle-pair mean); sort a
clone and assert the original is unchanged.

## Symptom: quartiles disagree with a reference tool

Cause: different interpolation (type-7 vs median-of-halves vs nearest-rank).
Fix: state the rule (type-7 here: Q1 7.0, Q3 13.5) and test the positions,
not just the values - conventions differ legitimately.

## Symptom: r outside [-1, 1] slightly (1.0000000002)

Cause: floating-point rounding in the ratio. Fix: clamp display to [-1, 1]
only at print time, keep raw for computation, and investigate if the excess
exceeds 1e-9 (that signals a formula bug, not rounding).

## Symptom: skew sign contradicts mean/median gap

Cause: miscentered powers (used raw instead of deviated values) or wrong
normalization. Fix: recompute m_3 from explicit deviations and check the
sign against mean-vs-median; they agree on clean data.

## Symptom: mode returns a surprise value

Cause: floating-point near-ties (7.0 vs 6.9999999) splitting frequencies, or
tie-breaking by first-seen. Fix: round/bin before tallying continuous data
and report all tied top values.

## Symptom: sample variance smaller than population variance

Cause: swapped divisors, or ss recomputed inconsistently between the two.
Fix: derive both from one ss (as the snippets do) and assert sampVar >
popVar for finite n > 1 - the inequality is algebraic, so violations prove
code bugs, never data quirks.
