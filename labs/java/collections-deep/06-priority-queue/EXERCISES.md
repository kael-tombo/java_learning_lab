# Exercises: PriorityQueue

## 1. Prove iteration is not sorted

```java
var pq = new java.util.PriorityQueue<>(java.util.List.of(5,3,8,1,9,2,7));
System.out.println(pq);                       // heap order
var drained = new java.util.ArrayList<Integer>();
var copy = new java.util.PriorityQueue<>(pq);
while (!copy.isEmpty()) drained.add(copy.poll());
System.out.println(drained);                  // sorted
assert drained.equals(drained.stream().sorted().toList());
```

## 2. Verify the heap property programmatically

Copy to an `ArrayList` and assert `get((i-1)>>>1) <= get(i)` for all i ≥ 1
after random offers, polls, and `remove(Object)` calls.

## 3. Measure growth with reflection

```java
Field f = java.util.PriorityQueue.class.getDeclaredField("queue");
f.setAccessible(true);
// run: java --add-opens java.base/java.util=ALL-UNNAMED ...
// offer 300 ints, print capacity at each change; expect 11,24,50,102,153,229,343
```

Confirm `new PriorityQueue<>(0)` throws `IllegalArgumentException`.

## 4. Max-heap + NPE probe

Build with `Comparator.reverseOrder()`, check `peek()` is the max while
iteration stays heap-ordered; confirm `offer(null)` throws NPE.

## 5. Top-k with a bounded heap

Given 100k random ints, keep a min-heap of size k=10 (poll when size > k).
Result holds the 10 largest; compare against `sorted().limit()` output.

## 6. Dijkstra with lazy deletion

Implement Dijkstra using `PriorityQueue<long[]>` of (dist, node); on poll,
skip entries whose dist exceeds the settled distance. Count skipped stale
entries vs `remove`-based updates and compare wall time.
