# Refactoring: Lock Framework

## synchronized → ReentrantLock (only when justified)

Before:

```java
synchronized (guard) { update(); }
```

After (only if you need timeout/interruption/fairness/conditions):

```java
private final ReentrantLock lock = new ReentrantLock();
lock.lock();
try { update(); } finally { lock.unlock(); }
```

Do not convert for style — `synchronized` keeps block structure and JIT
transparency. Convert for a named capability: `tryLock(t)`,
`lockInterruptibly()`, multiple conditions, or measured fair-mode need.

## Single wait-set → two conditions

Before (`notifyAll` wakes everyone):

```java
synchronized (this) {
    while (full()) wait();
    enqueue(x); notifyAll();
}
```

After:

```java
lock.lock();
try {
    while (count == N) notFull.await();
    buf[put++] = x; count++;
    notEmpty.signal();
} finally { lock.unlock(); }
```

Each `signal` now wakes only the relevant queue — the herd is gone.

## Ad-hoc permit counting → Semaphore

Before: an `int` + `synchronized` + manual wakeups. After: `Semaphore(n)`
with 1:1 acquire/release in try/finally. Delete the hand-rolled accounting —
and add a quiescence assertion on `availablePermits()` to catch drift.

## Upgrade-shaped code → release-and-reacquire

Before (deadlocks):

```java
readLock.lock();
try { writeLock.lock(); ... } finally { readLock.unlock(); }
```

After:

```java
readLock.lock();
boolean needsWrite;
try { needsWrite = check(); } finally { readLock.unlock(); }
if (needsWrite) {
    writeLock.lock();
    try { recheckThenMutate(); } finally { writeLock.unlock(); }
}
```

## Boolean-flag gates → CountDownLatch

One-shot start/completion gates: replace `volatile boolean + join loops` with
`CountDownLatch(n)`. No reset — if the gate must reopen, that is a
`CyclicBarrier`/`Phaser` (lab 09), not a latch.
