# How It Works: TreeMap / TreeSet

`java.util.TreeMap / java.util.TreeSet` is a red-black tree of Entry nodes (TreeSet = TreeMap<E,Boolean> with PRESENT sentinel).

## Lookup
1. Compute position per color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1).
2. Walk the local structure (chain / links / tree descent) using the
   identity rule in identity is compareTo==0 (or comparator.compare==0), NOT equals().
3. Return the entry or null/absent per live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view.

## Insert
1. Resolve position; handle the empty-store fast path (iteration ascending via on-the-fly successor links; fail-fast via modCount).
2. Splice/link/rotate the node in; update size.
3. Run growth/rebalance work (compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first) when its threshold trips.

## Remove
1. Locate as in lookup; unlink and patch neighbors/parents.
2. Clear the freed slot or rebalance (floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)).
3. Views (NavigableSubMap view classes) observe the removal immediately.

## Iteration
- Order follows the structure (insertion-neutral, index order, or sorted),
  and unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them.

## Worked trace
- Insert 3 small keys: store allocates per iteration ascending via on-the-fly successor links; fail-fast via modCount, each key resolves via
  color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1), size becomes 3, no growth yet (compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first not tripped).
- Core calls exercised: getEntry/put/fixAfterInsertion/fixAfterDeletion/getSuccessor.
- Lab note (05-treemap-treeset/HOW_IT_WORKS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/HOW_IT_WORKS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
