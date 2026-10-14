# Feature Engineering - Interview Questions

## Q1. One-hot, ordinal, or target for 10,000 product ids?

A: One-hot explodes (10k sparse columns) and ordinal invents order - both
rejected. Smoothed target encoding inside folds, or hashing for linear
models, with rare-level collapsing first. Justify by cardinality math, not
taste: 10k dummies at n = 50k is a variance disaster.

## Q2. Your validation accuracy drops 8 points on deploy. Diagnose leakage.

A: Audit every fitted constant: scaler means/sds, vocabularies, target
means - which saw full data (leaky 37.5-style) vs train folds? Refit
strictly fold-pure and re-estimate; the gap between leaky and clean
validation approximates the optimism that shipped.

## Q3. Scale for kNN but not for trees - explain.

A: kNN votes by distance: raw area (120) buries rooms (4) 30-to-1 without
scaling. Trees split one variable at a time, invariant to monotone rescale.
Scale for geometry (distances, gradients, penalties); skip for partitions.

## Q4. When do you log-transform?

A: Right-skewed positive predictors with multiplicative structure: log
linearizes ratios and equalizes leverage (2.4x span to 1.22x here). Check
positivity (shift/log guards), confirm the residual fan shrinks, and keep
interpretation in multiplicative terms (percent, not units).

## Q5. How do you encode an ordered level like education?

A: Ordinal integers only if spacing is defensible - usually it is not
(MSc-PhD gap vs BSc-MSc gap). Prefer one-hot, or target encoding with
folds, or monotonic-constrained models; never let 0..4 imply equal steps
without saying so.

## Q6. What breaks if test brings a new level?

A: Unfitted index: crash, silent misalignment, or column shift. Contract:
unknowns map to a declared fallback (all-zeros + unknown column) fixed at
fit; monitor unknown rates as feed-drift signal.

## Q7. Build CV that target encoding cannot leak through.

A: Nest encoding inside each fold: compute smoothed means on k-1 parts,
apply to the held-out part; outer test transformed only by full-train
fitted values. Assert with the row-id overlap checker from EXERCISES.md
task 8 - fail closed on any held-out id in a fit set.

## Q8. Ten million rows, plain JDK - fit a scaler?

A: Single streaming pass for min/max/sum (Welford for variance, selection
or sampling for median/IQR); store constants in the parameter object; apply
in a second pass or downstream. Fit cost O(n), apply O(n), memory O(1)
except quantiles - same contract, bigger n.
