# Mental Models: AQS

## 1. The ledger and the line

`state` is a ledger (one number: locked/unlocked, permits, latch count). The
queue is the line at the counter. The framework never confuses them: policy
writes the ledger, mechanism manages the line. Every bug is either a wrong
ledger entry (permit leak, missed unlock) or a line failure (lost wakeup,
cancelled node).

## 2. Barging as cutting the line

A nonfair newcomer walks straight to the counter and tries the CAS before
joining the line. If the counter is free *right now*, it is served. Throughput
rises (no usher overhead); anyone already in line can wait arbitrarily long.
Fair mode forces newcomers to the back of the line first.

## 3. Head as a "served" ticket stub

The head node is a torn ticket: its thread is already inside. It stays in the
holder only as a position marker so the next ticket knows whom to watch.
`getFirstQueuedThread()` peeks at the ticket *after* the stub.

## 4. `signal` as a room transfer, not a handoff

`await()` parks a thread in a side room (condition queue). `signal()` walks
that thread back to the main line's tail — it does NOT seat them at the
counter. They still race the line. Code that assumes "signalled = owns the
lock" is wrong; the `while` loop re-checks the real condition.

## 5. Downgrade as narrowing, upgrade as deadlock

Holding write then taking read = narrowing your grip (safe: you already
exclude everyone). Holding read then asking write = asking everyone else to
leave while you refuse to leave — including yourself. The model predicts the
rule: downgrade ok, upgrade deadlocks.

## 6. Permits as tokens in a bowl

`Semaphore(n)` is a bowl with `n` tokens. Acquire takes, release returns.
Over-release drops in tokens nobody took — the bowl overflows silently because
nobody counts the ceiling. The fix is accounting discipline (try/finally
pairing), not a bigger bowl.

## 7. Status bits as sticky notes on chairs

JDK 23 nodes carry sticky notes: `WAITING` ("wake the next chair"), `COND`
("this chair is in the side room"), `CANCELLED` ("chair empty, skip it").
The old notes (`SIGNAL`, `PROPAGATE`) said the same things in different
words — the seating protocol never changed.
