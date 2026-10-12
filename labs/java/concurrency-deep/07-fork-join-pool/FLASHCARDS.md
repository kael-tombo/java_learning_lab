# Flashcards: Fork-Join Pool

## Q/A pairs

**Q:** Deque discipline: owner end vs thief end?
**A:** Owner pushes/pops the same end (LIFO — hot, small first); thieves steal
the opposite end (FIFO — large, coarse chunks).

**Q:** What do `fork()`, `join()`, `invoke()` each do?
**A:** `fork` queues async (own deque if worker, submission queue if outsider);
`join` awaits + helps; `invoke` = fork + join from outside.

**Q:** How does `join()` avoid the naive deadlock?
**A:** It helps — executes other pending tasks while waiting — before parking.

**Q:** Canonical per-split shape?
**A:** Fork left, compute right directly, join left. One fork per split, not two.

**Q:** Threshold rule and task-count formula?
**A:** Leaves ~1–10µs; leaves ≈ n/t, total ≈ 2n/t. Too small → churn (262143
extreme); too large → idle cores (255 extreme).

**Q:** Common-pool parallelism on 8 CPUs?
**A:** 7 (CPUs − 1). Plain `new ForkJoinPool()` → 8 (CPUs). Cap `MAX_CAP =
0x7fff` (32767).

**Q:** How is common parallelism overridden?
**A:** System property `java.util.concurrent.ForkJoinPool.common.parallelism`
at JVM startup; factory/handler via matching properties.

**Q:** What does `ManagedBlocker` buy?
**A:** Pool compensation: a spare thread preserves parallelism while a worker
blocks — `getPoolSize()` exceeds `getParallelism()` (measured 2→3).

**Q:** `asyncMode` true vs false?
**A:** False (default, common pool): local LIFO for divide-and-conquer. True
(`newWorkStealingPool`): local FIFO for independent event tasks.

**Q:** `awaitQuiescence` vs `awaitTermination`?
**A:** Quiescence: no *active* tasks (fork-only drains). Termination: pool shut
down after `shutdown()`.

**Q:** Scoped-pool close on modern JDKs?
**A:** `ExecutorService.close()` since Java 19 — try-with-resources
(`close()` = shutdown + await).

**Q:** Which workloads must NOT use FJ?
**A:** Blocking-heavy (use fixed pools/virtual threads), tiny leaves (plain
loop wins), order-sensitive pipelines (steals reorder freely).

**Q:** Work-span bound?
**A:** E[T_P] = O(T₁/P + T∞) (Blumofe–Leiserson 1999): work over workers plus span.
