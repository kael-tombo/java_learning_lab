# Phaser — Performance

## Cost model per verb

- `arrive()`: one CAS on the state word, no waiter node, no park. Cheapest
  rendezvous participation available in the JDK.
- `arriveAndAwaitAdvance()`: arrival CAS plus park/unpark on the waiter
  stack for all but the final arrival. Same order as barrier await.
- `awaitAdvance(p)`: pure park (no arrival CAS) when the phase is still
  open; a single volatile read when already past. Cheapest way to observe.
- `register()`/`bulkRegister`: CAS loop on the state word; bulk form
  amortizes one CAS over n parties — always prefer it for spawns.
- `onAdvance`: runs on the final arrival's thread while everyone waits;
  its cost adds directly to every party's phase latency.

## Contention shape

All same-tier arrivals CAS one word, so arrival storms (thousands of
parties, microsecond phases) contend exactly like an `AtomicLong` hammer.
Symptoms: CAS-retry spin visible in profiles, phase latency growing with
party count. Remedies in order: bulk registration, tiering
(`new Phaser(parent)`) to split the word, then fewer/smaller phases.

## Tiering guidance

Single-level suffices into the hundreds of parties per phase on modern
hardware. Tier when arrival-CAS retries dominate profiles: group workers
(e.g., 64–256 per child), one child per socket/NUMA node, root reconciling
children. Each level adds one hop of wakeup latency per phase, so depth 2
covers enormous counts — deeper trees need measured justification.

## onAdvance discipline

Keep it a branch on `(phase, parties)`: bounded counters, convergence
flags read from volatiles, nothing blocking, nothing allocating heavily.
A millisecond of override work at 10k phases costs 10 seconds of aggregate
party waiting — the multiplier is the party count.

## Benchmarking notes

Drive with JMH: fixed party counts (4/16/128/1024), phase body sizes
(empty vs 10 us work), and mixed arrive/await shapes. Report per-phase
latency distribution (p50/p99), not just throughput — barrier pathologies
hide in tails. Compare against `CyclicBarrier` (fixed gang) and
`CountDownLatch`-per-iteration baselines on identical bodies so the
dynamic-membership premium is explicit.

## Long-run hygiene

Deregister retirees promptly: zombie parties inflate every future advance
(isTerminated checks, waiter scans) and hold references. For phased
services running weeks, track `getRegisteredParties()` as a metric and
alert on monotonic growth — it is the phaser analogue of a thread leak.
