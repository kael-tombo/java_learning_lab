# Model Evaluation — How It Works

## 1. Fix the splits before touching models
Partition data into train/validation/test with stratification, and lock
the test set. Fit all preprocessing (means, scales, vocabularies) on
train only; transform val/test with those fitted objects.

## 2. Train on train, decide on validation
Fit candidate models on train. Compare them and pick thresholds on
validation using the metric matched to the task (F1 or PR for
imbalance, log-loss/Brier for probabilities). Record every decision.

## 3. Score once on test
Run the selected model on test a single time per candidate. Report the
confusion matrix first, then derived rates, then probability scores.
The demo's single-pass computation (TP=4, FP=1, TN=4, FN=1 giving
0.8s across the board) is the shape of this report.

## 4. Check probabilities separately
If the model emits probabilities, compute log-loss and Brier against a
constant baseline (demo baseline: log-loss 0.69314..., Brier 0.25) and
inspect calibration bins. Good classification with bad probabilities
fails downstream decisions that use expected values.

## 5. Cross-validate for stability
For small data, run stratified K-fold (demo: 2 folds, 5 items each, 2
positives each) and report the spread across folds, not just the mean.
Wide spread means the point estimate is fragile.

## 6. Compare against baselines
Every metric needs a reference: majority-class accuracy, constant-0.5
log-loss/Brier, and the production incumbent's scores. A model that
beats no baseline has demonstrated nothing regardless of absolute
values.

## 7. Promote on the full record
Promotion uses test scores plus calibration plus stability plus cost.
The pipeline records all of them (see lab 02); evaluation supplies the
numbers, policy supplies the thresholds.
