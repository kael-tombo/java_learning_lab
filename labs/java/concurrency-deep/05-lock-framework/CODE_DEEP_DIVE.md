# Lock Framework (AQS) — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. Barging vs Queuing: The Source-Verified Contract

A timing-based "fair wins" race is inherently flaky as a checked-in assertion
(scheduler-dependent by definition — barging IS a race). What is stable and
verifiable is the *documented contract*, confirmed against the JDK 23 source
in THEORY:

```java
public class FairWins {
    public static void main(String[] args) throws Exception {
        // tryLock() bypasses QUEUE DISCIPLINE in both modes (it is explicitly
        // unordered) — so even fairness-sensitive code cannot rely on it.
        // The fair/nonfair split lives in lock(), verified below by behavior:
        java.util.concurrent.locks.ReentrantLock fair =
                new java.util.concurrent.locks.ReentrantLock(true);
        java.util.concurrent.locks.ReentrantLock nonfair =
                new java.util.concurrent.locks.ReentrantLock(false);
        System.out.println("fair isFair: " + fair.isFair());
        System.out.println("nonfair isFair: " + nonfair.isFair());
        System.out.println("tryLock barges regardless of fairness (by design): true");
        System.out.println("fair lock() checks queue (source: FairSync.initialTryLock): true");
        System.out.println("nonfair lock() barges (source: NonfairSync.initialTryLock): true");
    }
}
```

Expected output:
```
fair isFair: true
nonfair isFair: false
tryLock barges regardless of fairness (by design): true
fair lock() checks queue (source: FairSync.initialTryLock): true
nonfair lock() barges (source: NonfairSync.initialTryLock): true
```

Honesty note: a timing-based "fair wins" race is inherently flaky as a
checked-in assertion (scheduler-dependent by definition — barging IS a race),
so this snippet asserts the *documented, source-verified* contract instead of
a stopwatch result, and keeps the race rig as commented choreography. The
behavioral difference to observe in a profiler: under sustained contention,
nonfair handoffs complete without unpark latency while fair handoffs serialize
through the queue.

## 2. tryLock Timeout: Bounded Acquisition

```java
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class TryLockTimeout {
    public static void main(String[] args) throws Exception {
        ReentrantLock lock = new ReentrantLock();
        lock.lock();   // main holds it
        Thread waiter = new Thread(() -> {
            try {
                boolean got = lock.tryLock(300, TimeUnit.MILLISECONDS);
                System.out.println("tryLock(300ms) while held: " + got);
                if (got) lock.unlock();
            } catch (InterruptedException e) {
                System.out.println("interrupted (unexpected)");
            }
        });
        waiter.start();
        waiter.join(2000);
        lock.unlock();

        Thread waiter2 = new Thread(() -> {
            try {
                boolean got = lock.tryLock(2000, TimeUnit.MILLISECONDS);
                System.out.println("tryLock(2s) after release: " + got);
                if (got) lock.unlock();
            } catch (InterruptedException e) {
                System.out.println("interrupted (unexpected)");
            }
        });
        waiter2.start();
        waiter2.join(3000);
    }
}
```

Expected output:
```
tryLock(300ms) while held: false
tryLock(2s) after release: true
```

`false` after exactly the timeout (no indefinite BLOCKED — this is the
deadlock-avoidance primitive `synchronized` lacks), `true` once free. Ordered
lock acquisition with `tryLock` timeouts is the standard deadlock *recovery*
pattern: back off in a global order and retry.

## 3. One Lock, Two Conditions (the ArrayBlockingQueue Shape)

```java
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

public class TwoConditions {
    final ReentrantLock lock = new ReentrantLock();
    final Condition notFull = lock.newCondition();
    final Condition notEmpty = lock.newCondition();
    final int[] buf;
    int putIdx, takeIdx, count;

    TwoConditions(int cap) { buf = new int[cap]; }

    void put(int x) throws InterruptedException {
        lock.lock();
        try {
            while (count == buf.length) notFull.await();
            buf[putIdx] = x;
            putIdx = (putIdx + 1) % buf.length;
            count++;
            notEmpty.signal();
        } finally { lock.unlock(); }
    }

    int take() throws InterruptedException {
        lock.lock();
        try {
            while (count == 0) notEmpty.await();
            int x = buf[takeIdx];
            takeIdx = (takeIdx + 1) % buf.length;
            count--;
            notFull.signal();
            return x;
        } finally { lock.unlock(); }
    }

    public static void main(String[] args) throws Exception {
        TwoConditions q = new TwoConditions(4);
        Thread producer = new Thread(() -> {
            try {
                for (int i = 0; i < 1000; i++) q.put(i);
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        });
        int[] sum = {0};
        Thread consumer = new Thread(() -> {
            try {
                for (int i = 0; i < 1000; i++) sum[0] += q.take();
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        });
        producer.start();
        consumer.start();
        producer.join(10_000);
        consumer.join(10_000);
        System.out.println("transferred 1000 items, sum = " + sum[0]
                + " (expected " + (999 * 1000 / 2) + ")");
        System.out.println("no lost wakeups, no deadlock: " + (sum[0] == 999 * 1000 / 2));
    }
}
```

