# Fraud Detection System - Interview Questions

1. Why is accuracy misleading for fraud?
   - Extreme skew lets always-legitimate score highly while catching nothing at all.
2. How do you pick a threshold?
   - Minimize expected cost of misses versus reviews within review capacity.
3. Rules versus model: how do they split work?
   - Rules cover known patterns instantly; the model generalizes; review handles uncertainty.
4. What belongs in the request path?
   - Only cheap features, rules, and the warmed model; slow lookups stay async.
5. How does label delay distort evaluation?
   - Fresh windows undercount fraud; use mature windows for official metrics.
6. What is adversarial adaptation?
   - Attackers change behavior after blocks, so rules and features need refresh.
7. Queue overflows: options?
   - Tighten the band, order by risk, add reviewers, add emergency rules.
8. How do you detect train/serve skew?
   - Compare logged serving features against training values on overlap traffic.
9. What must never leak to callers?
   - Thresholds and rule internals; responses stay generic while logs stay detailed.
10. Fallback on feature timeout?
    - Safe default decision plus an alert, never an unbounded wait.
11. How do you size a review band from staffing?
    - Flag rate times decisions per hour against reviewer throughput; overflow sets the edge.
12. What reconciles reviewer labels with truth?
    - Mature dispute outcomes joined by key; reviewer precision is the tracked gap.
13. How do you split features across the latency budget?
    - Measure per-feature cost; inline what fits, precompute the rest with safe defaults.
14. What signals adversarial shift first?
    - Rule-hit decay and score-mix movement before labeled metrics can confirm.
15. Why version rules and thresholds like code?
    - Instant revert during attacks; unauthorized edits are direct fraud enablers.
16. What does band precision tell you that overall precision hides?
    - Whether reviewers' actual workload is fraud-dense or flood-diluted.
17. When does retraining start after a new attack pattern?
    - After labels mature; emergency rules cover the gap, never provisional labels.

## How to answer
- State the skew-aware reasoning first, then the latency and capacity constraints.
