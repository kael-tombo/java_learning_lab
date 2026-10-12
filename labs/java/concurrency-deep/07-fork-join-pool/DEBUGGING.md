# Debugging: Fork-Join Pool

## Is it parallel at all?

```java
System.out.println("common parallelism: " + ForkJoinPool.commonPool().getParallelism()
    + " (expect CPUs-1 = " + (Runtime.getRuntime().availableProcessors() - 1) + ")");
ForkJoinPool p = new ForkJoinPool();
System.out.println("plain ctor parallelism: " + p.getParallelism()
    + " (expect CPUs = " + Runtime.getRuntime().availableProcessors() + ")");
p.shutdown();
```

8 CPUs → 7 and 8. Property override (`common.parallelism`) shows here — if
the numbers differ from expectation, the JVM flags (not the code) did it.

## Threshold diagnosis

Time the sweep from PERFORMANCE.md and count tasks (instrument a static
counter in `compute()` or estimate `2n/t`). 262143-scale counts with slow
times = churn (raise t); 255-scale counts with idle cores in a profiler =
starvation (lower t). The U-curve minimum is the answer — per machine.

## Blocked-worker fingerprint

Throughput down + CPUs idle + stacks showing FJ workers in `park`/`WAITING`
on sockets/latches + `getPoolSize() == getParallelism()` = missing
`ManagedBlocker`. After the fix, `getPoolSize()` should exceed parallelism
(2→3 pattern) during blocks. No growth after wrapping = the block sits
outside the `block()` method (re-check placement).

## Quiescence vs termination hangs

Harness hangs after `shutdown()` + `awaitTermination`: tasks still fork
children post-shutdown (`RejectedExecutionException` in logs) or a task never
returns. Fork-only event shapes: use `awaitQuiescence(t)` and check its
boolean return — `false` means still active at the deadline, not dead.

## Common-pool interference

Suspect it when: FJ timings vary with unrelated stream/CF load, or
`commonPool-worker` stacks show foreign frames (stream pipelines, CF stages).
Isolate: run the task in a private `new ForkJoinPool(P)` — stable times there
prove noisy neighbors, and the fix is workload placement (blocking work out),
not pool tuning.

## Exception tracing

`join()`/`invoke()` rethrow the task's exception (unchecked wrap for checked
causes). `CountedCompleter` DAGs: check `getException()` on the root — child
failures record without travelling unless `completeExceptionally` propagates.
`throwsThrowable` in dumps distinguishes task failure from worker death.

## Tooling

Async-profiler wall-clock: attribute parked time to the holder/blocked frame.
JFR `Thread Park` events: steal-waits (short, frequent) vs blocking-waits
(long, rare) separate cleanly by duration histogram. `jstack`: all workers in
`awaitJoin` with empty deques = oversized threshold (nothing to steal).
