# 04-loss-functions - Loss Functions
## Overview
Regression uses MSE (mean squared error, RMSE its root); classification uses softmax plus cross-entropy -log p_true. CE penalizes confident wrong answers steeply.
## Key formulas
- MSE = mean((t-p)^2); RMSE = sqrt(MSE).
- softmax_i = e^(z_i-m)/sum e^(z_j-m); CE = -log p_true.
## What the snippets show
- Nn04A: MSE 0.0250 vs 0.2500 contrast pair.
- Nn04B: softmax summing to 1 with CE 0.4170.
## Try it
Swap true class to 2 in Nn04B and confirm CE rises to ~2.32.
## Formula reference
- MSE = mean e^2; MAE = mean |e|; Huber blends both at delta.
- CE = -log p_true; KL(p||q) adds teacher distribution (distillation).
- Label smoothing mixes one-hot with uniform, tames overconfidence.
## Worked example
- Errors [0.1,-0.2,0.2,-0.1]: squares 0.01,0.04,0.04,0.01; mean 0.025.
- RMSE 0.1581 same units as targets (not squared).
- CE 0.4170 = -log 0.6590; wrong-class-2 CE would be -log 0.0986 = 2.317.
## Pitfalls
- MSE punishes outliers quadratically; MAE/Huber for noisy targets.
- Softmax + CE needs logits (not probs) as input for stability.
- Class imbalance: weight CE terms or resample.
## Connections
- Distillation KL generalizes CE with soft teacher targets.
- RAG faithfulness counts overlap instead of likelihood.
## Exercises
1. Compute CE for true class 2 (answer ~2.32).
2. Show RMSE has the same units as targets.
3. Weight class-0 loss x2 and recompute.
