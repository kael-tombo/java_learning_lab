# Model Evaluation — Theoretical Foundation

## Core Concept

Evaluation answers one question honestly: **how will this model perform on
data it has never seen?** Everything in this lab serves that question —
metrics that measure the right thing, splits that prevent self-deception,
and procedures that keep the test set out of every decision, including
hyperparameter choices.

## The Confusion Matrix and Its Children

For binary classification, all count-based metrics derive from four
numbers (TP, FP, TN, FN):

- **Precision** = TP/(TP+FP) — of predicted positives, how many were real.
- **Recall** = TP/(TP+FN) — of real positives, how many were found.
- **F1** = 2·P·R/(P+R) — harmonic mean; punishes lopsided tradeoffs
  (a model with P=1.0, R=0.1 scores F1≈0.18, not 0.55).
- **Accuracy** = (TP+TN)/all — misleading under imbalance (99% negatives
  ⇒ 99% accuracy for a constant "no" classifier that finds nothing).

Rule: accuracy is reported only alongside prevalence; model selection on
imbalanced data uses precision/recall/F1 or PR-AUC, never accuracy alone.

## Thresholds, ROC, and PR Curves

A scoring classifier plus a threshold makes a decision rule. Sweeping the
threshold traces:

- **ROC curve** (TPR vs FPR) and **ROC-AUC**: threshold-independent ranking
  quality. AUC 0.5 = random, 1.0 = perfect separation.
- **PR curve** (precision vs recall): preferred under class imbalance —
  ROC-AUC flatters when negatives dominate because FPR dilutes in a huge
  denominator.

The operating threshold is a *business* decision (cost of false positives
vs false negatives), not a statistical one — tune it on validation, lock
it, then measure once on test.

## Proper Scoring Rules: Log-Loss and Brier

Hard 0/1 outcomes discard calibration — a model 99% sure and wrong is
worse than one 51% sure and wrong, but accuracy treats them identically:

- **Log-loss** = −mean(y·log p + (1−y)·log(1−p)) — infinite penalty for
  confident wrongness (clip predictions away from exactly 0/1).
- **Brier score** = mean((p − y)²) — bounded, interpretable as mean
  squared calibration error.

Both are *proper*: the expected score is minimized by reporting true
beliefs. Optimizing accuracy while ignoring calibration produces
confident, wrong, undeployable probabilities.

## Splits That Don't Lie

- **Train/validation/test**: fit on train, decide everything (features,
  hyperparameters, thresholds, early stopping) on validation, measure
  *once* on test. Every reuse of test is leakage that compounds silently.
- **Stratified K-fold**: each fold preserves class ratios — mandatory
  under imbalance (a random fold of 1% positives can easily contain none).
- **Temporal splits** for time-ordered data: train on the past, test on
  the future. Shuffling time series lets the model train on the future.
- **Preprocessing inside the fold**: scalers, imputers, and selectors fit
  on train folds only. Fitting on full data before splitting leaks test
  statistics into every training row.

## Key Invariants

1. Report prevalence with accuracy, or don't report accuracy.
2. Thresholds come from validation + costs, never from test.
3. Test is measured once; every prior decision uses train/validation.
4. Imbalanced data ⇒ PR curves and stratified folds.
5. Calibration is measured (log-loss/Brier), not assumed from accuracy.
