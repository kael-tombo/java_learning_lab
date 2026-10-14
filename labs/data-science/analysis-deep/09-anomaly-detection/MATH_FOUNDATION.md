# Math Foundation - Anomaly Detection

## 1. z-score properties

For any distribution, |z| > k flags at most 1/k^2 of points (Chebyshev:
P(|z| >= k) <= 1/k^2, so k = 3 caps at ~11%). Under normality the 3.0
cutoff passes ~0.3%. The gap between the two numbers is why "3 sigma"
means different things on different data - check shape, not folklore.

## 2. Tukey fences

Fences at Q1 - 1.5*IQR and Q3 + 1.5*IQR. On normal data about 0.7% of
points fall outside (a standard fact about the normal quartiles, easy
to confirm by simulation); on skewed data the outer fence flags the
long tail - transform first or accept the asymmetry explicitly.

## 3. Precision, recall, F1

P = TP/(TP+FP), R = TP/(TP+FN), F1 = 2PR/(P+R). Moving the threshold
down monotonically raises R and (after the top) lowers P; F1 peaks
where the harmonic balance sits. PrCurve's three rows are this curve
sampled at three points - plot all thresholds for the full picture.

## 4. Bayes PPV derivation

PPV = P(fraud | flag) = sens*prev / (sens*prev + fpr*(1-prev)). With
prev = 0.001, sens = 0.99, fpr = 0.01: numerator 0.00099, denominator
0.00099 + 0.00999 = 0.01098, ratio 0.0902. Per 100k: 99 true flags vs
999 false ones. Every digit verified by the BaseRate program.

## 5. Why rarity dominates quality

Hold sens = fpr-complement fixed and halve prevalence: PPV roughly
halves too (denominator dominated by fpr*(1-prev) ~= fpr). Conclusion:
below ~1% prevalence, cutting the false-positive rate moves PPV more
than raising sensitivity - engineer specificity first.

## 6. Masking arithmetic

One extreme point inflates sd so its own z shrinks: with ten points
near 10 plus one at 30, sd is 5.739 and z = 3.31 (still flags); add a
second extreme and both z-values collapse under 3. Robust center and
spread (median/MAD) resist because extremes never enter them.
