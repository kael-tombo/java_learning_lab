# Phaser — Why It Exists

## The limits of latch and barrier

`CountDownLatch` (Java 5) fires once: N `countDown`s open the gate forever.
`CyclicBarrier` (Java 5) reunites a fixed gang repeatedly but demands the
same party count every cycle, offers no arrive-without-waiting, and on any
breakage poisons itself — every waiter gets `BrokenBarrierException` and
the barrier is dead. Neither supports a party that joins late, leaves
early, signals without waiting, or waits without signalling.

## Computations that change shape mid-run

Iterative solvers converge partition by partition: finished partitions
should exit without holding the rendezvous open. Staged pipelines split
work dynamically — a coordinator spawns workers mid-phase and still needs
to rendezvous with them. Test harnesses attach late observers that must
not retroactively unblock an already-gated phase. These shapes need
membership that mutates during execution, which fixed gangs cannot express.

## What Phaser added (Java 7, JSR-166)

- **Dynamic registration**: `register()`/`bulkRegister(n)` add unarrived
  parties to the current phase; `arriveAndDeregister()` removes them. The
  barrier tightens and loosens around survivors.
- **Split signal/sync**: `arrive()` signals without waiting and
  `awaitAdvance(p)` waits without arriving — a producer can move on while
  consumers rendezvous, then rejoin the wait elsewhere.
- **Custom termination**: overriding `onAdvance(phase, parties)` ends the
  computation on any predicate (phase count, convergence flag), and the
  terminated phaser becomes an open gate instead of a broken barrier.
- **Tiering**: `new Phaser(parent)` builds trees that rendezvous thousands
  of parties without one giant arrival counter.

## What it deliberately is not

Phaser is not an executor, not a fork-join pool, and not a substitute for
latches in one-shot readiness or barriers in fixed gangs. Where membership
never changes, the simpler primitive reads better and fails less. Phaser
pays for itself exactly when the party set evolves over phases.
