# Quiz: Fork-Join Pool

## Questions (answers at end)

1. A worker's deque holds [oldest A … newest Z]. The owner pops which end?
   A thief steals which end? Why the asymmetry?
2. Why does fork-left / compute-right / join-left use one fork instead of two?
3. `n = 1M, t = 10K`: estimate leaves and total tasks. What breaks at `t =
   100`? At `t = 1M` on 8 workers?
4. State the work-span bound and what each term means.
5. 8 CPUs: common-pool vs plain-constructor parallelism? Name the property,
   the cap, and whether the common pool shuts down.
6. A task calls `latch.await()` inside `compute()`. What happens to effective
   parallelism, and what is the fix? What observable confirms the fix worked?
7. `getPoolSize() == 3`, `getParallelism() == 2`. Leak or expected? Explain.
8. `asyncMode=true` suits which workload, and which factory sets it by default?
9. Fork-only event workload: `awaitTermination` or `awaitQuiescence`? Why?
10. `join()` vs `Thread.join()` — what is the load-bearing difference?
11. Parallel stream over blocking HTTP calls stalls unrelated CF chains. Why,
    and what is the fix?
12. Java 19+ scoped pool shape? What does `close()` do?

## Answers

1. Owner pops newest end (LIFO: hot, cache-resident first). Thief takes oldest
   (FIFO: coarsest chunk per steal, fewest steals). Locality vs load balance.
2. The second half runs in the current worker — same parallelism, one fewer
   task object + queue op per split.
3. ~100 leaves, ~200 total. `t=100` → ~20K tasks of tiny leaves: churn
   dominates. `t=1M` → 1–2 tasks: 7 cores idle.
4. E[T_P] = O(T₁/P + T∞): total work over workers plus critical-path span —
   near-optimal when parallel work dwarfs the span.
5. Common 7 (CPUs−1) via `...ForkJoinPool.common.parallelism`; plain 8
   (CPUs); `MAX_CAP = 0x7fff`; common pool never shuts down.
6. Effective parallelism drops silently (parked reads as busy). Fix:
   `ManagedBlocker`/`managedBlock`. Confirm: `getPoolSize()` exceeds
   `getParallelism()` during blocks.
7. Expected — one compensation thread for a blocked worker, not a leak.
8. Independent never-joined submissions (event-style); `Executors
   .newWorkStealingPool()` defaults it.
9. `awaitQuiescence(t)` — waits for no *active* tasks; termination requires
   `shutdown()` lifecycle, wrong tool for fork-only drains.
10. FJ `join()` helps (executes pending tasks) before parking; `Thread.join()`
    only parks.
11. All three borrow the common pool — blocked stream workers shrink every
    borrower's parallelism. Fix: dedicated pool / virtual threads for blocking
    I/O; keep the common pool CPU-bound.
12. `try (var pool = new ForkJoinPool(n)) { ... }` — `close()` = shutdown +
    await termination.
