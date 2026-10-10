# Exercises: ArrayList Deep Dive

All tasks run on JDK 17+ with no dependencies. Reference: `java.util.ArrayList`.

## 1. Position probe (15 min)
- Using `java.util.ArrayList`, insert keys `"a".."h"` and print the position each lands in
  (bucket via `(spread & (n-1))`, index walk, or tree walk as applicable).
- Assert the invariant in growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf holds for your inputs.

## 2. Growth experiment (20 min)
- Bulk-load 100_000 elements; record time with and without presizing.
- Fact under test: two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact); set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it.
- Deliverable: two timings + one paragraph explaining the gap.

## 3. Null contract test (10 min)
- Call the null-key/null-element/null-value operations on `java.util.ArrayList`.
- Verify behavior matches: fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks. Write the JUnit assertions.

## 4. View-liveness check (15 min)
- Obtain `SubList view + fail-fast Itr/ListItr`, mutate through the view, and assert the backing
  collection changed (and vice versa).

## 5. Iterator discipline (15 min)
- Iterate and remove every second element: once via `collection.remove`
  (expect fail-fast or skip) and once via `iterator.remove()` (expect clean).
- Note: unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList.

## 6. Worst-case drill (20 min)
- Force the bad case for this structure (collisions / head inserts /
  reverse-sorted inserts) and measure the cost delta vs the uniform case.
- Relate results to: lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10; MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves).
