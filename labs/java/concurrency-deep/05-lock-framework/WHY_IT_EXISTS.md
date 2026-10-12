# Why the Lock Framework Exists

## The ceiling of `synchronized`

`synchronized` (lab 02) ties locking to block structure: entry acquires, exit
releases. That design leaves five gaps no block-structured lock can fill:

1. No bounded wait — a thread either blocks forever or never tries.
2. No interruption — `lockInterruptibly` has no monitor equivalent.
3. One wait-set per object — producer/consumer pairs share `wait()`/`notify()`.
4. No fairness choice — intrinsic locks barge, always.
5. No shared-mode primitives — semaphores, latches, read/write splits need a
   separate engine.

## The AQS answer (JSR-166, Java 5, 2004)

Doug Lea's `AbstractQueuedSynchronizer` factored every synchronizer into two
parts: an `int state` the subclass interprets, and a queue + parking protocol
the framework owns. `ReentrantLock`, `Semaphore`, `CountDownLatch`,
`ReentrantReadWriteLock` are thin `tryAcquire`/`tryRelease` policies over one
tested queue. `ConditionObject` gives each lock as many wait-queues as it
wants (`ArrayBlockingQueue` uses `notEmpty` + `notFull`).

## What each piece solves

- `ReentrantLock` + `tryLock(timeout)`: lock with a deadline — back off, retry
  with a different order, break deadlock cycles that `synchronized` cannot.
- `lockInterruptibly()`: shutdown paths can cancel a queued waiter instead of
  waiting for a lock that may never release.
- Fair mode: FIFO-ish admission for latency-sensitive handoffs where barging
  starvation is worse than the throughput cost.
- `Semaphore`: bounded resource pools (permits = connections, slots).
- `CountDownLatch`: one-shot start gates and completion rendezvous.
- `ReentrantReadWriteLock`: read-heavy workloads where shared reads scale and
  exclusive writes serialize; downgrade (write-to-read) is safe by design.

## What it deliberately does not do

- No block structure: `unlock` in `finally` is a programmer obligation.
- No JIT lock elision: library calls are opaque where bytecodes were visible.
- Fairness is advisory: even fair mode admits re-barging between `unlock` and
  successor wakeup — the guarantee is "no overt barging," not strict FIFO.
- `tryLock()` itself is unordered in both modes — never a fairness probe.
