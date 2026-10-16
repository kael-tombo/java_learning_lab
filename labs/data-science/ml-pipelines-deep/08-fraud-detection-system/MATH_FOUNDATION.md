# Fraud Detection System - Math Foundation

## Precision, recall, F1
- Precision = TP/(TP+FP); recall = TP/(TP+FN); F1 = 2PR/(P+R).
- With TP=80, FP=120, FN=20: P=0.400, R=0.800, F1=0.533.
- Accuracy = (TP+TN)/N is dominated by TN at high skew and hides recall collapse.

## Expected cost
- Cost = FN * cFN + FP * cFP over a fixed window.
- The operating point is the threshold minimizing this sum given capacity limits.
- The 10:1 ratio in the snippet is illustrative; organizations fit their own.

## Label maturity
- Observed fraud at age d is true fraud times labeled-fraction(d).
- Early evaluation multiplies recall down by the maturity fraction.
- Compare windows only at equal maturity ages.

## Threshold monotonicity
- Lowering the threshold weakly raises both TP and FP; precision can move either way.
- The precision-recall curve traced over thresholds is the correct summary, not one point.

## Worked precision shift
- Base triple tp 80, fp 120, fn 20 gives P 0.400, R 0.800, F1 0.533.
- Raising fp to 240: P = 80/320 = 0.250 with recall unchanged at 0.800.
- Reviewer impact: three of four flags innocent, queue load up, trust down.

## Worked cost comparison
- Illustrative 10:1 ratio prices each miss at ten reviews across thresholds.
- Middle threshold totals 320 against 350 and 440: balance beats extremes.
- At 5:1 the review term weighs more; recompute all three before moving.

## Maturity gating math
- A 90%-labeled bar admits only days past the threshold into official metrics.
- Early days multiply observed fraud down by their labeled fraction.
- Windows graduate explicitly; provisional numbers never revise silently.

## Iso-cost reasoning
- Equal-cost lines trade misses against reviews at the fitted ratio slope.
- Steeper ratios (costlier misses) push the operating point toward recall.
- Capacity caps the feasible region: unaffordable bands are off the map.

## Curve over point
- The precision-recall curve over thresholds dominates any single reported pair.
- F1 at one point summarizes the tradeoff there, never the whole frontier.
- Report the curve, mark the operating point, name the ratio behind it.
