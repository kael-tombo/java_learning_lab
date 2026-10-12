# StampedLock — Debugging

## Symptom: threads stuck, no progress (suspected self-deadlock)

A write-locked thread that re-acquires (directly or via a callee) parks
behind itself forever. In a thread dump look for a thread in
`StampedLock.writeLock/readLock` whose stack shows it already holds the
same lock higher up the stack (e.g., outer method took `writeLock`, inner
method takes it again). No `Blocked` on a monitor appears — it is parked
on the StampedLock queue. Fix by passing the stamp down instead of
re-acquiring; verify with a timed `tryWriteLock` probe that returns 0.

## Symptom: validation fails constantly

Instrument: count `validate` false-returns per thousand reads. Sustained
high rates mean the writer fraction times window length is too large
(MATH_FOUNDATION's `wT` model). Confirm with writer throughput logging,
then either shrink the optimistic body to bare field copies or switch the
path to plain `readLock()`. Sporadic bursts point at a periodic writer
(checkpoint thread, config reloader) — correlate timestamps.

## Symptom: torn or impossible values despite locking

The optimistic body acted before validation, or a field was read twice
(once for a check, once for use) with a write between. Audit that every
guarded field is copied exactly once into a local, validated, and only the
local is used thereafter. Watch for method calls on unvalidated data that
read the fields a second time internally.

## Symptom: UnsupportedOperationException from newCondition

Not a bug in your code's logic — it is the design. Both Lock views refuse
conditions. Migrate the wait/notify shape to `ReentrantLock` plus its
`Condition`, or restructure to polling/queue-based handoff.

## Symptom: reader-count drift / IllegalMonitorStateException-ish failures

A stamp unlocked twice, unlocked with the wrong typed method, or never
unlocked. Map each acquire to its release in review: `readLock` pairs
`unlockRead`, `writeLock` pairs `unlockWrite`, converted stamps pair
`unlock`. Add assertions (`isReadLocked`/`isWriteLocked`) at scope exits
in tests.

## Symptom: conversion always returns 0

Either genuine reader fan-out (many concurrent readers — expected) or a
leaked read hold somewhere keeping the count above one. Dump
reader-holding threads and check for missing `unlockRead` on exception
paths (missing `finally`).

## Tooling notes

- `jstack` / `jcmd Thread.print`: StampedLock park sites appear as
  `LockSupport.park` under `StampedLock.acquireWrite/acquireRead`.
- For validation-rate studies, wrap `validate` in a counting helper rather
  than sampling — the event is too cheap to observe externally.
- Reproduce self-deadlock only with timed attempts (`tryWriteLock`) in
  tests; the blocking form hangs the harness instead of failing it.
