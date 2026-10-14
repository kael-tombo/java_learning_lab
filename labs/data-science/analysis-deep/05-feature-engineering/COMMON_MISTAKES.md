# Feature Engineering - Common Mistakes

## 1. Scaling before splitting

Fitting mean/sd on all six values (37.5) instead of train four (25.0) is the
canonical leak: silent, small-looking, optimism-manufacturing. Split first,
fit second, apply third - order is the entire defense.

## 2. Ordinal-coding nominals

red=0/green=1/blue=2 prices color steps the world never set. Reserve
integers for true orders; one-hot the rest.

## 3. Full-data target means

Level means from all labels memorize; from folds they generalize. The
snippet's warning line exists because this mistake ships weekly somewhere.

## 4. Refitting vocabulary on test

Appending "yellow" at apply shifts no indices here ( Lucky: fallback
exists) - but rebuild-the-map pipelines renumber everything downstream.
Freeze the map; route unknowns to the declared fallback and monitor its rate.

## 5. Log of non-positive values

log(0) = -Infinity, log(negative) = NaN: silent matrix poison. Guard domains
or fit shifts before transforming, and count guarded rows.

## 6. Unscaled interactions dominating

area x rooms reaches 480 beside rooms at 4: raw products hog gradients and
penalties. Interact first, then scale the product like any numeric.

## 7. Min-max with unknown bounds

Future 60 maps to 1.25 - fine if consumers tolerate extrapolation, breaking
if they assume [0,1]. Prefer z/robust when bounds are unknowable; clip only
with logged counts.

## 8. Rare-level one-hot forests

Hundreds of near-constant dummy columns add variance, not signal. Collapse
tails to "other" (fitted on train) before encoding.

## 9. Forgetting the shift constant

log(x + c) with apply-time c != fit-time c silently redefines the feature.
Store c in the parameter object beside mean/sd.

## 10. Scaling the label along with the features

Standardizing the target with train constants then forgetting to invert at
prediction time ships predictions in z-units. Scale features freely, but
keep the label transform explicit, inverted, and tested end to end.
