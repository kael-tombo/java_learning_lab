# 02-logistic-regression - Logistic Regression
## Overview
Binary classifier: p = sigmoid(w.x + b), trained by minimizing cross-entropy with gradient (p - y) x. Decision boundary is the hyperplane w.x + b = 0.
## Key formulas
- sigmoid(z) = 1/(1 + e^-z); d sigmoid/dz = p(1-p).
- Loss: -[y log p + (1-y) log(1-p)]; gradient: (p-y)x, (p-y).
## What the snippets show
- Cml02A: sigmoid table plus CE=0.5516 on fixed predictions.
- Cml02B: GD finds w=4.0066, b=0, mapping +-1.5 to 0.0024/0.9976.
## Try it
Add label noise (flip one y) and watch w shrink and probabilities soften.
## Formula reference
- p = 1/(1 + e^-(w.x + b)); logit = log(p/(1-p)) = w.x + b.
- Loss per sample: -[y log p + (1-y) log(1-p)]; gradients (p-y)x, (p-y).
- Odds ratio e^w per unit x; decision at p = 0.5.
## Worked example
- p = [0.9, 0.2, 0.8] vs t = [1, 0, 1]: terms 0.1054, 0.2231, 0.2231; total 0.5516.
- Separable toy: w = 4.0066 gives logit(1.5) = 6.01, p = 0.9976.
- Symmetry check: sigmoid(-2) + sigmoid(2) = 0.1192 + 0.8808 = 1.0.
## Pitfalls
- Separable data drives ||w|| to infinity; probabilities saturate, not wrong but overconfident.
- Imbalanced classes shift b; consider class weights or threshold tuning.
- Log of 0: clamp p to [eps, 1-eps] in real code.
## Connections
- Cross-entropy reappears in neural net heads and distillation.
- Hinge loss (SVM lab) penalizes margin instead of log-likelihood.
## Exercises
1. Flip one label and confirm w shrinks toward 0.
2. Evaluate p at x = 0 for w = 2, b = 1 by hand.
3. Replace CE with squared error and note the slower learning.
