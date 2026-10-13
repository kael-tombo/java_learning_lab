# Architecture: From HB Edges to Fences to Silicon

## The lowering pipeline

```
JMM edge (hb rule: volatile, monitor, latch...)
  v  barrier plan (cookbook: which of LL/LS/SS/SL, which side)
  v  JIT emission (compiler barrier + platform fence instruction selection)
  v  silicon (x86 XCHG/MOV / ARM64 LDAPR/STLR/DMB / POWER lwsync/sync)
  ==> verdict (ordered) at the ladder price
```

Same edge, different machine code per platform; same verdicts
everywhere. The taxonomy is the portable layer — prices are local.

## The taxonomy (Doug Lea's JSR-133 cookbook vocabulary)

| Barrier | Forbids | JMM job in this lab |
|---|---|---|
| LoadLoad | load passing an earlier load | volatile/acquire reads see ordered data (snippet 2's reads) |
| LoadStore | store passing an earlier load | reads complete before subsequent publishes |
| StoreStore | store passing an earlier store | publication order: `data` before `flag` (snippet 4's accident) |
| StoreLoad | load passing an earlier store | full fence: Dekker safety (snippets 1/5's expensive row) |

Acquire (volatile read, monitor entry, `getAcquire`) = LoadLoad +
LoadStore *after* the operation. Release (volatile write, monitor
exit, `setRelease`) = LoadStore + StoreStore *before* it. Sequential
consistency for volatiles adds StoreLoad *after* each volatile store —
the single most expensive barrier and the one Dekker needs on both
sides. Fence counts across plain/release/volatile: 0/0/1 on x86 — the
structural reason the ladder has exactly one big step.

## x86 lowering (what the demos measure)

- Plain/read paths: plain MOVs both sides — acquire on TSO needs no
  fence instruction (compiler barrier only), so volatile reads land at
  ~1.3 ns vs plain ~1.0 ns (snippet 2: within 5x, effectively noise).
- Release stores (`lazySet`): compiler-barrier-only stores, ~1.3-1.4 ns
  rock-stable (snippet 3) — publication order without the system fence.
- Volatile stores (`set`): `XCHG` with implicit `lock` prefix =
  StoreLoad fence, ~10-18 ns measured (snippet 1: >3x plain, ~8-10x in
  practice) — the pipeline flush priced per store, unconditionally.
- The ladder plain <= release < volatile holds structurally (fence
  count 0/0/1); only the volatile step emits hardware ordering, which
  is why only it closes Dekker.

## ARM64 / POWER lowering (same taxonomy, different price list)

- ARM64: `STLR` (release store) cheaper than a `DMB`-fenced store,
  `LDAPR` (acquire load) cheap like x86 reads — release/acquire chains
  (lab 02 snippet 4) stay economical; SC-for-volatiles still pays full
  fencing where Dekker demands it.
- POWER: `lwsync` (lightweight, pairwise) vs `sync` (full, cumulative)
  — the same pair-vs-system distinction snippet 5 exhibits, cast in
  hardware instructions at the weakest setting.
- Java's mapping choice (acquire/release primitives plus fenced
  volatiles) is precisely the decision to expose both price points
  instead of fencing everything.

## Roach-motel placement (where fences sit)

Acquire fences sit *after* the operation (subsequent ops cannot move
before it; preceding plain ops may drift in from above). Release fences
sit *before* it (preceding ops cannot move after it; following plain
ops may drift in from below). The motel admits plain traffic from both
sides and releases none early — publication (`data` before `flag`)
safe, post-hoc observation unordered. Snippet 4's plain pair has no
motel at all: both operations wander, and x86's preserved StoreStore
happens to walk them in order — this time.
