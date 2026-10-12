# Phaser — Step by Step

## Exercise 1: three-phase rendezvous, exact returns

1. `Phaser p = new Phaser(1); p.bulkRegister(2);` — 3 parties, phase 0.
2. Start 2 workers looping `arriveAndAwaitAdvance()` 3 times.
3. Main loops `arrivals[i] = p.arriveAndAwaitAdvance()` 3 times.
4. Assert returns are exactly 1, 2, 3 (post-advance values).
5. Assert `getPhase() == 3` and `getUnarrivedParties() == 3` (next phase
   fully open), then `arriveAndDeregister()` for cleanup.

## Exercise 2: signal now, wait later

1. `new Phaser(1)` + `register()` = 2 parties (main + worker).
2. Worker calls `int k = phaser.arrive();` then immediately proceeds
   (set a flag proving it moved on), calling `awaitAdvance(k)` later.
3. Main asserts phase still 0 and `getUnarrivedParties() == 1` (itself).
4. Main calls `arriveAndAwaitAdvance()`; worker's pending await releases.
5. Join, assert phase 1, deregister. Note: no barrier or latch permits the
   split of step 2 across methods.

## Exercise 3: shrink the barrier mid-run

1. Main + 2 workers rendezvous phase 0 together.
2. Worker 0 calls `arriveAndDeregister()`; worker 1 and main call
   `arriveAndAwaitAdvance()`.
3. After phase 0, assert `getRegisteredParties() == 2`.
4. Advance phase 1 with survivors; assert phase 2 reached with 2 parties.

## Exercise 4: terminate on your predicate

1. Subclass with `onAdvance` returning `phase >= 1 || parties == 0`.
2. Advance once: assert phase 1, still alive.
3. Advance again: assert `isTerminated()` and `getPhase() < 0`.
4. Assert `arrive()` returns negative and `awaitAdvance(anything)` returns
   at once — the open gate, with no exceptions anywhere.

## Exercise 5: the stale-phase trap

1. Single-party phaser: `int k = solo.arrive();` then
   `awaitAdvance(k)` — assert instant return of k+1.
2. Two-party phaser where the second party never arrives: observe that
   awaiting a `getPhase()` snapshot has no defined meaning — always await
   your own arrival's return. Never block a demo harness on this; use
   `arriveAndDeregister` to exit cleanly.

## Review checklist

- Arrival values feed awaits; `getPhase()` never does.
- Every register has a matching arrival-or-deregister on all paths.
- `onAdvance` is a predicate, not a work site.
- Demos deregister main at the end so nothing outlives the test.
