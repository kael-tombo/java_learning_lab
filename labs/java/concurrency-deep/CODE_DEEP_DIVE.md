# Code Deep Dive — Concurrency Deep & Virtual Threads (concurrency-deep)

Six runnable snippets for the `concurrency-deep` lab: happens-before edges in the Java Memory Model, virtual threads and carrier pinning, structured concurrency, scoped values, `ForkJoinPool` task splitting, and `StampedLock` with `LongAdder`. Snippets 1, 2, 5 and 6 compile with `--release 21` and no preview flags. Snippets 3 and 4 use preview APIs on JDK 21-24, so they were compiled with `--release 23 --enable-preview` and run with `--enable-preview` on JDK 23.0.1.

## Snippet 1: JMM happens-before

The Java Memory Model only guarantees that a thread sees another thread's write if a happens-before edge connects them. The edges used here are: a volatile write followed by a volatile read of the same variable, `Thread.start()` and `Thread.join()`, and the hand-off through a `BlockingQueue` (`put` before the matching `take`). Writes made before the edge, such as the plain `port` and `host` fields, become visible with it, which is why only `ready` needs to be volatile.

Save as `HappensBefore.java`, then:

```bash
javac --release 21 -proc:none -d out HappensBefore.java
java -cp out HappensBefore
```

```java
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

public class HappensBefore {
    static class Config {
        int port;          // plain, non-volatile fields
        String host;
    }

    static Config published;        // plain field written before the volatile write below
    static volatile boolean ready;  // volatile write -> volatile read creates a happens-before edge
    static int beforeStart;         // visible to a thread because Thread.start() is an edge
    static int afterWork;           // visible to the starter because Thread.join() is an edge

    public static void main(String[] args) throws Exception {
        // Edge 1: volatile write/read publishes everything written before it.
        Thread reader = new Thread(() -> {
            while (!ready) {
                Thread.onSpinWait();
            }
            // Guaranteed to see port=8080 and host="db1": both writes precede the volatile write.
            System.out.println("reader sees port=" + published.port + " host=" + published.host);
        });
        reader.start();
        Config c = new Config();
        c.port = 8080;
        c.host = "db1";
        published = c;
        ready = true;                 // the publishing write
        reader.join();

        // Edge 2: start() and join().
        beforeStart = 7;
        Thread worker = new Thread(() -> {
            System.out.println("worker sees beforeStart=" + beforeStart);
            afterWork = beforeStart * 6;
        });
        worker.start();
        worker.join();
        System.out.println("main sees afterWork=" + afterWork);

        // Edge 3: a BlockingQueue hand-off. put() happens-before the matching take().
        BlockingQueue<int[]> queue = new ArrayBlockingQueue<>(1);
        Thread consumer = new Thread(() -> {
            try {
                int[] data = queue.take();
                System.out.println("consumer sees data[0..2]=" + data[0] + "," + data[1] + "," + data[2]);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        consumer.start();
        int[] payload = new int[3];
        payload[0] = 1;
        payload[1] = 2;
        payload[2] = 3;
        queue.put(payload);
        consumer.join();

        // Edge 4: join() again, this time handing over an immutable record (its components are final fields).
        record Pair(int a, int b) { }
        Pair[] holder = new Pair[1];
        Thread t = new Thread(() -> holder[0] = new Pair(3, 4));
        t.start();
        t.join();
        System.out.println("record via join: " + holder[0]);
    }
}
```

Observed output (JDK 23.0.1). Deterministic, and it would print the same on most hardware even with a bug in it: a passing run is not proof of correctness. Use the OpenJDK `jcstress` harness to test memory-model claims.

```text
reader sees port=8080 host=db1
worker sees beforeStart=7
main sees afterWork=42
consumer sees data[0..2]=1,2,3
record via join: Pair[a=3, b=4]
```

**Pitfall.** Dropping `volatile` from `ready` turns the loop `while (!ready)` into a data race. The code still compiles and often still works in tests, but the JMM permits the JIT to hoist the read out of the loop (an endless spin) or the reader to see `port == 0` after seeing `ready == true`. I did not reproduce a failure in this run, which is exactly why this bug reaches production: it depends on JIT, CPU and load. Review code for the missing edge, and use `jcstress` rather than loops of sleeps to look for it.

