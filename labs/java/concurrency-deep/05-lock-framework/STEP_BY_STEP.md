# Step by Step: Build a Mutex on AQS

## Goal

A working exclusive mutex from `AbstractQueuedSynchronizer`, then a condition
demo.

## Step 1 — Skeleton (5 min)

```java
import java.util.concurrent.locks.AbstractQueuedSynchronizer;

class Mutex extends AbstractQueuedSynchronizer {
    void lock() { acquire(1); }
    void unlock() { release(1); }
    boolean tryLock() { return tryAcquire(1); }
}
```

`acquire`/`release` are the framework's; you supply the `try*` policy.

## Step 2 — `tryAcquire` (10 min)

```java
@Override protected boolean tryAcquire(int a) {
    if (compareAndSetState(0, 1)) {
        setExclusiveOwnerThread(Thread.currentThread());
        return true;
    }
    return false;
}
```

State 0→1 by CAS wins; anything else queues. This is the nonfair shape (barge
first, queue second).

## Step 3 — `tryRelease` + guard (5 min)

```java
@Override protected boolean tryRelease(int a) {
    if (getState() == 0 || getExclusiveOwnerThread() != Thread.currentThread())
        throw new IllegalMonitorStateException();
    setExclusiveOwnerThread(null);
    setState(0);
    return true;
}
```

Returning `true` tells AQS to unpark a successor.

## Step 4 — Smoke test (5 min)

```java
Mutex m = new Mutex();
m.lock();
try { System.out.println("held: " + m.isHeldExclusively()); }
finally { m.unlock(); }
```

Add `isHeldExclusively()` returning owner-equality. Then run 8 × 50K
increments; expect exactly 400K.

## Step 5 — Reentrancy check (5 min)

Owner re-entry does `setState(getState() + 1)` with the 2³¹−1 overflow check;
release decrements, clearing the owner at 0. Compare with `FairSync` in THEORY.md.

## Step 6 — Condition (10 min)

```java
Condition c = lock.newCondition();
lock.lock();
try { while (!ready) c.await(); consume(); }
finally { lock.unlock(); }
// producer: lock.lock(); try { ready = true; c.signal(); } finally { lock.unlock(); }
```

## Done when

Counter exact, `tryLock` barges, condition demo needs its `while` loop.
