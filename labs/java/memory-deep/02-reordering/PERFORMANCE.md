# Performance: Reordering

## The cost question this lab answers

Reordering itself is free (it *is* the fast path: buffers, OoO issue,
hoisting exist to go faster). Ordering is what costs — and only the
fences you add. Snippet contrasts make the price list tangible before
lab 03 measures it precisely: plain Dekker pays nothing and races;
volatile Dekker pays per store and orders; locked Dekker pays
exclusion and serializes.

## Structural costs (x86; lab 03 measures them)

- Plain store;load pair: ~1 ns-class per operation, zero fences, race
  intact (~79% anomaly rate under rendezvous).
- Volatile pair: reads nearly free (~1.3 ns), stores fenced (~10 ns
  via `XCHG`) — the StoreLoad tax paid unconditionally per store for
  the 0/20000 verdict.
- Locked pair: uncontended enter/exit in the tens of ns; contended
  pairs serialize (throughput collapses to one pair at a time) for the
  same 0/20000 by a different mechanism.
- 1 ns drain: ~1 ns plus park call overhead per pair — buys a green
  run, guarantees nothing; the worst price/performance in the lab
  (paying without receiving the verdict).

## Why rates are not benchmarks

Anomaly percentages move with rendezvous tightness, core count,
frequency scaling, and power state — none of which is program cost.
Two machines reporting 79% vs 36% for snippet 1 are reporting
different overlap windows, not different code speeds. The portable
performance claims are fence counts (0/0/1 across plain/release/
volatile) and verdicts (nonzero/zero) — lab 03's ladder (plain ~1 ns,
release ~1.3-1.9 ns, volatile write ~10 ns) is where numbers become
quotable, as ratios within one JVM.

## Measurement discipline used here

- Fixed 20000 iterations per variant so rates compare within one
  machine; assertion bars at 1% (`bad > iters / 100`) and 0 hold at
  large margins rather than near them.
- Warm both paths in-JVM before comparing (frequency scaling dwarfs
  fence effects cold); compare within one JVM invocation so machine
  drift cannot confound ordering.
- Indexed traffic in timing-adjacent snippets defeats JIT elimination;
  the litmus drivers reuse daemon threads across rounds to exclude
  thread-creation cost from the anomaly measurement.

## Shipping guidance from the price list

- Two-flag mutual-observation protocols: pay volatile on both fields
  (fenced stores are the known, bounded tax) or serialize under one
  lock (known serialization cost). Never pay the drain (unbounded risk,
  zero guarantee) or release/acquire (pays something, still races at
  61-90%).
- Bulk handoff chains (message-passing, sequencing): pay
  release/acquire (snippet 4: intact over 50000 at a fraction of
  volatile cost) — the one shape where the cheaper mode's verdict is
  sufficient. Lab 03 details the ~8x per-store saving.
