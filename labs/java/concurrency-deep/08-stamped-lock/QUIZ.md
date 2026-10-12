# StampedLock — Quiz

## Q1. What does `tryOptimisticRead()` return when a writer holds the lock?

**A.** 0 — which `validate` always reports as invalid. The caller must fall
back to `readLock()`. Sampling under write hold never yields a usable stamp.

## Q2. What must an optimistic section avoid before validation?

**A.** All side effects and all uses of the data: no I/O, no mutation, no
branching on it, and no inconsistency-intolerant operations (indexing,
dividing, unbounded loops). Copy fields to locals, validate, then act.

## Q3. What does `validate(stamp)` actually check?

**A.** Whether the version bits of `stamp` still equal the version bits of
current `state`, checked after a load fence. Equality means no write
completed between sampling and the fence — the copied snapshot was stable.

## Q4. `tryConvertToWriteLock` returns 0. What happened and what do you do?

**A.** Conversion was refused — other readers hold the lock or a writer
intervened. Release the read hold with `unlockRead`, acquire `writeLock()`
explicitly, re-check the condition that motivated the write, then mutate.

## Q5. Is StampedLock reentrant? What happens on re-acquire?

**A.** No. There is no owner tracking, so a second acquire (even from the
holding thread) queues behind the first and waits forever — self-deadlock.
Pass stamps into callees instead of re-acquiring.

## Q6. What happens when you call `newCondition()` on either Lock view?

**A.** Both throw `UnsupportedOperationException`. StampedLock has no
wait-sets, so no `await`/`signal` exists. Use `ReentrantLock` for
condition-based designs.

## Q7. Which unlock pairs with a converted stamp?

**A.** The generic `unlock(stamp)` dispatches on stamp bits and handles any
stamp; typed `unlockRead`/`unlockWrite` are faster for unconverted stamps.
Every acquired stamp needs exactly one matching unlock.

## Q8. Why can stamps never serve as security capabilities?

**A.** They are finite, recycled after ~1 year of continuous operation, and
documented as guessable ("not cryptographically secure"). A stale or
guessed stamp may spuriously validate — it proves nothing about identity.

## Q9. When does optimism perform worse than a plain read lock?

**A.** When writer rate times window length is large: hot writers or long
optimistic sections make most attempts fail, so reads pay attempt plus
fallback — more than `readLock()` alone. Measure the crossover per
workload; it is not a constant.

## Q10. What is the sole-reader conversion guarantee?

**A.** A single outstanding reader converts to write atomically via CAS,
with no release/reacquire window for another writer to slip through.
Contended conversion (multiple readers) is refused with 0 instead.
