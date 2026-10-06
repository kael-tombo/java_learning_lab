# Exercises — Order Statistics

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.orderstats`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Trace quickselect

`a = [7, 3, 9, 1, 5, 8, 2, 6]`, `k = 3` (4th smallest). Assume the pivot is the **middle element** `a[mid]` each round for hand-tracing (then check your randomised version against the trace).

| round | `[lo, hi]` | pivot | partitioned array | pivot index | action |
|-------|------------|-------|-------------------|-------------|--------|
| 0 | [0, 7] | `a[3]=1` | `[1, 3, 2, 5, 6, 8, 7, 9]` | 0 | `p=0 < 3` → `lo=1` |
| 1 | [1, 7] | `a[4]=6` | `[1, 3, 2, 5, 6, 8, 7, 9]` | 4 | `p=4 > 3` → `hi=3` |
| 2 | [1, 3] | `a[2]=2` | `[1, 2, 3, 5, ...]` | 1 | `p=1 < 3` → `lo=2` |
| 3 | [2, 3] | `a[3]=5` | `[1, 2, 3, 5, ...]` | 3 | `p=3 == k` → return `5` |

**Verify:** sorted array is `[1,2,3,5,6,7,8,9]`, index 3 is **5**. ✓

Now instrument: count comparisons and array writes. Confirm `comparisons ≈ 3.4 n = 27` for `n = 8`... that's `Θ(1)`-sized so don't expect the constant to show. Instead measure at `n = 10⁶` and check the ratio to `Arrays.sort`.

---

## Exercise 2 — Prove the `3.4n` constant

Instrument quickselect with a comparison counter and run over 200 random permutations of `n = 10⁵`. Report:

| statistic | value |
|-----------|-------|
| mean comparisons / n | expect ≈ **3.386** |
| min / n | |
| max / n | |
| std dev / n | |

Repeat for:
- random pivot
- median-of-3 pivot
- ninther pivot
- first-element pivot (will be `Θ(n log n)` on random input? — **no**, it is still `Θ(n)` expected on *random* input; it is only `Θ(n²)` on *sorted* input. Verify and explain the asymmetry.)

Then build a **median-of-3 killer**: construct recursively the array where the median-of-3 is always the maximum. Verify it gives `Θ(n²)` comparisons on median-of-3 quicksort but `≈ 3.4n` on randomised quicksort. **This is the single most important experiment in the lab.**

---

## Exercise 3 — Stack safety experiment

Implement the **recursive** quickselect naively:

```java
static int selectRec(int[] a, int lo, int hi, int k) {
    if (lo == hi) return a[lo];
    int p = partition(a, lo, hi);
    if (p == k) return a[p];
    return p < k ? selectRec(a, p + 1, hi, k) : selectRec(a, lo, p - 1, k);
}
```

Run on `int[100_000]` sorted ascending with a **first-element** pivot. Catch the `StackOverflowError`.

Then implement the smaller-side-recurse version and show it completes with `O(log n)` stack. Measure stack depth by instrumenting a counter in the recursive frame.

**Answer in writing:** what is the *time* of the sorted input after the fix? (Still `Θ(n²)`.) Why does the stack fix not fix the time, and which one matters more in a service?

---

## Exercise 4 — Median-of-medians, traced

Implement it and trace on `a = [5, 4, 3, 2, 1, 9, 8, 7, 6, 10]` (n = 10, exactly two groups of 5) for `k = 4`:

1. Groups: `[5,4,3,2,1]` → sorted `[1,2,3,4,5]` → median `3`; `[9,8,7,6,10]` → sorted `[6,7,8,9,10]` → median `8`.
2. Medians `[3, 8]` → median of medians = `8` (upper median of a 2-element array) — **or `3` if you take the lower.** Document your convention.
3. Partition around the pivot. Show the guarantee: at least `3n/10 = 3` elements discarded on each side.

**Count comparisons at every level** and verify `≤ 3.386 n` for `n = 10⁶` (allow overhead; the bound is asymptotic).

**Also:** measure the wall-clock penalty vs randomised quickselect. Expect ~5–6×. Then answer: **in what situation would you actually ship median-of-medians?** (Hint: think about move-to-front, worst-case guarantees in real-time systems, and TDD.)

---

## Exercise 5 — Fenwick tree

Build a Fenwick over a frequency array of size `n = 1000` with values in `[0, 999]`, then:
- `add(i, 1)` for each of 10 000 randomly chosen indices (with duplicates).
- Query `findByOrder(k)` for every `k` in `1..total` and check against a linear scan over the cumulative counts.

**Verify the algorithm's crucial line.** Remove `k -= tree[next];` and find a failing `k`. Then explain in one sentence why binary lifting is `Θ(log n)` and not `Θ(log² n)` — i.e. why the count of the skipped block is available *during* the descent.

**Then implement the naive version** (binary search over the prefix-sum array, `O(log n)` per prefix query) and time both: `Θ(log² n)` vs `Θ(log n)`. Report the crossover on real hardware.

**Edge cases:** `n = 0`; `findByOrder(1)` on an all-zero tree; `findByOrder(total + 1)` (should return `-1`); a tree with a single huge frequency.

---

## Exercise 6 — Top-k: four strategies, one table

Implement:
1. Sort + slice
2. Bounded **max**-heap (k smallest)
3. Bounded **min**-heap (k largest)
4. Quickselect repeated k times

Measure on `n = 10⁶`, `k ∈ {1, 10, 100, 10⁴, 10⁵}`:

| `k` | sort+slice | heap | repeated quickselect | winner |
|-----|-----------|------|---------------------|--------|
| 1 | | | | |

**Verify the crossover predicted by the theory** (around `k ≈ 30`): repeated quickselect wins for small `k`, heap wins for large.

**Then the mistake experiment:** implement `kSmallest` with a **min**-heap instead of a max-heap. Measure the slowdown. Predict first: it becomes `Θ(n log k)` (every element costs a pop+push) instead of `Θ(n + A log k)`. Verify.

---

## Exercise 7 — Percentile tracker over a stream

Build a bounded-memory latency tracker:

```java
final class Percentiles {
    private final int capacity;
    private final PriorityQueue<Integer> topK;   // depends on percentile
    void record(int latencyMs);
    int percentile(double p);                    // e.g. 0.99
}
```

**Design question:** for a fixed percentile `p`, `k` is unknown *in advance* (you don't know how many samples the `k`-th smallest will correspond to). Solve it:
- keep the `B` **largest** observed latencies in a min-heap of size `B = 10 000`;
- approximate `p99 ≈ min(heap)` when the stream length exceeds `B/0.01 = 10⁶`.

Then explain why this is an *estimate* and quantify the error: for a stream of length `N` and buffer `B`, the relative error is `O(√(B/N))` (this is the standard quantile-estimator result).

**Compare with the exact alternative** (store all samples, sort at query time) and state the memory trade-off. Then write the `REAL_WORLD_PROJECT/README.md`: metrics to emit (p50/p90/p99/p99.9, and the *count* per percentile so consumers know the sample size), and how you prevent the classic failure of a fixed-size buffer silently truncating during an incident (the answer: emit the buffer size and the sample count in every metric).

---

## Exercise 8 — Reservoir sampling vs heap

Implement reservoir sampling and verify uniformity: run 100 000 trials of `reservoirSample(range(1..10), k=3)` and check every 3-subset appears at approximately the same frequency (χ² or just eyeball the histogram).

Then compute the expected error of a median estimated from a reservoir of `k = 1000` drawn from `N = 10⁶` Gaussian samples, and compare with the exact median. Answer: **what reservoir size do you need for the median to be within 1%?** (Use the fact that a sample median has standard error `≈ 1.253 σ/√k`.)

---

## Exercise 9 — Order-statistic tree (CHALLENGE-grade)

Implement an AVL tree with `size` at each node supporting `insert`, `delete`, `rank(x)`, `select(k)` in `Θ(log n)` each. ~150 lines.

Test invariants:
- BST ordering (in-order traversal is sorted).
- AVL balance factor `|h(left) − h(right)| ≤ 1` at every node.
- `size(node) == 1 + size(left) + size(right)` at every node.
- `select(rank(x)) == x` after random inserts/deletes.

Then compare `select(k)` timings against Fenwick (`Θ(log n)` but requires static data) and against sort-then-index.

---

## Exercise 10 — Interpolation select

Implement `interpolationSelect`:
- Compute `min`/`max` of the current range.
- Estimate the pivot value `v = min + (max − min)·k / size`.
- Binary-search for `v`'s position; partition there.

Measure on:
- uniform random `int[]`
- sorted `int[]` (should be great: `min`/`max` predict perfectly)
- **organ-pipe** input (should be catastrophic — the value distribution is nowhere near uniform)
- clustered Gaussian

Then implement the **guarded** version: after the first 8 iterations, if the pivot has not landed near the interpolated position, fall back to randomised quickselect. Measure all four inputs again and confirm it is `Θ(n)` on everything.

---

## Exercise 11 — Parallel median

Implement the parallel median from the CODE_DEEP_DIVE, fix the shared-counter bug with `LongAdder`, and measure on `n = 2²⁴, 2²⁶` with 1/2/4/8 threads.

Report the speedup curve and compare with `Θ(√n)` depth theory and with Amdahl's law. Then answer: **at what `n` is parallel selection worth it?** (Account for: thread startup ≈ 50 µs, array bandwidth ≈ 10 GB/s, and the `Θ(n)` work per element being ~1 cache line for the count pass but only a few bytes for the partition pass.)

---

## Exercise 12 — Debugging drills

1. `partition3Way` with `swap(a, i, gt--); i++;` — find a failing input and trace it.
2. `select` with `if (p < k) hi = p + 1; else lo = p - 1;` (swapped) — infinite loop? On what input?
3. `medianOfMedians` with `Arrays.sort(a, s, e)` instead of `e + 1` — how does the failure manifest? Does it break *correctness* or just the complexity bound? (Test: verify the answer is still right, but the comparison count exceeds `3.386 n`.)
4. Fenwick `findByOrder` missing `k -= tree[next]` — find the smallest failing `k`.
5. `kSmallest` using a min-heap — is it *incorrect* or just slow? (It's **correct** if you return the sorted heap contents — just slow. Prove this.)
6. Parallel median with a plain `int` counter incremented from 8 threads — how do you *detect* it? (Run it 10 000 times with `n = 10⁶`; it will fail within a few hundred runs.)

---

## Exercise 13 — Deliverable

`BENCHMARK/SelectionRace.java`: for `n ∈ {10⁴, 10⁵, 10⁶, 10⁷}` run `Arrays.sort`, randomised quickselect, 3-way quickselect, median-of-medians, sorted-input quickselect (adversarial), and bounded-heap top-10. Print a markdown table.

Then answer in writing, with numbers from your table: **at what `n` does each algorithm become the winner, and why does the comparison-count ratio (8×) not match the wall-clock ratio (≈ 1.5×) at `n = 10⁶`?** (Answer must reference cache behaviour: sorting's merges are sequential and prefetch-friendly; quickselect's partitions walk disjoint ranges but its first pass still touches every cache line.)