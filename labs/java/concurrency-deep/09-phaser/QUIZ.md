# Phaser — Quiz

## Q1. What do the seven verbs each do?

**A.** `register`/`bulkRegister` add unarrived parties; `arrive` signals
without waiting; `arriveAndAwaitAdvance` signals and waits;
`arriveAndDeregister` signals and leaves; `awaitAdvance` and its
interruptible twin wait without signalling; `onAdvance` decides
termination at each advance.

## Q2. `arrive()` returned 0 but `arriveAndAwaitAdvance()` returned 1. Why?

**A.** Different conventions: `arrive()` yields the arrival phase k (the
phase counted toward), while the combined call yields the post-advance
phase k+1. Both observed the 0 → 1 advance; they just name different ends.

## Q3. When does `awaitAdvance(p)` return?

**A.** As soon as the current phase differs from `p` — advanced past it or
terminated. If the phase already differs at call time it returns at once,
which is why awaiting stale values silently skips rendezvous.

## Q4. What does `register()` do to the current phase?

**A.** Adds unarrived parties to it — the phase cannot advance until the
newcomers arrive or deregister. Late joiners hold the phase; registration
is never retroactive.

## Q5. How does a Phaser terminate, and what does termination feel like?

**A.** `onAdvance` returns true (default: only at zero parties),
`forceTermination()`, or `int` wraparound. Afterwards `getPhase() < 0`
and every arrival/await passes through immediately — an open gate, with no
exceptions (unlike a broken `CyclicBarrier`).

## Q6. What must `onAdvance` never do?

**A.** Block, lock, or do heavy work — it runs on the final arrival's
thread while all parties wait. Keep it a pure predicate of
`(phase, registeredParties)` and volatile flags.

## Q7. A thread dies between `register()` and arrival. Consequence and fix?

**A.** Its unarrived slot holds the phase open forever; survivors park
indefinitely. Fix with `try/finally` + `arriveAndDeregister()` on failure
paths, or supervisor `forceTermination()` as a breaker.

## Q8. When is tiering (`new Phaser(parent)`) justified?

**A.** When arrival-CAS contention on one word dominates profiles
(thousands of parties, hot phases). Children rendezvous locally; each
occupies one parent slot. Single-level suffices until measured otherwise.

## Q9. Phaser vs CyclicBarrier vs CountDownLatch in one line each?

**A.** Phaser: dynamic reusable rendezvous with split signal/sync.
Barrier: fixed-gang reunion with breakage semantics. Latch: one-shot
countdown gate, never reusable.

## Q10. What is the phase-overflow hazard?

**A.** Phases are `int`s; 2^31 advances wrap to negative, reading as
spurious termination. Realistic only for hot loops running months — but
`phase < 0` guards must confirm via `isTerminated()` rather than assuming.
