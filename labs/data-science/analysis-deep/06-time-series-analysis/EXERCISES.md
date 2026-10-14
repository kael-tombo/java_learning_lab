# Exercises - Time Series

## 1. Difference a quadratic trend (runnable)

Take y = {1, 4, 9, 16, 25, 36}. First-difference it, then difference
the differences. Show the second differences are constant (2.0) and
explain why this means d = 2 suits a quadratic trend.

## 2. Beat seasonal-naive (runnable)

Series (period m = 4): {8, 6, 7, 9, 9, 7, 8, 10}. Forecast the last
two points with seasonal-naive (m = 4) and with plain naive. Compute
MAE of each over those two points and state which wins and why.

## 3. ACF cutoff hunt (runnable)

Extend TsAcf to lags 1..6 on {2, 8, 3, 9, 4, 10, 5, 11, 6, 12}.
Confirm even lags stay positive while odd lags turn negative, and
connect that to the series' zigzag shape.

## 4. MAPE trap (runnable)

Compute MAPE on actual {5, 0, 5} with pred {4, 1, 6} twice: once
skipping the zero (correct) and once substituting 0.001 for it.
Report both numbers and explain why the substitution is dishonest.

## 5. Rolling-origin backtest (runnable)

On {3, 5, 4, 6, 5, 7, 6, 8}, do rolling origins at t = 5 and t = 6
with a naive forecast of the next point. Average the two absolute
errors and compare with the single tail error at t = 7.

## 6. Residual whiteness check (paper)

Given residual ACF lags 1..4 = {0.05, -0.08, 0.03, 0.10} at T = 100,
use the +/-1.96/sqrt(T) band to decide whether the residuals look
like white noise. State the band value first.

## 7. Drift baseline (runnable)

On {2, 4, 6, 8, 10}, forecast the next point with mean (6.0), naive
(10.0), and drift (last + mean diff = 12.0). If the true next is 12,
rank the three by absolute error and state which structure drift exploits.

## 8. Variance-stabilizing choice (paper)

Levels {100, 200, 400, 800} double each step with seasonal swings that
double too. Argue additive vs multiplicative decomposition in three
lines, then state the transform (log) that makes the additive form fit.
