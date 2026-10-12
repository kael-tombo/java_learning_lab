# StampedLock — Internals

Source: `java.base/share/classes/java/util/concurrent/locks/StampedLock.java`
(JDK 23). Read it alongside this file; every claim below names its anchor.

## tryOptimisticRead (one volatile read)

```java
((s = state) & WBIT) == 0 ? (s & SBITS) : 0
```

If the write bit is set, return 0 — never a version. Otherwise return the
version bits. No CAS, no fence on issue; the fence lives in `validate`.

## validate (fence + compare)

`validate` calls `Unsafe.loadFence()` then compares `(stamp & SBITS)` with
`(state & SBITS)`. The fence orders the caller's field reads before the
version re-read, closing the reordering hole where a stale version check
could pass over torn data. `validate(0L)` is always false because stamp 0
carries no version that a real state word can match.

## Version advance on writes

Write release advances the sequence portion of `state`, so each completed
write cycle invalidates all stamps issued before it. Two rapid writes bump
twice; validation fails on either. Stamps recycle only after the sequence
wraps — documented as no sooner than ~1 year of continuous operation.

## tryConvertToWriteLock branches

- Write stamp presented while writing → return the stamp unchanged.
- Read stamp with exactly one reader unit present → CAS reader→write.
- Optimistic stamp with the lock otherwise free → CAS to write.
- Anything else (multiple readers, writer present, intervening write) →
  return 0. The 0 is a refusal, not an error; the caller releases and takes
  `writeLock()` explicitly.

## Non-reentrancy mechanism

There is deliberately no `exclusiveOwnerThread` field (contrast
`ReentrantLock`). A second `writeLock()` from the holding thread enqueues
behind the first hold exactly like a foreign thread would — the queue has
no way to know they are the same thread, so it waits forever.

## Condition refusal

Both view classes override `newCondition()` to throw
`UnsupportedOperationException` unconditionally. There is no wait-set, no
`await`/`signal` path, and no workaround short of a different lock.

## asReadLock / asWriteLock adapters

The views translate `Lock.lock()` into `readLock()`/`writeLock()` and stash
the resulting stamp in thread-local-ish view state for `unlock()`. That
stash is the "owner-ish bookkeeping" THEORY warns about: convenient for
interop, slower than raw stamps, and still condition-free.

## Interruptible and timed acquires

`readLockInterruptibly`, `writeLockInterruptibly`, `tryReadLock(timeout)`,
and `tryWriteLock(timeout)` share the pessimistic queue path; only the
optimistic attempt is non-blocking and non-interruptible by construction.
