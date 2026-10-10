# Refactoring: TreeMap / TreeSet

## Smell 1: Manual rehash / rescan loops
- Before: hand-rolled index math or full scans around `java.util.TreeMap / java.util.TreeSet`.
- After: single `getEntry/put/fixAfterInsertion/fixAfterDeletion/getSuccessor` call; let color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1) do the positioning.
- Why: duplicates the JDK's tested path and usually gets identity is compareTo==0 (or comparator.compare==0), NOT equals() wrong.

## Smell 2: Copy-then-view confusion
- Before: `List<V> v = new ArrayList<>(map.values()); v.remove(x)` expecting
  map mutation (or vice versa).
- After: operate on `NavigableSubMap view classes` directly for live writes; copy only for
  snapshots.

## Smell 3: Mutable keys / inconsistent ordering
- Before: keys whose `hashCode/compareTo` change after insertion.
- After: immutable keys; comparator consistent with equals where possible.
- Note: identity is compareTo==0 (or comparator.compare==0), NOT equals(); floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n).

## Smell 4: Shared instance without a policy
- Before: static `java.util.TreeMap / java.util.TreeSet` touched by many threads.
- After: confine, wrap, or switch variant per unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them.

## Smell 5: Repeated growth on known loads
- Before: default constructor + 1M adds in a loop.
- After: presize once; compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first; iteration ascending via on-the-fly successor links; fail-fast via modCount.

## Checklist
- [ ] Keys immutable; null policy (live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view) respected.
- [ ] Iteration uses iterator remove/set, not collection remove.
- [ ] Capacity chosen from measurement, documented at construction.
