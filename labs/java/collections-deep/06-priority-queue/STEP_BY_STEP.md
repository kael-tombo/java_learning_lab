# Step by Step: Build a Heap by Hand

Insert 5, 3, 8, 1 into `new PriorityQueue<>()` (capacity 11, no growth).

1. `offer(5)`: array `[5]`. k=0, guard stops. Root 5.
2. `offer(3)`: place at 1. parent(1) = 0, 5 > 3 → pull 5 down.
   Array `[3, 5]`. k=0 stop.
3. `offer(8)`: place at 2. parent(2) = 0, 3 > 8? No → stays.
   Array `[3, 5, 8]`.
4. `offer(1)`: place at 3. parent(3) = 1, 5 > 1 → pull 5 down (k=1).
   parent(1) = 0, 3 > 1 → pull 3 down (k=0). Array `[1, 3, 8, 5]`.

Now `poll()`:

5. Save 1. Move last (5) to index 0, null index 3, size 4→3.
   Array `[5, 3, 8]`.
6. `siftDown(0)`: children 3, 8 → smaller is 3 → pull up.
   Array `[3, 5, 8]`. Index 1 has no children (2·1+1=3 ≥ size). Done.

Verify: parent(1)=0: 3≥3 ok; parent(2)=0: 8≥3 ok. Min-heap holds.

Now `remove(8)`: linear scan finds index 2 (last slot) → trivial branch,
null it, size 3→2. No sifting needed: `[3, 5]`.

Exercise: `offer(0)` on `[3, 5]` → place at 2, parent(2)=0, 3>0 → root.
Result `[0, 5, 3]` — children of 0 are 5 and 3, heap holds.
## Bonus trace: heapify [7, 5, 6, 1, 3]

`new PriorityQueue<>(List.of(7,5,6,1,3))` copies then heapifies from
`(5 >>> 1) - 1 = 1` down to 0:

1. `siftDown(1)` on 5 with children 1, 3 → pull 1 up: `[7, 1, 6, 5, 3]`.
2. `siftDown(0)` on 7 with children 1, 6 → pull 1 up; continue at index 1
   with children 5, 3 → pull 3 up: `[1, 3, 6, 5, 7]`.
3. Verify: 1 ≤ 3,6; 3 ≤ 5,7. Two siftDowns, five elements placed — O(n).

Contrast: five sequential offers would cost ~2+2+... ≈ 10 comparisons on
longer paths; heapify did it in 3 swaps total.
