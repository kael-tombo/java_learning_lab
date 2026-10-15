# Model Evaluation — History (confident facts only)

## What can be said safely
- Precision/recall language comes from information retrieval, where
  retrieved-vs-relevant is the same 2x2 structure as predicted-vs-actual.
  The F-measure's harmonic-mean form is the standard combination
  taught in retrieval and classification texts alike.
- ROC curves come from signal detection theory (radar/psychophysics)
  mid-20th century; their adoption for classifier comparison is
  documented in the ML literature without a single "first use" this
  lab needs to claim.
- Proper scoring rules (logarithmic, Brier/quadratic) are standard
  decision-theoretic tools; Hastie, Tibshirani, and Friedman present
  log-loss (deviance) and squared error as the canonical classification
  losses. The Brier score is the standard reference for probability
  calibration assessment.
- The train/validation/test split discipline and cross-validation are
  textbook methodology (Hastie et al., standard editions); Kohavi's
  work on cross-validation is the commonly cited empirical study of
  bias/variance in model selection.
- Calibration plots (reliability diagrams) are long-standing practice
  in forecasting; their ML use follows the same construction.
- Fawcett (2006) is the standard ROC reference; Saito & Rehmsmeier
  (2015) document why precision-recall replaces ROC under imbalance;
  Gneiting & Raftery (2007) formalize proper scoring rules.

## What this lab does not claim
No invention dates for metrics, no priority claims, no benchmark
numbers. The stable facts are the definitions, the formulas, and the
methodology — all verifiable in the references below.
