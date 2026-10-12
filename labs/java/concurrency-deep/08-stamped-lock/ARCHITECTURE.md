# StampedLock — Architecture

## The state word layout

One `volatile long state` carries everything. Conceptually, from the OpenJDK
source (`java.util.concurrent.locks.StampedLock`):

- `WBIT` — lowest bit region marking exclusive write hold.
- Reader count — units (`RUNIT`) above the write bit; each `readLock()`
  adds one, each `unlockRead` subtracts one.
- `SBITS` — the upper version bits, advanced on every write cycle and
  sampled by `tryOptimisticRead()`.

No thread IDs, no hold counts, no owner fields. That absence is the
architecture: reentrancy is unrepresentable, which is why re-acquire
self-deadlocks instead of re-entering.

## Component map

- **Stamp issuers**: `writeLock`, `readLock`, `tryOptimisticRead`, plus
  timed/interruptible variants (`tryWriteLock`, `readLockInterruptibly`).
  Only the optimistic issuer avoids CAS and queueing.
- **Validator**: `validate(stamp)` — load fence plus version comparison.
  Stateless, repeatable, safe to call on any stamp including 0.
- **Converter**: `tryConvertToWriteLock(stamp)` — the only path that
  changes mode without release/reacquire.
- **Releasers**: `unlockRead`, `unlockWrite`, generic `unlock(stamp)`.
- **Observers**: `isWriteLocked`, `isReadLocked`, `tryOptimisticRead`-based
  probes. `getReadLockCount`-style introspection reflects the counter.
- **Views**: `asReadLock()` / `asWriteLock()` adapt stamps to `Lock`,
  adding familiar `lock()/unlock()` shape at the cost of adapter overhead.
  Condition creation is refused on both.

## Queueing and parking

Pessimistic acquires park on an internal CLH-style waiter queue (shared with
the optimistic-fallback path). Optimistic attempts never enqueue — they
cannot block, time out, or be interrupted, because they never wait.

## Reader accounting limits

The reader count field is finite, so extreme reader fan-out is handled by
internal spillover logic rather than unbounded growth. Practical code never
approaches the cap; the point is that reader state lives in a fixed-width
counter, not a per-thread map.

## Data flow of one optimistic read

1. Volatile read of `state`; mask version bits → stamp (or 0).
2. Plain reads of guarded fields into locals (no fences yet).
3. `validate`: load fence, re-read `state`, compare version bits.
4. Valid → use locals. Invalid → discard locals, take `readLock()`, re-read.

## Why stamps instead of objects

A `long` stamp is allocation-free, copyable, and passable into callees —
the sanctioned pattern is to pass the stamp down rather than re-acquire.
The price is discipline: the compiler cannot pair acquire with release, so
`try/finally` around every stamp is a structural requirement, not style.
