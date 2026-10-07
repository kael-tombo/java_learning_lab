# Code Deep Dive — Java Concurrency Basics (concurrency)

Six runnable snippets for the `concurrency` lab: the six `Thread.State` values observed from outside, lost updates on a `volatile` counter, a hand-written bounded buffer with `ReentrantLock` and two `Condition`s, `ThreadPoolExecutor` queueing and rejection, `Future` versus `CompletableFuture` error handling, and CAS with the ABA problem. Each snippet is a single Java 21 source file using only the JDK. Output blocks were pasted from real runs on JDK 23.0.1; thread-timing dependent numbers are flagged as such.

## Snippet 1: Thread lifecycle

`Thread.State` has six values. `NEW` before `start()`, `RUNNABLE` while running or ready (a busy loop counts), `BLOCKED` while waiting to enter a `synchronized` block, `WAITING` inside `Object.wait()`, `join()` or `LockSupport.park()`, `TIMED_WAITING` in `sleep` or a timed wait, and `TERMINATED` after `run` returns. A thread woken from `Object.wait()` must re-acquire the monitor first, so it can pass through `BLOCKED` on the way out. `getState()` is a monitoring snapshot, which is why the snippet polls until the wanted state appears.

Save as `ThreadStates.java`, then:

```bash
javac --release 21 -proc:none -d out ThreadStates.java
java -cp out ThreadStates
```

```java
public class ThreadStates {
    static final Object MONITOR = new Object();
    static volatile boolean go;

    // Poll until the thread reaches the wanted state (or 5 s pass) and return what we saw.
    static Thread.State awaitState(Thread t, Thread.State wanted) throws InterruptedException {
        long deadline = System.nanoTime() + 5_000_000_000L;
        while (t.getState() != wanted && System.nanoTime() < deadline) {
            Thread.sleep(1);
        }
        return t.getState();
    }

    public static void main(String[] args) throws Exception {
        Thread worker = new Thread(() -> {
            while (!go) {
                Thread.onSpinWait();               // busy loop: RUNNABLE
            }
            synchronized (MONITOR) {               // main holds it first: BLOCKED
                try {
                    MONITOR.wait();                // Object.wait without timeout: WAITING
                    Thread.sleep(200);             // sleep with timeout: TIMED_WAITING
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }, "worker");

        System.out.println("before start():        " + worker.getState());
        synchronized (MONITOR) {
            worker.start();
            System.out.println("spinning:              " + awaitState(worker, Thread.State.RUNNABLE));
            go = true;                             // worker now tries to enter MONITOR, which main owns
            System.out.println("monitor owned by main: " + awaitState(worker, Thread.State.BLOCKED));
        }                                          // leaving the block releases MONITOR
        System.out.println("inside wait():         " + awaitState(worker, Thread.State.WAITING));
        synchronized (MONITOR) {
            MONITOR.notify();
        }
        System.out.println("inside sleep(200):     " + awaitState(worker, Thread.State.TIMED_WAITING));
        worker.join();
        System.out.println("after join():          " + worker.getState() + " alive=" + worker.isAlive());

        try {
            worker.start();
        } catch (IllegalThreadStateException e) {
            System.out.println("restarting a finished thread: IllegalThreadStateException");
        }
    }
}
```

Observed output (JDK 23.0.1). Deterministic: each state is awaited for up to 5 seconds before it is printed.

```text
before start():        NEW
spinning:              RUNNABLE
monitor owned by main: BLOCKED
inside wait():         WAITING
inside sleep(200):     TIMED_WAITING
after join():          TERMINATED alive=false
restarting a finished thread: IllegalThreadStateException
```

**Pitfall.** A `Thread` object is single use. Calling `start()` on one that has already run throws `IllegalThreadStateException`, as the last line shows. This usually appears in retry or restart logic that keeps the old `Thread` in a field; create a new `Thread` (or submit to an executor) for each run. A different frequent mistake is calling `run()` directly, which compiles and works but executes on the caller's thread: the thread name in a log line gives it away.

## Snippet 2: synchronized & volatile

`volatile` makes each individual read or write of that variable visible to other threads and ordered, but `counter++` is a read, an add and a write, so two threads can read the same value and both write back the same result. `synchronized` provides mutual exclusion and also a happens-before edge: releasing a monitor happens-before every later acquisition of the same monitor. A volatile stop flag is correct because one thread writes it and the others only read it.

Save as `SyncVsVolatile.java`, then:

