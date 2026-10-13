# Reordering — Theoretical Foundation

## Core Concept

Your program's source order is a *suggestion*. The JIT compiler reorders
operations (hoisting, sinking, elimination) within as-if-serial freedom;
the CPU executes out of order (Tomasulo, 1967: reservation stations issue
when operands are ready, reorder buffer commits in order) and buffers
stores invisibly. What you observe is constrained only by the JMM's edges
(lab 01) — everything else is free to move, and on real hardware it does
(this lab measures it: ~79% anomaly rate on the Dekker litmus).

## The Three Reordering Layers

1. **Compiler (javac + JIT)**: loop-invariant hoisting (`while (!flag)`
   reads lifted out of the loop — lab 03 volatile-semantics snippet 1
   *is* this phenomenon), common-subexpression elimination, dead-store
   removal, lock coarsening. Constraint: single-thread as-if-serial
   semantics (plus hb edges for synchronization actions).
2. **CPU execution**: out-of-order issue around stalls (cache misses hide
   behind independent work); commit stays in order, so single-threaded
   code never observes it. Multi-threaded code observes it through shared
   memory.
3. **Memory subsystem**: store buffers (writes retire to a per-core FIFO
   before reaching coherent cache — the Dekker mechanism), store-to-load
   forwarding (a core reads its *own* pending store early), invalidate
   queues (deferred coherence acknowledgments). These make *other cores'*
   writes appear late and out of order.

## x86-TSO: Only StoreLoad Escapes (Sewell et al., 2010)

x86 implements Total Store Order (SPARC heritage, formalized for x86 by
Sewell–Sarkar–Owens–Nardelli–Myreen): of the four order pairs, three are
preserved — LoadLoad, LoadStore, StoreStore — and exactly one is free:

- **StoreLoad may reorder**: a store followed by a load to a *different*
  address can appear swapped (store sits in the buffer while the load
  executes). This is the *only* hardware reordering on x86 — and it
  suffices for the Dekker anomaly (snippet 1).
- Loads never pass loads; stores never pass stores (to coherent memory).

Practical reading: on x86, message-passing (`data` then `flag`, both
plain) usually *works by accident* (StoreStore preserved) — and Dekker
(`flag` then read-other) fails loudly. "Works on x86" is one preserved
pair away from broken; ARM breaks both halves (next section).

## ARM/POWER: Weak Ordering (qualitative)

- **AArch64**: any pair may reorder in principle; ordering comes from
  explicit instructions — `DMB` (full barrier), one-way `LDAPR` (acquire)
  / `STLR` (release). ARMv8 is multi-copy-atomic (a write becomes visible
  to all cores at once once visible to any) — unlike POWER, which permits
  non-MCA propagation (cumulativity subtleties: IRIW observable on POWER,
  forbidden on ARMv8/x86).
- **POWER**: `sync` (full, cumulative) vs `lwsync` (lightweight); the
  weakest shipping model — litmus tests (IRIW, WRC) distinguish it in
  research literature, not in application code.
- **Java's mapping**: `volatile` read/write compile to acquire/release
  (`LDAPR`/`STLR` on ARM64) plus full fences where the JMM demands
  sequential consistency for the volatile chain (`DMB`); on x86 a volatile
  read is nearly free and a volatile write is an `XCHG` (implicit `lock`
  prefix = StoreLoad fence). Same JMM, different machine code per
  architecture — which is why volatile costs are platform-relative (lab 03
  THEORY).

## What the JVM Emits (and Doesn't Expose)

- No user-level fence intrinsics in `java.*` — ordering comes from
  `volatile`, monitors, `final`, and `VarHandle` modes
  (`getAcquire`/`setRelease`/`getOpaque`, lab 03 table).
- `Unsafe` (`jdk.internal.misc`) has `loadFence`/`storeFence`/`fullFence`
  — library-internals only (AQS, StampedLock's `validate`, atomic classes
  use them; application code must not).
- The JIT *inserts* barriers at synchronization actions and is *forbidden*
  from moving memory operations across them (compiler-side of the same
  contract the CPU honors in hardware).

## Dekker, Explained by the Layers

```
T1: x = 1 ──store buffer──▶ ... ──drain──▶ coherent cache
T1: r1 = y ──executes NOW──▶ reads stale 0 (T2's store still buffered)
(symmetric on T2)  ⇒  r1 == r2 == 0, forbidden under SC
```

Compiler uninvolved (no hoisting possible across the volatile rendezvous
spins — opaque calls pin the order); CPU OoO uninvolved (loads/stores to
different addresses, no dependency); the *store buffer* alone produces the
anomaly. Snippet 3 proves it by elimination: identical bytecode, 1 ns
drain delay, anomaly vanishes.

## Key Invariants

1. On x86, StoreLoad is the only hardware-reordered pair; Dekker is its
   signature.
2. Compiler reordering respects as-if-serial + hb; hardware reordering
   respects TSO (x86) or explicit barriers (ARM/POWER).
3. `volatile` (and stronger) forbids the anomaly on every platform —
   same source, portable ordering.
4. Timing changes (delays, scheduling) alter anomaly *rates*, never the
   *forbidden/allowed* verdict — the JMM rules the verdict.
5. Demonstrating an anomaly needs rendezvous (aligned windows); free
   running or barrier phasing hides it (this lab's probe history).
