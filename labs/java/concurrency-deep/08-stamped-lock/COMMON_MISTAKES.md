# StampedLock — Common Mistakes

## 1. Acting on unvalidated data

```java
// WRONG: branch on a possibly-torn snapshot
long s = lock.tryOptimisticRead();
if (point.x > LIMIT) alert();   // may fire on torn x
if (lock.validate(s)) { ... }
```

Fix: copy to locals, validate, then act. Nothing observable — no I/O, no
mutation, no branching into unsafe code — happens before validation.

## 2. Calling inconsistency-intolerant methods mid-read

Using an unvalidated value as an array index, divisor, or loop bound can
throw, divide by zero, or spin forever on torn input. Keep optimistic
bodies to plain field copies; move every computation past validation.

## 3. Re-acquiring under hold (self-deadlock)

```java
// WRONG: writeLock inside writeLock — deadlocks, no reentrancy
long s = lock.writeLock();
try { helperThatAlsoLocks(); } finally { lock.unlockWrite(s); }
```

Fix: pass the stamp into callees (which convert or use it), or restructure
so unknown/alien methods never run under the lock.

## 4. Ignoring conversion's 0

`tryConvertToWriteLock` returning 0 is routine contention, not an edge
case. Every call site needs the fallback: `unlockRead`, `writeLock`,
re-check the condition (state may have changed), then mutate.

## 5. Wrong unlock pairing

Each stamp needs exactly one matching unlock: `unlockRead` for read stamps,
`unlockWrite` for write stamps, `unlock` for converted-or-either stamps.
Double-unlock corrupts the reader count; skipped unlock leaks the hold.
`try/finally` every stamp, and never unlock a 0 stamp.

## 6. Expecting conditions

`asReadLock().newCondition()` and `asWriteLock().newCondition()` both throw
`UnsupportedOperationException`. Designs needing `await`/`signal` must use
`ReentrantLock` or `synchronized` — there is no StampedLock workaround.

## 7. Optimism over long sections or hot writers

Wide sample-to-validate windows and frequent writers turn every read into
attempt + fallback, slower than a direct read lock. Measure the crossover
(CODE_DEEP_DIVE snippet 2) and switch modes per workload.

## 8. Treating stamps as capabilities

Stamps are guessable, finite, and recyclable (~1 year bound). Never use
them as auth tokens, never hold one unvalidated across blocking calls, and
never store one as a long-lived "permit."
