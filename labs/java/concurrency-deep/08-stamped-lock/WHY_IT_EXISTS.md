# StampedLock — Why It Exists

## The gap in ReentrantReadWriteLock

`ReentrantReadWriteLock` (lab 05) solved reader/writer sharing but kept two
costs on every read acquisition: an atomic CAS on the shared state word and
queue bookkeeping for fairness and reentrancy. For read-mostly structures —
caches, coordinate points, configuration snapshots — readers vastly
outnumber writers, yet every reader still pays the CAS and contends on the
same cache line. Throughput plateaus on reader count, not on useful work.

Worse, read-to-write upgrade deadlocks. A thread holding a read lock that
tries to acquire the write lock waits for itself (plus every other reader),
and no lock manager can break the cycle without releasing first — which
opens a window where another writer slips in. Upgrade requires an awkward
release-reacquire dance that is easy to get wrong.

## What StampedLock changed

`StampedLock` (Java 8, JSR-166) removed owner tracking entirely and returned
a `long` stamp instead. That single decision bought two things:

1. **Optimistic reading.** `tryOptimisticRead()` samples a version number
   with one volatile read. No CAS, no queue, no shared-state mutation, so
   readers never contend with each other. A later `validate()` re-checks the
   version; on mismatch the reader retries under a pessimistic read lock.
   The common case (no concurrent writer) costs almost nothing.
2. **Atomic upgrade.** `tryConvertToWriteLock(stamp)` converts a sole-reader
   hold into write hold with one CAS — no release window. Contended
   conversions return 0 and the caller falls back explicitly.

## What was deliberately sacrificed

- **Reentrancy.** Without owner state the lock cannot recognize re-entry, so
  re-acquiring a held lock self-deadlocks. Code that calls unknown methods
  under the lock is disqualified by design.
- **Conditions.** No wait-sets exist, so both Lock views refuse
  `newCondition()` with `UnsupportedOperationException`.
- **Familiarity.** Stamps must be threaded through `unlockRead`/`unlockWrite`
  exactly once; the API is lower-level than `Lock.lock()/unlock()`.

## The design bet

Most shared state in servers is read far more often than written, and most
reads are short field copies. StampedLock bets that sampling-and-validating
beats mutual-excluding for exactly that shape — and the lab's measurements
(CODE_DEEP_DIVE snippet 2) confirm the direction: zero fallbacks with no
writers, graceful degradation as writer pressure rises.
