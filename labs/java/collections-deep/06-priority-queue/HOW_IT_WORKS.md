# How PriorityQueue Works

## The array is the tree

No `Node` class exists. For `[1, 3, 2, 5, 9, 8, 7]`:

- 1 is root. Children of 0: indices 1 (3) and 2 (2). Children of 1: 3 (5),
  4 (9). Every parent compares ≤ its children — that is the whole invariant.

## Insert: siftUp

`offer(0)` on that heap: place 0 at index 7, compare with parent
`(7-1) >>> 1 = 3` (value 5) → move 5 down; k=3, parent 1 (value 3) →
move 3 down; k=1, parent 0 (value 1) → 0 < 1? No: 0 < 1, so keep moving;
k=0, loop guard `k > 0` stops. Root becomes 0. Three comparisons, O(log n).

## Remove: last-to-root + siftDown

`poll()` saves 1, moves 7 (last) to index 0, then sifts down: children of
0 are 3 and 2 → smaller is 2 → pull 2 up; continue at index 2 with
children 8 and 7 → pull 7 up; 7 (leaf level) fits. New root 2.

## Heapify: why bulk load is O(n)

Leaves (n/2 nodes) need no work; their parents need ≤ 1 sift step, next
level ≤ 2, and so on. Total Σ (n/2^(h+1))·h ≤ 2n. `addAll` exploits this;
repeated `offer` does not.

## What the heap does NOT do

- It never sorts the array. Iteration, `toString`, `toArray` all show heap
  layout. Sorted output = repeated `poll()` (O(n log n) total).
- `remove(x)` finds by `equals` scan, swaps the last element into the hole,
  then tries `siftDown` first and `siftUp` if the element did not move
  (`es[i] == moved` check in `removeAt`).
