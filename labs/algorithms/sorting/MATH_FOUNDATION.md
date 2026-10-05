# MATH_FOUNDATION — Sorting Track
> Recurrences / Master theorem / amortized. Track `sorting`.

## 1. Recurrence toolkit
- T(n) = a·T(n/b) + f(n); Master 1/2/3.
- Mergesort 2T(n/2)+O(n) → Θ(n log n) case 2.
- Quicksort average is NOT Master (random splits) — linearity + split sum.

## 2. Master theorem cases
- 30s decision: compare f vs n^{log_b a}; check regularity for case 3.
- Drill: Strassen, Karatsuba, mergesort.

## 3. Quicksort average proof sketch
- E[T(n)] = (1/n)Σ(E[T(k)]+E[T(n-1-k)]) + cn.
- Symmetry doubles one sum; guess dn log n; verify by integral bound.
- Random pivot ⇒ each rank equally likely ⇒ balanced splits dominate.

## 4. Worst-case family
- Fixed pivot + sorted input ⇒ T(n)=T(n-1)+O(n) → Θ(n²).
- Adversary argument: any deterministic pivot has a killer permutation.

## 5. Quickselect expectation
- Good pivot (25-75%) with prob 1/2; cost series n + 3n/4 + ... ≤ 4n.
- Hence E[O(n)]; median-of-medians for worst O(n).

## 6. Lower bound
- n! permutations; decision tree height ≥ log₂(n!) = Ω(n log n) (Stirling).
- Non-comparison sorts escape via key structure (counting/radix).

## 7. Amortized: dynamic array/counter
- Push O(1) accounting; counter O(1) potential; DSU α preview.

## 8. 3-way + Dutch-flag counting
- All-equal: single partition scans once → Θ(n).
- formalize via region sizes: unscanned shrinks every step.

## 9. Practice proofs (do on paper)
- Prove mergesort via Master case 2.
- Prove quicksort average via split summation.
- Prove Ω(n log n) comparison bound.
- Prove amortized push O(1).

## Checklist
- [ ] State Master case in 30s. [ ] Sketch one amortized proof. [ ] Derive QS average.
