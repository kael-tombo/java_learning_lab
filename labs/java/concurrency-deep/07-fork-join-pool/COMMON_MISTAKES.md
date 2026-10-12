# Common Mistakes: Fork-Join Pool

## 1. Forking both halves

```java
left.fork(); right.fork(); left.join(); right.join();  // WASTE
```

One queue op saved per split by computing half inline:
`left.fork(); long r = right.compute(); left.join() + r`. The double-fork
version doubles task objects for zero extra parallelism.

## 2. Blocking inside tasks without ManagedBlocker

```java
protected Long compute() {
    latch.await();  // parks WITHOUT telling the pool: silent parallelism loss
    ...
}
```

Fix: wrap in `ForkJoinPool.managedBlock(...)`. Symptom: throughput drops with
idle CPUs and `getPoolSize() == getParallelism()` despite parked workers.

## 3. Tiny threshold (task storm)

Threshold 10 on 10M elements → ~2M tasks of nanosecond leaves. Queue churn
dominates; the measured extreme hit 262143 tasks where 255 sufficed. Fix:
sweep upward until leaves hit ~1–10µs.

## 4. Giant threshold (idle cores)

Threshold ≥ n/workers → fewer tasks than workers; 7 of 8 cores idle while one
grinds. Fix: `tasksPerWorker = (2n/t)/P` in the hundreds — shrink t.

## 5. Confusing `join()` with `Thread.join()`

FJ `join()` helps (executes pending tasks); `Thread.join()` parks. "Waiting"
inside FJ is productive by design — do not "optimize" it with extra threads.

## 6. Leaking non-daemon pools

```java
ForkJoinPool pool = new ForkJoinPool(8);  // never shut down: JVM hangs at exit
```

Fix on Java 19+: `try (var pool = new ForkJoinPool(8)) { ... }`
(`close()` = shutdown + await). Pre-19: `shutdown()` + `awaitTermination` in
finally. The common pool is exempt (never terminates).

## 7. Parallel streams for blocking I/O

```java
urls.parallelStream().map(this::blockingFetch)  // squats common pool
```

Every blocked worker stalls CF defaults and other streams. Fix: dedicated
pool + `submit(() -> urls.stream()...)` or virtual threads — keep the common
pool CPU-bound.

## 8. Assuming task counts

"More tasks = more parallelism" is false past saturation. Count: `2n/t` total
nodes. Past ~1000/worker, extra splits only add queue ops — the U-curve in
PERFORMANCE.md is the arbiter, not intuition.