## Snippet 2: virtual threads & carriers

A virtual thread (JEP 444, final in Java 21) keeps its stack in the heap and is scheduled onto a small pool of platform "carrier" threads, a `ForkJoinPool`; when it blocks in `sleep` or a `j.u.c` lock it unmounts and the carrier is free for others. The snippet limits the scheduler to one carrier and runs 10,000 sleeping tasks through it. On JDK 21-23 a virtual thread that blocks while holding a monitor (`synchronized`) is pinned: it keeps the carrier, so two such sleepers with one carrier run one after the other. JEP 491 (JDK 24) removed that limitation for `synchronized`.

Save as `VirtualCarriers.java`, then:

```bash
javac --release 21 -proc:none -d out VirtualCarriers.java
java -cp out VirtualCarriers
```

```java
import java.time.Duration;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantLock;

public class VirtualCarriers {
    static String carrierOf(Thread t) {
        // Virtual thread toString looks like VirtualThread[#22]/runnable@ForkJoinPool-1-worker-1
        String s = t.toString();
        int at = s.indexOf('@');
        return at < 0 ? "none" : s.substring(at + 1);
    }

    static long timeTwoSleepers(boolean useSynchronized) throws InterruptedException {
        CountDownLatch done = new CountDownLatch(2);
        long start = System.nanoTime();
        for (int i = 0; i < 2; i++) {
            Object monitor = new Object();
            ReentrantLock lock = new ReentrantLock();
            Thread.ofVirtual().start(() -> {
                try {
                    if (useSynchronized) {
                        synchronized (monitor) {
                            Thread.sleep(Duration.ofMillis(200));   // blocks while holding a monitor
                        }
                    } else {
                        lock.lock();
                        try {
                            Thread.sleep(Duration.ofMillis(200));   // blocks while holding a j.u.c lock
                        } finally {
                            lock.unlock();
                        }
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                done.countDown();
            });
        }
        done.await();
        return (System.nanoTime() - start) / 1_000_000;
    }

    public static void main(String[] args) throws Exception {
        // Must be set before the first virtual thread exists: the scheduler reads it once.
        System.setProperty("jdk.virtualThreadScheduler.parallelism", "1");
        System.setProperty("jdk.virtualThreadScheduler.maxPoolSize", "1");

        // 1. Ten thousand blocking tasks, one carrier thread.
        Set<String> carriers = ConcurrentHashMap.newKeySet();
        AtomicInteger virtualCount = new AtomicInteger();
        try (ExecutorService vts = Executors.newVirtualThreadPerTaskExecutor()) {
            for (int i = 0; i < 10_000; i++) {
                vts.submit(() -> {
                    if (Thread.currentThread().isVirtual()) {
                        virtualCount.incrementAndGet();
                    }
                    carriers.add(carrierOf(Thread.currentThread()));
                    Thread.sleep(Duration.ofMillis(100));
                    return null;
                });
            }
        } // close() waits for all submitted tasks
        System.out.println("tasks that ran on a virtual thread: " + virtualCount.get() + " of 10000");
        System.out.println("distinct carrier threads used: " + carriers.size() + " " + carriers);

        // 2. Blocking inside synchronized vs inside ReentrantLock, with a single carrier.
        System.out.println("2 sleepers, synchronized : ~" + timeTwoSleepers(true) + " ms");
        System.out.println("2 sleepers, ReentrantLock: ~" + timeTwoSleepers(false) + " ms");
    }
}
```

Observed output (JDK 23.0.1). The thread counts are deterministic. The millisecond figures are wall-clock measurements from this machine on JDK 23.0.1 and vary run to run; the roughly 2:1 ratio between the two lines is what matters. On JDK 24 or later I expect the `synchronized` line to fall to about the `ReentrantLock` line, per JEP 491, but I did not run it there.

```text
tasks that ran on a virtual thread: 10000 of 10000
distinct carrier threads used: 1 [ForkJoinPool-1-worker-1]
2 sleepers, synchronized : ~491 ms
2 sleepers, ReentrantLock: ~201 ms
```

