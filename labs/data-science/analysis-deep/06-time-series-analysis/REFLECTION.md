# Reflection - Time Series

## Self-check prompts

- Can I define stationarity without notes, and explain why AR(1) needs
  |phi| < 1?
- Given an ACF/PACF pair, can I argue for AR vs MA structure in words?
- Do I difference before reading order hints, and can I say why?
- Is my validation strictly past-vs-future with no transform leakage?
- Did my model beat seasonal-naive, and by how much, on which horizon?

## What surprised you

Write two sentences on the most surprising verified output (many pick
the TsErrors zero-skip or the TsAcf lag-2 spike) and why it surprised
you before you understood the mechanism.

## Error honesty

List one analysis where you could have picked the friendlier metric.
What did reporting MAE, RMSE, and MAPE together change about the story?

## Next step

Pick one: seasonal decomposition of a real monthly series, or a rolling
backtest comparing naive against drift. State the horizon first, then
run it - horizon choice before results is the discipline this lab
teaches.

## Teach-back test

Explain to a colleague why shuffling is leakage using only the quarantine
metaphor and one hand-drawn rolling-origin sketch. If they cannot repeat
the argument, the understanding is yours, not theirs - reteach until the
sketch survives without you.

## Commitment line

Write one sentence starting "In my next forecast I will..." naming a
single practice (tail holdout, baseline table, MAPE policy). Sign and
date it. Vague resolutions ("do better validation") do not count.

## Mistake journal

Log every forecasting mistake with two fields: which checkpoint-table
row was skipped, and what it cost. After ten entries the skipped row
with the highest total owns your next month of practice - data-driven
study, applied to yourself.
