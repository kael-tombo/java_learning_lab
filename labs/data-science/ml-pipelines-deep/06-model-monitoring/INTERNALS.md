# Model Monitoring - Internals

## PSI computation
- Bin the variable identically for reference and current windows; use shares, not counts.
- Per-bin term is (actual - expected) * ln(actual / expected); the sum is the PSI.
- The snippet PSI of 0.0378 comes mostly from bins 0 and 3 shifting share.
- Empty bins need smoothing or merging; ln(0) is undefined.

## KS computation
- Build both empirical CDFs on the pooled sorted grid of observed values.
- The statistic is the maximum absolute CDF gap; the snippet finds 0.250 at x=0.52.
- KS reacts to any distributional change but says nothing about which direction matters.

## Alert tradeoff
- Precision = TP/(TP+FP) over alerted incidents; recall = TP/(TP+FN) over real incidents.
- The snippet precision of 0.300 with recall 0.750 describes a noisy but sensitive monitor.
- Moving a threshold trades one for the other; there is no setting that maximizes both.

## Windowing
- Fixed windows give comparable statistics; sliding windows react faster but correlate.
- Reference windows stay pinned until deliberately refreshed, or every comparison drifts.
- Short windows are noisy; long windows are slow. Pair a fast dashboard with gated alerts.

## Smoothing and stability
- Shares must be positive: merge sparse bins or add a small epsilon before the log.
- Bin count moves PSI; report the binning beside the value or comparisons mislead.
- Sample size moves both statistics; small windows produce jumpy trends.

## Reading the snippet values
- PSI 0.0378 led by bins 0 and 3 means two share shifts dominate; the rest is quiet.
- Shifting bin 3 from 0.08 to 0.12 roughly doubles PSI with that bin dominating.
- KS 0.250 at x = 0.52 locates the gap; the x value starts the slice hunt.
- Precision 0.300 at recall 0.750 gives F1 = 2 * 0.3 * 0.75 / 1.05 = 0.429.

## Threshold mechanics
- Tightening a threshold converts some TP to FN and some FP to TN: recall falls, precision rises.
- Halving fp while doubling fn (the exercise) demonstrates the trade numerically.
- No threshold maximizes both; the operating point follows incident cost, set qualitatively.

## Maturity arithmetic
- Windows younger than the maturity bar are excluded from the official mean.
- Excluding them moves the mean toward joined reality, as the exercise shows.
- Recompute as labels land; each window graduates exactly once.
