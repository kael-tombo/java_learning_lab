# Internals - Causal Computations

## Stratified adjustment

One pass over cells accumulates stratum gaps and weights; O(cells)
time, O(strata) memory. Weights are population shares recomputed from
the same table - passing weights separately is banned (stale-weight
bug, see DEBUGGING.md).

## DiD arithmetic

Four means in, one subtraction out - O(1). All subtlety is in the
pre-trend check, which is a data pipeline (per-period means per group)
rather than an estimator, kept in a separate class deliberately.

## Balance diagnostics

Standardized mean gap per covariate per stratum: (mean_T - mean_C) /
pooled sd. O(n) per covariate. Values above ~0.1 signal the match did
not do its job; the number is descriptive, with no distributional
claims attached.

## Sensitivity loops

Vary one weight or one unmeasured-confounder strength across a grid and
recompute; O(grid * cells). Results render as a small table of
estimate-vs-assumption, the honest output format for fragile findings.

## Numerics

Rates are ratios of longs - cast before dividing (integer-division bug
is the top defect here). Adjusted gaps use Kahan-style compensated
summation when strata exceed a dozen; below that, plain sums suffice.

## Edge cases

- Single-stratum data: adjustment equals the naive gap - correct, with a
  logged warning that no confounding control occurred.
- Zero-cell strata (no treated severe cases): the gap is undefined there;
  report the covered population explicitly instead of borrowing weights.
- All-treated data: no contrast exists; the toolkit refuses rather than
  inventing a control group from thin air.

## Why longs for counts

Rates from longs cast at division are exact to double precision; float
accumulators over millions of rows drift. Evidence stays integral until
the last possible moment - a deliberate type-level choice.
