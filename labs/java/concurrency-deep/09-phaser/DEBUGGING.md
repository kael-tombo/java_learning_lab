# Phaser — Debugging

## Symptom: phase never advances (all parties parked)

One or more registered parties never arrived. Inspect
`getRegisteredParties()` vs `getUnarrivedParties()`: unarrived > 0 names
the deficit. Suspects in order: thread died between register and arrive
(check exception paths for missing `arriveAndDeregister` in `finally`),
a late-registered party never started (register before thread start, or
the start threw), an empty child tier occupying a parent slot. Fix the
slot leak; use supervisor `forceTermination()` only as a circuit breaker.

## Symptom: rendezvous "passes" without synchronizing

Someone awaited a stale `getPhase()` value: the phase had already moved,
so `awaitAdvance` returned instantly. Confirm by logging the awaited value
against the arrival returns — mismatches prove it. Replace every
`awaitAdvance(getPhase())` with awaiting the caller's own arrival value.

## Symptom: off-by-one phase assertions

Expected k, observed k+1 (or vice versa): the code mixed `arrive()` (k)
with `arriveAndAwaitAdvance()` (k+1) conventions. Rename variables to
`arrivalPhase`/`advancedPhase` and assert each against its own producer.
CODE_DEEP_DIVE snippet 1 pins the convention: three advances from 0 yield
1, 2, 3.

## Symptom: unexpected termination (negative phase early)

Candidates: custom `onAdvance` predicate firing early (log its inputs per
advance), registered count hitting zero (a worker deregistered that should
only have arrived), `forceTermination()` from a watchdog, or — only in
extreme hot loops — `int` wraparound. Distinguish by logging
`(phase, registeredParties)` at each advance and `isTerminated()` at the
surprise.

## Symptom: all parties stall at each advance (sawtooth latency)

`onAdvance` is doing work: profile the final-arrival thread and look for
application frames under `Phaser.doAdvance`/`onAdvance`. Move the work out
(one party computes post-advance asynchronously) and restore the override
to a predicate.

## Symptom: arrival-CAS contention at scale

Phase latency climbs with party count; profiles show CAS-retry spin on the
state word. Mitigate with `bulkRegister`, then tiering (children per
socket, root above), verifying each step with per-phase p99.

## Tooling notes

- `jstack`: parked phaser waiters show `LockSupport.park` under
  `Phaser.awaitAdvance`/`arriveAndAwaitAdvance`; the missing party is the
  thread NOT parked there.
- Track `getPhase`, `getRegisteredParties`, `getUnarrivedParties` as
  metrics in phased services — the triple narrates every stall.
- Never block a diagnostic harness on a suspect phase; probe with timed
  `awaitAdvanceInterruptibly` variants and dump state on timeout.
