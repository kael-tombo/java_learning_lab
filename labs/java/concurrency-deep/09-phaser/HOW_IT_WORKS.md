# Phaser — How It Works

## Phases and parties

The phaser tracks a current phase number (0, 1, 2, ...) plus registered,
arrived, and unarrived counts. Phase k advances when arrived(k) equals
registered(k) — every party owed for that phase has checked in. Then the
phase number increments, arrival counts reset, and `onAdvance(k, parties)`
runs to decide whether the phaser terminates instead of opening k+1.

## The seven verbs in detail

- `register()` / `bulkRegister(n)`: add n unarrived parties to the CURRENT
  phase and return the phase. The phase cannot advance until the newcomers
  arrive or deregister — late joiners hold it.
- `arrive()`: record arrival for the current phase, do not wait. Returns
  the arrival phase k — the value to pass to `awaitAdvance(k)` later.
- `arriveAndAwaitAdvance()`: arrive and park until the phase advances past
  k. Returns the POST-ADVANCE phase (k+1 on success, negative if the
  advance terminated the phaser).
- `arriveAndDeregister()`: arrive and simultaneously leave the party set.
  Counts toward the current advance, then reduces registered parties.
- `awaitAdvance(p)`: park while current phase equals `p`; return the
  current phase when it differs (advanced or terminated). Arrives nothing.
- `awaitAdvanceInterruptibly(p)`: same, but throws
  `InterruptedException` on interrupt (plus timeout overloads).
- `onAdvance(phase, registeredParties)`: hook invoked at each advance;
  return true to terminate. Default returns true only when registered
  parties reach zero.

## Termination: open gate, not broken barrier

Termination triggers: `onAdvance` returns true, registered count hits zero
(default hook), `forceTermination()` is called, or the `int` phase wraps
past 2^31 advances. Afterwards `isTerminated()` is true, `getPhase()` is
negative, and every arrival/await passes through immediately. Contrast
`CyclicBarrier`: breakage raises on all waiters; Phaser termination raises
on none.

## Tiering

`new Phaser(parent)` enrolls the child as one party of the parent: the
child's phase advances only with parent coordination. Build trees where
leaves rendezvous locally and roots reconcile globally — depth grows
logarithmically with party count instead of hammering one counter.

## Phase numbering discipline

Always await the phase YOUR arrival returned. `awaitAdvance(arrive())`
rendezvouses correctly; `awaitAdvance(getPhase())` may name a stale phase
that has already passed (instant return, skipped rendezvous) or one that a
never-arriving stranger holds open (hang). The arrival value is the only
phase number with caller-defined meaning.
