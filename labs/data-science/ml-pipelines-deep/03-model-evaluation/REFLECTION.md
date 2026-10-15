# Model Evaluation — Reflection

## What surprised you?
That every headline number in the demo (0.8, 0.23617, 0.055) is only
half the story without its reference: the matrix behind the rates, the
baseline behind the scores, the fold composition behind the mean.
Evaluation is comparative or it is nothing.

## Check your understanding
- Can you derive all four rates from 4/1/4/1 without looking, and
  explain the ...002 in the F1 print?
- Can you recompute Brier 0.055 from (0.01+0.01+0.04+0.16)/4?
- Can you explain why both folds hold exactly 2 positives using the
  round-robin argument?

## Connect to your own work
Take the last classifier you evaluated. Did you score test once or
peek repeatedly? Was preprocessing fit on train only? Which baseline
did you beat, and by how much? Rewrite its one-page report in the
matrix-first shape from STEP_BY_STEP.

## What to do next
- Add calibration binning to the LogLossBrier demo (3 bins) and read
  predicted vs observed per bin.
- Sweep a threshold over toy scores and hand-plot one ROC and one PR
  curve to feel their different sensitivities.
- Read the Hastie et al. cross-validation chapter and map each caution
  to a pipeline enforcement.

## One-sentence takeaway
Honest evaluation is a discipline of references — matrix, baseline,
folds, locked splits — that keeps every performance claim checkable.
