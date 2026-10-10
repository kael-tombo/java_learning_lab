# Refactoring: ConcurrentHashMap

## Smell 1: Manual rehash / rescan loops
- Before: hand-rolled index math or full scans around `java.util.concurrent.ConcurrentHashMap`.
- After: single `putVal/merge/compute/putIfAbsent` call; let putVal rejects null key/value with NullPointerException do the positioning.
- Why: duplicates the JDK's tested path and usually gets spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative wrong.

## Smell 2: Copy-then-view confusion
- Before: `List<V> v = new ArrayList<>(map.values()); v.remove(x)` expecting
  map mutation (or vice versa).
- After: operate on `weakly-consistent iterators (never throw CME)` directly for live writes; copy only for
  snapshots.

## Smell 3: Mutable keys / inconsistent ordering
- Before: keys whose `hashCode/compareTo` change after insertion.
- After: immutable keys; comparator consistent with equals where possible.
- Note: spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative; TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap.

## Smell 4: Shared instance without a policy
- Before: static `java.util.concurrent.ConcurrentHashMap` touched by many threads.
- After: confine, wrap, or switch variant per volatile tabAt/casTabAt reads; Node.val/next volatile.

## Smell 5: Repeated growth on known loads
- Before: default constructor + 1M adds in a loop.
- After: presize once; sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer; writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt).

## Checklist
- [ ] Keys immutable; null policy (counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot) respected.
- [ ] Iteration uses iterator remove/set, not collection remove.
- [ ] Capacity chosen from measurement, documented at construction.
