# MATH_FOUNDATION — Data Structures Advanced

## Fenwick
Each update walks parent indices: i → i + (i & −i), so it visits O(log n) cells. Query: i → i − (i & −i), also O(log n). Proof: i & −i extracts the lowest set bit, and subtracting removes it — the number of set bits in i bounds the walk.

## Segment tree
Tree height = ⌈log n⌉; each query visits at most 4 nodes per level → O(log n). Space: 2^(⌈log n⌉+1) − 1 < 4n.

## Skip list
Each item promoted upward with probability 1/2. Expected number of layers per item = 2. Search drops a level every time it overshoots; argument mirrors binary search → expected O(log n) levels and work.

## Union-find
Potential argument with "rank" classes: each find at a node with rank r increases its halving path; Tarjan's analysis gives m finds + n unions in O(m·α(n)).

## Bloom filter
After n insertions with k hashes into m bits, probability bit still 0 is ≈ (1 − 1/m)^(kn) ≈ e^(−kn/m). FPR = (1 − e^(−kn/m))^k. Minimize over k: k* = (m/n) ln 2 → FPR_min ≈ 0.6185^(m/n).

## Merkle
Tree of n leaves has n−1 internal hashes; proof needs one sibling hash per level → ⌈log n⌉ hashes.

## Suffix array
Construction via prefix doubling: sort by (rank[i], rank[i+k]) for k = 1, 2, 4, ... → O(n log² n). Kasai's LCP is O(n) using the property that LCP values change by at most ±1 under adjacent suffix moves.

## Treap
Expected height bound: probability node at depth d is related to "no earlier priority" among key neighbors — summing yields expected height 2 ln n + O(1).

## Checklist
- [ ] State BIT walk along set bits of i
- [ ] State Bloom FPR formula and k*
- [ ] Sketch DSU α(n) argument
- [ ] Sketch skip-list expected bound
