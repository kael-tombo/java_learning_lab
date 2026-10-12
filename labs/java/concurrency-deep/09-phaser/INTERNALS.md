# Phaser — Internals

Source: `java.base/share/classes/java/util/concurrent/Phaser.java`
(JDK 23). Every claim below names its anchor in that file.

## Packed state word

One `volatile long state` encodes phase (high bits), parties, and unarrived
counts via shifts and masks (`phaseShift`, `partiesShift`, `phaseMask`
constants). Helpers `getPhase()`, `getRegisteredParties()`,
`getUnarrivedParties()` are pure decodes — no locking, just bit
extraction. Termination is `phase < 0` after sign extension, so
`isTerminated()` is a single comparison.

## arrive() vs arriveAndAwaitAdvance() returns

`arrive()` returns the phase its arrival counted toward (arrival phase k):
the fast path CASes unarrived down and, when it was not the last arrival,
returns k directly. `arriveAndAwaitAdvance()` instead parks (unless it was
the final arrival driving the advance) and returns the phase observed on
wakeup — the post-advance phase k+1, or a negative value if the advance
terminated. That asymmetry is in the source's return paths, not convention.

## awaitAdvance(p) loop

`awaitAdvance` reads current phase once: if it already differs from `p`,
return immediately (no park — this is the stale-phase instant return).
Otherwise enqueue on the waiter stack for phase `p` and park until the
advance publishes a different phase or termination. Interruptible and
timed overloads add the corresponding unpark conditions.

## onAdvance invocation context

The advance path calls `onAdvance(phase, registeredParties)` inline on the
thread that recorded the final arrival — while all other parties are
parked. A slow override therefore stalls every party's wakeup; a throwing
override propagates on that thread. Keep it a pure predicate of its
arguments.

## Registration CAS

`register()`/`bulkRegister(int)` CAS-loop the state word: registered += n,
unarrived += n, bound to the phase observed at loop entry. If the phase
advanced mid-loop the CAS retries against the new phase — newcomers always
land in the actually-current phase, never retroactively satisfy an old one.

## Deregistration accounting

`arriveAndDeregister()` decrements unarrived (its arrival) AND registered
(its departure) in one state transition; if it is the final arrival it
also drives the advance. Zero-party advance → default `onAdvance` returns
true → termination. That is the whole "shrink mid-run" mechanism.

## Tiering mechanics

The child constructor registers with the parent (`parent.register()`),
and child advances `arrive` upward through `parentArrive` plumbing while
parent termination propagates down. A child with no parties of its own
still occupies one parent slot until deregistered — orphan tiers must be
cleaned up or the parent phase waits on an empty child.
