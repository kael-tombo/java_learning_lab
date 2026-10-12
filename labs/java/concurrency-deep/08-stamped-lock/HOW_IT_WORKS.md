# StampedLock — How It Works

## Three modes, one state word

The lock keeps a single `long state`. Writers hold an exclusive bit; readers
count in units; the remaining bits form a version sequence bumped by every
write hold/release cycle. From the JDK 23 source:

```java
tryOptimisticRead():  ((s = state) & WBIT) == 0 ? (s & SBITS) : 0
validate(stamp):      loadFence; (stamp & SBITS) == (state & SBITS)
```

## Mode 1: write lock

`writeLock()` sets the write bit exclusively. `unlockWrite(stamp)` clears it
and advances the version, which invalidates every outstanding optimistic
stamp at once. `isWriteLocked()` reports the bit. Only one writer, no
readers, no optimistic validity across it.

## Mode 2: pessimistic read lock

`readLock()` adds one reader unit (CAS, queued, interruptible and timed
variants exist). Concurrent readers coexist; a writer waits for all of them.
`unlockRead(stamp)` releases exactly one unit. Use it for long sections, hot
writers, or as the fallback after failed validation.

## Mode 3: optimistic read (not a lock)

`tryOptimisticRead()` is a sample, not an acquisition: if no writer holds,
it returns the current version bits; if a writer holds, it returns 0 (never
valid). Nothing is held, nothing is queued, nothing prevents a writer from
proceeding. The caller copies fields into locals, then calls `validate()`:

- `validate` issues a load fence so the field reads cannot drift past the
  version re-check, then compares stamp version bits against current state.
- Equal means no write completed between sample and fence: the snapshot was
  consistent, and the locals are safe to use.
- Unequal (or stamp 0) means retry under `readLock()`.

## Conversion

`tryConvertToWriteLock(stamp)` inspects the stamp and state together:

- write stamp held → return it (no-op success);
- sole-reader stamp → CAS reader unit to write bit (atomic upgrade);
- optimistic stamp with a free lock → CAS to write;
- anything contended → return 0; caller must `unlockRead` and `writeLock`.

## Unlock discipline

`unlockRead`/`unlockWrite` are typed and fast; `unlock(stamp)` dispatches on
stamp bits and accepts any stamp, slightly slower. Every acquired stamp
needs exactly one matching unlock. Stamps never nest.

## Lock views

`asReadLock()`/`asWriteLock()` wrap stamps in the `Lock` interface for APIs
that demand it. Both views' `newCondition()` throws
`UnsupportedOperationException` — there are no wait-sets inside.