```bash
javac --release 21 -proc:none -d out SyncVsVolatile.java
java -cp out SyncVsVolatile
```

```java
public class SyncVsVolatile {
    static final int THREADS = 4, PER_THREAD = 100_000;

    static volatile int volatileCounter;   // each read and each write is atomic, ++ is not
    static int syncCounter;                // guarded by LOCK
    static final Object LOCK = new Object();
    static volatile boolean stop;          // a one-writer flag is the legitimate volatile use

    static void runAll(Runnable body) throws InterruptedException {
        Thread[] ts = new Thread[THREADS];
        for (int i = 0; i < THREADS; i++) {
            ts[i] = new Thread(body);
            ts[i].start();
        }
        for (Thread t : ts) {
            t.join();
        }
    }

    public static void main(String[] args) throws Exception {
        int expected = THREADS * PER_THREAD;

        runAll(() -> {
            for (int i = 0; i < PER_THREAD; i++) {
                volatileCounter++;            // read, add, write: three steps
            }
        });
        System.out.println("volatile ++  : " + volatileCounter + " of " + expected
                + " (lost " + (expected - volatileCounter) + ")");

        runAll(() -> {
            for (int i = 0; i < PER_THREAD; i++) {
                synchronized (LOCK) {
                    syncCounter++;
                }
            }
        });
        System.out.println("synchronized : " + syncCounter + " of " + expected);

        // volatile is enough when one thread publishes a single value and the others only read it.
        Thread spinner = new Thread(() -> {
            long spins = 0;
            while (!stop) {
                spins++;
            }
            System.out.println("spinner saw stop=true after looping");
        });
        spinner.start();
        Thread.sleep(100);
        stop = true;
        spinner.join(2_000);
        System.out.println("spinner terminated: " + !spinner.isAlive());
    }
}
```

Observed output (JDK 23.0.1). Nondeterministic. The `volatile ++` total changes on every run (here 153534 of 400000); the `synchronized` row is always 400000 and the flag test always terminates.

```text
volatile ++  : 153534 of 400000 (lost 246466)
synchronized : 400000 of 400000
spinner saw stop=true after looping
spinner terminated: true
```

**Pitfall.** A `volatile` counter looks thread-safe, passes single-threaded tests, and loses updates under contention: this run lost 246466 of 400000 increments with no exception. You notice it only as totals that do not add up, and the amount changes between runs. Use `AtomicInteger`/`LongAdder` for counters or guard the compound action with a lock.

## Snippet 3: Locks & conditions

`ReentrantLock` is an explicit lock: the owning thread may lock it again (the hold count goes up), `tryLock(timeout)` lets a thread give up instead of blocking, and one lock can have several `Condition` queues. `Condition.await()` atomically releases the lock and parks the thread; `signal()` moves one waiter back to compete for the lock. With separate `notFull` and `notEmpty` conditions, a producer only wakes consumers and vice versa, and every wait sits inside a `while` loop because a woken thread must re-check its predicate.

Save as `BoundedBuffer.java`, then:

```bash
javac --release 21 -proc:none -d out BoundedBuffer.java
java -cp out BoundedBuffer
```

```java
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

public class BoundedBuffer<T> {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();
    private final ArrayDeque<T> items = new ArrayDeque<>();
    private final int capacity;

    BoundedBuffer(int capacity) { this.capacity = capacity; }

    void put(T item) throws InterruptedException {
        lock.lock();
        try {
            while (items.size() == capacity) {   // loop: guards against spurious wakeups
                notFull.await();
            }
            items.addLast(item);
            notEmpty.signal();
        } finally {
            lock.unlock();                        // always in finally
        }
    }

    T take() throws InterruptedException {
        lock.lock();
        try {
            while (items.isEmpty()) {
                notEmpty.await();
            }
            T item = items.removeFirst();
            notFull.signal();
            return item;
        } finally {
            lock.unlock();
        }
    }

    public static void main(String[] args) throws Exception {
        BoundedBuffer<Integer> buffer = new BoundedBuffer<>(3);
        List<Integer> consumed = new ArrayList<>();

        Thread producer = new Thread(() -> {
            try {
                for (int i = 1; i <= 20; i++) {
                    buffer.put(i);               // blocks whenever 3 items are already waiting
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        Thread consumer = new Thread(() -> {
            try {
                for (int i = 1; i <= 20; i++) {
                    consumed.add(buffer.take());
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        producer.start();
        consumer.start();
        producer.join();
        consumer.join();
        System.out.println("consumed in order: " + consumed);

        // Reentrancy and the hold count.
        ReentrantLock lock = buffer.lock;
        lock.lock();
        lock.lock();
        System.out.println("hold count after two lock() calls: " + lock.getHoldCount());
        lock.unlock();
        System.out.println("held by me after one unlock(): " + lock.isHeldByCurrentThread());

        // Another thread cannot get the lock; tryLock with a timeout reports it instead of hanging.
        boolean[] otherGotIt = new boolean[1];
        Thread other = new Thread(() -> {
            try {
                otherGotIt[0] = lock.tryLock(100, TimeUnit.MILLISECONDS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        other.start();
        other.join();
        System.out.println("other thread tryLock(100 ms) succeeded: " + otherGotIt[0]);
        lock.unlock();
        System.out.println("fully released: " + !lock.isLocked());
    }
}
```

