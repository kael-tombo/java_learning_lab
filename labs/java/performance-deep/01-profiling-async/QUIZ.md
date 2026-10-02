# QUIZ — Async Profiling

## 1. What does a virtual thread run on?
<details><summary>Answer</summary>A carrier thread (platform thread). Multiple virtual threads multiplex onto fewer carrier threads.
</details>

## 2. What is pinning?
<details><summary>Answer</summary>Virtual thread blocks carrier thread (e.g., `synchronized`, native call), preventing other virtual threads from using that carrier.
</details>

## 3. How to detect pinning in a flame graph?
<details><summary>Answer</summary>Search for `Thread.isVirtualThreadPinned()` or look for long-running `synchronized`/`native` frames on carrier threads.
</details>

## 3. What does StructuredTaskScope provide?
<details><summary>Answer</summary>Parent-child relationship for async tasks, automatic error propagation/cancellation, structured concurrency.
</details>

## 4. How to propagate context across async boundaries?
<details><summary>Answer</summary>OpenTelemetry Context API, `Context.current()`, `Context.makeCurrent()`, or framework-specific (Spring `TransactionSynchronizationManager`, Reactor `Context`).
</details>

## 4. What does `StructuredTaskScope.ShutdownOnFailure` do?
<details><summary>Answer</summary>Cancels all forks if any fails; propagates first exception.
</details>

## 5. How to trace CompletableFuture chains?
<details><summary>Answer</summary>OpenTelemetry context propagation + async-profiler correlation, or `CompletableFuture` stack trace analysis.
</details>

## 5. What is backpressure in reactive streams?
<details><summary>Answer</summary>Consumer signals demand (`request(n)`) to producer; producer respects demand, preventing overflow.
</details>

## 6. How to profile Reactor backpressure?
<details><summary>Answer</summary>Add `Hooks.onOperatorDebug()`, profile `request(n)` latency, monitor queue sizes between operators.
</details>

## 6. What is pinning in virtual threads?
<details><summary>Answer</summary>Virtual thread blocks carrier thread (synchronized, native call, file I/O), preventing carrier reuse.
</details>

## 7. How to detect pinning?
<details><summary>Answer</summary>Search flame graph for `Thread.isVirtualThreadPinned()`, enable `-XX:+LogVirtualThreadEvents`.
</details>

## 7. What causes pinning?
<details><summary>Answer</summary>`synchronized` blocks, native calls, file I/O in virtual threads.
</details>

## 8. Fix for pinning?
<details><summary>Answer</summary>Replace `synchronized` with `ReentrantLock`, use `StampedLock`, avoid native/file I/O in VT.
</details>

## 8. How to profile Reactor pipelines?
<details><summary>Answer</summary>`Hooks.onOperatorDebug()`, Micrometer Timers on operators, async-profiler with operator tags.
</details>

## 9. What is backpressure?
<details><summary>Answer</summary>Consumer signals demand (`request(n)`) to producer; producer respects demand, preventing overflow.
</details>

## 10. StructuredTaskScope vs CompletableFuture?
<details><summary>Answer</summary>StructuredTaskScope: structured concurrency, auto-cancellation, error propagation. CompletableFuture: ad-hoc, manual composition.
</details>