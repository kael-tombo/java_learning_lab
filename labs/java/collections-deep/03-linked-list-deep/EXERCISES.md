# Exercises: LinkedList Deep Dive

All tasks run on JDK 17+ with no dependencies. Reference: `java.util.LinkedList`.

## 1. Position probe (15 min)
- Using `java.util.LinkedList`, insert keys `"a".."h"` and print the position each lands in
  (bucket via `(spread & (n-1))`, index walk, or tree walk as applicable).
- Assert the invariant in node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last holds for your inputs.

## 2. Growth experiment (20 min)
- Bulk-load 100_000 elements; record time with and without presizing.
- Fact under test: no sentinel node: size==0 means first==last==null, every mutation branches on null; implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst.
- Deliverable: two timings + one paragraph explaining the gap.

## 3. Null contract test (10 min)
- Call the null-key/null-element/null-value operations on `java.util.LinkedList`.
- Verify behavior matches: fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal. Write the JUnit assertions.

## 4. View-liveness check (15 min)
- Obtain `ListItr / DescendingIterator`, mutate through the view, and assert the backing
  collection changed (and vice versa).

## 5. Iterator discipline (15 min)
- Iterate and remove every second element: once via `collection.remove`
  (expect fail-fast or skip) and once via `iterator.remove()` (expect clean).
- Note: unsynchronized; structural change must flow through link/unlink (size+modCount).

## 6. Worst-case drill (20 min)
- Force the bad case for this structure (collisions / head inserts /
  reverse-sorted inserts) and measure the cost delta vs the uniform case.
- Relate results to: Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs); doubly-linked symmetry: node.next.prev == node.prev.next == node.
