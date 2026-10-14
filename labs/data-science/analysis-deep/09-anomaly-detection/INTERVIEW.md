# Interview Q&A - Anomaly Detection

Q: z-score vs IQR - when which?
A: z for symmetric bulk with few extremes; IQR when extremes may mask
(mean/sd dragged) or the shape is skewed. Disagreement between them is
diagnostic, not a tie to break arbitrarily.

Q: What is masking? Show it.
A: Extremes inflate sd, shrinking their own z: one 30 among tens flags
(z 3.31), two 30s can both slide under 3 while IQR still catches them.

Q: State the base-rate fallacy with numbers.
A: prev 0.001, sens 0.99, fpr 0.01 -> PPV 0.0902; 99 true vs 999 false
per 100k. Rarity beats quality - specificity first.

Q: How do you pick a threshold?
A: Sweep to a P/R table, apply miss-vs-false-page costs, pick the row -
and tier the response around it rather than betting on one line.

Q: Explain isolation scoring simply.
A: Random-feature random-split trees: odd points isolate in few splits,
crowds need many. Mean depth over trees is the score. Intuition only.

Q: Detector pages 50x/night, mostly false. Fix?
A: Raise threshold per costs, tier (batch medium, log low), add
auto-remediation for known signatures, track precision-at-reviewed.

Q: No labels at all. Evaluate how?
A: Operator-graded top-k (precision-at-20/50) plus injected synthetic
anomalies for recall probes - state both as estimates, not truth.

Q: Bulk drifts after a product change. Symptom and fix?
A: Flag rate jumps with falling precision; re-fit the Window on the new
normal and re-sweep thresholds on schedule.

Q: IQR flags 8% of traffic. Normal?
A: No - ~0.7% is the normal-data rate. 8% means skew, a shifted bulk, or
a broken feed: transform, re-fit the Window, or fix the source before
tuning thresholds.

Q: Precision-at-20 is 0.1 with no labels. Ship to paging?
A: No: ship to batch review with grading, accumulate labels, re-sweep.
Paging at 0.1 precision burns on-call in a fortnight - tiers first.
