# Common Mistakes: Memory Barriers

## 1. Trusting accidental green (plain MP 0/2000)

Snippet 4 passes 2000 rounds on x86 (StoreStore preserved + coherence)
and guarantees nothing: the compiler may hoist the `data` read above
the spin, ARM may reorder the stores, and the JMM verdict is `race`
regardless. Green here, red elsewhere, undefined per spec. Convert to
volatile/latch and change the verdict while the output stays put.

## 2. Release/acquire as SC-lite for Dekker

`setRelease`/`getAcquire` on both Dekker sides still prints 61-90%
anomalies (snippet 5) — on x86 both compile to bare MOVs, ordering
nothing system-wide. Each pair chains correctly (my-release to
your-acquire) while the cross pair slips through. Only StoreLoad on
both sides (full volatile) or exclusion closes it. Match the mode to
the shape: chains for handoff, SC or lock for mutual observation.

## 3. Paying volatile for release jobs

Publishing sequence steps through `set` (volatile, ~10 ns) where
`lazySet` (release, ~1.3 ns) chains suffice burns ~8x per store for
ordering no consumer needs (snippet 3). The Disruptor-style pattern
(lab 02 snippet 4: 50000-intact chain) is the canonical release job:
one-directional, pairwise-consumed, fence-free on x86. Reserve the SC
fence for total-order shapes.

## 4. Assuming reads cost like writes

The barrier tax is directional on TSO: writes fence (~10 ns volatile
stores), reads (nearly) do not (~1.3 ns volatile reads, snippet 2).
Blanket "volatile is slow" reasoning either over-fences reads (free
performance left out) or under-fences stores (Dekker-shaped holes).
Read the ladder directionally: publish rarely, read freely.

## 5. Quoting absolutes across machines

~10 ns volatile stores here are ~18 ns elsewhere (frequency scaling,
microarchitecture): snippet absolutes are illustration, ratios
(>3x write fence, <5x read parity, >3x release saving) and verdicts
(zero vs nonzero) are the claims. Tests assert ratios exactly for this
reason (`volNs > plainNs * 3`, never `volNs > 5.0`).

## 6. Forgetting warmup inside the measurement

First-run frequency scaling dwarfs fence effects; cold comparisons
attribute turbo transitions to barriers. Snippets 1-3 warm both paths
(2M ops) in-JVM before measuring 20M — copy the harness, including
indexed slots (distinct locations per iteration) that defeat JIT
elimination. A loop over one location measures register allocation,
not memory ordering.

## 7. Opaque for publication (or plain for "cheap opaque")

`getOpaque`/`setOpaque` give atomicity plus eventual visibility with
*zero* ordering edges: progress counters and statistics only. Using
opaque for a flag guarding data reopens snippet 4's race with fancier
spelling; using plain for 64-bit counters reopens tearing on top.
Three rungs, three jobs: plain (racy, tearable), opaque (atomic,
unordered), release/acquire+ (ordered). Climb deliberately.

## 8. Fencing by hand through Unsafe

`loadFence`/`storeFence`/`fullFence` exist for library internals (AQS,
atomic classes), not application ordering — hand-placed fences carry
no JMM verdict and no portability (ARM needs different placement than
x86). Application code orders through volatile, monitors, latches, and
VarHandle modes; the JIT places the fences, the JMM guarantees them.
