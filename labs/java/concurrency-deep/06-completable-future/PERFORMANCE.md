# Performance: CompletableFuture

## Where time goes

1. Sync stage on completed future: one virtual call, no pool, no allocation
   beyond the node (~20–50ns). Free — chain aggressively.
2. `*Async` hop: queue + handoff to common-pool worker (~1–5µs). Worth it for
   >10µs bodies or stack-depth control; wasteful for getters.
3. `supplyAsync` default: common-pool submit when parallelism > 1; a fresh
   thread per task on 1-CPU targets (unbounded under storms).
4. `allOf` barrier: O(N) counter ticks + N inline `join()`s — microseconds for
   hundreds of inputs.

## Pool selection guide

```java
Executor cpuPool = ForkJoinPool.commonPool();            // CPU-bound *Async
Executor ioPool = Executors.newFixedThreadPool(200);     // blocking stages
 future.supplyAsync(() -> cpuCrunch(), cpuPool);
 future.supplyAsync(() -> blockingCall(), ioPool);
```

Blocking on the common pool shows up as: parallel streams stall, `*Async`
latency spikes, `commonPool-worker` threads all in `BLOCKED`/`WAITING`. The
fix is always the same — move the stage, not the pool size.

## Timeout overhead

`orTimeout`/`completeOnTimeout` schedule one `Delayed` task on the shared
`Delayer`. Cost per bounded future ≈ one timer enqueue/dequeue (~µs) —
negligible next to I/O, measurable in allocation storms (>100K futures/s want
fewer, coarser deadlines).

## Exception-path costs

`CompletionException` construction captures a stack trace per failed `join()`.
Hot failure loops (retries joining failed futures) pay trace-fill on every
iteration — extract the cause once, then branch on it.

## Tuning rules

- Default sync stages for transforms; `*Async` only to change threads
  (blocking body, isolation, stack control).
- One bounded I/O pool per dependency (separate failure domains); size by the
  wait/compute ratio, not core count.
- `orTimeout` from the p99 histogram + margin; re-measure per deploy target.
- Avoid `join()` inside small custom pools — chain instead of block.

## What NOT to do

- `supplyAsync(blockingIO)` on the default pool.
- `getNow(x)` as a "quick wait" — it never waits; use `get(t, unit)`.
- Deep sync-only chains (>1K stages) on one completion — stack depth; break
  with one `*Async` or restructure.
- `anyOf` hedging without cancelling losers — duplicate load forever.
