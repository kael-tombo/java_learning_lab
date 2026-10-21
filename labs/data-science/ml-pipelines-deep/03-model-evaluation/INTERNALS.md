# Model Evaluation — Internals

## Single-pass scoring
The scorer accumulates TP/FP/TN/FN plus log-loss and Brier numerators
in one linear pass over (label, prediction, probability) triples. No
second pass is needed for the standard scalar metrics; curves need the
scores retained for sorting.

## Curve construction
Sort items by score descending, sweep the threshold from +inf to -inf,
and trace (FPR, TPR) for ROC or (recall, precision) for PR. Each
distinct score is one step; ties advance in blocks. Area is the
trapezoid sum over steps. Cost is dominated by the sort (n log n).

## Calibration binning
Partition [0,1] into bins (commonly deciles), accumulate per-bin mean
predicted probability and observed positive rate, and plot or tabulate
the pairs. Gaps between the two columns are miscalibration per region;
bin counts weight their importance.

## Fold bookkeeping
The splitter stores fold ids per row plus the stratification key, so
any rerun reconstructs identical folds from the dataset version. Fold
models train independently and merge only at the reporting layer —
never by pooling predictions across different preprocessing fits.

## Numerical care
Clip probabilities into [1e-12, 1-1e-12] before logarithms; use double
accumulation for log-loss sums; report F1 with the understanding that
trailing digits like ...002 are representation noise on exact
fractions such as 4/5.
