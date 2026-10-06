# Model Evaluation - Quiz

## Question 1
Why is accuracy a poor metric under class imbalance?
A) It is always wrong
B) A model predicting the majority class scores high accuracy while failing on the minority class — use precision/recall/PR-AUC
C) It is signed
D) It changes dtypes

**Answer**: B

## Question 2
When do you prefer precision over recall?
A) Always
B) When false positives are costly (e.g. spam → labeling a real email spam)
C) When false negatives are costly
D) For balanced data

**Answer**: B

## Question 3
When do you prefer recall over precision?
A) Always
B) When false negatives are costly (e.g. cancer screening, fraud catching — missing a case is worse)
C) When false positives are costly
D) For balanced data

**Answer**: B

## Question 4
What does PR-AUC capture that ROC-AUC may not?
A) Nothing
B) Performance on the minority class — ROC-AUC can look high when negatives dominate, masking poor positive-class ranking
C) Speed
D) Memory

**Answer**: B

## Question 5
Why is a confusion matrix more informative than a single metric?
A) It is prettier
B) It shows which classes are confused with which — tells you the error structure, not just a count
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 6
What does a calibration curve tell you?
A) How fast the model is
B) Whether predicted probabilities match empirical frequencies — a model can rank well but be poorly calibrated
C) The metric
D) The plot

**Answer**: B

## Question 7
Why use cross-validation for a small dataset?
A) It is faster
B) A single split wastes data and gives a high-variance estimate — CV reuses data across folds
C) It changes dtypes
D) It is required

**Answer**: B

## Question 8
What does a learning curve diagnose?
A) The metric
B) Overfitting (big train/val gap) vs underfitting (both low) — tells you whether to get more data or more capacity
C) The plot
D) The speed

**Answer**: B

## Question 9
Why is a held-out test set important after model selection?
A) For aesthetics
B) Hyperparameter tuning adapts to validation — only an untouched test estimates true generalization
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 10
What does mean squared error penalize?
A) Small errors
B) Large errors heavily (squared) — sensitive to outliers; use MAE for a robust view of typical error
C) Nothing
D) The mean

**Answer**: B

## Question 11
Why report confidence intervals on metrics?
A) For aesthetics
B) A single metric value hides variance — the CI tells you how precise the estimate is
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 12
What does a metric on a stratified split preserve?
A) The mean
B) The class ratio in each fold — important for imbalanced data so folds are comparable
C) The variance
D) The seed

**Answer**: B

## Question 13
Why is "time-based split" required for evaluation of forecasting models?
A) It is faster
B) Random splits leak future information — evaluation overstates performance
C) It changes dtypes
D) It is required

**Answer**: B

## Question 14
What is a metric's business alignment?
A) A plot
B) The metric must map to the actual cost/benefit — a "good" F1 that doesn't move business KPI is the wrong metric
C) A speed
D) A dtype

**Answer**: B

## Question 15
Why is macro-average better than micro-average for multiclass imbalance?
A) It is faster
B) Macro averages each class equally — micro is dominated by the majority class
C) It changes dtypes
D) It is a plot

**Answer**: B
