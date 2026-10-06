# Exercises — Heap Sort

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.heap`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Trace `siftDown`

Using the swap version on `[9, 7, 8, 3, 5, 2, 1]` (already a valid min-heap at the root, so re-heapify from index 0 with value `9`):

| step | `root` | children | chosen smallest | action |
|------|--------|----------|------------------|--------|
| 1 | 0 | 7 (idx1), 8 (idx2) | 7 (idx1) | swap(0,1) → `7 9 8 3 5 2 1`, root=1 |
| 2 | 1 | 3 (idx3), 5 (idx4) | 3 (idx3) | swap(1,3) → `7 3 8 9 5 2 1`, root=3 |
| 3 | 3 | none (leaves start at 3) | — | `smallest == root`, return |

Result `[7, 3, 8, 9, 5, 2, 1]` — valid min-heap (every parent ≤ children: `7≤8,7≤2; 3≤9,3≤5`).

**Then re-run with the hole version** and confirm the *same* final array. Hole version after step 1: `value = 9`, `hole = 0`, picks `7`; writes `a[0] = 7`, `hole = 1`; picks `3`; writes `a[1] = 3`, `hole = 3`; loop exits (leaf); `a[3] = 9`. Identical. ✓

**Edge cases:** `size = 1` → loop condition `2*root+1 < size` false, no work. `root` a leaf → no work. All elements equal → picks no child, returns immediately.

---

## Exercise 2 — Prove the leaf formula

Empirically verify for `n = 1..200` that the set of leaf indices is exactly `[n/2, n)` and the last internal index is `n/2 - 1`.

```java
static List<Integer> leaves(int n) {
    List<Integer> r = new ArrayList<>();
    for (int i = 0; i < n; i++) if (2*i + 1 >= n) r.add(i);
    return r;
}
```

Then answer in writing: for `n = 7` and `n = 8`, what are the leaf sets and the last internal index? (`n=7`: leaves `{3,4,5,6}`, last internal `2`. `n=8`: leaves `{4,5,6,7}`, last internal `3`.) Explain why the answer changes from 4 to 4 leaves while the tree gains a node.

---

## Exercise 3 — Floyd build vs repeated push

Implement both:
```java
static void buildFloyd(int[] a)  { for (int i = (a.length >>> 1) - 1; i >= 0; i--) siftDown(a, i, a.length); }
static void buildPush(int[] a)   { MinHeap<Integer> h = new MinHeap<>(); for (int v : a) h.push(v);
                                  for (int i = 0; i < a.length; i++) a[i] = h.pop(); }
