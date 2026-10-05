# MATH_FOUNDATION — Lists Deep

## Amortized add for ArrayList
Each doubling copies n elements. Total copies up to capacity N: 1+2+4+...+N = 2N − 1 for N adds → amortized 2 writes per add → O(1).

## Linked-list vs array cache
Random access to element k in ArrayList is one address computation; LinkedList must follow k pointers — each node a cache-line mis. Doubling cost in pointer-chasing.

## Floyd's cycle
If tortoise moves 1/step, hare moves 2, then per i steps distance between them grows by 1 each step. Inside a cycle of length c they meet within c steps. Meeting at x, entry at μ, with τ steps to cycle: distance from head to μ = distance from meet to μ → two-pointer entry.

## LRU is O(1)
HashMap gives O(1) lookup; doubly-linked list gives O(1) unlink+relink after hit/evict. Each op is two O(1) primitives → O(1).

## Merge k sorted lists
Min-heap of k heads: each pop of a node, push its successor — O(N log k) total.

## Memory bound
ArrayList: N refs × 4–8 B plus array object overhead. LinkedList: N × (node with 2 refs + payload + header) ≈ N × (24–32 B). For N=1e5, LinkedList can be 10× the bytes.

## Checklist
- [ ] State amortized growth bound
- [ ] Explain Floyd's meet-up
- [ ] Prove LRU O(1) per op
- [ ] State merge-k O(N log k)