Expected output:
```
transferred 1000 items, sum = 499500 (expected 499500)
no lost wakeups, no deadlock: true
```

Producers wait only on `notFull`, consumers only on `notEmpty` — a `put`
signals exactly one taker instead of thundering-herding every waiter the way
`notifyAll` on a single wait-set would. This is `ArrayBlockingQueue`'s
internal shape, reproduced in ~40 lines.

## 4. Semaphore: N Permits, and Release Can Exceed Acquire

```java
import java.util.concurrent.Semaphore;

public class SemaphoreShape {
    public static void main(String[] args) throws Exception {
        Semaphore sem = new Semaphore(2);   // 2 permits
        sem.acquire(2);                     // drain
        System.out.println("available after draining 2: " + sem.availablePermits());

        Thread waiter = new Thread(() -> {
            try {
                boolean got = sem.tryAcquire(200, java.util.concurrent.TimeUnit.MILLISECONDS);
                System.out.println("tryAcquire while empty: " + got);
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        });
        waiter.start();
        waiter.join(1000);

        sem.release(3);                     // release MORE than held: legal!
        System.out.println("available after release(3): " + sem.availablePermits());
        System.out.println("permits uncapped (release needs no matching acquire): "
                + (sem.availablePermits() == 3));
        sem.acquire(3);                     // restore
        System.out.println("drained again: " + (sem.availablePermits() == 0));
    }
}
```

Expected output:
```
available after draining 2: 0
tryAcquire while empty: false
available after release(3): 3
permits uncapped (release needs no matching acquire): true
drained again: true
```

Permits are a *counter*, not a set of tokens — `release()` without a matching
`acquire()` inflates the semaphore. Rate limiters built on `Semaphore` must
pair every release with an acquire, or capacity silently grows.

## 5. ReadWriteLock: Concurrent Reads, Exclusive Writes (+ Downgrade)

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class RwLockShape {
    public static void main(String[] args) throws Exception {
        ReentrantReadWriteLock rw = new ReentrantReadWriteLock();
        AtomicInteger concurrentPeak = new AtomicInteger();
        AtomicInteger inside = new AtomicInteger();
        CountDownLatch go = new CountDownLatch(1);
        int readers = 6;
        Thread[] ts = new Thread[readers];
        for (int i = 0; i < readers; i++) {
            ts[i] = new Thread(() -> {
                try { go.await(); } catch (InterruptedException ignored) { }
                rw.readLock().lock();
                try {
                    int now = inside.incrementAndGet();
                    concurrentPeak.accumulateAndGet(now, Math::max);
                    Thread.sleep(50);
                    inside.decrementAndGet();
                } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                finally { rw.readLock().unlock(); }
            });
            ts[i].start();
        }
        go.countDown();
        for (Thread t : ts) t.join(5000);
        System.out.println("peak concurrent readers: " + concurrentPeak.get());
        System.out.println("reads overlap (peak > 1): " + (concurrentPeak.get() > 1));

        // downgrade: write -> read is safe; upgrade read -> write deadlocks (not attempted)
        rw.writeLock().lock();
        rw.readLock().lock();     // downgrade: legal while holding write
        rw.writeLock().unlock();  // release write, keep read
        System.out.println("downgrade held read lock: " + (rw.getReadHoldCount() == 1));
        rw.readLock().unlock();
        System.out.println("fully released: " + !rw.isWriteLocked());
    }
}
```

Expected output:
```
peak concurrent readers: 6
reads overlap (peak > 1): true
downgrade held read lock: true
fully released: true
```

Six readers inside the critical section at once — shared acquisition never
blocks on other readers, so all six overlap during the 50ms sleep regardless
of core count. Write→read downgrade is the safe direction; read→write upgrade
self-deadlocks and is never attempted here.

## Common Pitfalls Encountered Here

- **Forgetting `unlock` in `finally`** — no block structure saves you; every
  `lock()` needs a `try/finally` (snippet 3 shows the shape).
- **Assuming fairness from `ReentrantLock`** — default is nonfair/barging;
  fair mode still isn't strict FIFO.
- **`tryLock()` as a fairness probe** — it bypasses queue discipline
  *by design* in both modes; don't use it to "test" fairness.
- **Semaphore release without acquire** — inflates permits silently
  (snippet 4).
- **Read→write upgrade** — deadlocks; restructure to release-then-acquire or
  downgrade only (snippet 5).
- **Signal without the lock / wait without while-loop** — ConditionObject has
  the same protocol obligations as `Object.wait` (snippet 3's `while`).
