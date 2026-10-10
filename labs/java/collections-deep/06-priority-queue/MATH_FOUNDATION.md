# Math Foundation: Heaps

## Index arithmetic

Parent `p(k) = (k-1) >>> 1`, children `2k+1`, `2k+2`. Check: children of
`p(k)` always include k for k ≥ 1 (verify: k=5 → p=2 → children 5,6 ✓).
`p(0) = (0-1) >>> 1 = 0xFFFFFFFF >>> 1 = 2147483647` — unsigned shift turns
underflow into a huge index, which is why `siftUp` guards `k > 0`.

## Height = floor(log2 n)

A heap with n elements has height ⌊log₂ n⌋: level i holds ≤ 2^i nodes, and
Σ_{i=0}^{h} 2^i = 2^{h+1} − 1 ≥ n. So sift paths are ≤ ⌊log₂ n⌋ — e.g.
n = 1M → ≤ 20 comparisons per offer/poll.

## Heapify is O(n)

Cost = Σ over heights h of (nodes at height h)·h = Σ n/2^{h+1}·h
= n·Σ h/2^{h+1} = n·1 = O(n), since Σ h/2^h converges to 2. Worked: for
n = 10⁶, heapify ≈ 2M steps vs n·log n ≈ 20M for repeated offers — ~10×
cheaper bulk build.

## Growth math

Below 64: cap_{i+1} = 2·cap_i + 2 (11→24→50→102). Above: ×1.5
(102→153→229→343). Amortized copy cost per insert stays O(1): total copies
Σ cap_i < 3n regardless of the kink.

## Iterator order vs sorted order

Heap order satisfies only parent ≤ children (n−1 constraints); sorted
order needs all pairs ordered (~n²/2 constraints). Draining via poll costs
n·log n comparisons — the sorting lower bound, paid on exit instead of
entry.
