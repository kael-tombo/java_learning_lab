# Model Serving - Flashcards

Q: Name the three serving patterns. A: Batch, online, streaming.
Q: What is p99? A: Latency below which 99% of requests fall.
Q: Why size timeouts from p99? A: The tail, not the mean, stalls users.
Q: Batching tradeoff in one line? A: Throughput up, latency up.
Q: latency(B) formula? A: overhead + B * perItem.
Q: throughput(B) formula? A: B / latency(B), rising toward 1/perItem.
Q: What is shadow deployment? A: New version scores without acting, for comparison.
Q: What is a canary? A: Small live-traffic share to the new version.
Q: What is blue-green? A: Two stacks; traffic switches between them for fast rollback.
Q: Why warm up instances? A: To absorb cold-start cost before live traffic.
Q: What goes in a prediction log? A: Key, schema and model versions, prediction, latency.
Q: z for canary comparison? A: (r2-r1)/SE over the difference standard error.
Q: Top cause of post-deploy p99 spike? A: Cold instances or a slow dependency.
Q: Rollback mechanism? A: Routing change to the warm prior version.
Q: Schema change rule? A: Versioned contract; explicit policy for unknown fields.
Q: Batch-wait bound why? A: Keeps tail latency predictable at low traffic.
Q: Readiness vs liveness? A: Liveness is alive; readiness is warmed and traffic-ready.
Q: Latency legs? A: Preprocess + model + postprocess + network/queueing.
Q: Dynamic batching? A: Bounded wait to fill a batch within the latency cap.
Q: Batch path validation? A: Rows in vs rows out plus score-distribution check.
Q: Streaming state holds? A: Per-key windows and counters across events.
Q: Late-event policy options? A: Drop, update, or reprocess the window.
Q: Cache key must include? A: Model and schema versions.
Q: End-to-end latency measured where? A: At the gateway, plus per leg.
Q: Shadow load risk? A: Consumes production capacity; cap and shed first.
Q: Canary replica rule? A: Enough replicas per version to average instance noise.
Q: Mixed-version responses during shift? A: Expected; pin balancer pools per version.
Q: Batch worker readiness? A: Gate partition assignment on warmup success.
Q: Headroom sized from? A: Peak load measurement, not average load.
Q: Queue depth signals? A: Saturation approaching before timeouts spike.
Q: Preprocessing parity test? A: Identical inputs through both paths, diff outputs.
Q: Postprocessor calibration ships with? A: The evaluated weights as one bundle.
Q: Streaming checkpoint purpose? A: Survive restarts without losing windows.
Q: Contract migration done when? A: Client metrics show old shape gone.
Q: Incident replay needs? A: Version-tagged logs with inputs and outputs.
