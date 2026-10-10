# Exercises: ConcurrentHashMap

All tasks run on JDK 17+ with no dependencies. Reference: `java.util.concurrent.ConcurrentHashMap`.

## 1. Position probe (15 min)
- Using `java.util.concurrent.ConcurrentHashMap`, insert keys `"a".."h"` and print the position each lands in
  (bucket via `(spread & (n-1))`, index walk, or tree walk as applicable).
- Assert the invariant in putVal rejects null key/value with NullPointerException holds for your inputs.

## 2. Growth experiment (20 min)
- Bulk-load 100_000 elements; record time with and without presizing.
- Fact under test: sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer; writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt).
- Deliverable: two timings + one paragraph explaining the gap.

## 3. Null contract test (10 min)
- Call the null-key/null-element/null-value operations on `java.util.concurrent.ConcurrentHashMap`.
- Verify behavior matches: counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot. Write the JUnit assertions.

## 4. View-liveness check (15 min)
- Obtain `weakly-consistent iterators (never throw CME)`, mutate through the view, and assert the backing
  collection changed (and vice versa).

## 5. Iterator discipline (15 min)
- Iterate and remove every second element: once via `collection.remove`
  (expect fail-fast or skip) and once via `iterator.remove()` (expect clean).
- Note: volatile tabAt/casTabAt reads; Node.val/next volatile.

## 6. Worst-case drill (20 min)
- Force the bad case for this structure (collisions / head inserts /
  reverse-sorted inserts) and measure the cost delta vs the uniform case.
- Relate results to: spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative; TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap.
