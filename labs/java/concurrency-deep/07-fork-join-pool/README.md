# Lab 07 — Fork-Join Pool: README

## What this lab covers

`ForkJoinPool` runs divide-and-conquer tasks that create subtasks: `fork()` a
`RecursiveTask`, compute half directly, `join()` the other. Idle workers steal
from busy workers' deques — owner end LIFO (hot, small subtasks first), thief
end FIFO (large, coarse chunks). `join()` *helps* (executes pending tasks)
before parking, so fork-then-join chains make progress instead of deadlocking.

## Core facts (from THEORY.md)

- Verbs: `fork()` (queue async), `join()` (await + help), `invoke()` (fork +
  join from outside); canonical shape forks left, computes right directly.
- Threshold bounds task-creation overhead: leaf work ~1–10µs; task count ≈
  `2n/threshold` leaves (~2× that in total nodes).
- Common pool: parallelism = CPUs − 1 (measured 8→7), set via
  `java.util.concurrent.ForkJoinPool.common.parallelism`, cap `MAX_CAP =
  0x7fff`; never shuts down.
- Plain `new ForkJoinPool()` parallelism = CPUs (measured); `getPoolSize()`
  may exceed `getParallelism()` only via `ManagedBlocker` compensation
  (measured 2→3).
- `asyncMode=true` = FIFO local order (event-style, `newWorkStealingPool`);
  default `false` = LIFO (divide-and-conquer).
- Shutdown: `shutdown`/`shutdownNow`/`awaitTermination`/`awaitQuiescence`;
  `ExecutorService.close()` (i.e. try-with-resources) since Java 19.
- Parallel streams and CF defaults borrow the common pool.

## Map of this lab

- `THEORY.md` + `CODE_DEEP_DIVE.md` — stealing, verbs, thresholds, common-pool
  dials, `ManagedBlocker`, shutdown (ground truth, already done)
- `HOW_IT_WORKS.md`, `ARCHITECTURE.md`, `INTERNALS.md` — deque mechanics,
  pool topology, help-then-park
- `MATH_FOUNDATION.md` — work-span bound, `2n/threshold` sizing, measured
  counts (262143 vs 255)
- `STEP_BY_STEP.md`, `EXERCISES.md` — sum task, threshold sweep, blocker demo
- `PERFORMANCE.md`, `DEBUGGING.md`, `COMMON_MISTAKES.md`, `REFACTORING.md`
- `QUIZ.md`, `FLASHCARDS.md`, `HISTORY.md`, `REFERENCES.md`, reflection pair

## Prerequisites

- Lab 05 (parking/wakeup — steal queues reuse the same primitives)
- Lab 06 (CF default pool = the common pool studied here)
- Recursion comfort (`RecursiveTask.compute()` splits)

## Starter snippet

```java
ForkJoinPool pool = new ForkJoinPool();
long sum = pool.invoke(new SumTask(array, 0, n));  // fork-left/compute-right/join
pool.shutdown();
```

## Exit criteria

You can draw the deque ends, write the canonical fork/compute/join shape, size
a threshold from `2n/threshold`, state the common-pool defaults and dials,
route blocking calls through `ManagedBlocker`, and close scoped pools with
try-with-resources on 19+.
