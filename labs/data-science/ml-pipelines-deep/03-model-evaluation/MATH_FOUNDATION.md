# Model Evaluation — Math Foundation

## 1. From counts to rates
With TP=4, FP=1, TN=4, FN=1, n=10:

  precision = 4/(4+1) = 0.8
  recall = 4/(4+1) = 0.8
  accuracy = (4+4)/10 = 0.8
  F1 = 2(0.8)(0.8)/(0.8+0.8) = 1.28/1.6 = 0.8

Observed f1 prints 0.8000000000000002 because 0.8 has no exact binary
representation; the arithmetic is exact on the fractions.

## 2. Harmonic mean derivation
For P, R > 0, F1 is the reciprocal of the mean of reciprocals:

  1/F1 = (1/P + 1/R)/2, so F1 = 2PR/(P+R)

Consequence: F1 <= min(P, R) proximity — halving one side roughly
halves F1, while the arithmetic mean would only dip. That sensitivity
is the reason F1 leads when both errors matter.

## 3. Log-loss on the demo
Items (y, p): (1,0.9), (0,0.1), (1,0.8), (0,0.4):

  -log(0.9) - log(0.9) - log(0.8) - log(0.6), all divided by 4
  = 0.23617255159896325 (observed)

Constant 0.5 gives -log(0.5) = 0.6931471805599453 per item. The gap
0.457 is the information the model's probabilities add.

## 4. Brier on the demo
Squared errors: 0.01, 0.01, 0.04, 0.16; mean = 0.22/4 = 0.055
(observed). Constant 0.5 gives 0.25 per item, mean 0.25. Brier is in
probability-squared units; differences read directly as squared-error
improvements.

## 5. Why stratification preserves rates
With class sizes n0, n1 and K folds, round-robin gives each fold
floor or ceil of n_c/K items of class c. Demo: 6/2 = 3 negatives and
4/2 = 2 positives per fold exactly, so both folds hold rate 2/5 = 0.4
equal to the overall 4/10. Deviations are at most one item per class.
