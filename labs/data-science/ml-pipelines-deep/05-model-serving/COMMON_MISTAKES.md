# Model Serving - Common Mistakes

1. Sizing timeouts from the mean instead of p99, then failing at peak tail load.
   - Fix: budget from measured p99 under peak traffic per version.
2. Letting batch waits grow unbounded, turning an online path into a batch one.
   - Fix: cap batch-wait time so latency stays predictable at low traffic.
3. Judging a canary on tiny traffic without error bars and shipping noise.
   - Fix: predeclare share and duration; require the z-check to clear.
4. Skipping warmup, so every deploy starts with a latency spike.
   - Fix: gate traffic on warmup success with sample inferences.
5. Diverging preprocessing between training and serving, silently shifting features.
   - Fix: one shared code path, pinned and tested on identical inputs.
6. Changing schemas without version handling, breaking older clients.
   - Fix: versioned contracts with explicit missing and extra field policy.
7. No rollback drill, discovering at incident time that rollback does not work.
   - Fix: rehearse routing rollback while the prior version stays warm.
8. Logging predictions without model version, making incidents unreplayable.
   - Fix: log key, schema version, model version, prediction, and latency.
9. Treating streaming state as disposable, losing windows on every restart.
   - Fix: persist per-key state with checkpointing; define late-event policy explicitly.
10. Sharing one timeout across preprocessing, model, and network legs.
    - Fix: budget each leg separately so the slow leg is identifiable in histograms.
11. Deploying the model without the postprocessor calibration it was evaluated with.
    - Fix: version preprocessor, weights, and postprocessor as one bundle.
12. Caching predictions by key without versioning the cache entry.
    - Fix: include model and schema versions in the cache key; invalidate on promote.
13. Measuring latency at the model only, missing gateway and queue time users feel.
    - Fix: measure end-to-end at the gateway and per leg; report both.
14. Letting shadow traffic consume production capacity during peak.
    - Fix: cap shadow load and shed it first when latency budgets tighten.
15. One replica per version during canary, confusing instance noise with model signal.
    - Fix: run enough replicas per version that single-instance effects average out.

## Review habit
- Before any deploy, confirm budget, warmup, rollback, and replay in that order.
- After any incident, add the missing guard to this list before closing.
