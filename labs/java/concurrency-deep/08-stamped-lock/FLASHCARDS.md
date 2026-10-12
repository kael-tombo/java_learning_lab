# StampedLock — Flashcards

## Card 1

**Q:** Name the three StampedLock modes and the cheapest one.
**A:** Write lock, pessimistic read lock, optimistic read. Optimistic
sampling (one volatile read, no CAS) is cheapest.

## Card 2

**Q:** `tryOptimisticRead()` returned 0. Meaning and next step?
**A:** A writer held the lock at sample time. Copy anyway, then
`validate(0)` fails and you fall back to `readLock()`.

## Card 3

**Q:** State the validate-before-act rule in one sentence.
**A:** Copy guarded fields to locals, call `validate`, and use the locals
only if validation succeeded — otherwise discard and re-read under
`readLock()`.

## Card 4

**Q:** Why does `validate` need a load fence?
**A:** To order field copies before the version re-check; without it the
CPU could reorder reads so a mid-copy write goes undetected.

## Card 5

**Q:** `tryConvertToWriteLock` returns `ws != 0`. What is `ws`?
**A:** A write stamp replacing your old stamp — assign `stamp = ws` and
release with `unlock`/`unlockWrite`, not the old typed unlock.

## Card 6

**Q:** Conversion returned 0. Give the exact fallback sequence.
**A:** `unlockRead(stamp); stamp = writeLock();` re-check condition,
mutate, `unlock(stamp)` in `finally`.

## Card 7

**Q:** Is `writeLock()` reentrant from the holding thread?
**A:** No — it queues behind itself and deadlocks. No owner field exists
to recognize re-entry.

## Card 8

**Q:** What do both `asReadLock()`/`asWriteLock()` views do for
`newCondition()`?
**A:** Throw `UnsupportedOperationException` — StampedLock has no
wait-sets or conditions at all.

## Card 9

**Q:** Pair each acquire with its release.
**A:** `readLock`→`unlockRead`; `writeLock`→`unlockWrite`;
converted-or-either→generic `unlock(stamp)`. Exactly one unlock per stamp.

## Card 10

**Q:** When must you prefer plain `readLock()` over optimism?
**A:** Hot writers or long read sections — when most validations fail and
attempt-plus-fallback costs exceed a direct read lock.

## Card 11

**Q:** Why are stamps guessable and recyclable?
**A:** They are version-counter values in a finite field, wrapping after
~1 year of continuous operation — documented as not cryptographically
secure, never capabilities.

## Card 12

**Q:** What is the sanctioned alternative to locking inside a callee?
**A:** Pass the caller's stamp into the callee, which uses or converts it
— never re-acquire a held StampedLock.
