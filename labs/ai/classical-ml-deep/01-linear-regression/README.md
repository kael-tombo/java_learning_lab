# 01-linear-regression - Linear Regression
## Overview
Ordinary least squares: minimize ||Xw - y||^2. Closed form w = (X^T X)^-1 X^T y; iterative alternative is gradient descent w -= lr * X^T(Xw-y)/n. Fit quality is R^2 = 1 - SSE/SST.
## Key formulas
- Normal equations: X^T X w = X^T y.
- GD update: w -= lr * gradient; R^2 in [0,1] on training data with intercept.
## What the snippets show
- Cml01A: exact 2x2 normal-equation solve (w0=1.5000, w1=0.8000, SSE=1.8000).
- Cml01B: batch GD from zero reaches R^2=0.6320 after 200 steps.
## Try it
Change y to [2,4,6,8] and confirm the closed form returns w1=2, w0=0.
## Formula reference
- Objective: min_w ||Xw - y||^2; gradient 2 X^T(Xw - y)/n.
- Normal equations: X^T X w = X^T y; 2x2 inverse via 1/det [[d,-b],[-c,a]].
- R^2 = 1 - SSE/SST; SST uses mean(y) = 3.5 here, SST = 5.0.
- Standard errors need sigma^2 (X^T X)^-1; not computed in snippets.
## Worked example
- X^T X = [[4,10],[10,30]]: n = 4, sum x = 10, sum x^2 = 30.
- det = 120 - 100 = 20; w1 = (4*39 - 10*14)/20 = 0.8 with X^T y = [14,39].
- Predictions: 2.3, 3.1, 3.9, 4.7; residuals -0.3, -0.1, 1.1, -0.7; SSE = 1.8.
## Pitfalls
- X^T X singular when features collinear: use GD or drop a column.
- R^2 on training data overstates; intercept required for the [0,1] reading.
- GD lr too large diverges; 0.05 works on this scale, not universally.
## Connections
- Logistic regression reuses the linear score inside a sigmoid.
- Regularization adds lambda penalties to this exact objective.
## Exercises
1. Recompute w for y = [2,4,6,8] and confirm w0 = 0, w1 = 2.
2. Raise GD lr to 0.9 and watch the steps diverge.
3. Drop the bias column and explain why the fit degrades.
