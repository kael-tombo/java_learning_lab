# Exercises: TreeMap / TreeSet

All tasks run on JDK 17+ with no dependencies. Reference: `java.util.TreeMap`.

## 1. Position probe (15 min)
- Using `java.util.TreeMap / java.util.TreeSet`, insert keys `"a".."h"` and print the position each lands in
  (bucket via `(spread & (n-1))`, index walk, or tree walk as applicable).
- Assert the invariant in color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1) holds for your inputs.

## 2. Growth experiment (20 min)
- Bulk-load 100_000 elements; record time with and without presizing.
- Fact under test: compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first; iteration ascending via on-the-fly successor links; fail-fast via modCount.
- Deliverable: two timings + one paragraph explaining the gap.

## 3. Null contract test (10 min)
- Call the null-key/null-element/null-value operations on `java.util.TreeMap / java.util.TreeSet`.
- Verify behavior matches: live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view. Write the JUnit assertions.

## 4. View-liveness check (15 min)
- Obtain `NavigableSubMap view classes`, mutate through the view, and assert the backing
  collection changed (and vice versa).

## 5. Iterator discipline (15 min)
- Iterate and remove every second element: once via `collection.remove`
  (expect fail-fast or skip) and once via `iterator.remove()` (expect clean).
- Note: unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them.

## 6. Worst-case drill (20 min)
- Force the bad case for this structure (collisions / head inserts /
  reverse-sorted inserts) and measure the cost delta vs the uniform case.
- Relate results to: identity is compareTo==0 (or comparator.compare==0), NOT equals(); floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n).
