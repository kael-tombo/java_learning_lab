# How Open Addressing Works

## Normal lookup

Table n=8, keys A (index 1), B (index 1 → probes to 2), C (index 5).
`get(B)`: hash → 1, slot 1 holds A (not equals) → probe 2 → hit. Two
steps; clustering already visible (A and B share a run).

## Why deletion needs tombstones

`remove(A)` cannot null slot 1: `get(B)` probes 1 → EMPTY → "miss" — but B
sits at 2. Wrong answer. So slot 1 becomes DELETED: `get(B)` walks
1 (tombstone, continue) → 2 (hit). Correctness preserved; slot 1 is
reusable by the next insert.

## Why tombstones count toward load factor

A table with 8 live entries and 8 tombstones in n=16 probes like a full
table even though `size/n = 0.5`. The resize trigger must use
`(size + tombstones)/n`, and resize drops tombstones — that cleanup is
half the point of growing.

## Hash spreading in action

`String`-like hashes varying only in high bits: without `^ (h >>> 16)`,
`h & 7` collides systematically (low bits identical). XOR-folding mixes
high-bit entropy down where the mask can see it. One line, and the
difference between 1.5 and 50 probes at α=0.7+.

## Resize: rebuild, not copy

Doubling is not `arraycopy`: every live key is re-hashed into the new
mask (`h & 15` vs `h & 7` changes most positions). Entries redistribute;
runs dissolve; tombstones vanish. Cost O(n), amortized O(1) per insert
across the growth doubling sequence.
