# Quiz: PriorityQueue

## Q1. What does iteration over a PriorityQueue yield?

**A.** Heap order (the raw array), not sorted order. `[1, 3, 2, 5, 9, 8, 7]`
is a valid iteration. Sorted output requires draining via `poll()`.

## Q2. What is the parent index formula, and what is parent(0)?

**A.** `(k - 1) >>> 1`. `parent(0) = (0-1) >>> 1 = 2147483647` (unsigned
underflow) — which is why `siftUp` guards with `while (k > 0)`.

## Q3. What capacity does `new PriorityQueue<>()` allocate, and how does it grow?

**A.** Eager `Object[11]`. Growth is `oldCap + 2` below capacity 64
(11 → 24 → 50), then 50% (`oldCap >> 1`: 102 → 153 → 229).

## Q4. Why is bulk construction O(n) instead of O(n log n)?

**A.** `heapify()` starts at the last non-leaf `(n >>> 1) - 1` and sifts
down; most nodes are near leaves with tiny subtrees (Floyd's build, Σ
h/2^h converges).

## Q5. What happens on `offer(null)` — even with a custom comparator?

**A.** Immediate `NullPointerException`. The null check precedes any
comparison and is unconditional.

## Q6. How does `removeAt` restore the heap after removing a middle element?

**A.** Moves the last element into the hole, tries `siftDown`; if the
element did not move (`es[i] == moved`) it tries `siftUp` instead.

## Q7. Is PriorityQueue thread-safe? What breaks first under concurrency?

**A.** No. Concurrent offer/poll corrupts `size` and heap order silently;
iterators detect some interference via `modCount` (every offer bumps it)
but that is detection, not safety. Use `PriorityBlockingQueue`.
