# Model Monitoring - Math Foundation

## PSI
- PSI = sum over bins of (a_i - e_i) * ln(a_i / e_i), with e reference shares and a current shares.
- Each term is nonnegative; the sum is zero only for identical distributions.
- Derivation: symmetrized per-bin log-ratio weighted by share difference. Shares must be positive.

## KS statistic
- Empirical CDF F(t) = fraction of sample <= t; D = max_t |F_ref(t) - F_cur(t)|.
- Evaluated on the pooled sorted grid; no binning choice needed.
- D lies in [0, 1]; larger means the samples differ more somewhere.

## Alert precision and recall
- Precision = TP/(TP+FP); recall = TP/(TP+FN) over an incident set.
- Threshold moves both monotonically in opposite directions.
- F1 = 2PR/(P+R) summarizes one operating point, not the whole tradeoff.

## Windowing
- Fixed windows give independent comparisons; sliding windows overlap and correlate.
- Short windows raise variance as 1/n; long windows delay detection by their length.

## Worked PSI term
- One bin with e = 0.10 and a = 0.12 contributes (0.02) * ln(1.2) = 0.0036.
- Terms are nonnegative and zero only when a equals e exactly.
- The snippet total 0.0378 is about ten such bins, here concentrated in two.

## Worked alert tradeoff
- Snippet precision 0.300 with recall 0.750 gives F1 = 0.429 at that point.
- Halving fp raises precision; doubling fn lowers recall; F1 follows the pair.
- Report the triple (P, R, F1) per threshold instead of a single headline number.

## Sample-size scaling
- Window variance shrinks as 1/n; doubling samples narrows bands by 1/sqrt(2).
- Short windows react in hours but page on noise; long windows smooth but delay.
- The fast-dashboard plus gated-alert pair splits these duties deliberately.

## Maturity gating
- Official mean over mature windows excludes the young, unlabeled tail.
- As each window graduates, the official series extends by exactly one point.
- Provisional points never revise history silently; graduation is explicit.

## Gap location use
- KS reports where distributions differ most, not just how much.
- The x of the maximum gap selects the first slice and bin to inspect.
- PSI then attributes the shift across bins for the engineer-readable story.
