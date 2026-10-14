# Feature Engineering - Mental Models

## 1. Translation, not invention

Features translate what was measured into what the model can use: colors to
vectors, skewed areas to compressed scales, pairs to products. Good
translation preserves meaning across the conversion (counts recoverable from
one-hots); bad translation editorializes (ordinal numbers for nominal
colors invent an order).

## 2. Fit is learning; apply is plumbing

Fitting estimates something about the world (train mean 25.0); applying
routes new data through that estimate. Leakage is letting the future vote
in the estimate (mean 37.5). Keep the two verbs separate in code and in
speech, and most leakage bugs become sayable before they become shippable.

## 3. Scaling as unit conversion

z-scores convert to "train-sd units": test 100 reads as 6.71 sd from home -
an interpretable distance, not just a big number. Like currency conversion,
the rate must come from the home economy (train), never from a mix
including the purchase being converted.

## 4. Target encoding as borrowing answers

Replacing a level by its mean outcome borrows the answer sheet to write the
question. Borrowed inside train folds with smoothing, it generalizes; handed
the full sheet (all-data means), it memorizes. The suspicion to cultivate:
any feature built from labels is guilty until folded.

## 5. Interactions as chemistry

Area and rooms combine like reagents: the product captures what neither has
alone (big AND many-roomed). But chemistry explodes combinatorially - every
product is a new dimension that must earn its keep against overfitting, and
unscaled products dominate purely by magnitude.

## 6. The parameter store as a contract

Frozen constants are a signed contract between fit-time and apply-time:
same numbers, same columns, same fallbacks. Breaking the contract (refit,
reorder, rescale) voids every validation result downstream of it.
