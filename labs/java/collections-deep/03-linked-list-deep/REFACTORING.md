# Refactoring: LinkedList Deep Dive

## Smell 1: Manual rehash / rescan loops
- Before: hand-rolled index math or full scans around `java.util.LinkedList`.
- After: single `linkFirst/linkLast/linkBefore + unlink/unlinkFirst/unlinkLast` call; let node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last do the positioning.
- Why: duplicates the JDK's tested path and usually gets Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs) wrong.

## Smell 2: Copy-then-view confusion
- Before: `List<V> v = new ArrayList<>(map.values()); v.remove(x)` expecting
  map mutation (or vice versa).
- After: operate on `ListItr / DescendingIterator` directly for live writes; copy only for
  snapshots.

## Smell 3: Mutable keys / inconsistent ordering
- Before: keys whose `hashCode/compareTo` change after insertion.
- After: immutable keys; comparator consistent with equals where possible.
- Note: Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs); doubly-linked symmetry: node.next.prev == node.prev.next == node.

## Smell 4: Shared instance without a policy
- Before: static `java.util.LinkedList` touched by many threads.
- After: confine, wrap, or switch variant per unsynchronized; structural change must flow through link/unlink (size+modCount).

## Smell 5: Repeated growth on known loads
- Before: default constructor + 1M adds in a loop.
- After: presize once; no sentinel node: size==0 means first==last==null, every mutation branches on null; implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst.

## Checklist
- [ ] Keys immutable; null policy (fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal) respected.
- [ ] Iteration uses iterator remove/set, not collection remove.
- [ ] Capacity chosen from measurement, documented at construction.
