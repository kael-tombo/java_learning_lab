# TreeMap / TreeSet Deep Dive — Theoretical Foundation

## Core Concept

`TreeMap<K,V>` is a **red-black tree** of `Entry` nodes implementing `SortedMap`/
`NavigableMap`; `TreeSet<E>` is a `TreeMap<E, Boolean>` under the hood (the value
is a shared `PRESENT` sentinel). Red-black coloring is literal in the source:

```java
private static final boolean RED   = false;
private static final boolean BLACK = true;
```

Self-balancing guarantees **O(log n)** for get/put/remove — the guarantee HashMap
can't make under adversarial hashes, at the price of losing O(1) and iteration
order.

## Ordering: Where the Comparator Comes From

Three sources, resolved in order:

1. Constructor-supplied `Comparator` — used if present (the `getEntryUsingComparator`
   fast path exists purely so the field check happens once, not per node).
2. Else `Comparable<? super K>` — keys **must** implement `Comparable`; casting
   happens once at the root and each `compareTo` is on the declared type.
3. Neither → `ClassCastException` at first operation.

**Null keys are rejected** when ordering by natural comparison — `compare(key,
key)` is called on an *empty* map specifically to trigger the type/null check
before anything is inserted (`addEntryToEmptyMap` does this as its first act).
A custom comparator *may* permit nulls; the map itself never blocks them if the
comparator handles them. TreeSet inherits the same rule.

This differs from HashMap (one null key allowed, hashed to bucket 0) and from
ConcurrentHashMap (nulls banned outright).

## Lookup Is a Binary Search Tree Walk

```java
Entry<K,V> p = root;
while (p != null) {
    int cmp = k.compareTo(p.key);
    if (cmp < 0)      p = p.left;
    else if (cmp > 0) p = p.right;
    else              return p;     // equality via compareTo == 0, NOT equals()
}
return null;
```

**Key subtlety**: identity in a TreeMap is `compareTo(...) == 0` (or
`comparator.compare(...) == 0`), *not* `equals()`. A TreeSet built with a
case-insensitive comparator treats `"a"` and `"A"` as the same element — adding
the second is a silent no-return, and `equals` can disagree with the set's own
`contains`. This is a documented wart of the whole SortedSet family.

## Complexity and Why It Beats HashMap on Range Queries

| Operation | TreeMap | HashMap |
|-----------|---------|---------|
| get / put / remove | O(log n) | O(1) expected |
| firstKey / lastKey | O(log n) | O(n) — full scan |
| range query subMap(k1,k2) | O(log n + k) | O(n) to sort |
| iteration in key order | O(n) after O(log n) leftmost find | O(n) **unordered** |
| memory per entry | ~48 B (3 refs + key + val + boolean) | node ~32 B + array slot |

`firstKey` doesn't scan: it walks `left` pointers from the root — one descent,
O(log n). The whole point of the ordering is that *sorted access is native*.

## Red-Black Invariants (the four rules)

1. Every node is red or black.
2. The root is black.
3. Every leaf (`null` child) is black.
4. Red nodes never have red children (no two reds in a row).
5. Every path from root to a leaf has the same black count.

Rules 4+5 together bound the tree height to **≤ 2·log₂(n+1)** — that's the
entire reason O(log n) holds even in the worst case. The rebalancing after
insert/remove (`fixAfterInsertion`/`fixAfterDeletion`) does rotations plus color
flips; the classic result is **at most 2 rotations per insertion** and **at most
3 per deletion**, so balancing is cheap relative to the search that found the
position.

## Range Views Are Live, Not Copies

`headMap`, `tailMap`, `subMap` return **views**: mutations through the view
mutate the backing tree, and vice versa. They compose (`subMap(a,true,b,false)
.tailMap(c)`), which is how you express arbitrary intervals. The bounds are
checked against the *parent's* bounds at call time — a view cannot escape its
creator's range.

## Iteration: Weakly Consistent via modCount

`keySet().iterator()` is fail-fast like the rest of Collections — captures
`modCount`, throws `ConcurrentModificationException` on structural drift. The
iterator walks the tree in ascending order using a `successor` link computed
on the fly (it does not materialize a sorted array first — iteration is
O(n) total with O(log n) worst-case per `next()` for the first successor find).

## Navigable Extras That Justify the Class

- `floorKey/ceilingKey/higherKey/lowerKey` — nearest-neighbor lookups in O(log n),
  impossible on HashMap without sorting everything.
- `pollFirstEntry` — removes-and-returns the minimum in O(log n): this is why
  TreeMap backs priority-queue-like workloads where you also need lookups by key.
- `descendingMap()` — a reversed *view*, no copy.

## TreeSet-Specific Notes

- `add` returns false when an equivalent key exists (`compareTo == 0`), silently —
  no exception, no overwrite (unlike `put` on TreeMap, which replaces the value).
- Set algebra (`addAll`, `retainAll`, `removeAll`) on TreeSet is O(m·log n)
  for m = size of argument — versus O(n) HashSet union. Small n favors HashSet;
  large n with sorted iteration favors TreeSet.

## Key Invariants

1. Black-height (rule 5) is identical on every root-to-leaf path after every
   mutation — the balancing methods restore it before returning.
2. In-order traversal of the tree yields keys in ascending order; `firstKey`
   is the leftmost node, `lastKey` the rightmost.
3. Element identity is comparator-equivalence, which *may* disagree with
   `equals()` — never mix a TreeSet with code relying on `equals` semantics.
4. `size` is maintained incrementally (not recomputed), so `isEmpty()` is O(1).
