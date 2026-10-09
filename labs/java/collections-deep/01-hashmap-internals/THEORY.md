# HashMap Internals — Theoretical Foundation

## Core Concept

`java.util.HashMap` is a hash table with separate chaining that stores entries in a
`Node[] table` array. Each bucket is either a linked list of `Node` objects or, after
treeification, a small red-black tree. There is no ordering guarantee: iteration order
is unspecified and changes after resize.

## The put Path

```
put(key, value):
  1. if table == null -> resize()          // lazy allocation, starts at 16
  2. i = (h = spread(key.hashCode())) & (n - 1)
  3. if table[i] == null -> new Node linked directly
  4. else walk the bucket:
       - exact same key (hash equal && (== || equals)) -> replace, return old value
       - else append to list or tree; if bucket is a TreeifyBin, call putTreeVal
  5. if (++size > threshold) -> resize()
```

Two properties make step 2 valid: capacity is **always a power of two**, so
`h & (n - 1)` is equivalent to `h mod n` without a division, and negative hash codes
stay correct because the mask keeps only the low bits.

## The Spread Function

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

XOR-ing the high 16 bits into the low 16 matters because the bucket index only uses
the lowest `log2(n)` bits. For the default capacity of 16, a key whose hash differs
only in bits 16+ would otherwise always land in the same bucket; spread mixes those
bits down so distribution survives small table sizes.

## Load Factor and Resizing

- Default load factor: **0.75**; default capacity: **16**.
- Threshold = capacity × load factor; resize doubles capacity when exceeded.
- Resize rehashes each node once: because new capacity = 2 × old, a node either stays
  at index `i` or moves to `i + oldCapacity` — decided by one bit:
  `(e.hash & oldCapacity) == 0`.
- Doubling keeps amortized insertion cost O(1): each element is rehashed at most
  log₂(N) times over its lifetime, giving amortized O(1) per put.

Resizing to a non-power-of-two capacity (via the `HashMap(int, float)` constructor)
sacrifices the single-mask trick; HashMap normalizes non-power-of-two capacities up
to the next power of two anyway.

## Treeification (Java 8+)

When a bucket's list grows past **TREEIFY_THRESHOLD = 8** *and* the table has at
least **64** nodes, the list converts to a red-black tree (`TreeBin`), changing worst
case from O(n) to O(log n) per bucket.

- If the table is smaller than 64, HashMap **resizes first** instead of treeifying —
  small tables usually indicate a bad hash or too few buckets, not adversarial input.
- On **deletion**, the bin converts back to a list when the remaining tree gets
  structurally shallow — the JDK tests `root.right == null || root.left == null ||
  root.left.left == null` after unlinking. This is a depth heuristic, not a node
  count: a bin that untreeifies at 4 remaining nodes could survive at 5 depending
  on shape.
- On **resize**, a tree bin is split into two halves; each half with
  **UNTREEIFY_THRESHOLD = 6** or fewer nodes becomes a plain list again.
- Tree nodes keep their pre-spread `hash` and order by it, falling back to
  `Comparable` and finally `tieBreakOrder` (class name, then identity hash code)
  when hashes tie — so no ordering ever depends on calling `hashCode()` repeatedly
  during a lookup, and equal-hash keys still form a deterministic tree.

The tree path exists to defend against hash-flooding: an attacker who controls keys
and can force collisions (e.g. strings crafted to the same low bits) cannot push a
lookup past O(log n).

## Null Keys and Values

HashMap permits exactly one null key, hashed to bucket 0 (`hash(null) == 0`), and
unlimited null values. `get(null)` and `containsKey(null)` route through the same
bucket-0 path. This differs from `ConcurrentHashMap`, which rejects null keys and
values outright — in a concurrent map, `null` cannot distinguish "absent" from
"mapped to null", so the ambiguity was deliberately banned.

## Views: keySet, values, entrySet

All three are *views*, not copies: they share the backing table, and `values.remove(o)`
scans buckets calling `o.equals(value)`. `entrySet().iterator()` returns
`EntryIterator` whose `next()` wraps each node in a `Map.Entry` that writes straight
back into the table on `setValue` — so mutating through the view mutates the map.

## Failure Semantics

Iterators are **fail-fast**: each iterator remembers the modCount at creation and
throws `ConcurrentModificationException` on `next()` if the count drifted (checked
once per `next()`, not continuously). This is a best-effort heuristic, not a
guarantee — concurrent modification may go undetected if it happens not to bump the
counter the iterator observed. For real concurrency, use `ConcurrentHashMap`.

## Complexity Summary

| Operation | Average | Worst (pre-treeify) | Worst (treeified) |
|-----------|---------|---------------------|-------------------|
| get / containsKey | O(1) | O(n) | O(log n) |
| put | O(1) amortized | O(n) | O(log n) |
| remove | O(1) | O(n) | O(log n) |
| iteration over all N | O(N) | O(N) | O(N) |

## Key Invariants

1. Capacity is always a power of two; size ≤ threshold after every completed put.
2. Every node's bucket index equals `(node.hash & (table.length - 1))` — resize
   re-establishes this for all nodes.
3. `size` counts entries, not buckets; a table can have size > 0 with many empty
   buckets if hashes cluster.
4. `modCount` increments on structural changes (add/remove/rehash), not on value
   replacement of an existing key.
