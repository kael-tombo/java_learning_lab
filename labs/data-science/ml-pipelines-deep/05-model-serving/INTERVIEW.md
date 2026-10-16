# Model Serving - Interview Questions

1. When would you choose batch over online inference?
   - Batch for scheduled scoring where latency is flexible; online when each request needs an immediate answer.
2. Why size timeouts from p99 rather than the mean?
   - The tail determines user-visible stalls; the mean hides them inside a pleasant average.
3. How does batching trade latency for throughput?
   - Amortized overhead raises items/sec while each item waits longer; the cap picks the point.
4. What do shadow, canary, and blue-green each buy you?
   - Shadow compares safely, canary tests on small live traffic, blue-green makes rollback a routing change.
5. Why must preprocessing match training exactly?
   - Any divergence shifts features and silently degrades quality with no error raised.
6. What belongs in a prediction log?
   - Request key, schema version, model version, prediction, and latency: enough to replay.
7. How do you judge a canary fairly?
   - Predeclared share and duration, version-tagged error and latency bands, no early peeking.
8. What causes post-deploy p99 spikes?
   - Cold instances, GC pauses, or slow dependencies; warmup and timeouts mitigate them.
9. How do you keep rollback fast?
   - Keep the prior version warm and make rollback a tested routing change.
10. Where does queueing bite first?
    - Near saturation, waiting time grows steeply; headroom at peak is the control.
11. How do you keep preprocessing identical in training and serving?
    - One shared code path, pinned; diff its outputs on identical inputs.
12. What does a readiness check verify?
    - Warmed weights plus preprocessing loaded and sample scores succeeding.
13. How do you migrate a request schema safely?
    - Versioned contract, dual-serve old and new, retire on client metrics.
14. Where should prediction caching key on versions?
    - In the cache key itself: model plus schema versions, invalidated on promote.
15. How do you bound dynamic batching latency?
    - Cap the batch-wait time so low-traffic periods still meet the budget.
16. What separates liveness from readiness?
    - Liveness is running; readiness is warmed and allowed to take traffic.
17. How do you size replicas with headroom?
    - Peak requests per second over measured per-replica throughput, plus slack.

## How to answer
- Name the pattern, state the tradeoff quantitatively, then give the operational guard.
