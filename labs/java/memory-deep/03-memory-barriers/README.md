# Memory Barriers — README

Happens-before edges (lab 01) *are* barrier requirements: every rule
compiles to "emit this fence here" (compiler plus CPU). This lab opens
that lowering: the four barrier types, the acquire/release/SC assembly
from them, the roach-motel movement rule, the measured x86 price
ladder, and the two boundary exhibits — plain message-passing that
passes by accident (0/2000, still a race) and release/acquire Dekker
that races at 61-90%.

## What you will learn

- The JSR-133 cookbook taxonomy: LoadLoad, LoadStore, StoreStore,
  StoreLoad — which pair each forbids and which JMM job it serves.
- Acquire = LoadLoad + LoadStore *after*; release = LoadStore +
  StoreStore *before*; sequential consistency adds StoreLoad *after*
  each volatile store (the expensive one, the Dekker fence).
- Roach-motel movement: plain operations drift *into* sync regions,
  never *out* — publication safe, after-the-fact observation unordered.
- The measured x86 ladder: plain ~1 ns, release ~1.3-1.9 ns, volatile
  write ~10 ns, volatile read ~1.3 ns (ratios within one JVM; absolutes
  vary, fence counts do not).
- `lazySet` (release) vs `set` (volatile): same eventual visibility
  class, ~8x price gap, different ordering contract.
- Opaque: atomic plus eventually visible plus *unordered* — counters
  and statistics only, never publication, never flags.
- Why release/acquire chains order pairs but not systems (Dekker still
  fires), and why accidental green (plain MP 0/2000) means nothing.

## The five runnable demos (JDK 9+, verified on JDK 23, x86-64)

| # | Class | Comparison | Verdict |
|---|-------|-----------|---------|
| 1 | `WriteFenceCost` | plain vs volatile stores, 20M | `volatile > 3x plain: true` (~1 ns vs ~10 ns) |
| 2 | `ReadCheap` | plain vs volatile reads, 20M | `volatile < 5x plain: true` (~1.0 vs ~1.3 ns) |
| 3 | `ReleaseCheaper` | `set` vs `lazySet`, 20M | `>3x cheaper: true` (~10 ns vs ~1.3 ns) |
| 4 | `AccidentalCorrect` | plain message-passing, 2000 rounds | `0/2000`, AND verdict still `race` |
| 5 | `RaDekker` | release/acquire Dekker, 20000 | anomalies persist (`bad > iters/100: true`, 61-90%) |

Timing snippets compare within one JVM (warm both paths, then measure)
with indexed traffic defeating JIT elimination — machine drift cannot
confound the ordering, and ratios port while nanoseconds do not.

## How to work this lab

1. Read `THEORY.md` (taxonomy table, roach motel, x86 mapping with the
   ladder, why release/acquire fails Dekker, opaque).
2. Read `CODE_DEEP_DIVE.md` with sources; note the harness pattern
   (warmup, indexed slots, in-JVM comparison, ratio assertions).
3. Run 1-3 and record your machine's three ratios; run 4-5 and record
   the two verdicts (accidental zero, persistent nonzero).
4. Do `EXERCISES.md`: rebuild the ladder yourself, convert snippet 4
   to volatile/latch and feel nothing change in output while everything
   changes in verdict, convert snippet 5 to volatile/lock and watch
   61-90% fall to zero.
5. Finish with `QUIZ.md`, `INTERVIEW.md`, `REFLECTION.md`.

## Where this fits

- Previous: `01-jmm-foundations` (edges as contract), `02-reordering`
  (StoreLoad anomaly as motive).
- Next: `04-final-semantics` (freeze edge as barrier case study),
  `05-dcl-pattern` (volatile publication as the idiom this ladder
  prices).
- Carry forward: the taxonomy table, the ladder, and the sentence
  "chains order pairs, not systems."
