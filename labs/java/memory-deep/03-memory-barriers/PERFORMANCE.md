# Performance: Memory Barriers

## The ladder (measured x86-64, ratios portable, absolutes not)

```
plain store:      ~1.0-1.2 ns   (0 hardware fences; snippet 1)
release store:    ~1.3-1.4 ns   (compiler barrier only; snippet 3, rock-stable)
volatile store:   ~10-18 ns     (XCHG StoreLoad fence; snippet 1, >3x plain)
plain read:       ~0.9-2.2 ns   (snippet 2)
volatile read:    ~1.0-1.4 ns   (acquire nearly free on TSO; snippet 2, <5x)
ladder shape:     plain <= release < volatile (writes); reads ~= parity
```

Fence counts (0/0/1) predict the shape on every x86; ARM64 keeps the
ordering with a hotter price list (STLR vs DMB). Quote the shape and
the ratios — never the nanoseconds — outside this machine.

## What each row purchases (price vs verdict)

- ~1 ns plain: no verdict (Dekker 61-90%-class races; MP accident
  0/2000 signifying nothing). The control row: speed of unsoundness.
- ~+0.3-0.9 ns release over plain: pairwise chains (lab 02 snippet 4:
  50000 intact) — sequencing, pipelines, Disruptor-style handoff at
  near-plain cost. Insufficient for Dekker (snippet 5: 61-90%).
- ~+9 ns volatile-store over plain: total order over the volatile
  chain (Dekker 0/20000 everywhere) — mutual observation, guarding
  flags, DCL publication (lab 05's idiom). Paid per store,
  unconditionally, contended or not.
- ~+0.3 ns volatile-read over plain: ordered observation (LoadLoad +
  LoadStore after) at noise cost — read freely, publish rarely is the
  rational response on TSO.

## Measurement discipline (the harness contract)

- Warm both paths 2M ops in the same JVM, measure 20M back-to-back —
  frequency scaling and TieredCompilation settle inside the warmup, and
  drift cancels across adjacent windows.
- Indexed 1024-slot traffic (4 KB, L1-resident): defeats
  store-coalescing, load-commoning, and dead-store elimination; prices
  fences plus L1 hits, not DRAM or registers.
- Ratio assertions (`>3x`, `<5x`) with `max(..., 0.2)` floors: robust
  to coarse timers and turbo variance; absolute assertions would be
  machine fiction.
- Quiet box, fixed iterations, all counts reported (3 runs each):
  the snippets' numbers are reproducible *shapes*, not constants.

## Cost-avoidance rules that survive review

- Publish bulk state through one release/volatile reference, not per
  element: one fence per graph instead of one per field (the latch and
  volatile-reference patterns from lab 01, priced here).
- Prefer `lazySet`/`setRelease` for sequence advancement (chains
  suffice — ~8x saving per store); escalate to `set`/volatile only
  where the consumer observes mutually with another producer.
- Never spin on plain flags to "save" a fence: a burned core at full
  power dwarfs any fence saving within microseconds, and the spin
  itself may never observe the write (lab 01 mistake 1, priced in
  watts here).
- Read-heavy guard patterns (DCL, memoization) are the best trade in
  the building: fence paid once per publish, free ordered reads
  forever after — lab 05 quantifies the amortization.

## Scaling notes

Uncontended fences scale linearly (per-op tax, no interaction);
contended volatile stores serialize at the cache line (coherence
traffic multiplies the single-thread ladder); contended locks leave
the ladder entirely (scheduling dominates). Choose striped/atomics
where the ladder's per-op tax is fine but the lock's serialization is
not — the hb story unchanged, the coherence bill split.