**Pitfall.** On JDK 21-23, blocking inside `synchronized` (a `sleep`, a blocking socket read, a database call from a synchronized method) pins the carrier. With few carriers (the default parallelism equals the processor count) enough pinned threads stop all other virtual threads from making progress, and throughput collapses without an error. Find it with `-Djdk.tracePinnedThreads=full`, which prints the stack when a thread blocks while pinned, or the JFR event `jdk.VirtualThreadPinned`. Either replace the monitor with a `ReentrantLock` or move to JDK 24+.

## Snippet 3: structured concurrency

A `StructuredTaskScope` ties the lifetime of forked subtasks to a lexical block: `fork` starts each subtask on its own virtual thread, `join` waits, and closing the scope waits for every fork to finish, so none can outlive the method. `ShutdownOnFailure` cancels the remaining subtasks by interrupting them as soon as one fails, and `throwIfFailed` rethrows the first failure. In the second block, the failing subtask ends after 50 ms and the 5-second sibling is interrupted instead of running to completion.

**Preview API, shape changed in JDK 25.** Structured concurrency was a preview API in JDK 21 (JEP 453), 22 (JEP 462), 23 (JEP 480) and 24 (JEP 499). Those releases use `new StructuredTaskScope.ShutdownOnFailure()` and `new StructuredTaskScope.ShutdownOnSuccess<T>()`, which is what this snippet uses. JDK 25 (JEP 505) replaced the subclasses with factory methods: `StructuredTaskScope.open(Joiner...)`. This code will not compile on JDK 25 without being rewritten. Class files built with `--enable-preview` are tagged as preview and refuse to load without the flag (`UnsupportedClassVersionError: Preview features are not enabled`, seen when I ran it without the flag).

Save as `StructuredFanOut.java`, then:

```bash
javac --release 23 --enable-preview -proc:none -d out StructuredFanOut.java
java --enable-preview -cp out StructuredFanOut
```

```java
import java.time.Duration;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.StructuredTaskScope;
import java.util.concurrent.StructuredTaskScope.Subtask;
import java.util.concurrent.atomic.AtomicBoolean;

// PREVIEW API on JDK 21-24 (JEPs 453, 462, 480, 499): compile with --enable-preview.
// JDK 25 reshaped it (JEP 505): StructuredTaskScope.open(joiner) replaces new ShutdownOnFailure().
public class StructuredFanOut {
    static String slowUser() throws InterruptedException {
        Thread.sleep(Duration.ofMillis(80));
        return "alice";
    }

    static int slowOrderCount() throws InterruptedException {
        Thread.sleep(Duration.ofMillis(50));
        return 3;
    }

    public static void main(String[] args) throws Exception {
        // Success path: both subtasks must finish before the scope closes.
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            Subtask<String> user = scope.fork(StructuredFanOut::slowUser);
            Subtask<Integer> orders = scope.fork(StructuredFanOut::slowOrderCount);
            scope.join().throwIfFailed();
            System.out.println("user=" + user.get() + " orders=" + orders.get()
                    + " states=" + user.state() + "/" + orders.state());
        }

        // Failure path: one subtask fails, the scope cancels the sibling by interrupting it.
        AtomicBoolean siblingInterrupted = new AtomicBoolean();
        long start = System.nanoTime();
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            scope.fork(() -> {
                Thread.sleep(Duration.ofMillis(50));
                throw new IllegalStateException("inventory service down");
            });
            Subtask<String> sibling = scope.fork(() -> {
                try {
                    Thread.sleep(Duration.ofSeconds(5));
                    return "finished";
                } catch (InterruptedException e) {
                    siblingInterrupted.set(true);
                    throw e;
                }
            });
            try {
                scope.join().throwIfFailed();
            } catch (ExecutionException e) {
                System.out.println("join failed: " + e.getCause());
            }
            System.out.println("sibling state after failure: " + sibling.state());
        }
        long ms = (System.nanoTime() - start) / 1_000_000;
        System.out.println("sibling interrupted: " + siblingInterrupted.get()
                + ", total under 2 s instead of 5 s: " + (ms < 2_000));
    }
}
```

Observed output (JDK 23.0.1). Deterministic text. The snippet only prints whether the whole thing took under 2 seconds, not a duration.

