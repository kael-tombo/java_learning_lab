# Internals: TreeMap / TreeSet

Source: `java.util.TreeMap`. Field-level behavior verified in CODE_DEEP_DIVE.md.

## Store layout
- red-black tree of Entry nodes (TreeSet = TreeMap<E,Boolean> with PRESENT sentinel).
- Size/capacity counters kept incrementally; iteration ascending via on-the-fly successor links; fail-fast via modCount.

## Position computation
- Rule: color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1).
- Thresholds: identity is compareTo==0 (or comparator.compare==0), NOT equals().

## Mutation mechanics
- Growth/rebalance: compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first.
- Slot hygiene: floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n).
- Null handling: live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view.

## Concurrency/visibility
- unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them.
- Hot path: getEntry/put/fixAfterInsertion/fixAfterDeletion/getSuccessor; views: NavigableSubMap view classes.

## Invariants (must hold after every public op)
1. Position rule (color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1)) resolves every live entry.
2. Size equals live-entry count; freed slots hold no stale refs.
3. Thresholds (identity is compareTo==0 (or comparator.compare==0), NOT equals()) trigger before the next op, never lazily skipped.
4. Growth (compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first) preserves all entries exactly once.
- Lab note (05-treemap-treeset/INTERNALS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/INTERNALS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/INTERNALS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/INTERNALS.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
