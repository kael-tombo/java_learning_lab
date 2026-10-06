# Theory — Heap Sort

A binary heap is simultaneously a **priority queue** (get the extreme element fast) and a **sorting scaffold** (heap sort). Its distinguishing property is that the *structure* (shape) is fixed by the array layout, so no explicit tree exists and no allocation is ever required.

---

## 1. Structure: the complete binary tree and its array encoding

A **complete** binary tree is one where every level except possibly the last is completely filled, and the last level is filled left to right. This is exactly the shape an array-backed heap needs: no gaps, so no pointers.

For a 0-based array `a` of size `n`:

| Relation | Formula |
|----------|---------|
| left child of `i` | `2i + 1` |
| right child of `i` | `2i + 2` |
| parent of `i` | `(i - 1) / 2` (integer division, floor) |
| leftmost descendant depth | `⌊log₂ i⌋` |
| last node | `n - 1` |
| last **internal** node | `⌊n/2⌋ - 1` |

**Proof of the last-internal-node formula.** Nodes `0 .. ⌊n/2⌋-1` have at least one child because `2i+1 ≤ n-1` ⇔ `i ≤ (n-2)/2` ⇔ `i ≤ ⌊n/2⌋ - 1` (for even `n`) or `i ≤ (n-3)/2` (for odd `n`). Both collapse to `⌊n/2⌋ - 1`. This single fact is what makes Floyd's build linear — you only sift internal nodes.

**Why the shape matters for locality.** Depth `d` contains indices `[2^d - 1, 2^{d+1} - 2]`. Level `d` occupies a contiguous byte range of size `2^d · sizeof(T)`, so each level is contiguous in memory and levels are aligned to powers of two. The traversal `siftDown` hops *within* a level horizontally and moves down a level — hence poor temporal locality compared with merge sort's two linear streams. This is the single biggest reason heap sort underperforms despite equal asymptotics.

**Array ↔ tree example** for `[9, 7, 6, 3, 5, 2, 4]`:

```
        9                  (0)
      /   \
     7     6               (1, 2)
    / \   / \
   3   5 2   4             (3, 4, 5, 6)
```

---

## 2. The heap property and its exact scope

**Max-heap property (min-heap with `<=` instead of `>=`):**

> For every index `i` with `2i+1 < n`: `a[i] >= a[2i+1]` **and** (if `2i+2 < n`) `a[i] >= a[2i+2]`.

Three consequences people routinely get wrong:

1. **The property is purely local — parent vs its own children only.** It says *nothing* about a node vs its grandchildren, siblings, cousins, or any other node. `[9, 1, 8]` is a valid max-heap even though `9 > 8 > 1`.
2. **Being a heap does NOT mean sorted.** In order is a total order on all pairs; heap order is a partial order on edges only.
3. **The root is always the global maximum.** Proof: every node has a path to the root through non-decreasing edges (`a[parent] >= a[child]`), so `a[root] >= a[x]` transitively. This is the *only* global property.

Heap order is a **partial order**, and one partial order has many linear extensions — hence heapsort's instability and the many valid "sorted-by-heap" configurations.

---

## 3. `siftUp` — restoring the property upward

**Precondition:** the heap is valid except that a new element sits at leaf position `k`, and all of its ancestors up to `parent(k)` are still valid.
**Postcondition:** the heap is valid again.

```java
void siftUp(int k) {
    while (k > 0) {
        int parent = (k - 1) >>> 1;
        if (cmp(a[k], a[parent]) <= 0) break;   // parent already wins -> done
        swap(a[k], a[parent]);
        k = parent;
    }
}
```

**Loop invariant:** after `t` iterations, the element being sifted has moved up `t` levels and the heap property holds everywhere **except possibly along the path from that element to the root**. This is the standard "path invariant" that makes heap operations provably correct.

**Termination:** `k` strictly decreases toward 0, so at most `⌊log₂ n⌋` swaps.

**Cost:** `O(h)` where `h = ⌊log₂(k+1)⌋` is the height of the insertion position.

---

## 4. `siftDown` — restoring the property downward

**Precondition:** `k` may violate the property with respect to its children; all subtrees hanging off the path from `k` are already valid heaps.
**Postcondition:** the whole subtree rooted at `k` is a valid heap.

```java
void siftDown(int k, int size) {
    while (true) {
        int l = 2*k + 1, r = l + 1, largest = k;
        if (l < size && cmp(a[l], a[largest]) > 0) largest = l;
        if (r < size && cmp(a[r], a[largest]) > 0) largest = r;
        if (largest == k) return;              // heap property restored
        swap(a[k], a[largest]);
        k = largest;
    }
}
```

**Key insight — "compare with the current best, not with the parent":** if you swap with the parent first and then re-compare against the parent, you perform two comparisons per level. Choosing the larger child directly costs two comparisons per level but only one swap and *guarantees* the swapped-in child is the correct one.

