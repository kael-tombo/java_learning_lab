# Fraud Detection System - Common Mistakes

1. Tuning on accuracy at extreme skew, shipping a model that catches nothing.
   - Fix: tune and report precision, recall, and cost at the operating point.
2. Picking thresholds without review-capacity math, overflowing the queue on day one.
   - Fix: size the band from decisions-per-hour against expected flag rate.
3. Putting slow features in the request path and blowing the latency budget.
   - Fix: precompute slow signals async; serve inline from a fast store.
4. Evaluating on provisional labels and mistaking label lag for model decay.
   - Fix: official metrics on mature windows; provisional clearly marked.
5. Hard-coding thresholds or rules without versioning, blocking rollback.
   - Fix: version rules and thresholds like code with instant revert.
6. Revealing decision details to callers, helping attackers probe the boundary.
   - Fix: generic outcomes outside; internals stay in audited logs.
7. Ignoring adversarial adaptation; rules rot while attackers adjust.
   - Fix: scheduled rule and feature reviews driven by hit-rate trends.
8. Training on serving-skewed features from a divergent feature path.
    - Fix: single shared feature code path pinned in lineage.
9. Scoring every transaction with the model while rules could short-circuit.
    - Fix: order rules first; model compute is for traffic rules cannot decide.
10. Ordering review queues by arrival instead of risk.
    - Fix: score-plus-value ordering so scarce reviews hit the riskiest cases first.
11. Retraining the moment an attack starts, on immature labels.
    - Fix: emergency rules cover tonight; retraining waits for mature windows.
12. Using one threshold for all segments with different fraud mixes.
    - Fix: segment-aware bands where volume justifies them; global default otherwise.
13. Dropping rule-hit monitoring after the model ships.
    - Fix: rule hit rates are the adversarial tripwire; watch them permanently.
14. Letting safe defaults go unalerted until they dominate decisions.
    - Fix: alert on fallback rate; defaults are for survival, not operation.
15. Treating reviewer labels as ground truth without dispute outcomes.
    - Fix: reconcile reviews against mature dispute results; track reviewer precision.
   - Fix: single shared feature code path pinned in lineage.

## Review habit
- Weekly: queue depth, review precision, rule hits, score mix, label maturity.
- Monthly: threshold math re-fit against current review capacity.
