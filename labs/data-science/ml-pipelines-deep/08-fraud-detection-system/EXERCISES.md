# Fraud Detection System - Exercises

1. Run A08Metrics; raise fp to 240 and recompute precision/recall/F1.
   - Expect precision near 0.25 with recall unchanged; explain the reviewer impact.
2. In B08Cost, change the cost ratio to 5:1 and find the new minimum-cost threshold among the three points.
   - Recompute all three costs and name the winner; compare with the 10:1 answer.
3. Extend C08Lag with a maturity rule: compute metrics only on days with 90% or more labels.
   - Print which days qualify and the resulting evaluation window.
4. Implement the rule layer: two deterministic rules that short-circuit before model scoring.
   - Count rule hits versus model-scored cases on a twenty-row inline dataset.
5. Split ten features into inline vs async by a 5 ms budget with measured per-feature costs.
   - Document the safe default for each async feature when its value is missing.
6. Build a review queue: order ten scored cases by score, take the top 4, and compute precision in that band.
   - Report band precision separately from overall precision.
7. Simulate adversarial shift: move a fraud cluster in feature space and show which rule stops firing.
    - Report rule-hit rate before and after the shift.
8. Price a threshold move: given flag counts at three thresholds with the 10:1
   illustrative ratio, recompute expected cost and confirm the middle wins at 320.
    - Show all three cost lines; state which term dominates each extreme.
9. Size the review band from staffing: given decisions per hour and expected flag
   rate, compute the widest band reviewers can clear before cases age out.
    - Report band width, expected queue depth, and the overflow threshold.
10. Reconcile reviewer labels: given ten review decisions and later dispute outcomes,
    compute reviewer precision and name the cases reviewers missed.
    - Expect disagreement on at least one; report precision separately.
11. Split a blended feature set: given per-feature lookup costs and a 5 ms inline
    budget, choose the inline set maximizing coverage without breaching the cap.
    - Document async fallbacks for every excluded feature.
12. Detect rule decay: given twelve weeks of hit rates for three rules, flag the
    decaying rule and propose its replacement scope.
    - Report hit-rate slopes, not just endpoints, for each rule.
13. Audit a decision trail: given a blocked transaction record, verify score, rule
    hits, feature snapshot, and model version are all present and consistent.
    - Reject incomplete trails in writing, naming the missing evidence.
14. Run the adaptation drill: introduce a shifted fraud cluster, watch rule hits
    decay, ship an emergency rule, then confirm score mix stabilizes.
    - Log hit rate before, during cover, and after retraining separately.
   - Report rule-hit rate before and after the shift.

## Submission check
- All programs compile with `javac --release 21 -encoding UTF-8` and print pure ASCII; no real fraud figures are used anywhere.
