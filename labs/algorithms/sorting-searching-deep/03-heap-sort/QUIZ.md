# Quiz — Heap Sort

15 questions. Each key gives the reason.

---

## Q1
Why is Floyd's bottom-up heap build `Θ(n)` while building by `n` successive pushes is `Θ(n log n)`?

<details><summary>Answer</summary>

In Floyd's build, **most nodes are near the root of the tree but few are deep**: a node at height `h` costs `O(h)` and there are only `n/2^(h+1)` of them, so total work is `n · Σ h/2^(h+1) = n · 1 = Θ(n)`.

Successive `push` costs `O(log i)` *regardless of the element's actual height*, so `Σ log i = Θ(n log n)`.

**Key:** the exponential decay of node count by depth cancels the linear growth of depth. It is not that "heaps are cheap to build" — it is that *deep nodes are rare*.
</details>

## Q2
State the heap property precisely. Does it imply the array is sorted?

<details><summary>Answer</summary>

For every index `i` with valid children: `a[i] ≥ a[2i+1]` and `a[i] ≥ a[2i+2]`.

**It does not imply sortedness.** It is a *local* condition (parent vs own children). `[9, 1, 8]` is a valid max-heap: `9 ≥ 1` and `9 ≥ 8`, but the array is not sorted.

Only the root is globally extremal, and that follows transitively along the path to the root, not from the local rule alone.
</details>

## Q3
In heapsort, why must you pass the *shrinking* size to `siftDown` rather than `a.length`?

<details><summary>Answer</summary>

After `swap(a, 0, end)` the element at `a[end]` is already in its **final sorted position** and must never be touched again. Passing `a.length` lets `siftDown` treat `a[end..n-1]` as part of the heap, move those elements, and destroy the sorted suffix.

This is the classic heapsort bug: it produces output that often *looks* sorted on small inputs, so it survives casual testing.
</details>

## Q4
`push` into a heap is `O(log n)` worst case but `O(1)` amortised. Explain how both can be true.

<details><summary>Answer</summary>

**Worst case** is a single operation: insert a new maximum into a full heap and it travels from depth `⌊log₂ n⌋` to the root.

**Amortised** averages over the whole sequence: over `n` pushes, each tree edge is traversed at most twice (once by an element going up, once by the displaced parent going down), so total crossings `< 4n`, giving `< 4` per operation.

Amortised ≠ worst case. A pathological push cannot be repeated indefinitely because each one mutates the tree.
</details>

## Q5
What is the last internal node index in a heap of `n` elements, and why does the build loop start there?

<details><summary>Answer</summary>

**`⌊n/2⌋ − 1`.** Nodes at index `≥ ⌊n/2⌋` have no children, so `siftDown` on them costs one comparison and returns immediately — 50% of the array is skipped for free.

**Trap:** `(n - 1) >>> 1` gives a different answer when `n` is odd. For `n = 9`: `(9>>>1)-1 = 3` (correct), but `(9-1)>>>1 = 4`, which skips node 3 and leaves the heap invalid.
</details>

## Q6
Why is heapsort unstable? Give the mechanism.

<details><summary>Answer</summary>

`swap(a[0], end)` moves the maximum element from index 0 to index `end`, crossing over every element between them — including any element equal to it. That crossing reverses the original relative order of equal keys.

Merge sort avoids this because it merges two *sorted runs* by copying elements to fresh positions, never moving an element past an equal one.
</details>

## Q7
Heapsort and mergesort are both `Θ(n log n)`. Why is heapsort ~30% slower on large primitive arrays?

<details><summary>Answer</summary>

**Cache misses.** `siftDown` visits `2k+1, 2k+2, 4k+3, ...` — a different cache line per level. For `int[10⁷]` (40 MB, far beyond L3) that is ~23 misses per element extracted.

Mergesort streams two linear arrays; quicksort partitions sequentially. Heapsort's *comparison count* is nearly optimal (≈ 2 n log n vs the `n log n - 1.44n` floor) — it loses on memory access, not on comparisons.
</details>

## Q8
Heapsort's loop invariant and proof of correctness in three lines.

<details><summary>Answer</summary>

**Invariant:** at the top of iteration `end`, `a[0..end]` is a valid max-heap and `a[end+1..n-1]` holds the `n-1-end` largest elements in ascending final order.

**Step:** `a[0]` is the maximum of `a[0..end]`; swapping it to `end` and shrinking the heap places the next-largest element in its final position, and `siftDown` restores the invariant for `a[0..end-1]`.

