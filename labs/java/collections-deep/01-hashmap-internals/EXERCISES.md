# Exercises: HashMap Internals

All tasks run on JDK 17+ with no dependencies. Reference: `java.util.HashMap`.

## 1. Position probe (15 min)
- Using `java.util.HashMap`, insert keys `"a".."h"` and print the position each lands in
  (bucket via `(spread & (n-1))`, index walk, or tree walk as applicable).
- Assert the invariant in spreader `h ^ (h >>> 16)` folds high bits down holds for your inputs.

## 2. Growth experiment (20 min)
- Bulk-load 100_000 elements; record time with and without presizing.
- Fact under test: resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0; default capacity 16, load factor 0.75.
- Deliverable: two timings + one paragraph explaining the gap.

## 3. Null contract test (10 min)
- Call the null-key/null-element/null-value operations on `java.util.HashMap`.
- Verify behavior matches: null key allowed once, hash 0, bucket 0. Write the JUnit assertions.

## 4. View-liveness check (15 min)
- Obtain `entrySet().iterator() EntryIterator`, mutate through the view, and assert the backing
  collection changed (and vice versa).

## 5. Iterator discipline (15 min)
- Iterate and remove every second element: once via `collection.remove`
  (expect fail-fast or skip) and once via `iterator.remove()` (expect clean).
- Note: fail-fast via modCount, ConcurrentModificationException.

## 6. Worst-case drill (20 min)
- Force the bad case for this structure (collisions / head inserts /
  reverse-sorted inserts) and measure the cost delta vs the uniform case.
- Relate results to: TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64; TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties.
