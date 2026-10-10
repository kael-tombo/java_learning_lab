# Refactoring: HashMap Internals

## Smell 1: Manual rehash / rescan loops
- Before: hand-rolled index math or full scans around `java.util.HashMap`.
- After: single `put(k,v)/get(k)/remove(k)` call; let spreader `h ^ (h >>> 16)` folds high bits down do the positioning.
- Why: duplicates the JDK's tested path and usually gets TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64 wrong.

## Smell 2: Copy-then-view confusion
- Before: `List<V> v = new ArrayList<>(map.values()); v.remove(x)` expecting
  map mutation (or vice versa).
- After: operate on `entrySet().iterator() EntryIterator` directly for live writes; copy only for
  snapshots.

## Smell 3: Mutable keys / inconsistent ordering
- Before: keys whose `hashCode/compareTo` change after insertion.
- After: immutable keys; comparator consistent with equals where possible.
- Note: TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64; TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties.

## Smell 4: Shared instance without a policy
- Before: static `java.util.HashMap` touched by many threads.
- After: confine, wrap, or switch variant per fail-fast via modCount, ConcurrentModificationException.

## Smell 5: Repeated growth on known loads
- Before: default constructor + 1M adds in a loop.
- After: presize once; resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0; default capacity 16, load factor 0.75.

## Checklist
- [ ] Keys immutable; null policy (null key allowed once, hash 0, bucket 0) respected.
- [ ] Iteration uses iterator remove/set, not collection remove.
- [ ] Capacity chosen from measurement, documented at construction.
