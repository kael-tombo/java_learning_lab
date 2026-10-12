# Phaser — Why It Matters

## Phased algorithms are everywhere

Bulk-synchronous-parallel loops (compute, exchange, repeat), multi-stage
ETL pipelines with per-stage gates, game-engine tick barriers, distributed
test harnesses with setup/run/teardown phases: all rendezvous repeatedly
with a party set that shifts. Phaser is the JDK's native vocabulary for
that loop — register, arrive, advance, deregister — without rebuilding a
barrier per iteration.

## Correctness users feel

- **No lost wakeups on late joiners.** Because registration adds unarrived
  parties, a worker spawned mid-phase is automatically included in the
  current rendezvous instead of racing it.
- **Clean retirement.** Converged or failed participants deregister and the
  computation continues with survivors — no barrier reconstruction, no
  generation bookkeeping by hand.
- **Graceful end-of-life.** Termination opens the gate: stragglers pass
  through with negative returns instead of detonating
  `BrokenBarrierException` across every waiter.

## Where it does not matter

Fixed gangs should stay on `CyclicBarrier` (simpler, barrier action
included); one-shot readiness stays on `CountDownLatch`; task parallelism
with result composition belongs to executors and `CompletableFuture`.
Reaching for a Phaser with a static party count adds verbs without value.

## Interview and code-review signal

Reviewers probe three distinctions: `arrive()` (returns arrival phase k)
vs `arriveAndAwaitAdvance()` (returns k+1), awaiting your own arrival
value vs a stale `getPhase()`, and open-gate termination vs broken-barrier
semantics. Stating those crisply signals real barrier experience rather
than API familiarity.

## Operational payoff

Tiered phasers scale rendezvous to thousands of parties with logarithmic
coordination hops, and deregistration keeps long-running phased services
from accumulating zombie parties. Both properties show up directly in
sustained-iteration throughput (see PERFORMANCE.md).
