# Phaser — Visual Guide

## One phase lifecycle

```
phase k opens:   registered=3, unarrived=3
  A arrives  --> unarrived=2   (parks if awaiting)
  B arrives  --> unarrived=1
  C arrives  --> unarrived=0 = LAST: run onAdvance(k, 3)
                   false -> publish k+1, unpark all phase-k waiters
                   true  -> publish TERMINATED, release everyone
```

## The verb matrix in motion

```
register()            registered+1, unarrived+1  (holds current phase)
arrive()              unarrived-1, return k, keep going
arriveAndAwaitAdvance unarrived-1, park until phase != k, return k+1
arriveAndDeregister() unarrived-1 AND registered-1 (arrival + departure)
awaitAdvance(k)       park while current == k (arrives nothing)
onAdvance -> true     terminate: phase goes negative, gate opens
```

## Return-value asymmetry

```
during phase 0:
  arrive()                  returns 0  (arrival phase)
  arriveAndAwaitAdvance()   returns 1  (post-advance phase)
  awaitAdvance(0)           returns 1  (phase when released)
after termination:
  arrive()                  returns negative
  awaitAdvance(anything)    returns immediately (current negative phase)
```

## Late joiner holds the phase

```
phase 0: A, B arrived; C outstanding
  coordinator: register() -> D joins  (unarrived back up)
  phase 0 CANNOT advance until C and D both arrive
newcomers land in the current phase, never retroactively satisfied
```

## Shrinking mid-run

```
phase 0: A, B, C rendezvous (3 parties)
  A: arriveAndDeregister()   (counts for phase 0, then leaves)
phase 1: B, C only (2 parties) — barrier tightened around survivors
zero parties + default onAdvance -> terminated
```

## Tiering

```
      parent (root)
      /          \
  child1(100)  child2(100)
leaves rendezvous locally, each arrives once upward;
root advance cascades down. Depth ~ log(parties).
```

## Termination vs breakage

```
Phaser terminated:    arrive/await return at once, no exceptions (OPEN GATE)
CyclicBarrier broken: every waiter gets BrokenBarrierException (POISONED)
CountDownLatch done:  gate open, but one-shot — never reusable
```

## Stale-phase trap

```
k = arrive()  ->  awaitAdvance(k)  CORRECT (your phase, defined meaning)
s = getPhase() -> ... time passes ... awaitAdvance(s)  RISKY (may be stale:
instant return that skips the rendezvous, or a stranger-held phase)
```
