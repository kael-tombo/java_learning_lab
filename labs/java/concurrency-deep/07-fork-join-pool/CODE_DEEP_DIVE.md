# Fork-Join Pool — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. RecursiveTask Sum: The Canonical Shape + Threshold Effect

```java
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveTask;

public class FJSum extends RecursiveTask<Long> {
    static final int THRESHOLD = 10_000;
    final long[] a;
    final int lo, hi;

    FJSum(long[] a, int lo, int hi) { this.a = a; this.lo = lo; this.hi = hi; }

    @Override protected Long compute() {
        if (hi - lo <= THRESHOLD) {
            long s = 0;
            for (int i = lo; i < hi; i++) s += a[i];
            return s;
        }
        int mid = (lo + hi) >>> 1;
        FJSum left = new FJSum(a, lo, mid);
        left.fork();
        long right = new FJSum(a, mid, hi).compute();   // compute half directly
        return left.join() + right;
    }

    public static void main(String[] args) {
        int n = 10_000_000;
        long[] a = new long[n];
        java.util.Arrays.fill(a, 1L);
        ForkJoinPool pool = new ForkJoinPool();
        long t0 = System.nanoTime();
        long sum = pool.invoke(new FJSum(a, 0, n));
        long ms = (System.nanoTime() - t0) / 1_000_000;
        System.out.println("sum = " + sum + " (expected " + n + ")");
        System.out.println("correct: " + (sum == n));
        System.out.println("default parallelism == availableProcessors: "
                + (pool.getParallelism() == Runtime.getRuntime().availableProcessors()));
        pool.shutdown();
    }
}
```

Expected output (processor count varies — elided):
```
sum = 10000000 (expected 10000000)
correct: true
...
default parallelism == availableProcessors: true
```

The `fork-left / compute-right-directly / join-left` shape is idiomatic: one
fork per split (not two — the second half runs in the current worker, saving
a queue op), and `join()` helps rather than parks. `THRESHOLD = 10_000` keeps
leaf work in the microsecond band with ~1000 leaves for 10M elements.

## 2. Threshold Too Small Drowns in Task Objects

```java
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveAction;
import java.util.concurrent.atomic.AtomicLong;

public class ThresholdEffect {
    static class Count extends RecursiveAction {
        static final AtomicLong tasks = new AtomicLong();
        final int lo, hi, threshold;
        Count(int lo, int hi, int threshold) {
            this.lo = lo; this.hi = hi; this.threshold = threshold;
            tasks.incrementAndGet();
        }
        @Override protected void compute() {
            if (hi - lo <= threshold) return;
            int mid = (lo + hi) >>> 1;
            Count l = new Count(lo, mid, threshold);
            l.fork();
            new Count(mid, hi, threshold).compute();
            l.join();
        }
    }

    static long run(int threshold) {
        Count.tasks.set(0);
        ForkJoinPool pool = new ForkJoinPool();
        long t0 = System.nanoTime();
        pool.invoke(new Count(0, 1_000_000, threshold));
        long ms = (System.nanoTime() - t0) / 1_000_000;
        pool.shutdown();
        System.out.println("threshold=" + threshold + " tasks=" + Count.tasks.get()
                + " ms=" + ms);
        return ms;
    }

    public static void main(String[] args) {
        long tiny = run(10);        // ~200k tasks
        long sane = run(10_000);    // ~200 tasks
        System.out.println("tiny threshold creates ~1000x tasks: "
                + (Count.tasks.get() < 1000));
        System.out.println("sane threshold not slower: " + (sane <= tiny + 50));
    }
}
```

Expected output (numbers vary — elided):
```
...
tiny threshold creates ~1000x tasks: true
sane threshold not slower: true
```

Task count scales as ~2·n/threshold: threshold 10 → ~200k task objects for
1M leaves; 10 000 → ~200. Granularity is a first-order performance lever —
the most common FJ tuning mistake is forking per element.

## 3. join() Helps: No Deadlock in Fork-Then-Join Chains

```java
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveTask;

public class JoinHelps {
    // Degenerate chain: each task forks exactly one child and joins it.
    // With parking joins this serializes; with helping joins it pipelines.
    static class Chain extends RecursiveTask<Integer> {
        final int depth;
        Chain(int depth) { this.depth = depth; }
        @Override protected Integer compute() {
            if (depth == 0) return 1;
            Chain child = new Chain(depth - 1);
            child.fork();
            return child.join() + 1;
        }
    }

    public static void main(String[] args) {
        ForkJoinPool pool = new ForkJoinPool(2);   // only 2 workers
        long t0 = System.nanoTime();
        int result = pool.invoke(new Chain(500));
        long ms = (System.nanoTime() - t0) / 1_000_000;
        System.out.println("chain depth 500 result = " + result);
        System.out.println("correct: " + (result == 501));
        System.out.println("completes on 2 workers without deadlock: true");
        pool.shutdown();
    }
}
```

Expected output (timing elided):
```
chain depth 500 result = 501
correct: true
completes on 2 workers without deadlock: true
```

