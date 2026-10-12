# Phaser — Flashcards

## Card 1

**Q:** Phaser in one sentence: reusable, dynamic what?
**A:** Reusable dynamic barrier: phases advance only when every registered
party has arrived; parties may join/leave mid-execution.

## Card 2

**Q:** Which verb signals without waiting, and what does it return?
**A:** `arrive()` — records arrival, never parks, returns the arrival
phase k (feed it to `awaitAdvance(k)`).

## Card 3

**Q:** Which verb waits without arriving?
**A:** `awaitAdvance(p)` (and the interruptible/timed variants) — parks
until current phase differs from p; arrival counts untouched.

## Card 4

**Q:** State the return asymmetry.
**A:** `arrive()` → arrival phase k; `arriveAndAwaitAdvance()` →
post-advance phase k+1. Label them or stay off by one forever.

## Card 5

**Q:** `register()` lands newcomers in which phase, with what effect?
**A:** The current phase, as unarrived parties — the phase waits for them.
Never retroactive.

## Card 6

**Q:** How does a party both count and leave?
**A:** `arriveAndDeregister()` — its arrival completes the current phase,
then registered parties shrink for the next one.

## Card 7

**Q:** What ends a Phaser, and what does the morning after look like?
**A.** `onAdvance` → true (default at zero parties) or
`forceTermination()`. Phase goes negative; all calls pass through —
open gate, no exceptions.

## Card 8

**Q:** Why must `onAdvance` stay a fast predicate?
**A:** It runs on the final arrival's thread with everyone parked — slow
overrides stall the whole rendezvous and risk deadlock.

## Card 9

**Q:** Await whose phase number?
**A:** Your own arrival's return. `getPhase()` snapshots go stale: already
past (instant false sync) or stranger-held (hang).

## Card 10

**Q:** Tiering buys what at what price?
**A:** Splits arrival-CAS contention across levels (depth ~log parties);
each level adds one coordination hop of latency per phase.

## Card 11

**Q:** Open gate vs broken barrier?
**A:** Terminated Phaser passes everyone through silently; broken
`CyclicBarrier` raises `BrokenBarrierException` on all waiters.

## Card 12

**Q:** Phase overflow in one line?
**A:** `int` phases wrap after 2^31 advances to negative = spurious
termination; real only for hot loops running months.
