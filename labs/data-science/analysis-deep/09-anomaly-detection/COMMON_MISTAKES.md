# Common Mistakes - Anomaly Detection

1. Fixed cutoff worship. |z| > 3 is a starting convention, not a law -
   shape, masking, and costs all move the right line.
2. Fitting on incidents. Training the "normal" Window on outage data
   teaches the detector to bless failures.
3. Ignoring masking. One sd-based check on extreme-laden data protects
   the extremes; pair with IQR/robust-z always.
4. Threshold by gut. Un-swept thresholds hide the P/R tradeoff from the
   people paying its costs - sweep and show the table.
5. Forgetting prevalence. A 99/99 detector at 0.1% prevalence is 90%
   false pages; quote PPV at production volumes before launch.
6. Chasing sensitivity. Below ~1% prevalence, halving fpr beats raising
   sens - engineer specificity first.
7. Univariate-only vision. Joint anomalies pass every marginal fence;
   keep an isolation/multivariate second opinion.
8. Paging everything. Single-tier alerting burns on-call in weeks; tier
   page/batch/log with runbooks per tier.
9. Set-and-forget baselines. Drifting bulks rot precision silently;
   calendar re-fits with precision reviews.
10. Grading your own homework. Precision-at-k needs independent graders
    plus a rubric - self-graded detectors always pass.

11. Grading with the detector's own labels. Auto-confirmed flags ("it
    flagged, so it was right") circularly inflate precision - independent
    graders plus a rubric, or the number is fiction.
12. Sampling the sweep. Sweeping thresholds on a non-random "interesting"
    subset biases P/R toward the dramatic - sweep on consecutive labeled
    history, boring stretches included.

Rule of thumb: if PPV at production volumes is not on the launch slide,
the launch is not ready - compute it or postpone.

13. Tuning on the incident you must catch. Thresholds fit to one famous
    outage overfit to its shape - sweep on representative history, then
    confirm the famous case is caught, in that order.
