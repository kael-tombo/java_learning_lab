# Phaser — Theoretical Foundation

## Core Concept

`Phaser` (Java 7, JSR-166) is a **reusable, dynamic barrier**: N parties each
advance through numbered *phases*, and phase k completes only when every
party registered for it has *arrived*. Unlike `CyclicBarrier` (fixed party
count, one-shot-per-cycle) and `CountDownLatch` (one-shot, countdown only),
a Phaser supports parties that **register and deregister mid-execution**,
parties that arrive without waiting, and hierarchical tiering for scale.

## The Vocabulary (seven verbs, each a different synchronization shape)

| Call | Arrives? | Waits? | Leaves? |
|---|---|---|---|
| `register()` / `bulkRegister(n)` | — (adds unarrived parties to current phase) | no | no |
| `arrive()` | yes | no | no |
| `arriveAndAwaitAdvance()` | yes | yes (for phase advance) | no |
| `arriveAndDeregister()` | yes | no | yes |
| `awaitAdvance(phase)` | no | yes (until past `phase`) | no |
| `awaitAdvanceInterruptibly(phase)` | no | yes, interruptible | no |
| `onAdvance(phase, parties)` (override) | — | — | terminates if returns true |

The power rows are the ones barriers lack: `arrive()` without waiting (a
producer can signal completion and move on while consumers still rendezvous)
and `arriveAndDeregister()` (one-shot participants exit without holding the
phase open — the class javadoc's own main-thread pattern).

## Phase Numbering and Termination

- Phases count 0, 1, 2, ...; `getPhase()` returns the current phase, or a
  **negative** value once terminated (`isTerminated()` ⟺ phase < 0).
- `arrive()` returns the *arrival phase* (the phase the arrival counted
  toward) — capture it for `awaitAdvance(phase)`, which returns once the
  phaser advances *past* that phase. Note the asymmetry (source-verified):
  `arriveAndAwaitAdvance()` instead returns the phase *after* the advance
  — arriving during phase k yields k+1, never k.
- Termination happens when `onAdvance` returns true (default: true only when
  registered parties hit 0) or via `forceTermination()`. After termination
  all arrivals/awaits return immediately — a terminated Phaser is an open
  gate, not a broken one (contrast `CyclicBarrier`'s broken state, which
  poisons the barrier with `BrokenBarrierException`).

## Registration Timing: Late Joiners Hold the Phase

`register()` adds an **unarrived** party to the *current* phase — the phase
cannot advance until the newcomer also arrives (or deregisters). Consequences:

- A coordinator can spawn workers mid-phase and still rendezvous correctly
  (the javadoc's task-loop pattern: `register()` per task before starting
  its thread).
- Registering from *within* a phase action is safe; the phase simply waits
  for one more arrival.
- Deregistration is what lets phased computations *shrink*: solvers whose
  partitions converge call `arriveAndDeregister()` and the barrier
  tightens around the survivors.

## Tiering: Parents for Scale

`new Phaser(parent)` registers the child with its parent: the child phase
advances only with parent coordination, so a tree of Phasers rendezvouses
thousands of parties without one giant arrival counter. Each tier adds one
coordination hop per phase — depth ~log(parties) instead of a single
contention point. (Single-level suffices until arrival storms measurably
contend; tier when profiling says so, not before.)

## Phaser vs CyclicBarrier vs CountDownLatch

| | Phaser | CyclicBarrier | CountDownLatch |
|---|---|---|---|
| Party count | dynamic (register/deregister) | fixed at construction | fixed (countdown only) |
| Reusable | yes (phases) | yes (cycles) | no (one-shot) |
| Arrive-without-wait | yes (`arrive`) | no | yes (`countDown`) |
| Await-without-arrive | yes (`awaitAdvance`) | no | yes (`await`) |
| Termination control | `onAdvance` → true | breakage poisons | n/a |
| Failure mode | open gate after termination | `BrokenBarrierException` everywhere | silent under-count |

Pick the Phaser when membership changes over time (iterative solvers,
fork-join-ish staged pipelines with dynamic splits, test harnesses with
late-joining observers). Pick the barrier for fixed gangs; the latch for
one-shot readiness.

## The Classic Pitfalls (stated as rules)

1. **Awaiting your own arrival phase**: `awaitAdvance(arrive())` rendezvouses
   like `arriveAndAwaitAdvance()` — but the two return different numbers
   (`arrive()` yields the arrival phase k; the combined call yields k+1).
   `awaitAdvance(getPhase())` after others advanced can return *immediately*
   advanced can return *immediately* (phase already past). Always await the
   phase *your arrival* returned.
2. **Forgetting deregistration on exceptional paths**: a thread that dies
   between register and arrive holds its phase forever — wrap arrivals in
   `try/finally` with `arriveAndDeregister()` on the failure path, or use
   `forceTermination()` from a supervisor.
3. **Phase overflow**: phases are `int`s; 2³¹ advances wraps to negative =
   *spurious termination*. Realistic only for nanosecond-phased loops
   running months — documented, not feared.
4. **Blocking inside `onAdvance`**: it runs at the advance point; slow
   overrides stall every party. Keep it a predicate.

## Key Invariants

1. Phase k advances ⟺ arrived(k) == registered(k) (or forced termination).
2. `getPhase() < 0` ⟺ terminated; post-termination all waits pass through.
3. Registration adds *unarrived* parties to the current phase — never
   retroactively satisfied.
4. `onAdvance` true terminates; default terminates only at zero parties.
5. `awaitAdvance(p)` returns when current phase ≠ p (advanced past *or*
   terminated).