```

Instrument with a comparison counter and record, for `n = 10⁴ … 10⁶`:
- Floyd: comparisons and the *distribution* of sift depths per node.
- Push: comparisons.

**Verify the Θ(n) claim by bucketing.** Count how many nodes required exactly `h` swaps. You should see roughly `n/2` nodes with `h = 0`, `n/4` with `h ≤ 1`, etc. Produce a histogram and check that `Σ counts[h]·h ≈ 0.94 n`.

**Then compute the ratio** `comparisons_push / comparisons_floyd` and check it grows roughly like `log n`.

---

## Exercise 4 — Heap sort correctness harness

Write `boolean isSorted(int[] a)` and `boolean isPermutationOf(int[] input, int[] output)` (multiset equality, e.g. via `long` sum of `(value * 1_000_003L)` plus a `long[]` count array for exactness). Fuzz heapsort over 10 000 random arrays with `n ∈ [0, 30]` and values from `{-5..5}` (many duplicates).

**Expected**: `isSorted == true` and multiset equality always holds.

**Then the deliberate bug hunt.** Insert each of these and record which fuzz test catches it and the *smallest n* that catches it:
1. `siftDown(a, 0, a.length)` instead of `siftDown(a, 0, end)` in heapsort.
2. `for (int i = 1; i < (n >>> 1); i--)` instead of `for (int i = (n >>> 1) - 1; i >= 0; i--)` in build.
3. `<=` instead of `<` in the child comparison.
4. `swap(a, 0, --end)` combined with `siftDown(a, 0, end)`.

Write a regression test for each.

---

## Exercise 5 — Instability of heapsort

Build 4 records `(value, id)` all with the same value, run heapsort, and show ids come out permuted. Then find the **smallest** input where heapsort reorders two equal elements.

**Hint:** you need at least 3 elements with at least 2 equal, and the equal pair must interact with a `swap(a[0], end)`. Search exhaustively over all arrays of length 3 and 4 with values in `{0,1}`; report the smallest witness.

---

## Exercise 6 — Hole vs swap: measure

Implement both `siftDown` variants, wrap each in a counter of *array writes*, and compare:

| | writes per descent of depth `h` |
|---|---|
| swap | `2h` |
| hole | `h + 1` |

Then time both on `int[10⁷]` heapsort. Report the ratio and confirm the write counts are exactly as predicted (assert them in the test).

---

## Exercise 7 — `pop` and the memory-leak pitfall

Implement `pop()` **without** `store[size] = null`, then run: push 1 000 000 objects of 1 KB each, pop them all, drop all references, force `System.gc()`, and print `Runtime.totalMemory() - Runtime.freeMemory()`.

**Prediction:** retained heap stays ≈ 1 GB because the backing array still references every object.
**With the fix:** retained heap drops to near zero.

This is the most production-relevant exercise in the lab — it is the same class of bug as `ArrayBlockingQueue`'s discarded-node reference.

---

## Exercise 8 — `removeAt(i)`

Implement `boolean removeAt(int i)`:

```java
E removed = store[i];
store[i] = store[--size];
store[size] = null;
if (cmp.compare(store[i], store[parent(i)]) < 0) siftUp(i);   // moved element is too small -> go up
else siftDown(i);                                            // else it may be too big -> go down
if (size == 0) return true;                                   // after store[0] = store[size]
```

**Why must you choose?** If you always `siftDown`, the element can end up smaller than its parent, breaking the heap. If you always `siftUp`, it can end up larger than a child.

**Edge cases:** `i == 0` (always sift down, no parent); `size` becomes 0; `i >= size` → `IndexOutOfBoundsException`.

Then implement `remove(Object e)` in `O(log n)` using an **index map** `IdentityHashMap<E, Integer>` maintained on every swap — and explain why `java.util.PriorityQueue` does *not* do this (memory cost `O(n)` and hashCode instability under mutation).

---

## Exercise 9 — D-ary heap

Implement `DaryHeap` with configurable `d` and benchmark `d ∈ {2, 3, 4, 6, 8, 16}` for `n = 10⁵, 10⁶, 10⁷`.

**Predictions to check:**
- `n = 10⁵`: binary wins (everything fits in cache).
- `n = 10⁷`: `d = 4` wins by ~25%.
- `n = 10⁷`: `d ≥ 8` loses (comparisons `O(d log_d n)` grow as `d/log d`).

Compute the actual height `log_d n` for each and correlate with the timing curve. Then explain why `d = 4` is the answer you would put in a real system.

---

## Exercise 10 — Top-k with a heap

Implement `static <T> List<T> topK(List<T> input, int k, Comparator<? super T> cmp)` using a **min-heap of size `k`**:

```java
PriorityQueue<T> pq = new PriorityQueue<>(k, cmp);
for (T t : input) {
    pq.offer(t);
    if (pq.size() > k) pq.poll();     // evict the smallest
}
return new ArrayList<>(pq);
```

**Complexity:** `Θ(n log k)` time, `O(k)` space.

**Compare** with the alternatives and record all three timings on `n = 10⁷`, `k = 100`:
| Approach | Time | Space |
|----------|------|-------|
| Full sort | `Θ(n log n)` | `Θ(n)` |
| This heap | `Θ(n log k)` | `O(k)` |
| Quickselect | `Θ(n)` expected | `O(k)` (in-place partial) |

**Then answer the real question:** why is quickselect *not* what you use? (Because it destroys the input and needs the full array in memory; a streaming source can only use the heap.)

**Trace** `[5, 1, 9, 3, 7]` with `k = 3`, `cmp = natural`, keeping a min-heap of the 3 largest:
| step | offer | size | poll? | heap contents |
|------|-------|------|-------|---------------|
| 1 | 5 | 1 | no | [5] |
| 2 | 1 | 2 | no | [1, 5] |
| 3 | 9 | 3 | no | [1, 5, 9] |
| 4 | 3 | 4 | yes (evict 1) | [3, 5, 9] |
| 5 | 7 | 4 | yes (evict 3) | [5, 7, 9] |

---

## Exercise 11 — Parallel heapsort

Bucket-parallel heapsort: partition the array into `p` contiguous blocks, build a max-heap in each, then repeatedly take the global max. Answer in writing why this is a bad idea (the merge of `p` heap roots costs `O(p log p)` per extraction, so total `Θ(n log n log p)`).

Then implement **the right** alternative: **parallel selection** — split into `p` blocks, heapsort each in parallel, then `k`-way merge using a heap of size `p`. Total `Θ(n log(n/p) + n log p) = Θ(n log n)` with `Θ(n log(n/p)/p)` parallel depth. Measure 1/2/4/8 threads on `n = 10⁸` and report the speedup curve versus Amdahl's prediction.

---

## Exercise 12 — Debugging drills

1. `siftDown` with `if (l < size && a[l] < a[smallest]) smallest = l; if (r < size && a[r] < a[smallest]) smallest = r;` — this one is *correct*. Now remove the `l < size` guard from the second line. What happens on `n = 2`?
2. `buildMaxHeap` with `for (int i = (n - 1) >>> 1; i >= 0; i--)`. Which node is skipped and what input exposes it? (For `n = 9` this starts at `i = 4`, skipping node `3`.)
3. Heapsort where the outer loop is `for (int end = n - 1; end >= 0; end--)` (one extra iteration). What breaks?
4. `MinHeap.push` doing `store[++size] = e; siftUp(size);` — find the off-by-one. (The element is placed at `size+1` instead of `size`, leaving a `null` hole at `size` and sifting the wrong node.)

---

## Exercise 13 — Deliverable

`MINI_PROJECT/HeapViz.java`: an ASCII renderer that prints the heap as a tree with indices, and animates `push`, `pop`, and the Floyd build. Include a `heapSort` mode that colours each extracted maximum. Then write a one-page `REAL_WORLD_PROJECT/README.md` describing a **production priority-queue job scheduler**: metrics to instrument (queue depth p50/p99, task latency, eviction rate), the heap variant you'd choose and why, and how you would prevent the two classic failures (unbounded priority inversion via aging, and starvation via a FIFO tiebreaker on insertion counter).