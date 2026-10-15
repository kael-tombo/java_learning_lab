# Model Evaluation — Interview

## Q: Read this matrix: TP=4, FP=1, TN=4, FN=1. What do you report?
A: Precision 4/5=0.8, recall 4/5=0.8, F1 0.8 (observed ...002 is fp
noise), accuracy 8/10=0.8 — and I lead with the four counts, because
the rates alone hide the evidence size.

## Q: When does accuracy mislead?
A: On imbalanced data: 1% positives makes a constant-negative model
99% accurate with recall 0. I switch to precision/recall/F1 and PR
curves there.

## Q: ROC-AUC vs PR — which and when?
A: ROC-AUC grades ranking across thresholds; PR exposes weak positive
detection when negatives dominate, since FPR divides by the huge
negative count. Imbalanced problem: PR leads.

## Q: What is a proper scoring rule?
A: A probability score optimized in expectation by honest predictions.
Log-loss (demo 0.23617 vs 0.69314 baseline) and Brier (0.055 vs 0.25)
are the standards; both must beat the constant-0.5 reference.

## Q: Define calibration and why it matters.
A: Predicted-q items are positive at rate q. Rankings can be good while
magnitudes are off; any expected-value decision needs magnitudes right,
so I check binned observed rates on held-out data.

## Q: How do you split small imbalanced data?
A: Stratified K-fold: round-robin per class keeps every fold at the
overall ratio. Demo: 10 items, 4 positives, K=2 gives 5-item folds
with exactly 2 positives each (rate 0.4 preserved).

## Q: What is leakage via preprocessing?
A: Fitting transforms on all data before splitting, letting test
statistics into training. The fix is structural: fit on train only,
apply the fitted object to val/test.