```text
user=alice orders=3 states=SUCCESS/SUCCESS
join failed: java.lang.IllegalStateException: inventory service down
sibling state after failure: UNAVAILABLE
sibling interrupted: true, total under 2 s instead of 5 s: true
```

**Pitfall.** Because this is a preview API, the real failure mode is churn: code written against `ShutdownOnFailure` breaks when the JDK moves to the `open(Joiner...)` form, and a binary compiled with `--enable-preview` on JDK 23 cannot be run on another JDK major version at all. Keep preview code behind a small wrapper, do not ship it in libraries, and pin the JDK version in CI. Within one JDK, the other mistake is calling `Subtask.get()` before `join()`; on JDK 23 the API rejects it with `IllegalStateException: Owner did not join after forking subtasks` (checked in a separate scratch run) instead of returning a half-finished result.

## Snippet 4: scoped values

A `ScopedValue` is bound for the dynamic extent of a `run` or `call`: `get()` reads the innermost binding, nested `where(...)` rebinds only for the nested call, and the previous binding is back as soon as that call returns. There is no `set`, so the value cannot be changed by callees, and no `remove`, so it cannot leak past its scope. Threads started by `StructuredTaskScope.fork` inherit the bindings; a plain `new Thread` does not.

**Preview API before JDK 25.** Scoped values were a preview in JDK 21 (JEP 446), 22 (JEP 464), 23 (JEP 481) and 24 (JEP 487), and became final in JDK 25 (JEP 506). This snippet needs `--enable-preview` on JDK 21-24. Because it also uses `StructuredTaskScope.ShutdownOnFailure`, the fork part must be rewritten with `StructuredTaskScope.open(Joiner...)` for JDK 25 (JEP 505).

Save as `ScopedValueDemo.java`, then:

```bash
javac --release 23 --enable-preview -proc:none -d out ScopedValueDemo.java
java --enable-preview -cp out ScopedValueDemo
```

```java
import java.util.NoSuchElementException;
import java.util.concurrent.StructuredTaskScope;
import java.util.concurrent.StructuredTaskScope.Subtask;

// PREVIEW API on JDK 21-24 (JEPs 446, 464, 481, 487); final in JDK 25 (JEP 506).
// Compile and run with --enable-preview on JDK 23.
public class ScopedValueDemo {
    static final ScopedValue<String> USER = ScopedValue.newInstance();

    static void handle(String label) {
        System.out.println(label + ": USER=" + USER.get());
    }

    public static void main(String[] args) {
        System.out.println("outside any scope, isBound=" + USER.isBound()
                + ", orElse=" + USER.orElse("anonymous"));
        try {
            USER.get();
        } catch (NoSuchElementException e) {
            System.out.println("get() outside a scope: NoSuchElementException");
        }

        ScopedValue.where(USER, "alice").run(() -> {
            handle("outer");

            // Rebinding is visible only inside the nested run(); the binding reverts afterwards.
            ScopedValue.where(USER, "bob").run(() -> handle("nested"));
            handle("after nested");

            // A plain thread does NOT inherit scoped values.
            Thread plain = new Thread(() ->
                    System.out.println("plain thread: isBound=" + USER.isBound()));
            plain.start();
            try {
                plain.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }

            // Threads forked through StructuredTaskScope DO inherit the bindings.
            try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
                Subtask<String> child = scope.fork(() -> "forked child sees " + USER.get());
                scope.join().throwIfFailed();
                System.out.println(child.get());
            } catch (Exception e) {
                throw new IllegalStateException(e);
            }
        });
        System.out.println("after run(), isBound=" + USER.isBound());
    }
}
```

Observed output (JDK 23.0.1). Deterministic.

```text
outside any scope, isBound=false, orElse=anonymous
get() outside a scope: NoSuchElementException
outer: USER=alice
nested: USER=bob
after nested: USER=alice
plain thread: isBound=false
forked child sees alice
after run(), isBound=false
```

**Pitfall.** Binding a value and then handing work to a thread you created yourself, or to an ordinary `ExecutorService`, loses it: the output shows `plain thread: isBound=false`, and calling `USER.get()` there throws `NoSuchElementException`. Request-scoped data such as a user or trace id then appears missing only on some code paths. Pass the value as a parameter, rebind it inside the task with `ScopedValue.where(...)`, or fork through a `StructuredTaskScope`.

