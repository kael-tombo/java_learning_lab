# How the Lock Framework Works

## The two fields

```java
private volatile int state;
private transient volatile Node head;
private transient volatile Node tail;
```

`state` is the only shared mutable data. `head`/`tail` anchor a doubly-linked
queue of `Node`s, one per blocked thread. The head is always a dummy marker.

## Exclusive acquire, step by step

1. Fast path: `tryAcquire(arg)` — for `ReentrantLock`, CAS `state` 0→1 and
   record the owner. Success means no queue touched.
2. Slow path: create a `Node` for the current thread, CAS-append to `tail`.
3. Loop: if the predecessor is `head`, retry `tryAcquire` (the predecessor
   may have just released). On success, set self as `head`, unlink the old
   head, unpark the successor.
4. Otherwise park via `LockSupport.park` until unparked, interrupted, or timed
   out. On wakeup, go to step 3.

## Release, step by step

1. `tryRelease(arg)` — for `ReentrantLock`, decrement `state`; only the owner
   may do this; when `state` hits 0, clear the owner.
2. If the head's status says a successor waits (`WAITING` bit, JDK 23), unpark
   it. The successor then does its step-3 retry.
3. Ownership is NOT handed over: between `unlock` and the successor's retry, a
   barging newcomer can CAS `state` 0→1 first. That race is the documented
   nonfair behavior.

## Fair vs nonfair, precisely

- Nonfair `lock()`: unguarded `compareAndSetState(0, 1)` before consulting the
  queue — barges even when threads wait.
- Fair `lock()`: if `state == 0`, acquire only when `!hasQueuedThreads()` and
  the CAS succeeds; reentrant re-entry (`state + 1`) bypasses the queue check.
- `tryLock()` (no-arg): barges in both modes — unordered by specification.

## Condition handoff

`await()`: save reentrancy depth, release `state` fully, move the node to the
condition queue, park. `signal()`: move the longest-waiting condition node to
the sync queue. The moved node still must re-acquire — it races like any new
waiter, so the `while (conditionNotTrue) await()` loop is mandatory.

## Shared acquire sketch

`acquireShared`: loop `tryAcquireShared` (non-negative return = granted);
`Semaphore(5)` decrements permits, `CountDownLatch` blocks until count is 0,
read locks increment the high 16 bits of the packed `state`.
