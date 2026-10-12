# StampedLock — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. The Optimistic Pattern: Sample, Copy, Validate

```java
import java.util.concurrent.locks.StampedLock;

public class OptimisticPoint {
    static class Point {
        double x, y;
        final StampedLock lock = new StampedLock();
        void move(double dx, double dy) {
            long s = lock.writeLock();
            try { x += dx; y += dy; }
            finally { lock.unlockWrite(s); }
        }
        double distanceFromOrigin() {
            long s = lock.tryOptimisticRead();   // no CAS, no queue
            double cx = x, cy = y;               // plain reads into locals
            if (!lock.validate(s)) {             // writer intervened?
                s = lock.readLock();             // fall back
                try { cx = x; cy = y; }
                finally { lock.unlockRead(s); }
            }
            return Math.hypot(cx, cy);           // act ONLY on validated data
        }
    }

    public static void main(String[] args) throws Exception {
        Point p = new Point();
        p.move(3, 4);
        System.out.println("distance = " + p.distanceFromOrigin()
                + " (expected 5.0)");
        System.out.println("exact: " + (p.distanceFromOrigin() == 5.0));

        // stamp 0 is never valid
        System.out.println("validate(0) always false: " + !p.lock.validate(0L));
    }
}
```

Expected output:
```
distance = 5.0 (expected 5.0)
exact: true
validate(0) always false: true
```

`Math.hypot` runs on validated-or-fallback data only — never on a torn
(x-new, y-old) snapshot. The obligations from THEORY in one picture: locals
first, validate second, act third.

## 2. Optimism Pays Under Read Pressure, Costs Under Write Pressure

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.StampedLock;

public class OptimismPayoff {
    static class Counter {
        long v;
        final StampedLock lock = new StampedLock();
        void add(long d) {
            long s = lock.writeLock();
            try { v += d; } finally { lock.unlockWrite(s); }
        }
        long optimisticGet() {
            long s = lock.tryOptimisticRead();
            long c = v;
            if (!lock.validate(s)) {
                s = lock.readLock();
                try { c = v; } finally { lock.unlockRead(s); }
            }
            return c;
        }
        long pessimisticGet() {
            long s = lock.readLock();
            try { return v; } finally { lock.unlockRead(s); }
        }
    }

    public static void main(String[] args) throws Exception {
        Counter c = new Counter();
        int readers = 6, readsEach = 300_000;
        CountDownLatch go = new CountDownLatch(1);
        AtomicLong optFallbacks = new AtomicLong();

        // Phase 1: no writers — optimism should (almost) never fall back
        Thread[] ts = new Thread[readers];
        for (int i = 0; i < readers; i++) {
            ts[i] = new Thread(() -> {
                try { go.await(); } catch (InterruptedException ignored) { }
                for (int j = 0; j < readsEach; j++) {
                    long s = c.lock.tryOptimisticRead();
                    long x = c.v;
                    if (!c.lock.validate(s)) optFallbacks.incrementAndGet();
                }
            });
            ts[i].start();
        }
        go.countDown();
        for (Thread t : ts) t.join(30_000);
        System.out.println("read-only fallbacks = " + optFallbacks.get());
        System.out.println("no-writer optimism never falls back: " + (optFallbacks.get() == 0));

        // Phase 2: hammer writes while one reader samples — fallbacks happen
        CountDownLatch go2 = new CountDownLatch(1);
        AtomicLong fallbacks2 = new AtomicLong();
        Thread writer = new Thread(() -> {
            try { go2.await(); } catch (InterruptedException ignored) { }
            for (int j = 0; j < 200_000; j++) c.add(1);
        });
        Thread reader = new Thread(() -> {
            try { go2.await(); } catch (InterruptedException ignored) { }
            for (int j = 0; j < 200_000; j++) {
                long s = c.lock.tryOptimisticRead();
                long x = c.v;
                if (!c.lock.validate(s)) fallbacks2.incrementAndGet();
            }
        });
        writer.start();
        reader.start();
        go2.countDown();
        writer.join(30_000);
        reader.join(30_000);
        System.out.println("write-heavy fallbacks = " + fallbacks2.get());
        System.out.println("writer pressure causes fallbacks: " + (fallbacks2.get() > 0));
        System.out.println("counter exact (writes serialized): " + (c.v == 200_000));
    }
}
```

Expected output (fallback counts vary — elided):
```
...
no-writer optimism never falls back: true
...
writer pressure causes fallbacks: true
counter exact (writes serialized): true
```

Phase 1 asserts the mechanism (zero writers → validation always succeeds —
deterministic, not statistical). Phase 2 asserts the degradation direction
(any sustained writer makes *some* read straddle a write — near-certain with
200k overlapping ops). The exact counts are machine-dependent; the two
booleans are structural.

## 3. tryConvertToWriteLock: Upgrade That RRWL Can't Do

```java
import java.util.concurrent.locks.StampedLock;

