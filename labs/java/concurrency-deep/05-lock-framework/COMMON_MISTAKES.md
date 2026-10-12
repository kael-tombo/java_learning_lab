# Common Mistakes: Lock Framework

## 1. Unlock outside `finally`

```java
lock.lock();
doWork();          // throws -> lock stays at state != 0
lock.unlock();
```

Fix: `lock.lock(); try { doWork(); } finally { lock.unlock(); }`. A wedged
`state` parks every future acquirer forever — thread dumps show all threads
in `park` with one missing `unlock`.

## 2. Assuming `signal` transfers ownership

```java
// consumer: WRONG without loop
if (!ready) cond.await();
consume();  // another thread may have consumed first
```

`signal` only re-queues; the woken thread still races bargers. Always
`while (!ready) cond.await();`.

## 3. Read-to-write upgrade

```java
lock.readLock().lock();
try {
    lock.writeLock().lock();  // SELF-DEADLOCK: write waits for your read
} finally { lock.readLock().unlock(); }
```

Fix: release read before requesting write (re-check state after), or hold
write from the start. Downgrade (write→read) is the only safe direction.

## 4. Semaphore over-release

```java
sem.acquire();
try { work(); } finally { sem.release(); sem.release(); } // permits grow
```

Permits are uncapped — 3 stray releases on `Semaphore(5)` silently make 8.
Pair every release 1:1 with an acquire; audit with `availablePermits()`.

## 5. Using `tryLock()` as a fairness probe

`tryLock()` barges even in fair mode (unordered by spec). Fairness applies to
`lock()` / `lockInterruptibly()` only. Testing fairness with `tryLock` proves
nothing.

## 6. `await()` without owning the lock

`cond.await()` without holding the lock throws `IllegalMonitorStateException`
— same rule as `Object.wait()`. Condition and lock are bound at creation
(`lock.newCondition()`); awaiting on a different lock's condition is a bug.

## 7. Ignoring `InterruptedException` from `lockInterruptibly`

```java
try { lock.lockInterruptibly(); } catch (InterruptedException e) { /* swallow */ }
```

The node already unlinked; swallowing hides shutdown. Restore the interrupt
(`Thread.currentThread().interrupt()`) or propagate.

## 8. Counting on the old waitStatus constants

Code or comments referencing `SIGNAL = -1 / PROPAGATE = -3` describe the
pre-rewrite AQS. JDK 23 uses `WAITING = 1, COND = 2, CANCELLED = 0x80000000`
with bitwise ops. The protocol is stable; the encoding is not API — never
branch on these internals.
