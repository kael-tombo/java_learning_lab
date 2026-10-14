# Flashcards - Anomaly Detection

Q: Anomaly vs tail in one line?
A: Anomaly = different mechanism + rare; tail = rare but same mechanism.

Q: z-score formula and conventional cutoff?
A: (x - mean)/sd; flag |z| > 3.

Q: Tukey fences?
A: Outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR].

Q: What is masking?
A: Extremes inflate mean/sd so their own z-scores shrink below cutoff.

Q: Robust alternative to mean/sd?
A: Median and MAD (median absolute deviation).

Q: Isolation intuition?
A: Random splits isolate odd points in few steps, crowds in many;
average depth is the score.

Q: Threshold down -> P? R?
A: Recall rises, precision (eventually) falls.

Q: PPV formula?
A: sens*prev / (sens*prev + fpr*(1-prev)).

Q: Base-rate demo numbers?
A: prev 0.001, sens 0.99, fpr 0.01 -> PPV 0.0902; 99 true vs 999 false
per 100k.

Q: Rarity vs quality lesson?
A: Below ~1% prevalence, cutting fpr moves PPV more than raising sens.

Q: Chebyshev bound at k = 3?
A: At most 1/9 (~11%) beyond |z| = 3 for any distribution.

Q: Normal data outside Tukey fences?
A: About 0.7% - more flags than that signals non-normality.

Q: Alert fatigue mechanism?
A: Low-precision paging trains on-call to mute; then real pages die too.

Q: Fix for fatigue?
A: Tiers (page/batch/log), costs-picked thresholds, outcome logging,
scheduled re-fits.
