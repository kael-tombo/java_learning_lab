# Feature Engineering - Flashcards

## Q1. One-hot red with vocabulary [red, green, blue]?

A: [1, 0, 0] - unit vector at the level's index; no order, no distances.

## Q2. When is ordinal encoding valid?

A: Only for genuinely ordered levels (small < medium < large). On nominal
colors it invents an order the model prices as real.

## Q3. What is target encoding, and its rule?

A: Level replaced by (smoothed) mean target. Rule: fit inside train folds
only, never on full labels - otherwise the answer leaks into the question.

## Q4. Min-max of 20 on {10..50}?

A: (20-10)/40 = 0.25. Full map: 0, 0.25, 0.5, 0.75, 1.0. New extremes break
the [0,1] range.

## Q5. z of 10 on {10..50}?

A: (10-30)/14.142135623730951 = -1.414213562373095. Train mean 0, variance
1 by construction.

## Q6. Robust scaling formula and demo?

A: (x - median)/IQR: demo maps to -1.0..1.0 exactly. Immune to tails up to
50% contamination (median breakdown point).

## Q7. Train-only numbers?

A: Fit mean 25.0, sd 11.180339887498949 on {10,20,30,40}; test 25 -> 0.0,
test 100 -> 6.7082039324993685. Leaky all-data mean 37.5 is the warning.

## Q8. Why does leakage mute alarms?

A: Test-shaped constants (37.5) pull extremes toward center: z 6.71 honest
vs ~4.9 leaky. The outlier looks less outlying because it voted.

## Q9. Log areas 50/80/120?

A: 3.912023005428146, 4.382026634673881, 4.787491742782046. Span compresses
2.4x to 1.22x; requires positive inputs.

## Q10. Interaction products for the housing rows?

A: 100.0, 240.0, 480.0 (area x rooms). Lets linear models price bundles
beyond sums of parts.

## Q11. What is the hashing trick?

A: hash(level) into fixed width: bounded memory, no vocabulary, random
collisions. Good for wide linear text models; bad for exact identities.

## Q12. Encode/scale/interact in what order?

A: Encode, transform skew, interact, scale - interactions of raw magnitudes
before scaling get their fair (not dominant) weight.

## Q13. Smoothed target formula?

A: (k*levelMean + m*global)/(k + m): A(2/10) with m=10, global 0.5 gives
0.35. m is the prior strength (Bayes flavor).

## Q14. Box-Cox in one line?

A: Fitted power transform (Box and Cox 1964) generalizing log (lambda = 0);
turns transform-picking from craft into estimation.
