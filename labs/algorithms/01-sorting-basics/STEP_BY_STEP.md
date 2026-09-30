# Step-by-Step Execution Guide — Sorting Basics

## 1. Bubble Sort Execution Flow

1. Determine array length $n$. If $n \le 1$, terminate immediately.
2. Initialize outer loop counter $i = 0$ to $n - 2$.
3. Set flag `swapped = false`.
4. Initialize inner loop counter $j = 0$ to $n - i - 2$ (the last $i$ elements are already in their final sorted positions).
5. Compare adjacent elements: if $arr[j] > arr[j + 1]$, swap them and set `swapped = true`.
6. At the end of inner pass, test `swapped`: if `false`, array is completely sorted, break early.
7. Return the sorted array.

---

## 2. Selection Sort Execution Flow

1. Determine array length $n$. If $n \le 1$, terminate immediately.
2. Outer loop from $i = 0$ to $n - 2$: assume current slot $i$ holds minimum index (`minIdx = i`).
3. Inner loop scans unsorted suffix from $j = i + 1$ to $n - 1$:
   - If $arr[j] < arr[minIdx]$, update `minIdx = j`.
4. After inner loop, if `minIdx != i`, swap elements at $i$ and $minIdx$.
5. Advance $i$. Slot $i$ is now guaranteed to hold the $i$-th smallest element.
6. Return the sorted array.

---

## 3. Insertion Sort Execution Flow

1. Determine array length $n$. If $n \le 1$, terminate immediately.
2. Outer loop from $i = 1$ to $n - 1$:
   - Save candidate element $key = arr[i]$.
   - Initialize pointer $j = i - 1$ pointing to the end of the sorted prefix $[0 \dots i-1]$.
3. Shift loop: while $j \ge 0$ AND $arr[j] > key$:
   - Copy element one position to the right: $arr[j + 1] = arr[j]$.
   - Decrement $j$ by 1.
4. Place stored key in newly opened vacancy: $arr[j + 1] = key$.
5. The prefix $[0 \dots i]$ is now fully sorted.
6. Repeat until $i = n - 1$.
