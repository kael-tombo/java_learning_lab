# FLASHCARDS — Async Profiling

| # | Front | Back |
|---|-------|------|
| 1 | Virtual thread carrier? | Platform thread that runs multiple virtual threads |
| 2 | Pinning definition? | VT blocks carrier (synchronized, native, file I/O) |
| 3 | Pinning detection? | `Thread.isVirtualThreadPinned()`, `-XX:+LogVirtualThreadEvents` |
| 4 | Pinning causes? | `synchronized`, native calls, file I/O in VT |
| 5 | Pinning fix? | `ReentrantLock`, `StampedLock`, avoid native/file I/O in VT |
| 6 | StructuredTaskScope? | Parent-child async tasks, auto-cancellation, error propagation |
| 7 | ShutdownOnFailure? | Cancels all forks on first failure, propagates exception |
| 7 | Context propagation? | OpenTelemetry Context, `Context.current()`, framework-specific |
| 7 | CompletableFuture tracing? | OpenTelemetry context + async-profiler correlation |
| 7 | Backpressure? | Consumer signals demand (`request(n)`) to producer |
| 8 | Reactor backpressure profiling? | `Hooks.onOperatorDebug()`, Micrometer Timers, `request(n)` latency |
| 8 | Pinning detection? | `Thread.isVirtualThreadPinned()`, `-XX:+LogVirtualThreadEvents` |
| 8 | Pinning causes? | `synchronized`, native calls, file I/O in VT |
| 8 | Pinning fix? | `ReentrantLock`, `StampedLock`, avoid native/file I/O in VT |
| 9 | Reactor debugging? | `Hooks.onOperatorDebug()`, Micrometer Timers, async-profiler |
| 9 | Push vs pull? | Push: HTTP endpoints (OIDC). Pull: workers lease/ack. |
| 9 | Ordering keys? | Per-key order at throughput ceiling; shard hot keys. |
| 10 | Poison handling? | DLQ + maxDeliveryCount → quarantine. |
| 10 | Concurrency math? | Instances ≈ RPS·latency/concurrency; virtual threads raise it free. |
| 11 | Push vs pull? | Push: HTTP endpoints (OIDC). Pull: workers lease/ack. |
| 11 | Ordering keys? | Per-key order at throughput ceiling; shard hot keys. |
| 11 | Poison handling? | DLQ + maxDeliveryCount → quarantine. |
| 11 | Concurrency math? | Instances ≈ RPS·latency/concurrency; virtual threads raise it free. |
| 11 | minScale 0 trade? | Zero idle cost vs cold starts — pair with native/CRaC for latency paths. |
| 12 | SLO alerting? | Burn-rate on p99/errors, not raw thresholds. |
| 12 | Flyway placement? | Pre-deploy Job (same race argument, third cloud). |
| 12 | Migration rule? | Backward-compatible, expand-then-contract. |
| 13 | Spot rule? | Batch only; never the serving path. |
| 14 | Buy-down basis? | Measured-steady baseline only. |
| 15 | Rehearsal count? | Three: find, validate, prove-the-clock. |