Observed output (JDK 23.0.1). Deterministic: one producer and one consumer, so the consumed order is always 1..20.

```text
consumed in order: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
hold count after two lock() calls: 2
held by me after one unlock(): true
other thread tryLock(100 ms) succeeded: false
fully released: true
```

**Pitfall.** Forgetting `unlock()` on an exception path is the failure that `synchronized` cannot have. If code between `lock()` and `unlock()` throws and `unlock()` is not in a `finally`, the lock stays held for the life of the thread, and every other thread that needs it blocks. The last part of the output shows what those threads experience: while the lock is held, `tryLock(100 ms)` from another thread returns `false`. In a thread dump the symptom is many threads parked on the same `ReentrantLock` with one owner that is doing something unrelated.

## Snippet 4: Executors & pools

`ThreadPoolExecutor` creates threads up to `corePoolSize` for new tasks, then queues tasks, and only when the queue is full does it grow toward `maximumPoolSize`; if that is impossible too, the rejection policy runs (`AbortPolicy`, the default, throws `RejectedExecutionException`). `Executors.newFixedThreadPool(2)` uses a `LinkedBlockingQueue` whose capacity is `Integer.MAX_VALUE`, and the first output block shows that number. The second pool has one thread and a queue of one, so the third task is rejected.

Save as `PoolBehavior.java`, then:

```bash
javac --release 21 -proc:none -d out PoolBehavior.java
java -cp out PoolBehavior
```

```java
import java.util.Set;
import java.util.TreeSet;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class PoolBehavior {
    public static void main(String[] args) throws Exception {
        // 1. A fixed pool of 2 runs 4 tasks on exactly 2 threads; the other 2 tasks wait in the queue.
        ExecutorService fixed = Executors.newFixedThreadPool(2);
        Set<String> threadNames = java.util.Collections.synchronizedSet(new TreeSet<>());
        Future<?>[] futures = new Future<?>[4];
        for (int i = 0; i < 4; i++) {
            futures[i] = fixed.submit(() -> threadNames.add(Thread.currentThread().getName()));
        }
        for (Future<?> f : futures) {
            f.get();
        }
        System.out.println("threads used by 4 tasks: " + threadNames);
        System.out.println("fixed pool queue capacity: "
                + ((ThreadPoolExecutor) fixed).getQueue().remainingCapacity() + " (effectively unbounded)");
        fixed.shutdown();

        // 2. A bounded pool: 1 thread + queue of 1 -> the third task is rejected.
        ThreadPoolExecutor bounded = new ThreadPoolExecutor(
                1, 1, 0, TimeUnit.SECONDS, new ArrayBlockingQueue<>(1));
        CountDownLatch release = new CountDownLatch(1);
        CountDownLatch running = new CountDownLatch(1);
        Runnable blocker = () -> {
            running.countDown();
            try {
                release.await();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };
        bounded.execute(blocker);                 // starts the single worker thread
        running.await();
        bounded.execute(blocker);                 // sits in the queue
        try {
            bounded.execute(blocker);             // no thread free, queue full
        } catch (RejectedExecutionException e) {
            System.out.println("third task rejected: RejectedExecutionException");
        }
        System.out.println("active=" + bounded.getActiveCount() + " queued=" + bounded.getQueue().size());
        release.countDown();
        bounded.shutdown();
        System.out.println("terminated in time: " + bounded.awaitTermination(5, TimeUnit.SECONDS)
                + ", completed tasks=" + bounded.getCompletedTaskCount());

        try {
            bounded.execute(blocker);
        } catch (RejectedExecutionException e) {
            System.out.println("submit after shutdown: RejectedExecutionException");
        }
    }
}
```

