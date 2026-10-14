# Debugging - Causal Inference

## 1. Integer division zeroes your rates

`90 / 100` is 0 in Java. Symptom: all rates 0.0 or 1.0. Fix: make one
operand double (`90.0 / 100`) - every snippet here does this openly.

## 2. Pooled-first analysis

Symptom: conclusions flip when a reviewer stratifies. Fix: always
tabulate treatment-by-stratum cells before any pooled number; treat the
pooled rate as suspect until strata agree.

## 3. Stale weights in adjustment

Symptom: adjusted gap ignores a regrouping. Cause: weights passed
separately from counts. Fix: recompute population shares from the same
table object on every call (architecture enforces this).

## 4. Parallel trends asserted, never plotted

Symptom: DiD number with no pre-period figure. Fix: plot both groups'
pre-history; diverging lines invalidate the read before discussion.

## 5. Matched samples that are not balanced

Symptom: adjusted estimate published while covariates still differ.
Fix: print the balance table first; standardized gaps above ~0.1 mean
re-match or re-stratify, not re-interpret.

## 6. Collider conditioning by subgroup

Symptom: effect appears only inside a post-treatment subgroup (e.g.
hospitalized). Fix: re-estimate on the full randomized sample; subgroup
analyses are exploratory, not confirmatory.

## 7. Dropped assumption strings

Symptom: an estimate travels into slides without its license. Fix: the
record type carries {estimate, assumption} jointly - review any code
that prints one field without the other.

## 8. Weights that do not sum to one

Symptom: adjusted gap outside every stratum gap (impossible for convex
weights). Cause: hand-passed shares after regrouping. Fix: recompute
shares from the table object; assert the sum is 1.0 within 1e-12.
