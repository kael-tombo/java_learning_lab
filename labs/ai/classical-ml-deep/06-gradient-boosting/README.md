# 06-gradient-boosting - Gradient Boosting
## Overview
Sequential additive model: each weak learner fits the negative gradient (residuals for squared loss), scaled by learning rate and added to the ensemble. Shrinkage trades steps for generalization.
## Key formulas
- Squared loss: residual r = y - F; update F += lr * h(x).
- Absolute loss gradient is the sign; its constant minimizer is the median.
## What the snippets show
- Cml06A: one boosting step cuts SSE 5.00 -> 1.2500.
- Cml06B: median SAE 10.0 beats mean-based SAE 12.0 under an outlier.
## Try it
Set lr=1.0 in Cml06A and confirm SSE hits 0 in one step (overfit on this toy).
## Formula reference
- Additive: F_m = F_{m-1} + lr h_m; h_m fits -dL/dF (residuals for squared loss).
- Squared: r = y - F; absolute: sign(y - F); Newton step needs hessian.
- Shrinkage lr < 1 requires more trees M; depth caps interaction order.
## Worked example
- F0 = 3.5; residuals [-1.5,-0.5,1.5,0.5]; lr 0.5 adds half each back.
- New preds: 2.75, 3.25, 4.25, 3.75; SSE = 0.5625 + 0.0625 + 0.5625 + 0.0625 = 1.25.
- Median of [1,2,3,10] is 2.5 (mean of middle two for even n: (2+3)/2).
## Pitfalls
- Too many trees overfit; early-stop on validation.
- lr = 1 memorizes this toy; real data needs 0.01-0.1 + subsampling.
- Squared loss chases outliers; absolute/Huber resists them.
## Connections
- Random forest reduces variance in parallel; boosting reduces bias sequentially.
- Residual idea mirrors ResNet skip connections conceptually.
## Exercises
1. Run lr = 1.0 and confirm one-step SSE = 0.
2. Fit two stump rounds on residuals by hand.
3. Swap in absolute loss and find the first update.
