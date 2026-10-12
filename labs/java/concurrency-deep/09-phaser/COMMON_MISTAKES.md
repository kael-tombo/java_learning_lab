# Phaser — Common Mistakes

## 1. Awaiting a stale getPhase() instead of your arrival

```java
// WRONG: phase may advance between sampling and awaiting
int p = phaser.getPhase();
doWork();
phaser.awaitAdvance(p);   // may return instantly — rendezvous skipped
```

Fix: `int k = phaser.arrive(); ... phaser.awaitAdvance(k);` or use
`arriveAndAwaitAdvance()`. Only your arrival value has defined meaning.

## 2. Confusing the two return conventions

`arrive()` yields the arrival phase k; `arriveAndAwaitAdvance()` yields
k+1. Code that stores one and compares against the other is off by one
forever: label variables `arrivalPhase` vs `advancedPhase` and never mix
them.

## 3. Forgetting deregistration on failure paths

A thread that dies between `register()` and its arrival holds the phase
open forever — every survivor parks indefinitely. Wrap arrivals in
`try/finally` with `arriveAndDeregister()` on the failure path, or give a
supervisor `forceTermination()` authority.

## 4. Registering and never arriving

Each `register()` adds an unarrived party the current phase must wait for.
Spawn-then-crash without arrival wedges the phase identically to mistake
3 — register immediately before starting the worker, and account for the
slot if the start itself throws.

## 5. Blocking inside onAdvance

`onAdvance` runs on the final arrival's thread with all parties parked.
I/O, locking, or heavy scans there stall the entire rendezvous and risk
deadlock (it re-enters locks waiters hold). Keep it a pure predicate on
`(phase, registeredParties)` plus volatile flags.

## 6. Treating termination like breakage

Post-termination `arrive()` returns negative and awaits pass through —
normal open-gate behavior, not errors. Code that throws on negative phases
invents failures at exactly the computation's end. Check `isTerminated()`
and exit cleanly.

## 7. Orphaned tiers

A child created with `new Phaser(parent)` occupies one parent slot even
with zero parties of its own. Forgetting to deregister empty children
leaves the parent waiting on nothing — always pair tier creation with a
deregistration path.

## 8. Phase-overflow blindness

`int` phases wrap after 2^31 advances to negative (spurious termination).
Only hot loops running months qualify — but guards of the form
`phase < 0 → error` must instead consult `isTerminated()` and expected
phase counts.
