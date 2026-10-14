# Visual Guide - Anomaly Detection

## 1. Histogram with fences

Bulk histogram plus vertical lines for mean +/- 3sd and Tukey fences.
Agreement (lines near each other) vs disagreement (z wide from masking)
is visible in one glance.

## 2. Boxplot per segment

Box per hour/device/version with whiskers at the fences; points beyond
are the flags. Segmented boxes localize the anomaly source faster than
any global list.

## 3. Score-ordered strip

Points ranked by score with true labels colored; the threshold as a
sliding line. Dragging it (mentally) shows TP/FP/FN counts shifting -
the tradeoff made tactile.

## 4. P/R tradeoff curve

Recall on x, precision on y, thresholds annotated (0.8/0.5/0.2 from
PrCurve). Stakeholders point at the curve where costs bite - the
operating point picks itself.

## 5. Bayes waterflow

Sankey-style flow: 100k events -> 100 true cases + 99900 normal ->
99 + 999 flags -> PPV 9% pool. Widths proportional; nobody forgets the
999 after seeing the band.

## 6. Alert-tier dashboard

Three lanes (page/batch/log) with volumes, precision-at-reviewed, and
time-to-triage per lane. Drift shows as lane migration - medium
swelling means the bulk moved.

## 7. Drift strip

Center/spread bands over calendar time with re-fit markers; flag-rate
line below. Drift shows as the bulk walking out of its bands weeks before
precision visibly dies - the strip is the early warning.

## 8. Incident replay strip

Timeline of a caught incident: score trace, threshold line, tier actions
with timestamps. Replays train new on-call faster than any runbook and
expose where minutes were actually lost.
