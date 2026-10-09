# Build Your Own HashMap — Theoretical Foundation

## Core Concept

Designing a hash table forces every decision `java.util.HashMap` hides from
you: how buckets are stored, what happens on collision, when to grow, and how
deletion leaves (or doesn't leave) holes. Two families exist:

- **Separate chaining** — each bucket holds a list/tree (what HashMap does).
- **Open addressing** — everything lives *in* the array; collisions probe to
  another slot (what Python `dict` and Java's own `IdentityHashMap` do).

This lab builds an open-addressing map, because chaining hides the hard parts
inside a sub-structure while open addressing makes every one of them visible.

## The Five Decisions You Must Make

### 1. Hash normalization: fold to a table index

Raw `hashCode()` is any `int`. Table sizes are powers of two, so the index is
`h & (n - 1)` — which only uses the **low bits**. A poor `hashCode` that varies
only in high bits (`31*x` style multipliers often do) would collide
systematically. The JDK's fix, worth stealing:

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

XOR the high 16 bits into the low ones so *all* bits influence the index. Rule:
**never** use `& (n-1)` on a raw hash without spreading first.

### 2. Probe strategy on collision

- **Linear probing** `(i+1) % n` — best cache behavior (adjacent slots are one
  cache line), but suffers *clustering*: runs of occupied slots merge into
  bigger runs and probe times balloon.
- **Quadratic probing** `(i + i²/2) % n` — breaks clusters into small groups;
  needs care to guarantee a full-table probe sequence exists.
- **Double hashing** — two hash functions; theoretically uniform, two hash
  computations per probe, poor locality.

Linear probing's clustering is the trade you accept for speed; keeping the load
factor modest (below ~0.7) is what keeps runs short.

### 3. Load factor and growth trigger

`α = size / capacity`. Expected probes for a successful linear-probe lookup ≈
½(1 + 1/(1−α)); unsuccessful ≈ ½(1 + 1/(1−α)²). The numbers explode near 1:

| α | avg probes (hit) | avg probes (miss) |
|---|------|------|
| 0.5 | 1.5 | 2.5 |
| 0.7 | 1.9 | 6.3 |
| 0.9 | 5.6 | 52.6 |

This is why open addressing **must** cap α well below 1 (the JDK chaining map
tolerates α up to 0.75 before growing; pure open-addressing tables often use
0.5–0.7). Unlike chaining, a full open-addressing table cannot accept *any*
insert — there is no fallback structure.

### 4. Deletion: tombstones

With linear probing you can't simply null a slot on `remove` — a later probe
that reaches it would stop early and miss a key placed beyond it. Standard
solutions:

- **Tombstone** (DELETED marker): probes continue through it; it's reusable by
  the next insert. Downside: tombstones accumulate and degrade α.
- **Backward-shift deletion** (used by Robin Hood / Wikipedia's table): walk
  subsequent occupied slots backward to fill the hole, re-establishing the probe
  chain. No tombstones, more work per delete.

### 5. Growth policy

Grow (typically double) when α crosses the cap: rehash every live entry into a
bigger table. Cost is O(n) per grow, amortized O(1) per insert — exactly the
same amortization argument as ArrayList's array copy, but the copy is now
*n* hash-and-place operations instead of `arraycopy`.

## Why java.util.HashMap Chooses Chaining + Trees

Knowing what you *didn't* choose teaches the trade-offs:

- Chaining never needs tombstones (unlink is local), tolerates α > 1 (lists
  just get longer), and stores one entry per node regardless of table density.
- Open addressing wastes nothing on node headers but needs tombstones and hard
  α caps.
- HashMap additionally treeifies a bin after 8 entries (and table ≥ 64) so the
  pathological "all keys collide" case degrades from O(n) list scans to
  O(log n) tree walks — an escape hatch open addressing in its simplest form
  lacks.

`IdentityHashMap` (open addressing, linear probing) and `EnumMap` (flat array,
no hashing at all) show the JDK using the other approach when its constraints
(linear probe, fixed key domain) fit.

## Correctness Checklist for Your Implementation

1. **`hash & (n-1)` requires n a power of two** — and the spread step
   (`^ (h >>> 16)`) first.
2. **`get` and `remove` must use identical probe sequences**, and both must
   treat tombstones as "keep probing."
3. **Two keys equal by `equals` must have equal `hashCode`** — otherwise they
   probe differently and the map contains both (violating the Map contract).
4. **Null keys**: define it once (HashMap allows one, hash 0; open-addressing
   tables can allow null by hashing it to 0 uniformly).
5. **Iteration must skip empty *and* tombstoned slots.**
6. **Rehash must not re-apply the spread hash** incorrectly — store the
   normalized index or recompute from `hashCode()` consistently.

## Complexity (what your table should achieve)

| Operation | Average | Worst (pathological) |
|-----------|---------|----------------------|
| get / put / remove | O(1) | O(n) — everything collides |
| grow (amortized per insert) | O(1) | — |
| full iteration | O(capacity) | includes empty/tombstone slots |

The gap between column 1 and 2 is entirely determined by your hash spread, probe
strategy, and α cap — the three knobs this lab makes you turn.
