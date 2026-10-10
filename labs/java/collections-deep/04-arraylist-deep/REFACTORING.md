# Refactoring: ArrayList Deep Dive

## Smell 1: Manual rehash / rescan loops
- Before: hand-rolled index math or full scans around `java.util.ArrayList`.
- After: single `add/get/set/remove/ensureCapacity/trimToSize` call; let growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf do the positioning.
- Why: duplicates the JDK's tested path and usually gets lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10 wrong.

## Smell 2: Copy-then-view confusion
- Before: `List<V> v = new ArrayList<>(map.values()); v.remove(x)` expecting
  map mutation (or vice versa).
- After: operate on `SubList view + fail-fast Itr/ListItr` directly for live writes; copy only for
  snapshots.

## Smell 3: Mutable keys / inconsistent ordering
- Before: keys whose `hashCode/compareTo` change after insertion.
- After: immutable keys; comparator consistent with equals where possible.
- Note: lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10; MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves).

## Smell 4: Shared instance without a policy
- Before: static `java.util.ArrayList` touched by many threads.
- After: confine, wrap, or switch variant per unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList.

## Smell 5: Repeated growth on known loads
- Before: default constructor + 1M adds in a loop.
- After: presize once; two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact); set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it.

## Checklist
- [ ] Keys immutable; null policy (fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks) respected.
- [ ] Iteration uses iterator remove/set, not collection remove.
- [ ] Capacity chosen from measurement, documented at construction.
