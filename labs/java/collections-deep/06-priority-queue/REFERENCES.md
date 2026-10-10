# References: PriorityQueue

- OpenJDK source: `src/java.base/share/classes/java/util/PriorityQueue.java`
  — `siftUp`/`siftDown`, `heapify`, `removeAt`, growth via
  `ArraysSupport.newLength`.
- OpenJDK source: `src/java.base/share/classes/java/util/concurrent/PriorityBlockingQueue.java`
  — the lock-based thread-safe sibling.
- J. W. J. Williams, "Algorithm 232 — Heapsort", *CACM* 7(6), 1964 — the
  binary heap and sift operations.
- R. W. Floyd, "Algorithm 245 — Treesort 3", *CACM* 7(12), 1964 — O(n)
  bottom-up heap construction.
- Cormen et al., *Introduction to Algorithms* (CLRS), Ch. 6 "Heapsort" —
  sift correctness, heapify analysis, heap vs sorted-array trade-offs.
- Bloch & Gafter, *Java Puzzlers* / Bloch, *Effective Java* (Item 14,
  "Consider implementing Comparable") — ordering contracts the heap relies
  on.
- Goetz et al., *Java Concurrency in Practice* — why unsynchronized
  collections + fail-fast iterators are not a concurrency strategy.
- `java.util.Queue`, `java.util.Comparator` javadoc — `offer` vs `add`,
  `poll` vs `remove`, `peek` vs `element` null/throw matrix.
## Javadoc entry points

- `java.util.PriorityQueue` — constructor contracts (`initialCapacity < 1`
  rejection), Queue-method null/throw matrix (`offer` vs `add`, `poll` vs
  `remove`, `peek` vs `element`).
- `java.util.Queue` and `java.util.Collection` — `addAll` bulk path that
  heapifies instead of offering one by one.
- `java.util.Comparator` (`reverseOrder`) — the one-line max-heap switch.

## Further reading

- Sedgewick & Wayne, *Algorithms* (4th ed.), Ch. 2 "Priority Queues" —
  binary-heap API, swim/sink (their names for siftUp/siftDown), heapsort.
- OpenJDK `ArraysSupport.newLength` — the shared growth routine behind the
  +2-below-64 / 50%-above rule.
- *Java Concurrency in Practice*, Ch. 5 — `PriorityBlockingQueue` as the
  concurrent counterpart and why its `peek` still locks.
