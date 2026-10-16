# Model Interpretability — Math Foundation

## 1. Permutation importance arithmetic
Baseline 6/6 = 1.0; permuted 4/6 = 0.6666666666666666:

  importance = 1.0 - 4/6 = 2/6 = 1/3 = 0.33333333333333337 (observed)

The repeating decimal is exact rational 1/3 in binary floating point.
Importance is a difference of two rates on the same rows — paired
comparison, not two independent samples.

## 2. Shapley derivation for 2 players
Orders and margins with v({})=0, v({1})=4, v({2})=3, v({1,2})=10:

  order (1,2): m1 = 4-0 = 4, m2 = 10-4 = 6
  order (2,1): m2 = 3-0 = 3, m1 = 10-3 = 7
  phi1 = (4+7)/2 = 5.5, phi2 = (3+6)/2 = 4.5

Efficiency: 5.5+4.5 = 10.0 = v({1,2}) - v({}). The 0.5 weights are
1/2! per order — the uniform average over joining orders.

## 3. Weighted least squares (LIME surrogate)
Minimize sum_i w_i (y_i - a - b dx_i)^2. Normal equations give:

  b = (Sw Sxy - Sx Sy) / (Sw Sxx - Sx^2)
  a = (Sy - b Sx) / Sw

with Sw, Sx, Sy, Sxx, Sxy the w-weighted sums. Demo yields b =
3.9999999999999982 against truth 4.0. Symmetric dx with symmetric
weights makes Sx ~ 0, so b ~ Sxy/Sxx: covariance over variance.

## 4. Why the intercept exceeds f(x0)
For convex f, weighted average of f(x0+dx) exceeds f(x0) (Jensen).
Observed intercept 4.0571 > 4.0 is that lift: the line anchors to
lifted neighbor values while the slope still matches the tangent.

## 5. PDP as a conditional average
PDP(x_s) = mean over background of f(x_s, x_c). It is an expectation
over the empirical background distribution — change the background,
change the curve. No background, no PDP reading.