**"Hole" variant** (fewer writes, the classic textbook form): move the hole down first, then place the value at the bottom. Halves memory traffic on the descent path — the value travels down in a register rather than being written at every level.

```java
void siftDownHole(int k, int size) {
    int hole = k;
    int value = a[k];
    while (2*hole + 1 < size) {
        int child = 2*hole + 1;
        if (child + 1 < size && cmp(a[child+1], a[child]) > 0) child++;
        if (cmp(value, a[child]) >= 0) break;
        a[hole] = a[child];
        hole = child;
    }
    a[hole] = value;
}
```

**Termination:** `k` strictly increases toward a leaf, so at most `⌊log₂ n⌋` iterations. This *pathological worst case* (the new element always beats both children) is precisely why "repeated `push` is `O(n log n)`" — see §5.

---

## 5. Amortised analysis of `push`

**Worst case:** `Ω(log n)`. Build a perfect heap by inserting elements in BFS order; the last insertions start at the deepest level and must travel to the root.

**Amortised:** consider the sequence of `n` pushes. The `i`-th push performs at most `⌊log₂ i⌋` swaps (it starts at depth `⌊log₂ i⌋`). Total:

```
Σ_{i=1}^{n} ⌊log₂ i⌋  ≤  n·log₂ n − (n−1) + O(log n)   ≈  n log n
```

That gives O(log n) amortised, which is **wrong** — the standard result is O(1). The tighter argument:

```
Σ_{i=1}^{n} ⌊log₂ i⌋  =  Σ_{h≥1} #{ i ≤ n : ⌊log₂ i⌋ ≥ h }  =  Σ_{h≥1} (n − 2^h + 1)
```

Wait — that is again `n log n - 2n`. The resolution is that the bound `⌊log₂ i⌋` per push is far too pessimistic for *sequential* pushes. The standard amortised argument uses the **potential method** with potential `Φ = size` (number of elements):

- **Amortised cost of `push`** = actual cost + ΔΦ.
- `push` may cause `s` swaps where `s ≤ ⌈log₂(size+1)⌉`. But the amortised cost is *not* `s`; rather, sum over all pushes, `Σ s ≤ 2n`, because the swaps move elements along tree edges and each edge is "charged" to the *deep* element it passes.

The rigorous statement (standard result, e.g. Weiss): **n pushes into an initially empty heap cost Θ(n) total**, because the total number of levels traversed by all sifts is `Σ_{h} 2^h = 2n`. Equivalently: at height `h` there are at most `2^h` nodes, each of which can be traversed at most twice (once going up, once coming down), so total work `≤ Σ 2^h = 2n`.

**Individual worst case stays `O(log n)`** — inserting a new maximum into a full heap is `Θ(log n)`. Amortised ≠ worst case.

**`pop` is `O(log n)` both amortised and worst** — you always sift the last element down from the root, and the worst case (it belongs at the bottom) is always available.

**Consequence for heapsort:** building by repeated `push` gives `Θ(n log n)`; building by Floyd's bottom-up method gives `Θ(n)`. For sorting, Floyd wins.

---

## 6. Floyd's build: the Θ(n) proof

```java
void buildHeap(int[] a, int n) {
    for (int i = (n >>> 1) - 1; i >= 0; i--) siftDown(a, i, n);
}
```

**Correctness argument:** process internal nodes in **decreasing index order**. When we `siftDown(i)`, every child of `i` has index `> i` and hence has already been made a valid heap. Its whole subtree is therefore a valid heap. `siftDown` then only needs to fix the edges from `i` downward. By induction over decreasing `i`, the entire array is a valid heap at the end.

**Cost.** A node at height `h` requires at most `h` swaps, i.e. `O(h)` work. The number of nodes at height exactly `h` is `⌈n/2^(h+1)⌉` (nodes `2^h-1 .. 2^{h+1}-2`). So:

```
            ⌊log n⌋   ⌈n/2^(h+1)⌉ · O(h)
T(n)  =     Σ    O  (                              )
            h = 0
      ≤ n · Σ_{h≥0}  O(h / 2^(h+1))
      = n · O(1)                      because  Σ_{h≥0} h/2^(h+1) = 1
      = Θ(n)
```

The generating function: `Σ_{h≥0} h x^h = x/(1-x)²`, at `x = 1/2` gives `Σ h/2^{h+1} = 1`. **The exponential growth of the denominator cancels the linear growth of the height.** That is the entire content of the "build a heap in linear time" result.

**Sharpness.** The Θ(n) bound is tight because in the worst case (e.g. reverse-sorted input, or an input engineered so each node must descend fully) the sum is dominated by the many shallow-but-numerous nodes. No build can be `o(n)` because it must at least read every element.

