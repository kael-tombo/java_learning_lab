# StampedLock — Refactoring

## Migrating from ReentrantReadWriteLock

Candidate code: read-mostly, short reads, rare writes, no conditions, no
re-acquire under hold. Migration steps:

1. Replace the field type and both acquire sites; thread the `long` stamp
   through `unlockRead`/`unlockWrite` in `try/finally`.
2. Convert hot short reads to tryOptimisticRead + validate + fallback.
3. Replace release-reacquire upgrade dances with `tryConvertToWriteLock`
   plus the mandatory 0-fallback (release, `writeLock`, re-check).
4. Delete `newCondition()` usages or abort the migration — StampedLock has
   no replacement for them.
5. Run the PERFORMANCE.md crossover harness; keep pessimistic reads where
   writers are hot.

## Before / after: point read

```java
// Before: every reader CASes
rwLock.readLock().lock();
try { return Math.hypot(x, y); } finally { rwLock.readLock().unlock(); }

// After: readers sample for free, writers unchanged
long s = sl.tryOptimisticRead();
double cx = x, cy = y;
if (!sl.validate(s)) {
    s = sl.readLock();
    try { cx = x; cy = y; } finally { sl.unlockRead(s); }
}
return Math.hypot(cx, cy);
```

## Before / after: upgrade

```java
// Before: release window (another writer may slip in)
readUnlock(); writeLock(); recheck(); mutate();

// After: atomic sole-reader conversion with explicit fallback
long ws = sl.tryConvertToWriteLock(s);
if (ws == 0L) { sl.unlockRead(s); s = sl.writeLock(); recheck(); }
else s = ws;
try { mutate(); } finally { sl.unlock(s); }
```

## Adopting Lock views at API boundaries

Where an API demands `java.util.concurrent.locks.Lock`, pass
`asReadLock()`/`asWriteLock()` instead of raw stamps — but keep raw stamps
on inner hot paths, since the views add stash overhead per call.

## When to refactor away from StampedLock

- Conditions appear → `ReentrantLock` + `Condition`.
- Reentrant call shapes appear → `ReentrantLock` / RRWL.
- Writers dominate → plain read locks or lock striping.
- State fits immutability or copy-on-write → drop locking reads entirely.

## Review checklist for the diff

Stamps paired 1:1 with unlocks, conversion 0 handled, no method under hold
re-acquires, no `newCondition`, optimistic bodies side-effect-free,
crossover measured not assumed.
