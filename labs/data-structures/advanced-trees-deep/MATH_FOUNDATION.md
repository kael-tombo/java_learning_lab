# MATH_FOUNDATION — Advanced Trees (Deep)

## 1. Red-black height
Let a "black-height" bh(x) be black nodes on any path x→leaf. Every red node has black children, so along any root-to-leaf path, at least h/2 nodes are black. Hence n ≥ 2^(bh) − 1 and h ≤ 2 bh ≤ 2 log(n+1).

## 2. AVL height
Let N(h) be min nodes for height h. N(h) = 1 + N(h−1) + N(h−2), N(0)=1, N(1)=2 → N(h) grows like φ^h where φ=(1+√5)/2. So h ≤ log_φ n ≈ 1.44 log2 n.

## 3. Splay amortized analysis
Define potential Φ = Σ log(size(x)). A zig-zig/zig-zag step reduces Φ enough to pay for the two rotations plus O(1); a zig costs O(1) plus one rotation. Summing over m ops on n nodes gives O(m log n) total → amortized O(log n).

## 4. Treap expected height
For random priorities, the probability that a given node is the LCA of itself and two others is 2/(j−i+1); indicator analysis over merges yields expected height ≈ 2 ln n. Each of ~12n rotations occurs with probability proportional to inverse spans.

## 5. B-tree
Order m: each node has between ⌈m/2⌉−1 and m−1 keys. Minimum nodes at height h is about (m/2)^(h−1) → h ≤ log_{m/2}(n).

## 6. Trie bound
Search for a word of length L visits exactly L nodes → O(L) regardless of n.

## 7. Join/merge algebra
A treap join is O(log n) because the split by priority defines the pivot: all rotations needed is bounded by the expected height of one side.

## Checklist
- [ ] Derive h ≤ 2 log(n+1) for red-black
- [ ] Derive AVL φ bound
- [ ] Sketch splay potential proof
- [ ] State treap expected height constant (~2 ln n)