**Counter-intuitive consequence:** the *average* `siftDown` is cheap. Most nodes are leaves (half of all nodes) and `siftDown` on a leaf costs one comparison and returns immediately.

---

## 7. Heap sort

```
heapsort(a):
    n = a.length
    buildMaxHeap(a, n)                 // Θ(n)
    for (i = n - 1; i >= 1; i--) {
        swap(a[0], a[i])               // put the max at the end of the unsorted region
        siftDown(a, 0, i)              // size shrinks: a[0..i-1] is the remaining heap
    }
```

**Loop invariant:** at the start of iteration `i`, `a[0..i]` is a valid max-heap of `i+1` elements, and `a[i+1..n-1]` contains the `n-i-1` largest elements in sorted order.

**Correctness sketch:** by the invariant, `a[0]` is the maximum of `a[0..i]`. Swapping it to position `i` and shrinking the heap region by one places the next-largest element in its final position. Inductively, `a[1..n-1]` ends sorted.

**Time:** build `Θ(n)` + `n-1` iterations × `siftDown` ≤ `O(log n)` each = **`Θ(n log n)` in all cases**. There is no best case: even a sorted input costs `Θ(n log n)`, since the max is at the root and must be swapped to the end each time.

**Properties:**

| Property | Value | Why |
|----------|-------|-----|
| Space | **O(1)** | In-place, no allocation |
| Stability | **No** | `swap(a[0], a[i])` moves the max across any equal elements sitting near the root |
| Worst case | `Θ(n log n)` guaranteed | Heap shape is data-independent |
| In-place | Yes | Only index arithmetic |
| Adaptivity | No | Sorted input costs the same as random |

---

## 8. Why heap sort loses to quicksort in practice

Asymptotically equal, yet `Arrays.sort` (dual-pivot quicksort) is ~30% faster on `int[]`. The reasons, in order of impact:

1. **Cache misses.** `siftDown` visits indices `2k+1`, `2k+2`, `4k+3`, ... For `n = 10^7` the array is 40 MB — far beyond L3. Each level of the descent is a different cache line. Quick sort's partition walks memory *sequentially*.
2. **Branch misprediction.** The `largest = ...` selection has data-dependent branches that a modern predictor cannot learn. Quick sort's inner loop is a simple, highly predictable comparison.
3. **Writes.** The hole variant of `siftDown` writes one element per level; a swap writes two.
4. **Constant factors in `n log n`.** Heapsort does ~`2 log n` comparisons per extraction; quicksort does ~`1.39 log n`.

**Where heapsort still wins:**
- **Guaranteed `O(n log n)`** with no probabilistic argument — the right choice for a *real-time* or *adversarial-input* system where you cannot accept a stack overflow or a timeout.
- **O(1) space** when you cannot afford a Θ(n) buffer.
- **Large heaps where only the extreme matters** — `PriorityQueue`, `nsmallest`/`nlargest` over iterators, k-way merge, Dijkstra's priority queue.

---

## 9. Beyond the binary heap

| Structure | `push` | `pop` | `findMin` | Notes |
|-----------|--------|-------|-----------|-------|
| Binary heap | O(1) amortised | O(log n) | O(1) | cache-unfriendly |
| D-ary heap (d=4) | O(log₄ n) | O(4 log₄ n) | O(1) | fewer levels, more comparisons; **better cache behaviour**, wins for d = 4 on real hardware |
| Pairing heap | O(1) | O(log n) amortised | O(1) | best empirical `pop`, poor worst case, bad locality |
| Binomial heap | O(log n) | O(log n) | O(1) | meldable, used in union-find variants |
| Fibonacci heap | O(1) amortised | O(log n) amortised | O(1) | needed for Dijkstra with decrease-key to reach `O(m + n log n)` |
| Skew heap | O(log n) amortised | O(log n) amortised | O(1) | self-adjusting, meldable, simplest to implement correctly |
| Leftist heap | O(log n) | O(log n) | O(1) | `meld` in `O(log n)` guaranteed, meldable |

**Why D-ary heaps win in practice:** with fanout `d`, height is `log_d n = log₂ n / log₂ d`. For `d = 4` and `n = 10^7`, height is `≈ 11.6` instead of `≈ 23.3`, so `siftDown` touches half as many cache lines, and the 4 sibling elements almost always share cache lines. Measured: a 4-ary heap beats a 2-ary heap by ~25% for n > 10⁶.

**Why Fibonacci heaps exist:** Dijkstra with a decrease-keyable priority queue needs `push`/`decreaseKey` to be Θ(1) amortised to achieve `O(m + n log n)`. A binary heap gives `O((m + n) log n)`. The constants are terrible and the structure is notoriously hard to implement correctly, so binary heaps are used in practice and the theoretical gain is ignored unless `m >> n`.