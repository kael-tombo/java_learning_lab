# Feature Engineering - Why It Exists

## Models speak numbers, data speaks otherwise

Regressors multiply magnitudes, regularizers penalize them, gradient steps
scale with them - none accepts "blue" or "N/A" as input. Feature engineering
exists as the translation bureau between human-recorded columns and numeric
matrices: encodings for categories, scalings for magnitudes, transforms for
skew, products for combinations. Without it, most columns cannot enter most
models at all.

## Raw magnitudes mislead optimizers

Area 120 beside rooms 4: one gradient step sized for areas explodes rooms,
one sized for rooms crawls on areas. Scaling to comparable units (z 1.41 vs
rooms-scale) exists because optimization geometry, not statistics, demands
it - the demo's three lenses are three answers to "comparable to what?".

## Skew breaks linear assumptions gently, then suddenly

Right-tailed predictors exert lever-arm influence far beyond their count:
three areas 50/80/120 already span 2.4x. Logs and Box-Cox exist to compress
tails before they wag the fit - Tukey's re-expression ladder made this
routine half a century ago, and it still rescues linear models weekly.

## Combinations need constructing

No linear model discovers area-x-rooms on its own; the product must be
built (100/240/480) to be priced. Interactions exist because the world
prices bundles, not just parts - big-many-roomed houses exceed the sum -
and the builder, not the fitter, decides which bundles to offer.

## Leakage did not exist before pipelines

Hand-fit single models leak less: the analyst sees every number. Automated
pipelines with hidden fit stages leak by default - imputers, scalers, and
encoders all "just run" on whatever data they are handed. The fit/apply
separation exists because automation removed the human witness; the
parameter store and the split-first rule put a witness back in code.

## Translation quality compounds downstream

Model selection, tuning, and ensembling all assume features mean what they
claim. One invented ordinal, one leaky scaler, one unscaled product - each
quietly biases every comparison built on top. Translation done carefully
once pays off across hundreds of downstream fits; done carelessly, it taxes
all of them.
