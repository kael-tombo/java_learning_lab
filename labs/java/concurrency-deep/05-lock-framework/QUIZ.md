# Quiz: Lock Framework

## Questions (answers at end)

1. AQS splits synchronizers into policy and mechanism. Which methods belong to
   the subclass, and which to the framework?
2. Thread A holds a nonfair `ReentrantLock`. Threads B, C wait in the queue.
   Thread D calls `lock()`. Can D acquire before B? Why?
3. Same setup with a *fair* lock, but D calls `tryLock()`. Can D acquire
   before B? Why?
4. What is the queue head, and when does a thread become head?
5. JDK 23 defines `WAITING = 1, COND = 2, CANCELLED = 0x80000000`. A blog says
   "set SIGNAL on the predecessor." What is wrong with that advice?
6. `await()` is called with reentrancy depth 3. What happens to `state`, and
   what is restored on re-acquire?
7. `signal()` wakes a condition waiter. Who owns the lock at the moment of
   waking? What must the woken thread still do?
8. `Semaphore(5)` shows `availablePermits() == 8`. What happened?
9. `state = 0x00020001` in a `ReentrantReadWriteLock`. How many readers and
   writer holds?
10. Why does read→write upgrade deadlock while write→read downgrade is safe?
11. A waiter times out in `tryLock(300ms)`. What happens to its queue node?
12. Fair mode still permits one barging window. Where exactly?

## Answers

1. Subclass: `tryAcquire`/`tryRelease`/`tryAcquireShared`/`tryReleaseShared`/
   `isHeldExclusively`. Framework: `acquire`, `release`, queueing, parking,
   `ConditionObject` mechanics.
2. Yes — nonfair `lock()` CAS-barges before consulting the queue.
3. Yes — `tryLock()` is unordered in both modes; fairness never applies to it.
4. Head is a dummy position marker; a thread sets itself as head exactly when
   its `tryAcquire` succeeds.
5. `SIGNAL` belongs to the pre-rewrite encoding. JDK 23 uses bitwise
   `WAITING`/`COND`/`CANCELLED`; the protocol is the same, the constants are not.
6. `state` drops fully (3→0); on re-acquire the depth 3 is restored before return.
7. Nobody transfers ownership — the signaller still holds it (or just
   released it). The woken thread must re-acquire through the sync queue race.
8. Three stray `release()` calls without matching acquires; permits are uncapped.
9. Readers = `0x0002` = 2, writer holds = `0x0001` = 1.
10. Upgrade: the write request queues behind the requester's own read hold,
    which never releases while blocked — self-deadlock. Downgrade: the writer
    already excludes everyone, so adding a read hold changes nothing.
11. Marked `CANCELLED` and unlinked; successors re-link to a live predecessor.
12. Between `unlock` and the successor's wakeup-retry: a newcomer can win the
    CAS in that gap. Fair forbids *overt* barging, not the race itself.
