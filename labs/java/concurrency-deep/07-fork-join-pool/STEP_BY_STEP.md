# Step by Step: Sum, Sweep, Block

## Goal

A canonical `RecursiveTask` sum, a threshold sweep, and a `ManagedBlocker`
demo — about 45 minutes.

## Step 1 — Canonical sum (10 min)

```java
class Sum extends RecursiveTask<Long> {
    static int THRESHOLD = 10_000;
    final long[] a; final int lo, hi;
    Sum(long[] a, int lo, int hi) { this.a = a; this.lo = lo; this.hi = hi; }
    @Override protected Long compute() {
        if (hi - lo <= THRESHOLD) {
            long s = 0; for (int i = lo; i < hi; i++) s += a[i]; return s;
        }
        int mid = (lo + hi) >>> 1;
        Sum left = new Sum(a, lo, mid);
        left.fork();
        long right = new Sum(a, mid, hi).compute();
        return left.join() + right;
    }
}
```

Run 10M ones in a plain pool: assert sum == n and `getParallelism() ==
availableProcessors()`. Note the single fork — the right half runs inline.

## Step 2 — Threshold sweep (10 min)

Time thresholds 100 / 10K / 1M with a `compute()`-call counter. Expect the
U-curve: 100 → ~20K tasks (churn), 10K → ~200 (sweet spot), 1M → a handful
(idle cores). Compute `2n/t` predictions first, then compare measured counts.

## Step 3 — Parallelism asserts (5 min)

```java
System.out.println("common: " + ForkJoinPool.commonPool().getParallelism());
System.out.println("plain: " + new ForkJoinPool().getParallelism());
```

8 CPUs → 7 and 8. Set `-Djava.util.concurrent.ForkJoinPool.common.parallelism=4`,
re-run, watch the common value move — startup property, no API revert.

## Step 4 — ManagedBlocker probe (10 min)

Run the EXERCISES.md probe: pool of 2 + `managedBlocker` sleeping 500ms.
Watch `getPoolSize()` go 2→3 during the block. Then put `latch.await()` bare
in a `compute()` and show the sag; wrap it and show recovery.

## Step 5 — asyncMode peek (5 min)

Build LIFO (`false`) and FIFO (`true`) pools of 4; run the recursive sum in
both (expect near-tie) and 10K fire-and-forget submissions drained by
`awaitQuiescence` (expect FIFO fairer tails). One paragraph on why each fits.

## Step 6 — Scoped close (5 min)

```java
try (var pool = new ForkJoinPool(4)) {
    long s = pool.invoke(new Sum(a, 0, a.length));
}
```

JVM exits cleanly (19+). Pre-19: `shutdown()` + `awaitTermination` in finally.

## Done when

Sum exact, U-curve measured with counts near `2n/t`, 7/8 asserts green,
2→3 compensation observed, scoped pool exits clean.
