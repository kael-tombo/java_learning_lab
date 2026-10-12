# Flashcards: Lock Framework

## Q/A pairs

**Q:** What are the two fields at the heart of AQS?
**A:** A volatile `int state` (subclass-defined meaning) plus `head`/`tail`
of a CLH-variant waiter queue.

**Q:** Who defines what `state` means?
**A:** The subclass via `tryAcquire`/`tryRelease` (`tryAcquireShared`/
`tryReleaseShared`); AQS owns queuing, parking, wakeup.

**Q:** What does the queue head always represent?
**A:** A dummy marker — its thread already acquired. A thread becomes head
exactly when it acquires.

**Q:** How does nonfair `ReentrantLock.lock()` acquire?
**A:** Unguarded `compareAndSetState(0, 1)` first — barges even with waiters.

**Q:** How does fair `lock()` differ?
**A:** When `state == 0`, only acquires if `!hasQueuedThreads()` plus a
successful CAS. Reentrant re-entry bypasses the queue check.

**Q:** Does `tryLock()` respect fairness?
**A:** No — unordered in both modes, barges regardless.

**Q:** JDK 23 AQS status constants?
**A:** `WAITING = 1`, `COND = 2`, `CANCELLED = 0x80000000`, mutated with
bitwise Unsafe ops. Old `SIGNAL`/`PROPAGATE` scheme is gone.

**Q:** What does `Condition.await()` do to `state`?
**A:** Releases it fully (saving reentrancy depth), parks on the condition
queue; restores depth on re-acquire.

**Q:** What does `signal()` transfer?
**A:** Queue membership only (condition queue → sync queue tail). Never lock
ownership — re-acquisition still races.

**Q:** `Semaphore(5)` permit ceiling?
**A:** None — over-release grows `state` past 5 silently.

**Q:** `ReentrantReadWriteLock` state layout?
**A:** High 16 bits readers, low 16 bits writer holds, `MAX_COUNT = 65535`
each; overflow throws.

**Q:** Downgrade vs upgrade?
**A:** Write→read downgrade is safe; read→write upgrade deadlocks (write
waits behind your own read hold).

**Q:** What unlinks on interrupt/timeout?
**A:** The waiter's node is marked `CANCELLED` and skipped by successors;
the queue self-heals.

**Q:** Reentrancy overflow guard?
**A:** Past 2³¹−1 holds: `Maximum lock count exceeded`.
