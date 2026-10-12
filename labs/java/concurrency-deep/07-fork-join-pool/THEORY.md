# Fork-Join Pool — Theoretical Foundation

## Core Concept

`ForkJoinPool` executes **divide-and-conquer tasks that create subtasks**:
`fork()` a `RecursiveTask`, compute half directly, `join()` the other half.
Idle workers *steal* tasks from busy workers' queues — so a wildly
unbalanced recursion still saturates all cores without any central
dispatcher. It is the engine behind parallel streams, `CompletableFuture`'s
default pool, and every hand-rolled `RecursiveTask`.

## Work-Stealing: One Deque Per Worker

Each worker owns a double-ended queue:

- The owner pushes and pops at the **same end (LIFO)** — the most recently
  forked (smallest, hottest, most cache-resident) subtask runs first.
- A thief steals from the **opposite end (FIFO)** — the oldest (largest,
  coarsest) chunk, minimizing steal frequency and maximizing the stolen
  work per steal.

This asymmetry is the whole trick: local LIFO optimizes cache locality;
remote FIFO optimizes load balance. The theoretical bound (Blumofe–Leiserson,
1999): expected time O(T₁/P + T∞) — total work over workers plus the span
(critical path) — i.e., near-optimal whenever parallelism dwarfs the span.

## The Three Verbs: fork / join / invoke

| Call | Meaning | Caller blocks? |
|---|---|---|
| `task.fork()` | queue async (in own deque if worker, else shared submission queue) | no |
| `task.join()` | await result; **worker helps first** (executes other pending tasks while waiting) | yes |
| `pool.invoke(task)` | fork + join from outside | yes |
| `task.invoke()` | direct compute if small, fork/join path otherwise | yes |

`join()`'s helping behavior is what prevents the classic deadlock: a worker
waiting on its own subtask keeps executing instead of parking, so
fork-then-immediately-join chains (the naive style) still make progress.
Do *not* confuse `join()` with `Thread.join()` — the former works, the
latter parks.

Computing directly vs forking at the leaves: the `THRESHOLD` in every
`RecursiveTask.compute()` (`if (hi - lo < THRESHOLD) computeDirectly()`)
bounds task-creation overhead. Too small → millions of task objects, queue
churn dominates. Too large → fewer tasks than workers, cores idle. Rule:
threshold such that leaf work is ~1–10µs (hundreds to thousands of tasks per
worker, not millions).

## Common Pool: Defaults and Dials (source-verified, JDK 23)

- **Parallelism** = `availableProcessors − 1` (measured: 8 CPUs → 7),
  overridable via system property
  `java.util.concurrent.ForkJoinPool.common.parallelism`; hard cap
  `MAX_CAP = 0x7fff` (32767).
- **Factory/handler** likewise via `...common.threadFactory` /
  `...common.exceptionHandler` properties.
- **Never shuts down**: the common pool lives for the JVM's lifetime —
  size it via properties at startup (`common.parallelism`), because no API
  call reverts it.

## ManagedBlocker: The Blocking Escape Hatch

A worker that parks (I/O, `CountDownLatch.await`, `synchronized` on a held
monitor) without telling the pool *reduces effective parallelism* — the pool
can't distinguish "working" from "parked." `ManagedBlocker` is the protocol:

```java
pool.managedBlocker(new ManagedBlocker() {
    public boolean block() throws InterruptedException { socket.read(...); return true; }
    public boolean isReleasable() { return finished; }
});
```

While a worker blocks inside `block()`, the pool may spawn a **compensating
thread** to preserve parallelism (`getPoolSize()` can exceed
`getParallelism()` — the javadoc for `getPoolSize` says exactly this).
`ForkJoinPool.managedBlock()` is also what `CompletableFuture`'s blocking
helpers and parallel-stream blocking ops use internally. Rule: any
potentially-blocking call inside a FJ task goes through `ManagedBlocker`,
or the pool silently degrades to fewer effective workers.

## asyncMode (FIFO vs LIFO Local Ordering)

Constructor flag `asyncMode`: `false` (default) = local LIFO (good for
divide-and-conquer: fresh subtasks first); `true` = local FIFO (good for
event-style/never-joined tasks: older tasks first, fairer latency). The
common pool runs asyncMode=false. `newWorkStealingPool()` (Executors)
creates asyncMode=true pools — matching its "independent submitted tasks"
workload. Pick by workload shape, not by benchmark superstition.

## Shutdown Discipline (non-common pools)

`shutdown()` (no new tasks, drain), `shutdownNow()` (attempt stop + return
unexecuted), `awaitTermination(t)` (bounded wait), `awaitQuiescence(t)`
(FJ-specific: wait until no *active* tasks — returns whether quiescent).
`invoke()` after shutdown → `RejectedExecutionException`. Leaked
non-daemon FJ pools hold the JVM open exactly like leaked thread pools —
`try (var pool = new ForkJoinPool(n))` isn't AutoCloseable... actually
`ForkJoinPool` implements `AutoCloseable` since Java 19 (extends
`AbstractExecutorService` + `close()` = shutdown + await). Prefer
try-with-resources for scoped pools on 19+.

## When FJ Is the Wrong Tool

- **Blocking-heavy workloads** — threads-per-task (fixed pool sized to
  concurrency, or virtual threads) beats work-stealing when tasks mostly
  wait. FJ assumes CPU-bound divisibility.
- **Tiny workloads** — task objects + queue ops dwarf sub-microsecond leaf
  work; a plain loop wins (parallel-stream overhead on small arrays is the
  same phenomenon).
- **Ordered I/O pipelines** — stealing reorders execution freely; ordering
  guarantees need explicit sequencing.

## Key Invariants

1. Owner end LIFO, thief end FIFO — per worker deque, always.
2. `join()` helps (executes) before it parks — no worker idles while its
   own queue is non-empty.
3. Common-pool parallelism = CPUs − 1 unless the property says otherwise;
   the pool never terminates.
4. Blocking inside tasks without `ManagedBlocker` silently shrinks effective
   parallelism.
5. `MAX_CAP` (32767) bounds declared parallelism; `getPoolSize()` may exceed
   `getParallelism()` only via compensation.
