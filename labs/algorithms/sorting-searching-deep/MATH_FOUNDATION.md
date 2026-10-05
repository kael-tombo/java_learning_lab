# MATH_FOUNDATION — Sorting & Searching Deep Track
> Recurrences / Master theorem / amortized. Track `sorting-searching-deep`.

## 1. Recurrence toolkit
- T(n) = a·T(n/b) + f(n); Master 1/2/3.
- Mergesort 2T(n/2)+O(n) → Θ(n log n).
- Binary search T(n)=T(n/2)+O(1) → Θ(log n).

## 2. Master theorem cases
- 30s decision: compare f vs n^{log_b a}; regularity for case 3.
- Quicksort average is non-Master (random splits); use split summation.

## 3. Sorting lower bound
- Decision tree ≥ n! leaves → height ≥ log₂(n!) = Ω(n log n) via Stirling.
- Holds for comparison model only; counting/radix escape via keys.

## 4. Linear-sort math
- Counting: O(n+k) count + prefix + scatter; stable by reverse scatter.
- Radix LSD: d passes × O(n+k) = O(d(n+k)); needs stable digit sort.

## 5. Quickselect expectation
- Good pivot prob 1/2; cost ≤ n + 3n/4 + ... ≤ 4n → E[O(n)].

## 6. String matcher math
- KMP amortized: text pointer advances or state drops; O(n+m) total.
- RK: expected O(n+m) with verify cost bounded by low collision rate.

## 7. Amortized: dynamic array/counter/DSU
- Push O(1), counter O(1), DSU α; telescoping reuse arguments.

## 8. Cache/IO awareness (sketch)
- Binary jumps miss cache; Eytzinger/B-tree layouts reduce misses.
- External mergesort: Θ((n/B) log_{M/B}(n/B)) IOs.

## 9. Practice proofs (do on paper)
- Prove Ω(n log n) comparison bound.
- Prove binary Θ(log n) via Master.
- Prove quicksort average via split sum.
- Prove KMP amortized linear scan.

## Checklist
- [ ] State Master case in 30s. [ ] Sketch one amortized proof. [ ] Derive one sort bound.
