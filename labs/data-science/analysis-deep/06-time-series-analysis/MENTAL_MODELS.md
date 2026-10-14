# Mental Models - Time Series

## 1. Memory with fading echoes

Today = weighted echo of recent days plus fresh noise. AR phrases it as
echoes of values, MA as echoes of shocks - same intuition, two doors.

## 2. Stationarity as a level playing field

You can only learn "typical behavior" if typical stays put. Trend means
the field itself is moving; differencing stops the field so you can
study the game.

## 3. ACF/PACF as an X-ray

ACF shows all ripples including secondhand ones; PACF filters to the
direct bone at each lag. Cutoffs tell you how many bones matter.

## 4. The future quarantine

The test tail is quarantined: nothing learned past its border may cross
back. Every leak (scaling on full data, shuffling) breaks quarantine.

## 5. Baselines as sparring partners

Naive and seasonal-naive are the gym partners your model must beat
daily. If it cannot win the easy rounds, it is not ready.

## 6. Horizon fog

Each step ahead adds fog. Near forecasts are headlights, far ones are
guesses in mist - intervals must visibly widen.

## 7. Residuals as the conscience

Leftover pattern in residuals is the model confessing incompleteness.
White-noise residuals are a clean conscience, not proof of truth.

## 8. Differencing as stopping the escalator

Trend is an escalator: measuring step patterns while riding confuses
motion with structure. Differencing steps off onto solid floor - the
remaining wiggles are the series' own, readable at last.

## 9. Baselines as the null hypothesis

Every model is a claim ("structure beyond last-value memory exists").
Naive is the null; rolling error is the test statistic. Ship only on
rejection - otherwise the claim is fashion.
