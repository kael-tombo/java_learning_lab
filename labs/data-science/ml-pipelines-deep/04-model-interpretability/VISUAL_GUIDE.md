# Model Interpretability — Visual Guide

## Global vs local
```
global:  which features matter overall?  -> permutation ranks, PDP curves
local:   why this prediction?            -> LIME coefficients, SHAP shares
```

## Permutation importance (demo)
```
baseline:  6/6 correct = 1.0
shuffle x1 (reverse): 4/6 = 0.6666666666666666
importance = 1.0 - 0.6667 = 0.33333333333333337
```

## Shapley split (demo game)
```
orders:  (1,2): margins 4, 6     (2,1): margins 7, 3
phi1 = (4+7)/2 = 5.5    phi2 = (3+6)/2 = 4.5
sum 10.0 = v({1,2}) -> efficiency holds
pie:  [player1 55% | player2 45%] of the 10.0 total
```

## LIME surrogate (demo f(x)=x^2 at x0=2)
```
true curve:  parabola, gradient 4 at x0
samples:     x0 + {-0.4..0.4}, gaussian kernel width 0.3
fit:         slope 3.9999999999999982 ~= 4, intercept 4.0571
picture:     tangent line hugging the curve near x0, drifting far away
```

## Stability sketch
```
kernel 0.3 -> slope ~4.00
kernel 0.6 -> slope moves (wider view, more curvature averaged in)
lesson: the coefficient is a function of settings, not just the model
```
