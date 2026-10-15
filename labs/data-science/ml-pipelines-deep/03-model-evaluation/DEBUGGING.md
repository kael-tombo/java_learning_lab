# Model Evaluation — Debugging

## Symptom: accuracy 0.99 but users report misses
Likely class imbalance: a 1%-positive problem gives 0.99 to a constant
negative predictor. Check the matrix: TP near 0 with high TN. Fix: lead
with precision/recall/F1 and PR curves; set the operating threshold on
validation for the business cost ratio, not 0.5.

## Symptom: validation great, test poor
Likely test reuse (selection on test) or preprocessing leakage. Check:
was preprocessing fit on train only? How many times was test scored
during selection? Fix: lock test to one scoring per candidate; refit
transforms on train and re-evaluate to measure the leakage gap.

## Symptom: log-loss good but decisions bad
Likely miscalibration: ranking is fine, probability magnitudes are off.
Check calibration bins: predicted-q vs observed rate per bin. Fix:
recalibrate (e.g. Platt/isotonic on validation) or threshold on
validation rather than trusting raw 0.5.

## Symptom: fold scores swing wildly
Likely small data without stratification, or leakage varying per fold.
Check per-fold positive counts first (demo preserves 2/5 exactly when
stratified). Fix: stratify; if spread persists, the point estimate is
fragile — report the interval, not the mean.

## Symptom: F1 prints 0.8000000000000002
Not a bug: binary floating-point cannot represent 0.8 exactly. Check
with fractions (4/5) to confirm. Fix: round for display; compare with
tolerance in tests, never exact equality on doubles.

## Debugging checklist
1. Read the matrix before any rate.
2. Verify split lineage and preprocessing fit scope.
3. Compare against constant/majority baselines.
4. Check calibration if probabilities drive decisions.
5. Confirm fold composition before trusting the mean.
