# Model Serving - Step by Step

1. Freeze the model artifact and assign it a version string.
   - Record training data version, code commit, and parameters alongside.
2. Define request and response schemas, including units and missing-field policy.
   - Unknown fields are ignored or rejected per the versioned contract, never guessed.
3. Build preprocessing shared with training so features match exactly.
   - One code path serves both; divergence here is silent quality loss.
4. Add warmup: load weights and score sample inputs before accepting traffic.
   - Gate traffic on warmup success; cold instances must not take requests.
5. Deploy beside production; run shadow scoring to compare outputs.
   - Compare prediction distributions per version before acting on any of them.
6. Open a canary share; watch error rates and p50/p99 per version.
   - Predeclare share and duration; do not judge on the first hour of noise.
7. Shift traffic in steps; keep instant rollback to the prior version.
   - Rollback is a routing change, tested by drill, not a redeploy under pressure.
8. Log every prediction with version and latency for later replay.
    - Replay reconstructs any incident window exactly as served.
9. Add prediction caching keyed on request plus model and schema versions.
    - Invalidate on promotion; verify invalidation with a version-bump test.
10. Split the p99 budget across legs and instrument per-leg timing.
    - Each leg gets an owner and an alert; no shared anonymous timeout.
11. Rehearse peak load against warmed replicas before declaring headroom.
    - Record queue depth at peak; set the warning level below the observed knee.
12. Dual-serve schema versions during client migration; retire the old on metrics.
    - Rejection logs by client version prove when migration is complete.
13. Cap shadow load and define shed order before it touches production capacity.
    - Shadow is the first load dropped when budgets tighten, never the last.
14. Pin balancer pools per version for the duration of stepped shifts.
    - Mixed-version responses are expected during shifts and must stay attributable.

## Rollout checklist
- Warmup green, shadow compared, canary predeclared, rollback drilled, logs replayable.
- Revisit the checklist whenever preprocessing, schema, or hardware changes.
- A skipped check is a recorded risk with an owner, never a silent omission.
- File the completed checklist with the promotion record for audit.
   - Replay reconstructs any incident window exactly as served.

## Done when
- p99 per version is under budget, rollback drill passes, and logs replay cleanly.