## Snippet 5: ForkJoinPool

Each `ForkJoinPool` worker owns a deque. `fork()` pushes a task on the current worker's deque, and idle workers steal from the other end of busy workers' deques. The usual pattern is to fork one half and run the other half directly with `compute()`, then `join()` the forked half, so the worker never waits idle. The `threshold` decides how far the range is split; with 1,000,000 elements the leaf-task counts printed are 1, 4, 128 and 1024 for thresholds 1,000,000, 250,000, 10,000 and 1,000.

Save as `ForkJoinSum.java`, then:

```bash
javac --release 21 -proc:none -d out ForkJoinSum.java
java -cp out ForkJoinSum
```

```java
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveTask;
import java.util.concurrent.atomic.AtomicInteger;

public class ForkJoinSum extends RecursiveTask<Long> {
    static final AtomicInteger LEAVES = new AtomicInteger();

    private final int[] data;
    private final int from, to, threshold;

    ForkJoinSum(int[] data, int from, int to, int threshold) {
        this.data = data;
        this.from = from;
        this.to = to;
        this.threshold = threshold;
    }

    @Override
    protected Long compute() {
        if (to - from <= threshold) {
            LEAVES.incrementAndGet();
            long sum = 0;
            for (int i = from; i < to; i++) {
                sum += data[i];
            }
            return sum;
        }
        int mid = (from + to) >>> 1;
        ForkJoinSum left = new ForkJoinSum(data, from, mid, threshold);
        ForkJoinSum right = new ForkJoinSum(data, mid, to, threshold);
        left.fork();                       // push to this worker's deque; idle workers may steal it
        long r = right.compute();          // run the other half directly: no extra task hop
        return left.join() + r;
    }

    public static void main(String[] args) {
        int n = 1_000_000;
        int[] data = new int[n];
        for (int i = 0; i < n; i++) {
            data[i] = i % 100;
        }
        long sequential = 0;
        for (int v : data) {
            sequential += v;
        }

        ForkJoinPool pool = new ForkJoinPool(4);
        try {
            for (int threshold : new int[] {n, 250_000, 10_000, 1_000}) {
                LEAVES.set(0);
                long result = pool.invoke(new ForkJoinSum(data, 0, n, threshold));
                System.out.println("threshold=" + threshold + " leaf tasks=" + LEAVES.get()
                        + " sum=" + result + " matches sequential=" + (result == sequential));
            }
            System.out.println("parallelism=" + pool.getParallelism()
                    + " stealCount=" + pool.getStealCount());
        } finally {
            pool.shutdown();
        }
        System.out.println("common pool parallelism=" + ForkJoinPool.commonPool().getParallelism()
                + " on " + Runtime.getRuntime().availableProcessors() + " processors");
    }
}
```

Observed output (JDK 23.0.1). Leaf counts and sums are deterministic. `stealCount` and the common-pool parallelism are machine- and run-dependent (here 20 steals, parallelism 7 on 8 processors).

```text
threshold=1000000 leaf tasks=1 sum=49500000 matches sequential=true
threshold=250000 leaf tasks=4 sum=49500000 matches sequential=true
threshold=10000 leaf tasks=128 sum=49500000 matches sequential=true
threshold=1000 leaf tasks=1024 sum=49500000 matches sequential=true
parallelism=4 stealCount=20
common pool parallelism=7 on 8 processors
```

**Pitfall.** Tasks that block (sleep, socket I/O, waiting on a lock) tie up a worker for the whole wait. The common pool, which parallel streams and `CompletableFuture.supplyAsync` without an executor also use, has only `processors - 1` workers (7 here), so a handful of blocking tasks can stall unrelated work elsewhere in the same JVM. A thread dump shows the `ForkJoinPool.commonPool-worker-N` threads parked while the CPU is idle. Use a dedicated pool for blocking work, or `ForkJoinPool.managedBlock`. Setting the threshold so low that tasks are tiny just adds scheduling overhead; to choose it, measure with JMH.

## Snippet 6: StampedLock/LongAdder

