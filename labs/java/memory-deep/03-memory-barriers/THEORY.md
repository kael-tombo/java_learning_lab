# Memory Barriers — Theoretical Foundation

## Core Concept

A memory barrier (fence) forbids a *class* of reorderings across a point
in the instruction stream. The JMM's edges (lab 01) *are* barrier
requirements: every happens-before rule compiles to "emit this barrier
here" (compiler + CPU). Four barrier types (Doug Lea's JSR-133 cookbook
vocabulary) cover the four operation pairs:

| Barrier | Forbids | JMM job |
|---|---|---|
| LoadLoad | load → later load reorder | volatile/acquire reads see ordered data |
| LoadStore | load → later store reorder | reads complete before subsequent publishes |
| StoreStore | store → later store reorder | publication order (data before flag) |
| StoreLoad | store → later load reorder | the expensive one: full fence, Dekker safety |

Acquire (volatile read, monitor entry, `getAcquire`) = LoadLoad + LoadStore
after the operation. Release (volatile write, monitor exit, `setRelease`) =
LoadStore + StoreStore before it. Sequential consistency for volatiles adds
StoreLoad *after* each volatile store — the single most expensive barrier,
and the one Dekker needs on both sides.

## Roach Motel Semantics (the one-paragraph version)

Plain operations drift *into* synchronization regions, never *out*:

- **Acquire** (`monitorenter`, volatile read, `getAcquire`): subsequent
  operations cannot move *before* it — but preceding plain operations MAY
  move *after* it, into the region from above.
- **Release** (`monitorexit`, volatile write, `setRelease`): preceding
  operations cannot move *after* it — but following plain operations MAY
  move *before* it, into the region from below.

Net: the motel (locked region, volatile op neighborhood) admits plain
traffic from both sides and releases none early. "Check in, never check
out" — which is why publication (`data` before `flag`) is safe but
observation-after-the-fact is not ordered.

## x86 Mapping (measured in this lab)

- Volatile/plain **reads**: ~1 ns both (measured 1.0–1.4 vs 0.9–2.2) —
  acquire on TSO is nearly free (no fence instruction; compiler barrier
  only).
- Plain **stores**: ~1 ns (measured 1.0–1.2, array slots).
- Release (`lazySet`) stores: ~1.3–1.4 ns (measured, rock-stable) —
  compiler barrier only on x86, no hardware fence.
- Volatile **stores**: ~10–18 ns (measured 9.6–18.5) — `XCHG` (implicit
  `lock` prefix = StoreLoad fence). The ~8x tax is one instruction's
  pipeline flush, not a syscall.
- The ladder plain ≤ release < volatile holds structurally on x86
  (fence count 0/0/1); only the volatile step emits hardware ordering.

ARM64 differs in degree, not kind: `STLR` (release store) is cheaper than
a full `DMB`-fenced store, `LDAPR` (acquire load) cheap like x86 reads —
same taxonomy, different price list (lab 02 THEORY).

## Why Release/Acquire Doesn't Fix Dekker (snippet 5's lesson)

Dekker needs a *total* order over the four operations (each side must see
the other's store). Release/acquire gives *pairwise* chains (my release →
your acquire), and chains don't compose into a total order across two
independent pairs — the two release/acquire pairs each order locally while
the cross pair still slips through the store buffers. Only StoreLoad on
both sides (full `volatile`, or locks) restores the total order. Measured:
61–90% anomaly rate under release/acquire — indistinguishable from plain.

## Opaque: Atomicity Without Ordering

`VarHandle.getOpaque/setOpaque`: atomic access, eventual visibility, *zero*
ordering edges — weaker than release/acquire, stronger than plain (which
additionally permits tearing on 64-bit and indefinite staleness). Use for
progress counters and statistics where any value is fine and order is
meaningless. Never for publication, never for flags guarding data.

## Key Invariants

1. Acquire = LoadLoad+LoadStore after; Release = LoadStore+StoreStore
   before; SC adds StoreLoad after volatile stores.
2. Plain ops check into sync regions from both sides, never out (roach
   motel).
3. On x86: reads ~free, plain/release stores ~1 ns, volatile stores ~10 ns
   (fence count decides).
4. Release/acquire chains order pairs, not systems — Dekker still fires.
5. Opaque = atomic + eventually visible + unordered; publication needs
   release or stronger.
