# History: Lock Framework

## synchronized era (Java 1.0–1.4)

Intrinsic locks plus `wait`/`notify` were the only tools: block-structured, one
wait-set, no timeout, no interruption, always-barge. Large servers built their
own semaphore and latch layers on top — inconsistently and often incorrectly.

## JSR-166 and Java 5 (2004)

Doug Lea's JSR-166 delivered `java.util.concurrent`, with AQS as its locking
core. One tested queue plus per-class `tryAcquire` policies replaced the ad-hoc
era: `ReentrantLock`, `Semaphore`, `CountDownLatch`,
`ReentrantReadWriteLock`, and `ConditionObject` (multiple wait-queues per lock)
all shipped on the same engine.

## The CLH lineage

AQS's queue descends from the Craig–Landin–Hagersten (CLH) queue lock: each
waiter watches its predecessor. AQS inverts spinning into parking
(`LockSupport.park` until the predecessor releases and unparks) — the change
that keeps queued waiting cheap instead of burning cache lines.

## Steady refinement (Java 6–17)

Reentrancy overflow guards, shared-mode propagation for semaphores/latches,
`tryLock` timeout paths, and cancellation healing (`cleanQueue`) matured
without changing the public contract. `ReentrantReadWriteLock`'s 16/16-bit
packing with `MAX_COUNT = 65535` dates from this era and is unchanged.

## JDK 23 AQS rewrite

The internals were re-implemented around bitwise Unsafe status ops with new
constants `WAITING = 1`, `COND = 2`, `CANCELLED = 0x80000000`. The older
`SIGNAL`/`CONDITION`/`PROPAGATE` encoding disappeared from the source. Public
behavior — barging rules, fair checks, condition migration, uncapped permits,
downgrade/upgrade semantics — is preserved; only guides that quote the old bit
layout went stale.

## What endures

The policy/mechanism split (subclass defines `state`, framework owns the
queue) has survived every rewrite. Learn it once: each new synchronizer since
2004 — including `StampedLock`'s neighbors and lab 09's `Phaser` internals —
reuses the same two-field shape.
