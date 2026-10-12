# Architecture: Fork-Join Pool

## Pool topology

```text
+---------------- ForkJoinPool ------------------+
|  submission queue (outsiders: invoke/execute)  |
|  +----------+  +----------+  +----------+     |
|  | Worker 1 |  | Worker 2 |  | Worker 3 | ... |
|  | deque    |  | deque    |  | deque    |     |
|  | LIFO<->  |  | LIFO<->  |  | LIFO<->  |     |
|  +----------+  +----------+  +----------+     |
|  steals travel FIFO across deques              |
+------------------------------------------------+
```

Workers scan: own deque first (LIFO pop), then random-victim steals (FIFO
take), then the shared submission queue. No central dispatcher sits in the
hot path.

## Sizing and dials (JDK 23, source-verified)

- Common pool: parallelism = `availableProcessors − 1` (measured 8→7) via
  `java.util.concurrent.ForkJoinPool.common.parallelism`; factory/handler via
  `...common.threadFactory` / `...common.exceptionHandler`; hard cap
  `MAX_CAP = 0x7fff` (32767). Lives for the JVM lifetime — no shutdown.
- Plain `new ForkJoinPool()`: parallelism = `availableProcessors`.
- `getPoolSize()` vs `getParallelism()`: equal normally; size exceeds
  parallelism only under `ManagedBlocker` compensation (measured 2→3).

## Borrowers of the common pool

Parallel streams, CF `*Async` defaults, `Arrays.parallel*` — all share it.
A blocking task from any borrower degrades all borrowers: the architecture
has no bulkhead between them. Blocking workloads get their own pool (or
virtual threads), never the common one.

## Task class choice

- `RecursiveTask<V>`: returns a value (`compute()` → V; `join()` → V).
- `RecursiveAction`: side effects only (`compute()` → void).
- `CountedCompleter`: manual pending-count completion for DAG-shaped
  (non-tree) fan-ins — escape hatch when fork/join nesting does not fit.

## Shutdown architecture (non-common pools)

`shutdown()` (drain, no new tasks) → `awaitTermination(t)` (bounded) or
`awaitQuiescence(t)` (FJ-specific: no *active* tasks). `shutdownNow()`
attempts stop + returns unexecuted. Since Java 19, `ForkJoinPool extends
AbstractExecutorService` + `AutoCloseable`: `try (var p = new
ForkJoinPool(n))` closes via shutdown + await — the scoped-pool default.

## Source paths (OpenJDK)

- `java.base/java/util/concurrent/ForkJoinPool.java`
- `java.base/java/util/concurrent/ForkJoinTask.java`
- `java.base/java/util/concurrent/RecursiveTask.java` / `RecursiveAction.java`
- `java.base/java/util/concurrent/CountedCompleter.java`
