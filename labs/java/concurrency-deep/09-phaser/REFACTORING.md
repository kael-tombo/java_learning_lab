# Phaser — Refactoring

## Migrating from CyclicBarrier (membership now dynamic)

Candidate: fixed barrier where parties started joining/leaving mid-run, or
breakage handling sprawls across catch blocks. Steps:

1. Replace `new CyclicBarrier(n, action)` with `new Phaser()` plus
   `bulkRegister(n)`; move the barrier action into explicit post-advance
   code (or an `onAdvance` predicate plus a follow-up task).
2. Replace `await()` with `arriveAndAwaitAdvance()`; capture the return
   (post-advance phase) where the old code assumed cycles.
3. Replace breakage recovery (`BrokenBarrierException` resets) with
   termination handling: `isTerminated()` checks and clean exit.
4. Convert early-exit paths to `arriveAndDeregister()` instead of barrier
   reset acrobatics.

## Migrating from per-iteration CountDownLatch

Candidate: loops rebuilding a latch per phase with manual generation
counters. Replace the rebuild with one Phaser: `register()` newcomers,
`arriveAndAwaitAdvance()` per iteration, `arriveAndDeregister()` for
retirees. Delete the generation bookkeeping — phases are the generations.

## Before / after: shrinkable rendezvous

```java
// Before: fixed barrier, retiree must break or rebuild it
barrier.await();                      // leaver has no clean exit
if (done) { barrier.reset(); ... }    // disturbs survivors

// After: retiree counts and leaves; survivors continue untouched
if (done) phaser.arriveAndDeregister();
else phaser.arriveAndAwaitAdvance();
```

## Before / after: split signal and sync

```java
// Before: latch forces signal+wait coupling per participant
latch.countDown(); latch.await();     // one-shot only

// After: reusable, separable across methods
int k = phaser.arrive();              // signal here...
produceMore();
phaser.awaitAdvance(k);               // ...synchronize there
```

## When to refactor away from Phaser

- Membership static again → `CyclicBarrier` (simpler, barrier action).
- One-shot readiness → `CountDownLatch`.
- Result-composing task graphs → executors / `CompletableFuture`.
- Lifetime-scoped concurrency → structured concurrency (lab 10).

## Review checklist for the diff

Arrival values (not `getPhase()`) feed awaits; every register has a
failure-path deregister; `onAdvance` is a predicate; termination handled
as open-gate; tiers deregistered; no `BrokenBarrierException`-style
thinking left behind.
