# 03 — Heap Sort

<div align="center">

**Binary Heap · Heapify · Sift Up/Down · Array-Backed Heap · Heap Sort**

</div>

---

## Learning Objectives

- Maintain the complete binary tree ↔ array mapping (`left(i)=2i+1`, `right(i)=2i+2`, `parent(i)=(i-1)/2`)
- Implement `siftUp` / `siftDown` and prove they terminate with the max-heap property restored
- Distinguish max-heap, min-heap, and the exact heap-order relation
- Explain the `O(1)`-amortised argument for `push`/`pop` and the `O(log n)` worst case
- Build a heap in `Θ(n)` bottom-up (not `Θ(n log n)`)
- Derive the `Floyd` build bound: sum over heights of `n/2^(h+1)` nodes × `O(h)`
- Understand why heap sort loses to quicksort in practice despite equal asymptotics

## Prerequisites

- Trees and tree traversal (breadth-first order = heap array order)
- Recursion or an explicit loop for `siftDown`
- `01-comparison-sorts` for the comparison-lower-bound context

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 75 minutes
- **Total**: 5–6 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| Complete binary tree | Every level full except possibly the last, which is filled left to right |
| Array layout | Index `i` ⇒ children `2i+1`, `2i+2`; parent `(i-1)/2`. No pointers needed |
| Heap property | Every node ≥ both children (max-heap) or ≤ both children (min-heap) |
| Heapify / siftDown | Restore the property by pushing a node down to its correct depth |
| SiftUp | Restore the property after inserting at the leaf, moving toward the root |
| Height of node | `⌊log₂(index+1)⌋` — the reason heap build is `Θ(n)`, not `Θ(n log n)` |
| Last leaf | Index `⌊n/2⌋ - 1` holds the parent of the final node; nodes from there up are *internal* |
| Amortised `O(1)` push | Sift-up is cheap because the new leaf is tiny relative to a full binary tree |
| `peek` | `O(1)` — read `a[0]` |
| Heap sort | Build max-heap `Θ(n)`, then repeatedly swap root to end and `siftDown(0, --size)` |

## Complexity Snapshot

| Operation | Best | Worst | Amortised | Space |
|-----------|------|-------|-----------|-------|
| `peek` | Θ(1) | Θ(1) | Θ(1) | — |
| `push` | Ω(1) | O(log n) | **O(1)** | O(1) |
| `pop` | Ω(log n) | O(log n) | O(log n) | O(1) |
| `addAll(k)` | Θ(k) | Θ(k) | Θ(k) | O(1) amortised |
| `removeAt(i)` | — | O(log n) | O(log n) | O(1) |
| `increaseKey`/`decreaseKey` | — | O(log n) | O(log n) | O(1) |
| Build max-heap (Floyd) | Θ(n) | Θ(n) | Θ(n) | O(1) |
| Build by repeated push | Θ(n log n) | Θ(n log n) | Θ(n log n) | O(1) |
| **Heap sort** | Θ(n log n) | Θ(n log n) | Θ(n log n) | **O(1)** |

## Algorithms Covered

### Binary Heap as a Priority Queue
- `peek()` returns the extreme element in Θ(1)
- `push` amortised Θ(1), `pop` O(log n)
- **Why amortised:** when a node at height `h` is pushed, it sifts up at most `h` levels; summing `h` over all `n` insertions gives `Θ(n)`, hence O(1) average. The worst single insertion is `O(log n)` (inserting into a perfectly balanced tree at the deepest level).

### Floyd's Build (Θ(n))
```java
for (int i = (n >>> 1) - 1; i >= 0; i--) siftDown(a, i, n);
```
**Proof sketch:** a node at height `h` costs `O(h)`. There are at most `⌈n/2^(h+1)⌉` nodes at height `h`, and the deepest nodes have height 0. So

```
Σ_{h=0}^{⌊log n⌋} ⌈n / 2^(h+1)⌉ · O(h)
≤ n · Σ_{h≥0} h / 2^(h+1)
= n · Σ h / 2^{h+1}
= n · 1        (since Σ h x^h = x/(1-x)^2 at x=1/2 gives Σ h/2^{h+1} = 1)
= Θ(n)
```

The key cancellation: the `2^h` growth of the denominator beats the linear growth of `h`. Contrast with building by `n` pushes: `Θ(n log n)`.

### Heap Sort
```
1. Build a max-heap: O(n)
2. For i = n-1 down to 1:
       swap(a[0], a[i])       // move current max to the sorted tail
       siftDown(a, 0, i)      // restore heap on the shrinking prefix
```
- Θ(n log n) **guaranteed** — no input can unbalance a heap.
- **O(1) space** and no allocation.
- **Unstable** (the `swap(a[0], a[i])` moves the max across equal elements).
- **Poor cache behaviour** — `siftDown` jumps around the array (`2i+1`), unlike the sequential scans of merge/quick sort.

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/heap-sort/` | Heap + heapsort implementations |
| `src/test/java/com/alglab/heap-sort/` | JUnit 5 tests |
| `SOLUTION/` | Worked exercise solutions |
| `TESTS/` | Randomised property tests |
| `BENCHMARK/` | Heapsort vs quicksort vs mergesort |
| `MINI_PROJECT/` | Animated heap visualiser |
| `REAL_WORLD_PROJECT/` | Priority-queue job scheduler |
| `CHALLENGE/` | D-ary heaps, pairing heap, binomial heap |
| `DIAGRAMS/` | Array↔tree layouts, sift-down traces |