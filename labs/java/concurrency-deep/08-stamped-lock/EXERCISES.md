# StampedLock — Exercises

All snippets compile on JDK 9+ with no dependencies. Each has an assertion
of expected behavior — make it print `true` before moving on.

## 1. Optimistic point read

Implement `distanceFromOrigin()` on an (x, y) point guarded by StampedLock
using tryOptimisticRead + validate + readLock fallback (CODE_DEEP_DIVE
snippet 1). Assert `distance == 5.0` after `move(3, 4)`, and assert
`!lock.validate(0L)`. Then deliberately move `Math.hypot` before the
validate call and explain why a concurrent writer could corrupt it.

## 2. Fallback counter

Build the `OptimismPayoff.Counter` harness: 6 readers x 300k reads, zero
writers, counting validation failures. Assert zero fallbacks. Add one
writer doing 200k increments concurrently and assert fallbacks become
nonzero while the final counter is exactly 200000. Record both counts.

## 3. Sole-reader upgrade

Take `readLock()`, inspect a cell, call `tryConvertToWriteLock`, and on
nonzero write 42 and `unlockWrite`. Assert success and value. Then hold
two concurrent read locks and attempt conversion from one: assert 0,
release, take `writeLock()` explicitly, write 7. Explain which source
branch each case exercised.

## 4. Non-reentrancy probe

Hold `writeLock()`; from the same thread call
`tryWriteLock(200, MILLISECONDS)` and assert 0 (use timed attempts only —
blocking `writeLock()` would hang). Release and assert `!isWriteLocked()`.
Repeat with a second thread attempting while held; assert it is also
refused. Write one paragraph on why no owner field implies this outcome.

## 5. View interop + condition refusal

Obtain `asReadLock()` and `asWriteLock()`; lock/unlock each while asserting
`isReadLocked()`/`isWriteLocked()`. Assert both views' `newCondition()`
throws `UnsupportedOperationException`. Then write the migration note: what
lock replaces StampedLock when `await`/`signal` is required?

## 6. Workload crossover measurement

Extend exercise 2: sweep writer shares (0%, 1%, 10%) with JMH or a timed
harness comparing optimistic-get vs pessimistic-get throughput. Find the
crossover where plain `readLock()` wins on your machine. Report reader
count, writer share, and both throughputs — the number is yours, not a
textbook constant.

## 7. Stamp-passing refactor

Take any helper that currently re-acquires the lock internally and refactor
it to accept the caller's stamp (converting if it needs write). Verify
with a single-threaded test plus the timed re-entry probe from exercise 4.
