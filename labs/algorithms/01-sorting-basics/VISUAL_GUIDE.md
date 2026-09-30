# Visual Guide — Sorting Basics

## 1. Bubble Sort State Progression

Tracing with array `[5, 3, 8, 4, 2]`:

```
Initial: [5, 3, 8, 4, 2]

Pass 1:
  [5, 3, 8, 4, 2] -> 5 > 3 -> Swap!   -> [3, 5, 8, 4, 2]
  [3, 5, 8, 4, 2] -> 5 < 8 -> Keep    -> [3, 5, 8, 4, 2]
  [3, 5, 8, 4, 2] -> 8 > 4 -> Swap!   -> [3, 5, 4, 8, 2]
  [3, 5, 4, 8, 2] -> 8 > 2 -> Swap!   -> [3, 5, 4, 2, (8)]  <-- 8 placed in final spot

Pass 2:
  [3, 5, 4, 2, 8] -> 3 < 5 -> Keep    -> [3, 5, 4, 2, 8]
  [3, 5, 4, 2, 8] -> 5 > 4 -> Swap!   -> [3, 4, 5, 2, 8]
  [3, 4, 5, 2, 8] -> 5 > 2 -> Swap!   -> [3, 4, 2, (5), (8)] <-- 5 placed

Pass 3:
  [3, 4, 2, 5, 8] -> 3 < 4 -> Keep    -> [3, 4, 2, 5, 8]
  [3, 4, 2, 5, 8] -> 4 > 2 -> Swap!   -> [3, 2, (4), (5), (8)] <-- 4 placed

Pass 4:
  [3, 2, 4, 5, 8] -> 3 > 2 -> Swap!   -> [(2), (3), (4), (5), (8)]

Final: [2, 3, 4, 5, 8]
```

## 2. Selection Sort State Progression

Finding the minimum element in the unsorted suffix and performing at most 1 swap per pass:

```
Initial: [5, 3, 8, 4, 2]

Pass 0: Unsorted: [5, 3, 8, 4, 2] | min=2 at idx 4 -> Swap(0, 4) -> [(2),  3,  8,  4,  5]
Pass 1: Unsorted: [3, 8, 4, 5]    | min=3 at idx 1 -> No swap!    -> [(2,  3),  8,  4,  5]
Pass 2: Unsorted: [8, 4, 5]       | min=4 at idx 3 -> Swap(2, 3) -> [(2,  3,  4),  8,  5]
Pass 3: Unsorted: [8, 5]          | min=5 at idx 4 -> Swap(3, 4) -> [(2,  3,  4,  5), (8)]

Final: [2, 3, 4, 5, 8]
```

## 3. Insertion Sort State Progression

Shifting larger elements right to insert the key into the sorted prefix:

```
Initial: [5, 3, 8, 4, 2]

Step 1: Prefix [5], Key = 3
  3 < 5 -> Shift 5 right: [5, 5, 8, 4, 2] -> Place 3: [(3, 5), 8, 4, 2]

Step 2: Prefix [3, 5], Key = 8
  8 > 5 -> No shifts needed: [(3, 5, 8), 4, 2]

Step 3: Prefix [3, 5, 8], Key = 4
  4 < 8 -> Shift 8: [3, 5, 8, 8, 2]
  4 < 5 -> Shift 5: [3, 5, 5, 8, 2]
  4 > 3 -> Stop shifting -> Place 4: [(3, 4, 5, 8), 2]

Step 4: Prefix [3, 4, 5, 8], Key = 2
  2 < 8, 5, 4, 3 -> Shift all: [3, 3, 4, 5, 8] -> Place 2: [(2, 3, 4, 5, 8)]

Final: [2, 3, 4, 5, 8]
```
