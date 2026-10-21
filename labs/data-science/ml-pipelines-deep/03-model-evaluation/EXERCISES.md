# Model Evaluation — Exercises

## 1. Recompute the matrix first
Cover the observed output. From y={1,0,1,1,0,1,0,0,1,0} and
p={1,0,0,1,0,1,1,0,1,0}, tally TP/FP/TN/FN by hand, then derive
precision, recall, F1, accuracy. Uncover and compare with TP=4, FP=1,
TN=4, FN=1 and the 0.8 line.

## 2. Asymmetric errors
Change the last prediction from 0 to 1 (one extra FP). Recompute by
hand: TP=4, FP=2, TN=3, FN=1, precision 4/6=0.6667, recall still 0.8.
Run and confirm. State which error type moved and which metric noticed.

## 3. Baseline beating
In LogLossBrier, replace probs with {0.6,0.4,0.6,0.4}. Predict whether
log-loss still beats 0.69314 before running. Run, record both scores,
and explain why weaker confidence moves scores toward baseline.

## 4. Perfect vs constant
Set probs to the labels exactly {1,0,1,0} (clipped). Predict log-loss
near 0 and Brier 0. Run and confirm. Then set all to 0.5 and confirm
the baseline pair (0.69314..., 0.25) reproduces.

## 5. Break stratification
Modify StratifiedKFold to take contiguous halves (0-4, 5-9) as folds.
Count positives per fold by hand (fold0: 0, fold1: 4), run, and confirm.
Write the one-sentence lesson about small imbalanced folds.

## 6. Leakage audit
Write the preprocessing order for a scaler + model: fit scaler on
train, transform val/test, train, select on val, score test once. Then
describe the exact violation in "fit scaler on all data, then split"
and why it inflates scores.
