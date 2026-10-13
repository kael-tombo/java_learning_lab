# Refactoring: Reordering

## Pattern 1: free-running litmus -> rendezvoused litmus

Before: two threads looping freely, anomaly counts near zero,
engineer concludes "no reordering here."

After: the lab's volatile-flag handshake (`go`/`done1`/`done2`,
`onSpinWait`, daemon racers, main driver resetting `x = y = 0` per
round). Counts jump to tens of percent with no change to the measured
bodies. Rule: modify harness tightness, never infer verdicts from
loose-harness rates.

## Pattern 2: drain-as-fix -> edge-as-fix

Before (diagnostic only):

```java
x = 1;
LockSupport.parkNanos(1); // hides the anomaly, guarantees nothing
r1slot = y;
```

After (choose by shape):

```java
volatile int x, y;  // ordering fix: 0/20000, portable
// OR
synchronized (LOCK) { x = 1; r1slot = y; } // exclusion fix: 0/20000
```

Why: the drain pays delay per pair for a still-racy program; the edge
pays a fence (or serialization) for a verdict. Delete every
sleep-between-accesses "fix" on sight — lab 02's elimination argument
is the citation.

## Pattern 3: barrier-per-iteration -> spin rendezvous (for litmus)

Before: `CyclicBarrier` aligning iteration starts — clean-looking,
wide windows, suppressed rates, misleading greens.

After: volatile `go`/`done` spins — tighter windows, honest rates.
(Boundaries: production code should prefer barriers/phasers for real
coordination; the spin rendezvous is test instrumentation for litmus,
burning cores deliberately for nanosecond alignment. Do not ship the
spin as coordination.)

## Pattern 4: release/acquire Dekker -> volatile Dekker

Before: `X.setRelease(1); r1 = Y.getAcquire()` — modern-looking modes,
61-90% anomalies, race intact.

After: plain `volatile` fields — 0/20000. Keep release/acquire where
it belongs (snippet 4's message-passing chain: 50000 intact at a
fraction of volatile cost) and escalate where Dekker's total order
demands it. The refactor is one mode step, decided by shape analysis,
not by "stronger sounds better."

## Pattern 5: split or half-applied fixes -> complete the pair

- Volatile on one field only: still races (the plain side's StoreLoad
  still escapes) — volatile *both*.
- Lock around stores only: still races (loads overlap outside) — the
  whole store;load *pair* inside one lock.
- Rendezvous flags made plain "for speed": reopens spin hoisting —
  handshake stays volatile while bodies stay plain.

## Refactoring checklist

- Name the verdict before and after (nonzero vs zero), with 20000
  fixed iterations and 3 runs each.
- Change one variable per step (handshake, delay, mode, scope).
- Assert verdicts in tests (`bad > iters/100`, `bad == 0`), never
  exact counts.
- Leave a comment naming the mechanism (buffer) and the guarantee
  (ordering vs exclusion) so the next reader does not re-drain it.
