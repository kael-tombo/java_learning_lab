# Math Foundation: Work-Stealing

## 1. Work-span bound (Blumofe–Leiserson 1999)

For total work T₁ (single-thread time) and span T∞ (critical-path time) on P
workers, randomized work-stealing gives expected time:

```
E[T_P] = O(T₁/P + T∞)
```

Near-linear speedup whenever T₁/P dominates T∞ (plenty of parallel work,
short critical path). A sum over 10M elements: T₁ ≈ 10ms, T∞ ≈ log₂(10M)
splits ≈ 24 steps — the bound predicts ~T₁/P scaling, which is what the
threshold sweep in EXERCISES.md measures.

## 2. Threshold task-count arithmetic

Range length n, leaf threshold t: leaves ≈ n/t, total nodes ≈ 2n/t
(each split makes two children until leaves):

```
n = 1_000_000, t = 10_000  ->  ~100 leaves, ~200 tasks
n = 1_000_000, t = 100     ->  ~10_000 leaves, ~20_000 tasks
```

Measured reference from CODE_DEEP_DIVE.md: one configuration yielded 262143
total tasks vs 255 across the threshold sweep — a ~1000× node-count swing
from the same input. Task objects + queue ops dominate below ~1µs leaves;
cores idle when tasks < workers × small factor.

## 3. Leaf-sizing rule

Target leaf work 1–10µs → tasks per worker in the hundreds-to-thousands:

```
tasksPerWorker = (2n/t) / P,   want 10²–10³
```

n = 10M, P = 8, t = 10K → ~2000 nodes / 8 ≈ 250 per worker. Good. t = 1M →
~20 nodes / 8 ≈ 2–3 per worker: one slow leaf stalls its worker with nothing
to steal — rebalance by shrinking t.

## 4. Steal-count sketch

Thieves steal FIFO (coarsest chunks): each steal transfers ~half the victim's
remaining work in expectation. Steals ≈ O(P × T∞) — proportional to span, not
to total work. Deep unbalanced trees (long span) steal often; balanced splits
rarely. Random victim choice keeps contention off any single deque.

## 5. Common-pool sizing arithmetic

CPUs = 8 → common parallelism 7 (CPUs − 1), plain pool 8 (CPUs). One blocked
common-pool worker without `ManagedBlocker` cuts effective parallelism 7→6
(~14% throughput loss for CPU-bound borrowers); two blocked → 7→5 (~29%).
Compensation restores it: pool size 2→3 measured with one blocker — the +1 is
the spare, not a leak.

## 6. Speedup ceiling (Amdahl combo)

Serial fraction s (merge, threshold checks, splits) caps speedup at 1/s
regardless of P. s = 2% → max 50× even with infinite workers. Measure the
serial merge before adding workers — FJ scales the leaves, never the root.
