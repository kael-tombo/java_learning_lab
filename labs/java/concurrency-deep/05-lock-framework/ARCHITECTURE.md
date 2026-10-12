# Architecture: AQS-Based Synchronizers

## Layer diagram

```
+-------------------+  +----------------+  +-------------------+
| ReentrantLock     |  | Semaphore      |  | CountDownLatch    |
| (exclusive,       |  | (shared,       |  | (shared, one-shot)|
|  reentrant)       |  |  N permits)    |  |                   |
+--------+----------+  +-------+--------+  +--------+----------+
| ReentrantReadWriteLock (exclusive write + shared read)      |
+-------------------------+-----------------------------------+
| AbstractQueuedSynchronizer: state + CLH-variant queue + park|
+-------------------------+-----------------------------------+
| LockSupport.park/unpark + Unsafe CAS/bitwise ops            |
+------------------------------------------------------------+
```

## Policy vs mechanism split

- Policy (subclass): `tryAcquire`, `tryRelease`, `tryAcquireShared`,
  `tryReleaseShared`, `isHeldExclusively`. Defines what `state` means.
- Mechanism (AQS): `acquire`, `acquireInterruptibly`, `tryAcquireNanos`,
  `acquireShared`, `release`, `releaseShared`, queue management, `ConditionObject`.

## Where each class lives (OpenJDK paths)

- `java.base/java/util/concurrent/locks/AbstractQueuedSynchronizer.java`
- `.../locks/ReentrantLock.java` (`NonfairSync`, `FairSync` inner classes)
- `.../locks/ReentrantReadWriteLock.java` (`Sync` with 16/16-bit packing)
- `.../Semaphore.java` (`NonfairSync`/`FairSync` over permits)
- `java.base/java/util/concurrent/CountDownLatch.java`

## Sync-queue vs condition-queue topology

One sync queue per AQS instance; zero or more condition queues per
`ConditionObject` created from the lock. `await()` migrates sync→condition;
`signal()` migrates condition→sync-tail. The sync queue is the only path to
ownership; condition queues are pure waiting rooms.

## ReentrantReadWriteLock packing

One `int state`: high 16 bits = reader count, low 16 bits = writer hold
count, `MAX_COUNT = 65535` each. A single `state` CAS updates either half.
Overflow past 65535 throws — reader fan-out above 64K concurrent readers is a
design error, not a scaling target.

## ConditionObject fan-out (ArrayBlockingQueue pattern)

One lock, two conditions: `notEmpty` for takers, `notFull` for putters. Each
`signal()` wakes only the relevant queue — this is the architectural fix for
the single-wait-set limit of `synchronized`.

## Design constraints to respect

- `unlock` must run in `finally`; the framework cannot enforce it.
- Fairness costs a queue check plus handoff latency — default nonfair unless
  starvation evidence says otherwise.
- Shared-mode wakeups propagate (release wakes a chain while permits allow);
  exclusive wakeups unpark one successor.
