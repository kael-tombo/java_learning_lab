# Visual Guide: Fork-Join Pool

## The deque (the only drawing that matters)

```text
Worker 1 deque:  [ steal(A, oldest) ... forked(Y) forked(Z, newest) ]
                   ^thief takes HERE      ^owner pushes/pops HERE
```

Owner arrow at the new end (LIFO); thief arrow at the old end (FIFO). Draw
both arrows on every deque sketch — a deque with one arrow is half the story.

## Steal balancing

```text
before: W1 [A][B][C][D][E][F] (busy)    W2 [] (idle)
steal:  W2 takes A (oldest, coarsest)
after:  W1 [B][C][D][E][F]              W2 [A -> splits to A1 A2 ...]
```

One steal transfers the largest chunk; the thief subdivides locally. Skewed
trees balance in O(span) steals, not O(work) — draw steals as rare, fat
arrows, not a stream of small ones.

## Join-helping timeline

```text
worker: fork(L) ... compute(R) ... join(L)?
  join finds L incomplete:
    pop own M -> run M .... pop own N -> run N .... steal O -> run O
    L completes (by self or thief) -> return L.result
  park: ONLY if deque empty AND steals fail AND L still incomplete
```

The wait bar is filled with real work blocks — never an idle gap until the
last resort. Contrast with a `Thread.join()` bar: solid idle until the signal.

## Threshold U-curve

```text
time ^
     |\___ t=100 (churn: ~262143 tasks, queue ops dominate)
     |    \___ t=10K (sweet spot: ~leaves in the 1-10us band)
     |        \___ t=1M (starvation: ~255 tasks, cores idle)
     +----------------------------------> threshold t (log scale)
```

Mark your measured minimum with its task count ≈ `2n/t`. The curve moves per
machine — redraw, don't memorize.

## Compensation footprint

```text
pool(2): [W1 working][W2 BLOCKED in block()]  -> spare W3 added
getPoolSize 2 -> 3, getParallelism stays 2
block ends -> W3 parks, size drifts back
```

Size-above-parallelism is the receipt — draw the +1 thread labeled with the
blocker's name.

## Shutdown map

```text
shutdown() -> no new tasks, drain -> awaitTermination(t) -> true/false
fork-only stream -> awaitQuiescence(t) -> quiescent? (no active tasks)
19+: try (var p = new ForkJoinPool(n)) { invoke } // close = shutdown + await
common pool: NO arrow to shutdown (lives with the JVM)
```

The common pool drawn without any exit arrow is the reminder: size it at
startup or live with it.
