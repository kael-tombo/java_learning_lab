# Feature Engineering - Reflection

## Prompts

1. Test 100 scores z 6.71 honestly, ~4.9 leaked. A manager calls both
   "standardized, so comparable". Correct them in two sentences.
2. Colors must enter a regularized linear model with n = 200 and 3 levels.
   One-hot or target encoding? Defend with the bias/variance trade, not
   fashion.
3. Your log(area) helped; a teammate proposes log(rooms) too (rooms 2,3,4).
   Evaluate: what does log buy on {2,3,4}, and what does it cost in
   interpretation?
4. Design the fold-nested target encoding for 5-fold CV in six bullet
   steps, naming exactly which rows each mean sees.

## Self-check sketches

1. "Standardized against different worlds: 6.71 measures from train-only
   constants (new data judged by old rules); 4.9 let the new point move the
   ruler. Only the first generalizes."
2. One-hot: 3 levels cost 2-3 columns at n = 200 - affordable, unbiased, no
   label use. Target encoding spends label information to save 2 columns:
   bad trade at this size; revisit past hundreds of levels.
3. log buys little (2-4 span is already linear-scale) and costs the natural
   "per room" reading; skip it - transforms must earn their distortion, and
   near-symmetric small-range variables rarely pay.
4. Split into 5 folds; for fold k compute smoothed means on the other 4;
   apply to fold k; repeat for all 5; fit final encoder on full train for
   test; never let any mean see its own applied rows.

## Habits worth keeping

- Split before fit, always; say "fit on train" out loud when writing it.
- Count unknowns and out-of-range values at every apply - drift announces
  itself there first.
- Keep the six-number demo (means 25.0/37.5, z 6.71) as the pocket parable
  for any leakage debate.