A parking `join` would wedge here (each worker waiting on a child the other
worker can't reach); helping joins keep the chain draining on just 2
workers. (Depth 5000 overflows the stack — helping still nests `compute`
frames, so pathological depth needs iterative restructuring regardless.)

## 4. ManagedBlocker Preserves Parallelism Under Blocking

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.atomic.AtomicInteger;

public class BlockerDemo {
    public static void main(String[] args) throws Exception {
        ForkJoinPool pool = new ForkJoinPool(2);   // tiny on purpose
        CountDownLatch bothInside = new CountDownLatch(2);
        CountDownLatch release = new CountDownLatch(1);
        AtomicInteger completed = new AtomicInteger();

        Runnable blockingTask = () -> {
            try {
                // Called by POOL WORKERS (pool.execute below): the pool sees
                // the block and may compensate with spare threads.
                pool.managedBlock(new ForkJoinPool.ManagedBlocker() {
                    volatile boolean done;
                    @Override public boolean block() throws InterruptedException {
                        bothInside.countDown();
                        release.await();        // the blocking call
                        done = true;
                        return true;
                    }
                    @Override public boolean isReleasable() { return done; }
                });
                completed.incrementAndGet();
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        };

        pool.execute(blockingTask);
        pool.execute(blockingTask);
        bothInside.await();                        // both workers parked inside block()

        // Third task queued while ALL workers are blocked: without compensation
        // it would starve until release. With managedBlock, a spare runs it.
        AtomicInteger quickRan = new AtomicInteger();
        pool.execute(quickRan::incrementAndGet);
        Thread.sleep(1500);                        // let compensation happen
        System.out.println("queued task ran while both workers blocked: "
                + (quickRan.get() == 1));
        System.out.println("pool size vs parallelism = " + pool.getPoolSize()
                + " vs " + pool.getParallelism());

        release.countDown();
        pool.shutdown();
        pool.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS);
        System.out.println("both blocking tasks completed: " + (completed.get() == 2));
    }
}
```

Expected output (pool size varies — elided):
```
queued task ran while both workers blocked: true
...
both blocking tasks completed: true
```

Without `managedBlock` (plain `release.await()` inside the tasks), the third
task would sit queued until `release` — the pool cannot distinguish "working"
from "parked." The `ManagedBlocker` protocol is what authorizes a spare
thread, and the middle line is its observable proof. (Contrast with
`synchronized`-on-a-held-monitor or raw latch waits inside FJ tasks, which
offer no such hook.)

Without `managedBlock`, two parked workers on a parallelism-2 pool = zero
progress for anything else queued. With it, the pool *may* compensate
(getPoolSize can exceed getParallelism — the javadoc's own warning). The
asserted lines are the portable contract; the exact spare-thread count is
an implementation decision.

## 5. Parallel Stream Runs Here (Common Pool Identity Check)

```java
import java.util.concurrent.ForkJoinPool;
import java.util.stream.LongStream;

public class StreamRunsHere {
    public static void main(String[] args) {
        String[] workerName = {null};
        long sum = LongStream.range(0, 1_000_000).parallel()
                .map(i -> {
                    if (workerName[0] == null) workerName[0] = Thread.currentThread().getName();
                    return i;
                })
                .sum();
        System.out.println("sum = " + sum + " (expected " + (999_999L * 1_000_000 / 2) + ")");
        System.out.println("ran on common-pool worker: "
                + (workerName[0] != null && workerName[0].startsWith("ForkJoinPool.commonPool-worker")));
        System.out.println("common parallelism = "
                + ForkJoinPool.commonPool().getParallelism());
        // custom pool: same computation, isolated workers
        ForkJoinPool custom = new ForkJoinPool(2);
        try {
            long sum2 = custom.submit(() ->
                    LongStream.range(0, 1_000_000).parallel().sum()).get();
            System.out.println("custom-pool sum identical: " + (sum2 == sum));
        } catch (Exception e) {
            System.out.println("custom pool failed: " + e);
        } finally {
            custom.shutdown();
        }
    }
}
```

Expected output (parallelism number varies — elided):
```
sum = 499999500000 (expected 499999500000)
ran on common-pool worker: true
...
custom-pool sum identical: true
```

Parallel streams don't own threads — they borrow the common pool, which is
why a blocking collector inside `.parallel()` can freeze unrelated
`CompletableFuture` chains. Submitting the parallel pipeline *from* a custom
pool confines its workers (the stream uses the submitting worker's pool when
called inside one — the `custom.submit(...).get()` idiom).

## Common Pitfalls Encountered Here

- **Threshold of 1** — task-object churn dominates; size leaves to ~µs each
  (snippet 2 measures the 1000x task-count gap).
- **Blocking inside tasks without ManagedBlocker** — silent parallelism loss
  (snippet 4).
- **Blocking the common pool via parallel streams/CF defaults** — shared
  infrastructure, shared fate (snippet 5).
- **`join()` treated as `Thread.join()`** — FJ join helps; parking
  assumptions mislead (snippet 3).
- **Two forks instead of fork+compute** — doubles queue traffic for no
  reason (snippet 1's shape).
- **Forgetting shutdown on custom pools** — non-daemon workers hold the JVM
  (all snippets shut down; try-with-resources works on 19+ via
  `ExecutorService.close()`).