public class ConvertUpgrade {
    public static void main(String[] args) {
        StampedLock lock = new StampedLock();
        int[] cell = {0};

        // Case A: sole reader converts without release/reacquire window
        long rs = lock.readLock();
        boolean observedZero = cell[0] == 0;
        long ws = lock.tryConvertToWriteLock(rs);
        System.out.println("sole-reader conversion succeeded: " + (ws != 0L));
        if (ws != 0L) {
            cell[0] = 42;
            lock.unlockWrite(ws);
        } else {
            lock.unlockRead(rs);
        }
        System.out.println("value written: " + (cell[0] == 42));

        // Case B: conversion while ANOTHER reader holds -> 0, fallback path
        long r1 = lock.readLock();
        final long[] r2holder = {0};
        Thread other = new Thread(() -> {
            long r2 = lock.readLock();
            r2holder[0] = r2;
            try { Thread.sleep(500); } catch (InterruptedException ignored) { }
            lock.unlockRead(r2);
        });
        other.start();
        try { Thread.sleep(100); } catch (InterruptedException ignored) { }
        long ws2 = lock.tryConvertToWriteLock(r1);
        System.out.println("contended conversion refused (0): " + (ws2 == 0L));
        // mandatory fallback: release read, take write explicitly
        lock.unlockRead(r1);
        long wfull = lock.writeLock();
        cell[0] = 7;
        lock.unlockWrite(wfull);
        try { other.join(2000); } catch (InterruptedException ignored) { }
        System.out.println("fallback write landed: " + (cell[0] == 7));
    }
}
```

Expected output:
```
sole-reader conversion succeeded: true
value written: true
contended conversion refused (0): true
fallback write landed: true
```

Case A exercises the source's `m == RUNIT && a != 0` CAS branch (single
reader → write, atomically). Case B exercises refusal + the mandatory
fallback. Under `ReentrantReadWriteLock`, Case A self-deadlocks — the
upgrade gap is StampedLock's signature feature.

## 4. NOT Reentrant: Self-Deadlock on Re-acquire

```java
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.StampedLock;

public class NotReentrant {
    public static void main(String[] args) throws Exception {
        StampedLock lock = new StampedLock();
        // NOTE: timed attempts everywhere — a raw writeLock() re-entry would hang
        // forever, which hangs the harness rather than demonstrating the point.
        long held = lock.writeLock();
        Thread other = new Thread(() -> {
            try {
                long s = lock.tryWriteLock(300, TimeUnit.MILLISECONDS);
                System.out.println("second writer admitted while held (unexpected): " + (s != 0L));
                if (s != 0L) lock.unlockWrite(s);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        other.start();
        other.join(2000);
        System.out.println("holder still owns write lock: " + lock.isWriteLocked());
        lock.unlockWrite(held);

        // same-thread re-entry: also refused (no owner tracking to recognize it)
        long s2 = lock.writeLock();
        long reentry = lock.tryWriteLock(200, TimeUnit.MILLISECONDS);
        System.out.println("same-thread write re-entry refused/timed-out: " + (reentry == 0L));
        if (reentry != 0L) lock.unlockWrite(reentry);
        lock.unlockWrite(s2);
        System.out.println("released cleanly: " + !lock.isWriteLocked());
    }
}
```

Expected output:
```
second writer admitted while held (unexpected): false
holder still owns write lock: true
same-thread write re-entry refused/timed-out: true
released cleanly: true
```

No owner tracking means no re-entry recognition: the second acquire queues
behind the first *even in the same thread*. (A raw `writeLock()` re-entry
would deadlock permanently — the snippet uses timed attempts so the
demonstration terminates.) Contrast `ReentrantLock`, which counts entries.

## 5. asReadLock Views: Lock Interface + Conditions

```java
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.StampedLock;

public class LockViews {
    public static void main(String[] args) throws Exception {
        StampedLock sl = new StampedLock();
        Lock readView = sl.asReadLock();
        Lock writeView = sl.asWriteLock();

        readView.lock();
        System.out.println("read view held, isReadLocked: " + sl.isReadLocked());
        readView.unlock();
        System.out.println("released: " + !sl.isReadLocked());

        writeView.lock();
        System.out.println("write view held, isWriteLocked: " + sl.isWriteLocked());
        writeView.unlock();
        System.out.println("released: " + !sl.isWriteLocked());

        // NO conditions anywhere: both views refuse newCondition()
        boolean readRefuses = false, writeRefuses = false;
        try { readView.newCondition(); } catch (UnsupportedOperationException e) { readRefuses = true; }
        try { writeView.newCondition(); } catch (UnsupportedOperationException e) { writeRefuses = true; }
        System.out.println("read view newCondition refused: " + readRefuses);
        System.out.println("write view newCondition refused: " + writeRefuses);
    }
}
```

Expected output:
```
read view held, isReadLocked: true
released: true
write view held, isWriteLocked: true
released: true
read view newCondition refused: true
write view newCondition refused: true
```

The views trade raw-stamp speed for `Lock` interop (`try/finally` idioms,
APIs taking `Lock`) — but not conditions: StampedLock has no wait-sets at
all. Code needing `await`/`signal` stays with `ReentrantLock`/`synchronized`.

## Common Pitfalls Encountered Here

- **Acting on unvalidated reads** — torn snapshots driving I/O/branches
  (snippet 1's validate-before-hypot shape).
- **Re-entering** — self-deadlock, no owner tracking (snippet 4).
- **Ignoring conversion's 0** — the fallback path is mandatory (snippet 3).
- **Calling unknown methods under the lock** — they may re-acquire (javadoc
  prohibition, snippet 4's reason).
- **Optimism over long sections or hot writers** — fallback storms cost more
  than plain read locks (snippet 2's phase 2).
- **Treating stamps as capabilities** — finite, guessable, recyclable after
  ~1 year; never security tokens, never held unvalidated indefinitely.
