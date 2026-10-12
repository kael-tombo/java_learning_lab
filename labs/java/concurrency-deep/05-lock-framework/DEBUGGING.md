# Debugging: Lock Framework

## Thread-dump reading

- Threads in `jdk.internal.misc.Unsafe.park` + `AbstractQueuedSynchronizer.parkAndCheckInterrupt`
  are queued waiters — normal under contention, suspicious when permanent.
- `locked <0x...>` lines with `ReentrantLock$NonfairSync` identify the owner;
  no owner + non-zero queue = wedged `state` (missed `unlock`).
- One thread in `await()` (`ConditionObject.await`) + rest in `acquireQueued`
  = signal never sent or sent on the wrong condition.

## Key introspection calls

```java
ReentrantLock lock = new ReentrantLock();
lock.hasQueuedThreads();      // anyone waiting?
lock.getQueueLength();        // how many (estimate)
lock.getFirstQueuedThread();  // head-adjacent waiter
lock.isHeldByCurrentThread();
lock.getHoldCount();          // reentrancy depth
sem.availablePermits();       // permit accounting drift?
```

Growing `getQueueLength()` with a live owner = oversized critical section.
Growing queue with NO owner = missed `unlock` or exception path.

## Reproducing starvation

Nonfair starvation needs sustained contention: N threads looping
`lock(); tinyWork(); unlock()` while one victim records acquire latency. Plot
p50 vs p99 victim wait — fair mode collapses p99 toward the mean at a small
throughput cost. `tryLock()`-based probes invalidate the test (unordered).

## Permit-drift check

```java
int before = sem.availablePermits();
runWorkload();
int after = sem.availablePermits();
// after != before -> over-release or leaked acquire
```

`Semaphore` never self-corrects; log `availablePermits()` at quiescence after
every load test.

## RWLock deadlock fingerprint

Writer in `park` (`writeLock().lock()`) + readers idle but holding read locks
= attempted upgrade. Dump hold counts: a thread with `getReadHoldCount() > 0`
blocked in `writeLock()` is the self-deadlock — restructure to release-read-
then-write with a re-check.

## Condition bugs

- Missed signal: `signal()` ran before `await()` with no predicate flag — add
  the boolean predicate + `while` loop.
- Wrong condition: `notFull.signal()` when the waiter sits on `notEmpty` —
  name conditions after the predicate they guard and signal the matching one.
- `awaitNanos` returns remaining nanos, not a boolean — a `<= 0` check is the
  timeout test; ignoring the return treats timeout as success.

## Tooling

`jstack <pid>` for queue snapshots; JFR `Java Monitor Blocked` events for
wait-time histograms; async-profiler wall-clock mode to attribute parked time
to the holding stack, not the waiter.
