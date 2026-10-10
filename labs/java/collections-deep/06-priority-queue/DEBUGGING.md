# Debugging: PriorityQueue

## Assert the heap invariant

When output looks wrong, check the structure first — copy to a list and
verify every parent ≤ child:

```java
var a = new java.util.ArrayList<>(pq);
for (int i = 1; i < a.size(); i++)
    assert ((Comparable) a.get((i - 1) >>> 1)).compareTo(a.get(i)) <= 0;
```

If this fails with single-threaded code, the comparator is inconsistent
(non-transitive) — the heap cannot hold an ordering that contradicts
itself. Fix the comparator, not the queue.

## ClassCastException in siftUp

Stack shows `siftUpComparable` → mixed element types or non-Comparable
elements under natural ordering. Print the offending element's class at
the offer site; generics erasure hides this until runtime.

## "Elements come out in weird order"

Not a bug until proven: log `poll()` sequence (must be non-decreasing)
separately from iteration order (heap layout). If poll order violates
monotonicity, suspect concurrent mutation or a stateful comparator.

## Stale entries after priority change

Mutating an element's priority field *after* offering it silently breaks
the heap (positions were computed from old values). Priorities must be
effectively immutable while queued; to update, `remove` + re-`offer`
(O(n)) or use the lazy stale-entry idiom.

## Capacity surprises

Reflect on the `queue` field (`--add-opens java.base/java.util=ALL-UNNAMED`)
to confirm growth 11 → 24 → 50 → 102 → 153. Unexpected retention usually
means `poll`/`remove` nulled slots correctly but the caller holds
references to drained elements elsewhere.

## CME from iterators

`ConcurrentModificationException` during iteration = structural change
(every `offer` bumps `modCount`, even without growth). Iterate over a
copy or drain instead.
