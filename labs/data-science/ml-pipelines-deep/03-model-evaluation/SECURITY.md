# Model Evaluation — Security

## Threats specific to evaluation
- Test-set exposure: test rows leak into training data or
  preprocessing fits, inflating scores. Mitigate with access controls
  on the test split and fit-only-on-train enforcement.
- Metric gaming: optimizing the reported number instead of the goal
  (threshold tuned to a quirk, probabilities sharpened for log-loss
  without calibration). Mitigate with multi-metric reports and locked
  test scoring.
- Label leakage: a feature encodes the label (id columns, future
  fields), producing perfect scores that vanish in production.
  Mitigate with feature audits on high-recall surprises.
- Evaluation tampering: edited score files promote a weak model.
  Mitigate by writing scores into the tracked run record (lab 02)
  with hashes, not sidecar CSVs.

## Controls
- Test data readable by the evaluation job only; analysts get metrics,
  not rows.
- Fitted preprocessing objects versioned and hashed; refit anywhere
  downstream is a pipeline failure.
- Promotion requires the full report (matrix, rates, probability
  scores, fold spread), not a single headline number.

## Demo connection
The preprocessing-leak exercise shows how fitting on all data first
moves scores without changing the model — a miniature of the access
failure above. Stratification shows the benign side of careful data
handling: identical folds from versioned inputs.
