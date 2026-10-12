# Exercises: Fork-Join Pool

All snippets compile on JDK 9+ with no dependencies.

## 1. Canonical sum + parallelism asserts

Write `FJSum extends RecursiveTask<Long>` per CODE_DEEP_DIVE.md section 1
(fork-left / compute-right / join). Assert: sum correct on 10M ones, and
`pool.getParallelism() == availableProcessors()` for a plain pool vs
`commonPool().getParallelism() == availableProcessors() - 1`.

## 2. Threshold sweep + task counts

Count `compute()` invocations with an `AtomicLong` at thresholds 100 / 10_000
/ 1M over 1M elements. Confirm `total ≈ 2n/t` (100 → ~20K, 10K → ~200) and
time each: report the U-curve minimum. Reference: the lab's measured extremes
span 262143 vs 255 tasks — place your counts on that spectrum.

## 3. Double-fork waste demo

Version A: fork-left/compute-right/join. Version B: fork both, join both.
Count tasks and time both on the same input — B creates ~2× the queue ops for
the same result. Keep A; delete B with a comment why.

## 4. ManagedBlocker compensation probe

```java
ForkJoinPool pool = new ForkJoinPool(2);
System.out.println("before: " + pool.getPoolSize());
pool.managedBlocker(new ManagedBlocker() {
    public boolean block() throws InterruptedException {
        Thread.sleep(500);
        System.out.println("during: size=" + pool.getPoolSize()
            + " parallelism=" + pool.getParallelism());
        return true;
    }
    public boolean isReleasable() { return false; }
});
```

Expect size 2→3 during the block (compensation). Then run `latch.await()`
inside `compute()` *without* the blocker and show throughput sag vs the
wrapped version.

## 5. asyncMode contrast

`new ForkJoinPool(4, defaultFactory, null, false)` (LIFO) vs `(…, true)`
(FIFO) on: (a) recursive sum — LIFO wins or ties; (b) 10K independent
`ForkJoinTask`-style submissions drained via `awaitQuiescence` — FIFO fairer
tails. Report both timings, one paragraph each on why.

## 6. Scoped pool close (Java 19+)

```java
try (var pool = new ForkJoinPool(4)) {
    long s = pool.invoke(new FJSum(a, 0, n));
}
```

Prove no leak: JVM exits promptly; contrast with an unclosed pool holding it.
Pre-19 runtimes: `shutdown()` + `awaitTermination` in finally — write that path
too and note `close()` is unavailable.