`StampedLock.tryOptimisticRead()` returns a version stamp without taking any lock; the reader copies fields into locals and calls `validate(stamp)`, which is false if any write lock was taken in between, in which case it falls back to a real read lock. The lock is not reentrant, and `tryConvertToWriteLock` succeeds only when the caller is the sole reader. `LongAdder` keeps a base value plus a table of cells; threads that collide on a CAS spread across the cells, and `sum()` adds them up.

Save as `StampedAndAdder.java`, then:

```bash
javac --release 21 -proc:none -d out StampedAndAdder.java
java -cp out StampedAndAdder
```

```java
import java.util.concurrent.atomic.LongAdder;
import java.util.concurrent.locks.StampedLock;

public class StampedAndAdder {
    static class Point {
        private final StampedLock sl = new StampedLock();
        private double x, y;

        void move(double dx, double dy) {
            long stamp = sl.writeLock();
            try {
                x += dx;
                y += dy;
            } finally {
                sl.unlockWrite(stamp);
            }
        }

        double distanceFromOrigin() {
            long stamp = sl.tryOptimisticRead();   // no lock taken, just a version stamp
            double cx = x, cy = y;                 // may be torn if a writer intervenes
            if (!sl.validate(stamp)) {             // a write happened: fall back to a real read lock
                stamp = sl.readLock();
                try {
                    cx = x;
                    cy = y;
                } finally {
                    sl.unlockRead(stamp);
                }
            }
            return Math.sqrt(cx * cx + cy * cy);
        }
    }

    public static void main(String[] args) throws Exception {
        Point p = new Point();
        p.move(3, 4);
        System.out.println("distance = " + p.distanceFromOrigin());

        // Optimistic stamps are invalidated by any later write.
        StampedLock sl = new StampedLock();
        long optimistic = sl.tryOptimisticRead();
        System.out.println("validate before write: " + sl.validate(optimistic));
        long w = sl.writeLock();
        sl.unlockWrite(w);
        System.out.println("validate after write:  " + sl.validate(optimistic));

        // StampedLock is not reentrant; upgrade explicitly instead of locking twice.
        long r = sl.readLock();
        long upgraded = sl.tryConvertToWriteLock(r);
        System.out.println("sole reader upgraded to write lock: " + (upgraded != 0L) + " isWriteLocked=" + sl.isWriteLocked());
        sl.unlock(upgraded);

        long r1 = sl.readLock();
        long r2 = sl.readLock();       // second reader (here the same thread: reads are shared)
        long failed = sl.tryConvertToWriteLock(r1);
        System.out.println("upgrade with another reader present: " + (failed != 0L ? "succeeded" : "refused (returned 0)"));
        sl.unlockRead(r1);
        sl.unlockRead(r2);

        // LongAdder: striped cells absorb contended increments; sum() adds them up.
        LongAdder adder = new LongAdder();
        Thread[] ts = new Thread[8];
        for (int t = 0; t < ts.length; t++) {
            ts[t] = new Thread(() -> {
                for (int i = 0; i < 100_000; i++) {
                    adder.increment();
                }
            });
            ts[t].start();
        }
        for (Thread t : ts) {
            t.join();
        }
        System.out.println("LongAdder sum after 8 x 100000 increments: " + adder.sum());
        System.out.println("sumThenReset: " + adder.sumThenReset() + ", then sum: " + adder.sum());
    }
}
```

Observed output (JDK 23.0.1). Deterministic: the `LongAdder` total is exact after the threads are joined.

```text
distance = 5.0
validate before write: true
validate after write:  false
sole reader upgraded to write lock: true isWriteLocked=true
upgrade with another reader present: refused (returned 0)
LongAdder sum after 8 x 100000 increments: 800000
sumThenReset: 800000, then sum: 0
```

**Pitfall.** The lock does not know about the current thread. A thread that holds a read stamp and then calls `writeLock()` waits for readers to drain, including itself, and hangs forever; the thread dump shows it parked inside `StampedLock`. The output shows the safe route: `tryConvertToWriteLock` succeeds for a sole reader and returns 0 (refused) when a second reader exists, so you must handle the 0 by releasing and re-acquiring. Also, data read optimistically must not be used (as an index, say) before `validate` returns true.
