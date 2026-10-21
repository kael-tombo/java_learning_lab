# Model Evaluation — Common Mistakes

## 1. Leading with accuracy on imbalanced data
Accuracy divides by all items, so rare positives barely register. The
1%-positive majority classifier scores 0.99 while finding nothing. Lead
with PR/F1 when positives are rare.

## 2. Reporting rates without the matrix
Precision 0.8 with TP=4/FP=1 differs operationally from TP=800/FP=200.
Same rate, different evidence. Always publish the four counts.

## 3. Tuning on the test set
Each test-guided decision spends test validity. After enough peeks the
test set is a second validation set and reports optimism. Lock test to
single scorings per candidate.

## 4. Preprocessing leakage
Fitting scalers, imputers, or selectors on all data before splitting
lets test statistics into training. Fit on train, apply elsewhere —
no exceptions for "unsupervised" steps.

## 5. Trusting ROC-AUC alone on imbalance
FPR's denominator (all negatives) makes bad positive detection look
cheap. Pair ROC with PR whenever negatives dominate.

## 6. Confusing sharp with calibrated
Confident probabilities (near 0/1) feel accurate but may be
systematically off. Check binned observed rates before using
probabilities in expected-value math.

## 7. Exact double equality in tests
Asserting f1 == 0.8 fails on the observed ...002 representation noise.
Compare with tolerance (e.g. |a-b| < 1e-9).

## 8. Averaging folds without the spread
Mean F1 across folds hides instability. Report min/max or standard
deviation; a wide spread vetoes promotion regardless of the mean.
