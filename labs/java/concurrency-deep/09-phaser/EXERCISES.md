# Phaser — Exercises

All snippets compile on JDK 9+ with no dependencies. Assert each printed
`true` before moving on.

## 1. Exact phase counting

`new Phaser(1)` + `bulkRegister(2)`; two workers and main each advance 3
phases via `arriveAndAwaitAdvance()`. Assert main's returns are exactly
1, 2, 3, final `getPhase() == 3`, `getUnarrivedParties() == 3`, then main
`arriveAndDeregister()`. Explain why the returns are k+1 rather than k.

## 2. Arrive without waiting

Main + one worker (register). Worker records `int k = arrive()`, proves it
moved on (flag/latch), then `awaitAdvance(k)` elsewhere. Main asserts
phase still 0 with 1 unarrived (itself), then `arriveAndAwaitAdvance()`
flips to 1 and the worker's await releases. State what barrier/latch
cannot express this split.

## 3. Dynamic shrink

Main + 2 workers rendezvous phase 0; worker 0 `arriveAndDeregister()`s
while the rest `arriveAndAwaitAdvance()`. Assert registered drops 3 → 2
and phase 1 completes with survivors (final phase 2). Describe the solver
analogue (converged partitions retiring).

## 4. Predicate termination

Subclass with `onAdvance` → `phase >= 1 || parties == 0`. Advance twice
from 1 party: assert alive at phase 1, `isTerminated()` with negative
phase after the second. Assert post-termination `arrive() < 0` and
immediate `awaitAdvance`. Contrast with `CyclicBarrier` breakage in one
paragraph.

## 5. Stale-phase trap (safe version)

Single-party phaser: `arrive()` then `awaitAdvance(arrival)` returns k+1
instantly — assert it. Then demonstrate the trap by analysis (not by
hanging): explain what awaiting an early `getPhase()` snapshot does when
the phase already moved vs when a stranger holds it open.

## 6. Tiered rendezvous

Build `parent = new Phaser(1)` with 2 children `new Phaser(parent)`, each
child bulk-registering 3 workers. Advance all one phase; assert every
level reaches phase 1 and the parent's single slot per child sufficed.
Deregister children and assert the parent no longer waits on them.

## 7. Failure-path deregistration

Register a worker that throws between register and arrive; assert the
phase stalls (timed await times out), then fix with `try/finally`
`arriveAndDeregister()` and assert progress. Add a supervisor path calling
`forceTermination()` and assert the gate opens with negative phase.
