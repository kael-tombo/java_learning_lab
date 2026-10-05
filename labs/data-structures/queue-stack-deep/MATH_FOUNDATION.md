# MATH_FOUNDATION — Queue & Stack Deep

## Stack O(1)
Array grows by doubling; total copies for n pushes ≈ 2n → amortized O(1) per push. Each pop is one index decrement → O(1).

## Two-stack queue
Each push moves to inStack once; each pop moves from outStack once or refills outStack from inStack once. Across n ops, each element crosses each stack at most once → O(1) amortized per op.

## Binary heap
Complete binary tree with n nodes has height ⌈log n⌉. Sift-up/down visits at most height nodes → O(log n). Offer = append + sift-up; poll = swap last to root + sift-down.

## ArrayDeque ring
Indices advance mod capacity; no per-op copy. Growth copies k elements each doubling — overall O(1) amortized.

## Priority queue stability
A binary heap does not preserve insertion order among equals; stable ordering requires a secondary sequence number in the comparator.

## Checklist
- [ ] Derive amortized stack cost
- [ ] Derive two-stack queue bound
- [ ] State heap height
- [ ] State sift-up/down bound