**Termination:** at `end = 0` the sorted suffix is the whole array.
</details>

## Q9
Why must the Floyd build process internal nodes in *decreasing* index order?

<details><summary>Answer</summary>

Because a node's children have indices `2i+1, 2i+2 > i`. Processing in decreasing index order guarantees both children — and therefore their entire subtrees — are already valid heaps when `i` is processed. So `siftDown(i)` only has to fix the edges from `i` downward, and it can never break a child it moves into a valid subtree.

An increasing order visits the parent before the children, giving `Θ(n log n)` *and* no guarantee of validity.
</details>

## Q10
What is the amortised height-crossing bound proving `O(1)` `push`? What fraction of all pushes actually cost zero swaps?

<details><summary>Answer</summary>

Over `n` pushes the total number of level crossings is at most `2 · 2^h` summed over heights `h = 0..H`, i.e. `2(2^(H+1) − 1) < 4n`. Divided by `n`: `< 4` per push.

**Zero-swap fraction:** measuring this is empirical, but the analysis shows the *majority* of pushes do not travel to the root; for random insertions the vast majority terminate within the first level or two. Instrument your `siftUp` and report the histogram — it is the cleanest empirical confirmation of amortised `O(1)` you can get.
</details>

## Q11
You need `O(1)` `peek`, `O(1)` amortised `push`, and `O(log n)` `pop` on `10⁷` elements. Which heap, and what beats it?

<details><summary>Answer</summary>

A **4-ary heap** (`D = 4`).

Binary heap height at `n = 10⁷` is `log₂ n ≈ 23.3`; 4-ary height is `log₄ n ≈ 11.7`. Each descent touches half as many cache lines, and the 4 siblings almost always share one line. Measured ≈ 25% faster than binary at that size.

**Pairing heaps** have better empirical `pop` but worse locality and no worst-case guarantee. Below `10⁶` elements plain binary wins — everything is cached.
</details>

## Q12
Why can `java.util.PriorityQueue` not support `decreaseKey`, and how do you implement Dijkstra with it?

<details><summary>Answer</summary>

Supporting `decreaseKey` requires knowing an element's **index in the backing array** to sift it, which means an auxiliary `O(n)` map. `PriorityQueue` avoids that memory cost.

The standard workaround is **lazy deletion**: push a new `(dist, node)` entry whenever a shorter path is found, and on pop skip entries whose stored distance no longer equals `dist[node]`. Cost: up to `m` entries instead of `n`, so `O(m log m)` rather than `O(m + n log n)`.
</details>

## Q13
Prove the upper bound `Σ_{h≥0} h/2^(h+1) = 1` and state its role.

<details><summary>Answer</summary>

Using `Σ_{h≥0} h x^h = x/(1-x)²` with `x = 1/2`:

```
Σ_{h≥0} h/2^(h+1) = x · x/(1-x)² = (1/2)(1/2)/(1/2)² = 1
```

**Role:** it is the constant factor in Floyd's bound. Total build work `≤ n · 1 = n`, giving `Θ(n)`. The identity is the entire reason the sum converges despite `h` growing without bound — the `2^h` denominator wins.
</details>

## Q14
You have `n = 10⁸` and a hard memory cap that forbids allocating a `Θ(n)` buffer. Which sort, and what is the guarantee?

<details><summary>Answer</summary>

**Heapsort** — `Θ(n log n)` worst case with `O(1)` auxiliary space.

Alternatives rejected:
- Mergesort/timsort: `Θ(n)` buffer.
- Quicksort: `O(log n)` stack *if* you recurse on the smaller side; `Θ(n²)` worst-case time and possible `StackOverflowError` without that fix.
- Radix sort: needs `Θ(n)` counts array.

Heapsort is the textbook "guaranteed `O(n log n)`, no allocation" answer, and it is the correct one when an adversarial input is a real threat (a timeout *is* an outage).
</details>

## Q15
Your streaming top-k system processes `10⁷` items with `k = 100`. Why is quickselect (theoretically `Θ(n)`) not the right choice, and what do you use?

<details><summary>Answer</summary>

Quickselect needs the whole array resident and it **destroys the input's order**. A streaming source can only be consumed once.

Use a **min-heap of size `k`**: offer each item, and when size exceeds `k`, evict the minimum. Time `Θ(n log k)`, space `O(k)`.

If instead you have all `10⁷` items in memory and only need them once, quickselect *is* better (`Θ(n)` vs `Θ(n log k)`) — so the deciding factor is **streaming vs in-memory**, not asymptotic preference.
</details>