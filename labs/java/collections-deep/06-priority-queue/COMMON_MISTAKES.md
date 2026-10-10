# Common Mistakes: PriorityQueue

## 1. Iterating and expecting sorted order

`for (int x : pq)` and `pq.toString()` show heap layout (`[1, 3, 2, 5...]`).
Fix: drain a copy — `while (!copy.isEmpty()) out.add(copy.poll())` — or
`pq.stream().sorted().toList()` for a view.

## 2. Offering null

`offer(null)` throws NPE before any comparison, even with a null-tolerant
comparator. Guard at the call site; heaps cannot represent "null priority".

## 3. Mixing Comparable and Comparator elements

Constructing with a comparator then relying on natural ordering (or raw
types mixing `Integer` and `String`) surfaces as `ClassCastException`
inside `siftUp` at insertion time, not at construction. Keep element types
uniform.

## 4. Using `remove(x)` / `contains(x)` in hot paths

Both are O(n) `equals` scans. In schedulers this turns O(log n) logic into
O(n) per tick. Pair with a `HashSet`/`HashMap` for membership, or use
lazy deletion (skip stale entries at poll).

## 5. Assuming thread safety

Concurrent `offer`/`poll` corrupts `size` and the heap invariant silently
(no CME to save you off-iterator). Use `PriorityBlockingQueue` or confine
the queue to one thread.

## 6. TreeSet comparator returning 0 for distinct items

Switching to `TreeSet` to "get sorted iteration" drops tasks whose
priorities compare equal. If you need both sortedness and duplicates, drain
the PriorityQueue instead.

## 7. Re-offer instead of decrease-key

The JDK has no `decreaseKey`. The idiom is offer-the-update + skip-stale
at poll (Dijkstra pattern), not `remove` + `offer` (which costs O(n)).
