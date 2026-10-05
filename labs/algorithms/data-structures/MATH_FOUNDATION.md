# MATH_FOUNDATION — Data Structures Track
> Recurrences / Master theorem / amortized. Track `data-structures`.

## 1. Recurrence toolkit
- T(n) = a·T(n/b) + f(n); Master cases 1/2/3.
- Segment build: T(n) = 2T(n/2) + O(1) → Θ(n).
- Balanced BST ops: T(n) = T(n/2) + O(1) → Θ(log n).
- Quicksort avg: T(n) = 2T(n/2) + O(n) → Θ(n log n).

## 2. Master theorem cases
- Case 1: f smaller → leaves dominate: Θ(n^{log_b a}).
- Case 2: f equal → Θ(n^{log_b a} log n).
- Case 3: f larger + regularity → Θ(f(n)).
- Drill: mergesort, Strassen, heap-build variants.

## 3. Graph counting
- Handshaking: Σ deg(v) = 2E.
- BFS/DFS each edge examined ≤ twice → O(V+E).
- Dense E=Θ(V²): matrix wins; sparse: list wins.

## 4. Amortized: dynamic array
- Double on full; n pushes cost ≤ 3n → O(1) amortized.
- Accounting: 3 credits per push (1 now, 2 saved for copy).
- Halving policy: shrink at 1/4 to avoid thrash.

## 5. Amortized: union-find
- Rank/size + path compression → O(α(n)) per op.
- Potential: Φ = Σ rank-ish measure; path halves flatten future cost.
- Without compression: O(log n) by size alone.

## 6. Amortized: binary counter
- n increments flip O(n) bits total → O(1) amortized each.
- Potential Φ = number of 1-bits; telescopes increments.

## 7. Heap analysis
- Sift height ≤ log n → O(log n) ops.
- Bottom-up heapify: Σ (n/2^{h+1})·O(h) = O(n).
- k-way merge: O(n log k) via size-k heap.

## 8. BST expectations
- Random insert order: expected height O(log n).
- Adversarial sorted order: Θ(n) chain → balance needed.
- Trie: O(L) independent of n; space = total prefixes.

## 9. Practice proofs (do on paper)
- Prove BFS layer correctness by induction on distance.
- Prove heapify is O(n) via level summation.
- Prove DSU-by-size height ≤ log n.
- Prove dynamic-array 3-credit accounting.

## Checklist
- [ ] State Master case in 30s. [ ] Sketch one amortized proof. [ ] Derive BFS bound.
