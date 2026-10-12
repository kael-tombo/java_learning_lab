# Refactoring: Fork-Join Pool

## Sequential loop → RecursiveTask (only when large + CPU-bound)

Before:

```java
long sum = 0;
for (long v : a) sum += v;
```

After (n in the millions, CPU-bound):

```java
try (var pool = new ForkJoinPool()) {
    sum = pool.invoke(new SumTask(a, 0, a.length));
}
```

Do not convert small arrays — task overhead exceeds leaf work (parallel-stream
overhead on small inputs is the same phenomenon wearing a different API).

## Double-fork → fork/compute/join

Before: `left.fork(); right.fork(); left.join() + right.join()`. After:
`left.fork(); long r = right.compute(); left.join() + r`. Halves queue ops
per split with identical parallelism — mechanical, always apply.

## Blocking task → ManagedBlocker

Before: `latch.await()` / `socket.read()` bare inside `compute()`. After:
wrap in `pool.managedBlock(...)` / `managedBlocker(...)`. The pool compensates
(size > parallelism) instead of silently degrading. Alternatively move the
workload off FJ entirely (fixed pool / virtual threads) if mostly-waiting.

## Shared-pool blocking stream → isolated pool

Before: `urls.parallelStream().map(this::blockingFetch)` on the common pool.
After:

```java
Executor ioPool = Executors.newFixedThreadPool(100);
List<R> out = ioPool.submit(() ->
    urls.stream().map(this::blockingFetch).toList()).get();
```

Or virtual threads per fetch. The common pool stays CPU-bound for all its
borrowers.

## Manual pool lifecycle → try-with-resources (19+)

Before: `pool = new ForkJoinPool(n); ... pool.shutdown();` (and the missing-
await variant that leaks). After: `try (var pool = new ForkJoinPool(n))`. One
line owns the whole lifecycle; pre-19 code keeps explicit
`shutdown` + `awaitTermination` in finally.

## Fixed pool for recursion → FJ (when tasks beget tasks)

`ThreadPoolExecutor` + recursive submission + blocking join wedges or idles;
FJ's per-worker deques + join-helping fit task-creating tasks. Migrate when
profiling shows the shared queue contended and join-waits idle — not before.
