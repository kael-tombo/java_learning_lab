# 10-anomaly-detection - Anomaly Detection
## Overview
Univariate flags: z-score (|x-mean|/std > threshold) assumes roughly normal data; IQR fences (Q1-1.5 IQR, Q3+1.5 IQR) resist skew. Both are screening rules, not proofs.
## Key formulas
- z = (x - mean)/std; flag |z| > 2 (or 3).
- Fences: Q1 - 1.5 IQR, Q3 + 1.5 IQR.
## What the snippets show
- Cml10A: z=2.44 flags 30, rest |z| <= 0.53.
- Cml10B: fence 15.0 flags the same single point.
## Try it
Replace 30 with 14 and confirm both rules go quiet.
## Formula reference
- z = (x - mean)/std; flag |z| > 2 (~5%) or 3 (~0.3%) under normality.
- IQR fences: Q1 - 1.5 IQR, Q3 + 1.5 IQR; quartiles via sorted order stats.
- Multivariate: Mahalanobis (x-mu)^T S^-1 (x-mu); isolation forests for nonlinear.
## Worked example
- Sum = 95, mean 95/7 = 13.5714; var = 317.714/7 = 45.388, std 6.7370.
- z(30) = 16.4286/6.7370 = 2.44 > 2 flagged; next largest |z| = 0.53.
- Fence 12 + 3 = 15: 30 outside, rest inside.
## Pitfalls
- Mean/std themselves corrupted by outliers (masking); prefer IQR/MAD for screening.
- Threshold 2 vs 3 changes verdicts; calibrate on clean validation.
- Multivariate anomalies hide in margins; check joint views.
## Connections
- z-scores standardize features for SVM/k-means too.
- Robust stats (median/MAD) harden every estimator here.
## Exercises
1. Replace 30 with 14; confirm both rules go quiet.
2. Use threshold 3 and recount flags.
3. Add 60 alongside 30 and observe masking.
