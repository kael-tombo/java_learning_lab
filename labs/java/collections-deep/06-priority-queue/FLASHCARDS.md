# Flashcards: PriorityQueue

**Q: Backing structure?**
A: Flat `Object[] queue`, no nodes. Index 0 = minimum.

**Q: Parent / children index formulas?**
A: Parent `(k-1) >>> 1`; children `2k+1`, `2k+2`.

**Q: `parent(0)` value and why it matters?**
A: 2147483647 (unsigned underflow of -1). `siftUp` guards `k > 0`.

**Q: offer / poll / peek costs?**
A: O(log n) / O(log n) / O(1).

**Q: contains / remove(Object) costs?**
A: O(n) `equals` scan + O(log n) sift for remove.

**Q: Default capacity and growth?**
A: Eager 11; +2 below 64, 50% above. 11 → 24 → 50 → 102 → 153.

**Q: Heapify start index and cost?**
A: `(n >>> 1) - 1` down to 0; O(n) total.

**Q: `offer(null)`?**
A: Always NPE, before any comparison.

**Q: Iteration order?**
A: Heap order, not sorted. Drain with poll for sorted output.

**Q: `removeAt` two-branch logic?**
A: siftDown first; if unmoved, siftUp.

**Q: modCount behavior?**
A: Unconditional ++ on every offer; ++ on non-empty poll. Fail-fast.

**Q: Thread-safe alternative?**
A: `PriorityBlockingQueue` — same heap + ReentrantLock.

**Q: Duplicates by equals?**
A: All retained; `remove(one)` deletes first array-slot match.
