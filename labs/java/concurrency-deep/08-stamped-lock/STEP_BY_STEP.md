# StampedLock — Step by Step

## Exercise 1: the optimistic read, line by line

Given a `Point { double x, y; StampedLock lock; }`:

1. `long s = lock.tryOptimisticRead();` — sample the version. If a writer
   holds the lock you get 0, which will simply fail validation below.
2. `double cx = x, cy = y;` — plain reads into locals. These may be torn
   (cx new, cy old). Do nothing observable with them yet.
3. `if (!lock.validate(s))` — fence and re-check. False means a write
   completed mid-copy; discard `cx`/`cy` entirely.
4. Fallback: `s = lock.readLock(); try { cx = x; cy = y; } finally {
   lock.unlockRead(s); }` — now the snapshot is stable.
5. `return Math.hypot(cx, cy);` — the first and only use of the data.

Check yourself: no I/O, no mutation, no method calls on `cx`/`cy` before
step 5. Anything inconsistency-intolerant (indexing, dividing) waits too.

## Exercise 2: read-then-write upgrade

1. `long s = lock.readLock();` — inspect under a pessimistic read.
2. Decide mutation is needed; call `long ws = lock.tryConvertToWriteLock(s);`
3. If `ws != 0`: set `s = ws`, mutate, `finally { lock.unlock(s); }`.
4. If `ws == 0`: `lock.unlockRead(s); s = lock.writeLock();` then mutate
   and re-check the condition (state may have changed during the window).
5. Confirm exactly one unlock executes on every path.

## Exercise 3: prove non-reentrancy safely

1. Take `long held = lock.writeLock();`.
2. From the same thread call `lock.tryWriteLock(200, MILLISECONDS)` — never
   the blocking form, which would hang the demo.
3. Observe the 0 return: even the owner is refused.
4. `lock.unlockWrite(held);` and assert `!lock.isWriteLocked()`.

## Exercise 4: prove the condition refusal

1. Get `Lock rv = lock.asReadLock(), wv = lock.asWriteLock();`.
2. Wrap each `newCondition()` in try/catch for
   `UnsupportedOperationException`; assert both throw.
3. Conclude: any `await`/`signal` design needs a different lock.

## Exercise 5: measure the optimism boundary

1. Run the CODE_DEEP_DIVE snippet 2 harness with no writers; assert zero
   fallbacks (deterministic).
2. Add one hammering writer; observe fallbacks appear.
3. Keep raising writer share until the optimistic path costs more than
   plain `readLock()` — that crossover is workload-specific, so record
   your machine's number rather than memorizing one.

## Review checklist

- Locals first, validate second, act third.
- Conversion 0 always has a fallback.
- Timed attempts only when demonstrating refusal.
- `try/finally` pairs every stamp with its unlock.
