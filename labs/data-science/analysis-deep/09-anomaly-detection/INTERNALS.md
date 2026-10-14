# Internals - Anomaly Computations

## Quartiles by sort

O(n log n) via Arrays.sort; index rules documented at the call site
(n/4, 3n/4 on the sorted array). Deterministic, no interpolation
disputes at lab sizes. Streaming quantiles (t-digest style) are out of
scope - noted, not implemented.

## Median/MAD

Two sorts (values, then absolute deviations), O(n log n). The 0.6745
scale factor calibrates MAD to sd under normality - stated where used,
with the normality dependence explicit.

## Threshold sweep

O(T * thresholds): one pass per threshold. With labeled history under
~1e6 rows this is instant; the table (not a curve object) is the output
so reviewers see every row the decision rests on.

## Bayes arithmetic

O(1): four doubles. Cast counts to double before dividing; guard
prev = 0/1 (degenerate: PPV undefined/1) with explicit exceptions, not
silent NaN propagation.

## Alert-volume projection

flags/day = volume * (sens*prev + fpr*(1-prev)); true pages = volume *
sens * prev. Integer truncation uses floor with the remainder reported
so "99 vs 999" style statements stay exact.

## Edge cases

- All-identical history: spread 0 makes every z 0/0 - report "no variance"
  and fall back to rule-based flags (exact-duplicate vs novel value).
- Single-label sweeps (no positives): recall undefined - report P only,
  with the missing class stated, not zero-filled.
- Tied scores across the threshold: counts jump discontinuously - break
  ties deterministically (by index) and document the rule.

## Why count tables, not curves

The Sweep output is a table of (threshold, TP, FP, FN) rows: reviewers
audit rows, plots hide them. Curves render from the table for humans;
decisions cite the table for the record.
