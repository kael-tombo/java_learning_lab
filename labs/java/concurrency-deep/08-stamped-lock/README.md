# StampedLock — README

`java.util.concurrent.locks.StampedLock` (Java 8) is a stamp-returning lock
with three modes: write, pessimistic read, and optimistic read. It trades
away reentrancy and conditions to buy something no `ReadWriteLock` has:
nearly-free optimistic reads — one volatile read, no CAS, no queue entry.

## The core pattern

```java
long stamp = lock.tryOptimisticRead();
double x = point.x, y = point.y;      // copy to locals, no side effects
if (!lock.validate(stamp)) {          // writer intervened?
    stamp = lock.readLock();          // fall back to pessimistic read
    try { x = point.x; y = point.y; }
    finally { lock.unlockRead(stamp); }
}
use(x, y);                            // act only on validated data
```

## Ground rules (source-verified)

- `tryOptimisticRead()` returns a stamp, or 0 when a writer holds the lock.
- `validate(stamp)` uses a load fence; stamp 0 is never valid.
- Optimistic sections must be side-effect-free until validated.
- `tryConvertToWriteLock(stamp)` returns 0 on contention — the fallback path
  (`unlockRead` + `writeLock`) is mandatory, not defensive.
- NOT reentrant: re-acquiring a held lock deadlocks against yourself.
  No owner tracking exists to recognize re-entry.
- NO conditions: `newCondition()` on both `asReadLock()`/`asWriteLock()`
  views throws `UnsupportedOperationException`.
- Stamps are finite, recyclable after ~1 year of continuous operation, and
  guessable — never treat them as security capabilities.

## When to use it

Read-mostly state with short critical sections, rare writes, no callbacks
under the lock, and no need for `await`/`signal`. Write-heavy data, long
read sections, or reentrant call shapes belong with `ReentrantReadWriteLock`
or `ReentrantLock` (see WHY_IT_EXISTS.md and REFACTORING.md).

## Lab map

- THEORY.md / CODE_DEEP_DIVE.md — authoritative semantics + runnable demos.
- HOW_IT_WORKS.md, INTERNALS.md, ARCHITECTURE.md — mechanism and state bits.
- STEP_BY_STEP.md, VISUAL_GUIDE.md, MENTAL_MODELS.md — learning scaffolds.
- EXERCISES.md, QUIZ.md, FLASHCARDS.md — practice and recall.
- COMMON_MISTAKES.md, DEBUGGING.md, PERFORMANCE.md — failure modes.
- HISTORY.md, REFERENCES.md, MATH_FOUNDATION.md — context and models.
- SECURITY.md, REFACTORING.md, REFLECTION.md — hardening and transfer.
- WHY_IT_EXISTS.md, WHY_IT_MATTERS.md — motivation and payoff.
