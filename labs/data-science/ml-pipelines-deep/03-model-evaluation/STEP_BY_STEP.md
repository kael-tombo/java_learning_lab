# Model Evaluation — Step by Step

## Step 1. Count the matrix by hand
Labels {1,0,1,1,0,1,0,0,1,0}, preds {1,0,0,1,0,1,1,0,1,0}. Tally each
position: TP=4, FP=1, TN=4, FN=1. Run ConfusionMetrics and confirm.

## Step 2. Derive the rates
Precision 4/5=0.8, recall 4/5=0.8, F1=2(0.8)(0.8)/1.6=0.8 (observed
0.8000000000000002 via floating point), accuracy 8/10=0.8. Note the
trailing ...002 is representation, not a finding.

## Step 3. Score probabilities
Labels {1,0,1,0}, probs {0.9,0.1,0.8,0.4}. Run LogLossBrier: log-loss
0.23617255159896325, Brier 0.055. Compare with the constant-0.5
baseline (0.6931471805599453, 0.25) and confirm both favor the model.

## Step 4. Stratify a split
Labels {0x6, 1x4}, K=2. Run StratifiedKFold: fold0 tests [0,2,4,6,8]
with 2 positives, fold1 tests [1,3,5,7,9] with 2 positives, overall
rate 0.4 preserved. Then try unstratified contiguous halves and show
the positive counts skew.

## Step 5. Break it on purpose (leakage demo)
Fit a scaler (mean) on all 10 labels including test, then "evaluate."
Record the number. Refit on train only and re-evaluate. The gap is the
leakage tax; its sign and size vary, but its existence is the lesson.

## Step 6. Pick the right lead metric
For a 1%-positive problem, write why accuracy and ROC-AUC mislead and
why PR/F1 lead. Cite the denominator argument: FPR divides by the huge
negative count, precision does not.

## Step 7. Write the report
One page: matrix, rates, probability scores vs baseline, fold spread,
and the locked test-set statement. No promotion without all five.