Observed output (JDK 23.0.1). Deterministic: the set of thread names is always the same two, even though which task ran on which thread varies.

```text
threads used by 4 tasks: [pool-1-thread-1, pool-1-thread-2]
fixed pool queue capacity: 2147483647 (effectively unbounded)
third task rejected: RejectedExecutionException
active=1 queued=1
terminated in time: true, completed tasks=2
submit after shutdown: RejectedExecutionException
```

**Pitfall.** The unbounded queue in `newFixedThreadPool` gives no back-pressure. If tasks arrive faster than the 2 threads finish them, the queue keeps growing until the heap is exhausted and the JVM fails with `OutOfMemoryError`; there is never a `RejectedExecutionException` to warn you. You notice it as `getQueue().size()` climbing and heap use rising steadily. Build a `ThreadPoolExecutor` with a bounded queue and an explicit rejection policy, and call `shutdown()`: pool threads are non-daemon, so a forgotten pool also keeps the JVM from exiting.

## Snippet 5: Futures & CompletableFuture

`Future.get()` blocks and wraps a task failure in a checked `ExecutionException`; a timed `get` that expires leaves the task running unless you call `cancel(true)`, which interrupts it. `CompletableFuture` composes stages (`thenCombine`, `thenApply`, `exceptionally`, `handle`) without blocking. A stage that throws completes exceptionally, `join()` throws the unchecked `CompletionException` and `get()` throws `ExecutionException`, both carrying the same cause. The snippet passes its own executor to `supplyAsync`; without one the task would run on `ForkJoinPool.commonPool()`.

Save as `FutureStyles.java`, then:

```bash
javac --release 21 -proc:none -d out FutureStyles.java
java -cp out FutureStyles
```

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class FutureStyles {
    static int slowSquare(int n) {
        try {
            Thread.sleep(50);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return n * n;
    }

    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(3);
        try {
            // Plain Future: get() blocks and wraps task failures in ExecutionException.
            Future<Integer> ok = pool.submit(() -> slowSquare(7));
            System.out.println("Future.get: " + ok.get());
            Future<Integer> bad = pool.submit(() -> {
                if (true) {
                    throw new IllegalStateException("boom");
                }
                return 0;
            });
            try {
                bad.get();
            } catch (ExecutionException e) {
                System.out.println("get() wraps: " + e.getClass().getSimpleName()
                        + " cause=" + e.getCause());
            }

            Future<Integer> slow = pool.submit(() -> {
                Thread.sleep(2_000);
                return 1;
            });
            try {
                slow.get(100, TimeUnit.MILLISECONDS);
            } catch (TimeoutException e) {
                System.out.println("get(100 ms): TimeoutException, cancel -> " + slow.cancel(true)
                        + ", isCancelled=" + slow.isCancelled());
            }

            // CompletableFuture: compose without blocking; pass the executor explicitly.
            CompletableFuture<Integer> a = CompletableFuture.supplyAsync(() -> slowSquare(3), pool);
            CompletableFuture<Integer> b = CompletableFuture.supplyAsync(() -> slowSquare(4), pool);
            CompletableFuture<String> combined = a.thenCombine(b, Integer::sum)
                    .thenApply(sum -> "3^2 + 4^2 = " + sum);
            System.out.println(combined.get());

            CompletableFuture<Integer> failing = CompletableFuture
                    .supplyAsync(() -> {
                        throw new IllegalArgumentException("bad input");
                    }, pool);
            System.out.println("exceptionally: " + failing.exceptionally(t -> -1).join());
            System.out.println("handle:        " + failing.handle((v, t) -> t == null ? "ok" : "failed with " + t).join());

            // join() throws CompletionException; get() throws ExecutionException; both wrap the same cause.
            try {
                failing.join();
            } catch (CompletionException e) {
                System.out.println("join() wraps: " + e.getClass().getSimpleName() + " cause=" + e.getCause());
            }
            try {
                failing.get();
            } catch (ExecutionException e) {
                System.out.println("get()  wraps: " + e.getClass().getSimpleName() + " cause=" + e.getCause());
            }
        } finally {
            pool.shutdownNow();
        }
    }
}
```

Observed output (JDK 23.0.1). Deterministic text: no thread names or timings are printed.

```text
Future.get: 49
get() wraps: ExecutionException cause=java.lang.IllegalStateException: boom
get(100 ms): TimeoutException, cancel -> true, isCancelled=true
3^2 + 4^2 = 25
exceptionally: -1
handle:        failed with java.util.concurrent.CompletionException: java.lang.IllegalArgumentException: bad input
join() wraps: CompletionException cause=java.lang.IllegalArgumentException: bad input
get()  wraps: ExecutionException cause=java.lang.IllegalArgumentException: bad input
```

**Pitfall.** Error handlers in `exceptionally` and `handle` receive the `CompletionException` wrapper, not the original exception. The `handle` line in the output reads `failed with java.util.concurrent.CompletionException: java.lang.IllegalArgumentException: bad input`, so `t instanceof IllegalArgumentException` is false there and a recovery branch that depends on it never runs. Unwrap with `t.getCause()` (checking that `t` is a `CompletionException` first) before choosing a recovery path.

## Snippet 6: atomics

`AtomicInteger.incrementAndGet` is a single atomic read-modify-write, so the counter is exact without a lock. A CAS loop reads the current value, computes a new one and calls `compareAndSet`, retrying if another thread got there first; the snippet uses it to keep a running maximum. CAS compares only the value, not the history, so a reference that went A→B→A looks unchanged. `AtomicStampedReference` pairs the reference with an int stamp that must match too.

Save as `AtomicsDemo.java`, then:

```bash
javac --release 21 -proc:none -d out AtomicsDemo.java
java -cp out AtomicsDemo
```

```java
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.atomic.AtomicStampedReference;

