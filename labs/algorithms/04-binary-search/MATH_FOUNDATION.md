# Mathematical Foundation — Binary Search

## 1. Recurrence and Big-O

Halving each step: T(n) = T(n/2) + O(1) ⇒ T(n) = Θ(log n) (Master theorem, a=1, b=2).

| Variant | Time | Space |
|---------|------|-------|
| Classic (distinct, sorted) | O(log n) | O(1) iterative, O(log n) recursive |
| Rotated distinct (LC 33) | O(log n) | O(1) |
| Rotated with duplicates (LC 81) | O(log n) avg, O(n) worst | O(1) |
| Peak element (LC 162) | O(log n) | O(1) / O(log n) recursive |

Worst-case comparisons: ⌈log2(n+1)⌉.

## 2. Why Duplicates Degrade to O(n)

If `nums[l] == nums[m] == nums[r]`, neither half can be proven sorted, so we shrink both ends by 1. On `[1,1,...,1]` searching for 2 this repeats n times ⇒ O(n).

## 3. Peak Gradient Proof Sketch

With `nums[-1] = nums[n] = -∞` and strict neighbors: if `nums[mid] < nums[mid+1]`, an ascent continues right and must crest before the `-∞` boundary, so a peak exists in `[mid+1, r]`; else one exists in `[l, mid]`. Halving preserves the invariant ⇒ O(log n).
