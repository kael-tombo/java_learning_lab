# Architecture: The Three Reordering Layers

## Layer map

```
Java source: x = 1; r1 = y   ||   y = 1; r2 = x     (Dekker shape)
  v  LAYER 1: javac + JIT (hoisting, sinking, elimination; pinned by sync actions)
  v  LAYER 2: CPU execution (Tomasulo 1967: issue when ready, commit in order)
  v  LAYER 3: memory subsystem (store buffers, forwarding, invalidate queues)
Cache coherence: single-location order only  ==>  (0,0) observed
```

Snippet 3 proves by elimination that on x86 the anomaly lives in layer
3: identical bytecode, 1 ns of drain time, anomaly gone. Layers 1-2 are
exonerated on this platform for this shape — not absent in general.

## Layer 1: compiler (javac + JIT)

- Legal moves: loop-invariant hoisting (`while (!flag)` reads lifted —
  lab 03's volatility exhibit), common-subexpression elimination,
  dead-store removal, lock coarsening. Constraint: single-thread
  as-if-serial semantics plus hb edges at synchronization actions.
- Why it is innocent here: nothing can hoist across the volatile-flag
  rendezvous spins (opaque spinning calls pin order), and the racer
  bodies (`x = 1; r1 = y`) offer no intra-thread optimization anyway.
  The store;load pair survives compilation exactly as written.

## Layer 2: CPU out-of-order execution (Tomasulo, IBM 360/91, 1967)

- Reservation stations issue each operation when its operands are
  ready; the reorder buffer commits in program order, so single threads
  never observe the reshuffling. Independent loads/stores to different
  addresses freely overlap while a stall resolves.
- Why it is innocent here: the store and load touch different
  addresses with no dependency — OoO *could* overlap them, but overlap
  alone does not make the store invisible; the buffer does. On ARM,
  CPU-level reorderings join the mix (more pairs escape), which is why
  the same verdict needs real fences there.

## Layer 3: memory subsystem (the culprit on x86)

```
T1: x = 1 ──store buffer (FIFO, invisible)──> ... ──drain──> coherent cache
T1: r1 = y ──executes NOW──> reads 0 (T2's store still buffered)
(symmetric on T2)  ==>  r1 == r2 == 0, forbidden under SC
```

- Stores retire to a per-core FIFO before reaching coherent cache; the
  core's own later load to a *different* address executes immediately
  against stale cache. Both loads beat both stores out of the buffers.
- `parkNanos(1)` between store and load lets the FIFO drain: same
  instructions, zero anomalies. No compiler theory survives that
  experiment — only the buffer explains it.

## x86-TSO framing (Sewell et al., 2010; SPARC heritage)

Of the four pairs, x86 preserves LoadLoad, LoadStore, StoreStore and
frees exactly StoreLoad — the Dekker pair. Practical corollary used in
lab 03's snippet 4: plain message-passing (`data` then `flag`, both
plain) usually *passes* on x86 by accident (StoreStore preserved) while
Dekker on the same machine fails loudly. One preserved pair is the
whole difference between "works" and "fires."

## ARM/POWER framing (qualitative)

- AArch64: any pair may reorder; order comes from `LDAPR` (acquire),
  `STLR` (release), `DMB` (full). ARMv8 is multi-copy-atomic (a write
  visible to one core is visible to all) — unlike POWER.
- POWER: `sync` (full, cumulative) vs `lwsync` (lightweight); permits
  non-MCA propagation (IRIW observable in research litmus).
- Java mapping: volatile read/write lower to acquire/release plus full
  fences where JMM SC-for-volatiles demands; on x86 a volatile read is
  nearly free and a volatile write is an `XCHG`. Same verdicts,
  different machine code — lab 03 prices them.
