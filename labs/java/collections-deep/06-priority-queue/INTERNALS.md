# Internals: PriorityQueue Source Map

File: `src/java.base/share/classes/java/util/PriorityQueue.java` (OpenJDK).

## Fields

- `transient Object[] queue` — heap storage; index 0 is min.
- `int size` — live count; stale slots nulled after this index.
- `transient int modCount` — fail-fast version stamp.
- `private final Comparator<? super E> comparator` — null = natural order.
- `private static final int DEFAULT_INITIAL_CAPACITY = 11`.

## Key methods

- `offer(E e)`: null check → grow via `ArraysSupport.newLength(oldCap,
  needed, oldCap < 64 ? oldCap + 2 : oldCap >> 1)` → `siftUp(size, e)`.
  `modCount++` is unconditional after the null check.
- `siftUp(int k, E x)`: loop `while (k > 0)`, parent `(k-1) >>> 1`
  (unsigned shift; `parent(0)` would be 2147483647, hence the guard).
- `poll()`: `siftDown` after last-to-root move; nulls the vacated slot;
  `modCount++` only on non-empty queue.
- `removeAt(int i)`: `siftDown(i, moved)`; if `es[i] == moved`, `siftUp`.
  Returns the element left for the iterator to handle.
- `heapify()`: `for (int i = (size >>> 1) - 1; i >= 0; i--) siftDown(i, ...)`.
- `grow(int minCapacity)`: rejects `initialCapacity < 1` in constructors
  with `IllegalArgumentException` ("for 1.5 compatibility" comment).
- `Itr`: fail-fast iterator walking raw indices 0..size in heap order;
  `remove` delegates to `removeAt(lastRet)` with the `moved`-element fixup.

## Sift direction choice

`siftDownComparable` picks the smaller child first (`if right < left use
right`), pulls it up, continues while a child exists. `siftUp` pulls the
parent down. Both move only references — O(log n) writes, zero allocation.