public class AtomicsDemo {
    static final int THREADS = 4, PER_THREAD = 100_000;

    public static void main(String[] args) throws Exception {
        // 1. incrementAndGet is one atomic read-modify-write.
        AtomicInteger counter = new AtomicInteger();
        // 2. A CAS loop keeps a running maximum without a lock.
        AtomicInteger max = new AtomicInteger(Integer.MIN_VALUE);

        Thread[] ts = new Thread[THREADS];
        for (int t = 0; t < THREADS; t++) {
            final int base = t * PER_THREAD;
            ts[t] = new Thread(() -> {
                for (int i = 0; i < PER_THREAD; i++) {
                    counter.incrementAndGet();
                    int candidate = base + i;
                    int current;
                    do {
                        current = max.get();
                    } while (candidate > current && !max.compareAndSet(current, candidate));
                }
            });
            ts[t].start();
        }
        for (Thread t : ts) {
            t.join();
        }
        System.out.println("counter = " + counter.get() + " (expected " + THREADS * PER_THREAD + ")");
        System.out.println("max     = " + max.get() + " (expected " + (THREADS * PER_THREAD - 1) + ")");
        System.out.println("accumulateAndGet(max, 5) -> " + max.accumulateAndGet(5, Math::max));

        // 3. ABA: the value goes A -> B -> A, and a plain CAS cannot tell.
        AtomicReference<String> ref = new AtomicReference<>("A");
        String seenByThreadOne = ref.get();
        ref.set("B");
        ref.set("A");
        System.out.println("AtomicReference CAS(A->C) after A->B->A: "
                + ref.compareAndSet(seenByThreadOne, "C"));

        AtomicStampedReference<String> stamped = new AtomicStampedReference<>("A", 0);
        int[] stampHolder = new int[1];
        String seen = stamped.get(stampHolder);
        int seenStamp = stampHolder[0];
        stamped.set("B", seenStamp + 1);
        stamped.set("A", seenStamp + 2);
        System.out.println("AtomicStampedReference CAS(A->C) after A->B->A: "
                + stamped.compareAndSet(seen, "C", seenStamp, seenStamp + 1));
    }
}
```

Observed output (JDK 23.0.1). Deterministic: the final counter and maximum are fixed, whatever the thread interleaving.

```text
counter = 400000 (expected 400000)
max     = 399999 (expected 399999)
accumulateAndGet(max, 5) -> 399999
AtomicReference CAS(A->C) after A->B->A: true
AtomicStampedReference CAS(A->C) after A->B->A: false
```

**Pitfall.** The ABA problem: the output shows the plain `AtomicReference` CAS succeeding (`true`) after `A→B→A`, while the stamped version refuses (`false`). In a lock-free stack or queue that recycles nodes, a thread that read `top = A`, was paused, and resumed after A was popped and pushed back, will CAS successfully against a `next` pointer that is no longer valid, corrupting the structure. It is rare and shows up as occasional lost or duplicated elements. Stamps, or never reusing nodes, avoid it.
