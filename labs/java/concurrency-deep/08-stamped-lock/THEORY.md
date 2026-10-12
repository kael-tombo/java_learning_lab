# StampedLock — Theoretical Foundation

## Core Concept

`StampedLock` (Java 8) is a lock that returns a **`long` stamp** instead of
holding owner state — and that one design decision buys a third lock mode no
`ReadWriteLock` has: **optimistic reading**. Try an optimistic read (nearly
free: one volatile read, no CAS, no queue), do the work, then `validate()`:
if no writer intervened, the data was consistent; if one did, fall back to a
pessimistic read lock and retry. Read-heavy workloads with rare writes go
from "readers serialize on a CAS" to "readers never touch shared state."

The three modes, from the JDK 23 source:

```java
tryOptimisticRead():  ((s = state) & WBIT) == 0 ? (s & SBITS) : 0
validate(stamp):      loadFence; (stamp & SBITS) == (state & SBITS)
```

An optimistic "lock" that isn't held — just a version number sampled and
re-checked. Writers bump the version; any mismatch fails validation.

## The Optimistic Pattern (and Its Obligations)

```java
long stamp = lock.tryOptimisticRead();
double x = point.x, y = point.y;      // plain reads, possibly torn vs writers
if (!lock.validate(stamp)) {          // writer intervened?
    stamp = lock.readLock();          // fall back: pessimistic
    try { x = point.x; y = point.y; }
    finally { lock.unlockRead(stamp); }
}
use(x, y);
```

The javadoc imposes three obligations most users miss:

1. **Optimistic sections must be side-effect-free.** The reads may observe an
   inconsistent snapshot (x from before a write, y from after) — any action
   taken on unvalidated data (I/O, mutation, branching into unsafe code)
   can misfire before `validate` ever runs. Copy fields to locals, validate,
   *then* act.
2. **Unvalidated sections can't call inconsistency-intolerant methods.**
   Anything that could throw/divide-by-zero/loop-forever on torn input
   (e.g., using x as an array index or divisor) must wait for validation.
3. **Stamps are finite and recyclable** — "may recycle after (no sooner
   than) one year of continuous operation." A stamp held unvalidated for
   absurd durations can validate spuriously. (Never happens in practice;
   documented for completeness — and a reminder stamps aren't capabilities:
   "not cryptographically secure... may be guessable.")

## tryConvertToWriteLock: Upgrade Without Dance

Read→write upgrade deadlocks under `ReentrantReadWriteLock` (lab 05).
`StampedLock` offers conditional conversion (source-verified branches):

- already writing → return stamp (no-op success);
- sole reader → CAS to write (no release/reacquire window);
- optimistic stamp + lock free → CAS to write;
- otherwise → return 0 (caller falls back to explicit `writeLock()`).

```java
long stamp = lock.readLock();
try {
    // ... inspect ...
    long ws = lock.tryConvertToWriteLock(stamp);
    if (ws == 0L) {                       // conversion failed: others reading
        lock.unlockRead(stamp);
        stamp = lock.writeLock();         // explicit acquire (may block)
    } else stamp = ws;
    // ... mutate ...
} finally { lock.unlock(stamp); }
```

Note `unlock(stamp)` (untyped) vs `unlockRead`/`unlockWrite`: the generic
form dispatches on the stamp bits — convenient, marginally slower than the
typed forms. And conversion can *fail spuriously-adjacent*: 0 means "not
now," not "never" — always code the fallback path.

## NOT Reentrant (source-verified javadoc)

"They are not reentrant, so locked bodies should not call other unknown
methods that may try to re-acquire locks." A write-locked thread calling
`writeLock()` again **deadlocks against itself** (no owner tracking to
recognize re-entry — that's precisely the state stamps eliminated). Passing
the stamp *into* callees (which use/convert it) is the sanctioned pattern;
re-acquiring inside is the forbidden one. This single property disqualifies
StampedLock wherever alien/callback methods run under the lock — exactly the
codebase shape where `ReentrantLock`'s forgiveness matters.

## StampedLock vs ReentrantReadWriteLock

| | StampedLock | RRWL |
|---|---|---|
| Optimistic reads | yes (no CAS, no queue) | no |
| Reentrant | **no** (self-deadlock) | yes |
| Conditions | none — `newCondition()` on both views throws `UnsupportedOperationException` (source-verified) | native `writeLock().newCondition()` |
| Interruptible acquire | `readLockInterruptibly` etc. exist | yes |
| Reader overflow | capped readers (spillover handling internal) | 65 535 (MAX_COUNT) |
| Cases favoring it | read-mostly, short critical sections, no callbacks under lock | reentrancy needed, conditions, familiarity |

`asReadLock()`/`asWriteLock()` adapt stamps to the `Lock` interface for
interoperation (including `newCondition()` on the views) — with the
performance caveat that adaptation reintroduces owner-ish bookkeeping the
raw stamp API avoids.

## When Optimism Loses

- **Write-heavy data**: validation fails most attempts → every read pays
  optimistic attempt + fallback pessimistic read. Past some writer fraction
  (workload-dependent — measure, don't guess), plain read locks win outright.
- **Long read sections**: the wider the window between sample and validate,
  the likelier a writer lands inside it. Optimism favors *short*,
  field-copy reads.
- **Irreversible actions mid-read**: see obligations — optimism composes
  only with pure reads.

## Key Invariants

1. `validate(s)` ⟺ no write completed between stamp issuance and the fence.
2. Stamp 0 is never valid (`tryOptimisticRead` returns 0 under write hold;
   `validate` always false on 0).
3. Every acquired stamp (read/write/converted) needs exactly one matching
   unlock — stamps don't nest or auto-release.
4. Lock bodies must be reentrancy-free and (for optimistic paths)
   side-effect-free until validated.
5. Conversion returns 0 on contention — the fallback path is mandatory, not
   defensive.
