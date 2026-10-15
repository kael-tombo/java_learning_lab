# Model Evaluation — Architecture

## Components
1. Splitter: stratified train/val/test and K-fold partitioner.
2. Preprocessing fitter: fits transforms on train, applies elsewhere.
3. Scorer: confusion matrix plus derived rates in one pass.
4. Probability assessor: log-loss, Brier, calibration bins.
5. Curve builder: ROC and PR curves over threshold sweeps.
6. Reporter: matrix-first reports with baselines attached.
7. Tracker sink: writes scores into the experiment record (lab 02).

## Data flow
Dataset version -> splitter (stratified) -> preprocessing (fit-train,
apply-rest) -> model -> scorer/assessor/curves -> reporter -> tracker.

## Key interfaces
- `split(data, k, stratify)`: returns fold assignments preserving
  class ratios when stratified.
- `confusion(y, p)`: returns (TP, FP, TN, FN).
- `rates(TP, FP, TN, FN)`: returns precision, recall, F1, accuracy.
- `probScores(y, probs)`: returns log-loss, Brier, calibration table.

## Ordering guarantees
Preprocessing fits precede any use on val/test; test scoring follows
validation decisions. The architecture enforces this by passing fitted
transform objects forward, never refitting downstream.

## Scaling notes
Scoring is linear in n and trivially parallel; curve building sorts
scores once (n log n). Calibration binning is one more linear pass.
None of this dominates training cost, so there is no excuse for
skipping it.
