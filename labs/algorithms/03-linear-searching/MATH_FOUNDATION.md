# Mathematical Foundation — Linear Searching

## 1. Cost Model

Each iteration does O(1) work (compare + index). For n elements:

- Best: T(n) = 1 = O(1)
- Worst: T(n) = n = O(n)
- Average (target uniform over positions): T(n) = (1 + 2 + ... + n)/n = (n+1)/2 = Θ(n)

## 2. Big-O Summary

| Case | Time | Space |
|------|------|-------|
| Best | O(1) | O(1) |
| Average (found) | Θ(n) | O(1) |
| Worst | O(n) | O(1) |
| Unsuccessful | Θ(n) | O(1) |

Sentinel search: same asymptotics; constant factor ≈ 1 comparison/iteration instead of 2.

## 3. Linear vs Binary (incl. LC 162 Peak)

- Sorted data, q queries: sort once O(n log n) + q·O(log n) vs q·O(n) linear. Sorting pays off iff q is large.
- Peak element: linear scan finds a peak in O(n); the gradient property (`nums[-1] = nums[n] = -∞`, strict neighbors) admits O(log n) binary search — see LEETCODE_SOLUTION.md.
