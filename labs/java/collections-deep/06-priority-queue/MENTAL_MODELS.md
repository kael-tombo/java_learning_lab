# Mental Models: PriorityQueue

## 1. The array IS the tree

Stop picturing nodes and pointers. Indices are addresses: parent
`(k-1)>>>1`, children `2k+1/2k+2`. If you can do that arithmetic you can
predict every heap state on paper.

## 2. Only the root has a contract

`peek()`/`poll()` promise the minimum. Nothing else promises anything —
not iteration order, not `toString`, not index 1 (which is merely the min
of its subtree). Code that reads `queue.get(1)`-equivalents is broken.

## 3. Sifting, not sorting

Insert and remove each repair one root-to-leaf path. The other n − log n
elements never move. A heap is a machine for maintaining "min at top"
with minimum disturbance, not a sorter that happens to be lazy.

## 4. Last-to-root is the trick

Removal avoids shifting n elements by teleporting the last element to the
hole and letting it sink. Any time you see "swap with last, then restore"
(ArrayList remove, heap poll), it is the same O(n)→O(log n) trade.

## 5. Heapify builds bottom-up

Leaves are already heaps of size 1. `heapify` starts at the last non-leaf
`(n>>>1)-1` and fixes each subtree once. Work concentrates where the
subtrees are tiny — hence O(n), not O(n log n).

## 6. Growth has a kink at 64

Below 64 the queue adds `oldCap + 2` (roughly doubling from 11); above,
1.5× like ArrayList. Small-heap workloads (Dijkstra frontiers, k-way
merges) live left of the kink; bulk pipelines live right of it.

## 7. Fail-fast, not thread-safe

`modCount++` on every `offer` means an iterator notices interference and
throws. That is a bug detector, not a concurrency strategy — for threads,
switch structures (`PriorityBlockingQueue`), not expectations.
