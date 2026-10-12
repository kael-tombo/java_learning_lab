# Performance: Fork-Join Pool

## Where time goes

1. Task object + fork queue-op per split (~50–200ns). Dominates below ~1µs
   leaves — the floor of FJ granularity.
2. Steal (cross-thread deque take, ~µs). Rare in balanced splits (span-bound
   count), frequent in skewed trees.
3. `join()`-help: free progress (executes real work while waiting) — not
   overhead but overlapped throughput.
4. Common-pool contention with streams/CF: noisy-neighbor stalls, not pool
   overhead — isolate to measure FJ itself.

## Threshold sweep (do this first)

```java
for (int t : new int[]{100, 1_000, 10_000, 100_000}) {
    FJSum.THRESHOLD = t;  // or ctor param
    time(pool.invoke(new FJSum(a, 0, n)));
}
```

Expect a U-curve: tiny t → churn (task counts toward the 262143 end of the
measured range), huge t → idle cores (toward the 255 end). The minimum sits
where leaves land ~1–10µs. Re-sweep per machine — cache sizes move the floor.

## Parallelism and the common pool

Common = CPUs − 1 (8→7 measured): one core stays free for the submitting
thread. Plain `new ForkJoinPool()` = CPUs. `MAX_CAP` 32767 caps declarations,
not wisdom — past ~2× CPUs, CPU-bound FJ work only adds steal contention.

## ManagedBlocker cost/benefit

Compensation (+1 thread per blocker, 2→3 measured) preserves throughput while
blocking lasts; the spare parks when the blocker returns. Benefit: no silent
parallelism loss. Cost: thread churn per block episode — batch blocking calls
inside one `block()` rather than one `managedBlocker` per read.

## asyncMode selection

Divide-and-conquer (joined splits): default LIFO (`asyncMode=false`) — newest
subtasks hottest in cache. Event-style (never joined, `newWorkStealingPool`):
FIFO (`asyncMode=true`) — bounded wait per submission. Wrong mode costs
single-digit percent on balanced work, more on skewed arrival patterns.

## What NOT to do

- FJ for blocking-heavy pipelines — fixed pools or virtual threads win.
- Parallel streams over tiny arrays — task overhead exceeds leaf work (same
  U-curve, hidden threshold).
- Oversized plain pools for CPU-bound recursion — steal contention without
  speedup past ~CPUs.
- Ignoring `awaitQuiescence` vs `awaitTermination` — draining fork-only work
  with the wrong waiter hangs the harness, not the pool.
