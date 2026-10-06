# Exercises — Linear-Time Sorts

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.linear`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Counting sort, traced

Input `[4, 2, 2, 8, 3, 3, 1]` (min 1, max 8, `k = 8`). Fill the tables:

| v | `count[v]` after counting | after inclusive prefix (= end pos) |
|---|---------------------------|-----------------------------------|
| 1 | 1 | 1 |
| 2 | 2 | 3 |
| 3 | 2 | 5 |
| 4 | 1 | 6 |
| 5 | 0 | 6 |
| 6 | 0 | 6 |
| 7 | 0 | 6 |
| 8 | 1 | 7 |

**Scatter backward:**

| i | a[i] | v | slot | out |
|---|------|---|------|-----|
| 6 | 1 | 1 | `--count[1]=0` | out[0]=1 |
| 5 | 3 | 3 | `--count[3]=4` | out[4]=3 |
| 4 | 3 | 3 | `--count[3]=3` | out[3]=3 |
| 3 | 8 | 8 | `--count[8]=6` | out[6]=8 |
| 2 | 2 | 2 | `--count[2]=2` | out[2]=2 |
| 1 | 2 | 2 | `--count[2]=1` | out[1]=2 |
| 0 | 4 | 4 | `--count[4]=5` | out[5]=4 |

Result `[1,2,2,3,3,4,8]`. ✓

**Now redo with Convention B** (exclusive prefix, forward scatter) and confirm the *same* output — and then run a **forward scatter with the inclusive prefix** and show the two `2`s come out swapped, i.e. unstable.

**Edge cases:** all equal (`k = 1`); empty; single element; `[0, 0]`; `[5, -5]` (forces `k = 11` and a `-min` offset).

---

## Exercise 2 — Stability harness

Write `boolean isStable(IntUnaryOperator keyGen, int n, IntFunction<int[]> sorter)` by packing `(value, index)` into a `long`, sorting, and checking that indices ascend within each tie group.

Test over 3 000 random arrays with `n ∈ [2, 60]` and values from `{0, 1, 2}` (heavy ties) for: counting sort (both conventions), LSD radix, MSD hybrid, and `Arrays.sort(T[])` with a comparator.

**Expectation:** all counting/radix variants stable; all `Arrays.sort` variants stable; **any unstable variant you deliberately write fails.**

---

## Exercise 3 — The `k = max` trap, measured

Instrument your counting sort to log the allocated count-array size. Run on:
- `int[100]` with values in `{1_000_000 .. 1_000_099}` → 4 MB allocated for 100 elements.
- `int[2]` = `{0, Integer.MAX_VALUE}` → **the size of a `2³¹` int array. Observe the failure** (wrap in a try/catch or a guard).
- `int[10⁶]` of values in `{0, 10⁶-1}` → correct and fast.

Then implement the guard `if (k > 4*n) throw ...` and re-run: which cases now throw, and which still work? Explain why `k > 4n` is a reasonable trigger (counting sort is `Θ(n + k)`, so `k ≫ n` makes it *slower* than `Θ(n log n)` as well as memory-hungry).

**Rule of thumb:** counting sort is only worth it when `k = O(n)`.

---

## Exercise 4 — LSD radix, digit by digit

Sort `[170, 45, 75, 90, 802, 24, 2, 66]` with 10-bit digits (`B = 1024`):

| pass | shift | sorted by | array after |
|------|-------|-----------|-------------|
| 0 | 0 | low 10 bits | 170 45 75 90 802 24 2 66 (all < 1024, single digit → unsorted) |
| 1 | 10 | next 10 bits | **2 802** 170 45 75 90 24 66 |

Confirm with an instrumented run. Then explain why pass order **cannot** be reversed (do the MSD order and watch it fail on `[3, 24]`).

**Stability necessity proof, empirically:** break the inner scatter (use an inclusive prefix with forward scatter) and find an input that comes out wrong. `[1, 1024 + 1]` = `[1, 1025]`: after the buggy pass 0 the two 1s (low digit 1) may be reordered; pass 1 then sorts by the high digit only, leaving them in the wrong relative order. Verify.

---

## Exercise 5 — Signed keys

Sort `[-3, 2147483647, -2147483648, 0, -1, 1]` with:
1. no sign handling (expect: **wrong**, negatives at the end)
2. the `^ Integer.MIN_VALUE` flip
3. `Long` keys with `^ Long.MIN_VALUE`

Trace the flip for `-1`: `-1 ^ 0x80000000 = 0x7FFFFFFF = 2³¹ - 1`, and `Integer.MAX_VALUE ^ 0x80000000 = 0x7FFFFFFF` too — they're equal after the flip because `-1` and `MAX_VALUE` differ only in the sign bit. Explain why this is correct: in two's complement, `-1` is all ones, and flipping the sign bit maps the whole signed range onto `[0, 2³²)` **order-preservingly** (it is a bijection that reverses the meaning of the top bit, which is exactly what makes signed comparison identical to unsigned comparison of flipped keys).

**Add a test with `Integer.MIN_VALUE` and `Integer.MAX_VALUE`** — these are the two that catch every shift-based bug.

---

## Exercise 6 — Base selection sweep

Implement radix with a parameterised `BITS ∈ {1, 2, 4, 8, 11, 16, 21, 32}` and time each on `int[10⁶]` and `int[10⁷]`.

Report:

| BITS | `B` | passes | `count` array | time (10⁶) | time (10⁷) |
|------|-----|--------|---------------|-----------|-----------|
| 4 | 16 | 8 | 64 B | | |
| 8 | 256 | 4 | 1 KB | | |
| 11 | 2048 | 3 | 8 KB | | |
| 16 | 65 536 | 2 | 256 KB | | |
| 21 | 2M | 2 | 8 MB | | |
| 32 | 4G | 1 | 16 GB | OOM | OOM |

**Predict before running:** `BITS = 8` and `11` should be fastest for `10⁶`; `16` should win at `10⁷` because fewer passes beat cache misses; `21` should collapse because the count array no longer fits in cache. Then explain the observed minimum in terms of *memory traffic*, not operation count.

**Bonus:** plot `passes × array size` and find the value of `BITS` that minimises total bytes moved. Does it match the empirical winner?

---

## Exercise 7 — MSD hybrid vs LSD

Implement the MSD hybrid with cutoff `SMALL = 64`, and benchmark against LSD (`BITS = 11`) on:

| Distribution | LSD | MSD hybrid | `Arrays.sort` |
|---|---|---|---|
| uniform `int[10⁶]` | | | |
| all equal | | | |
| 100 distinct values | | | |
| 10⁶ distinct values | | | |
| already sorted | | | |
| alternating `0, 2³¹` | | | |

**Explain the two crossover points:** LSD wins on few-distinct-values input (every pass is a cheap full scan, MSD recurses forever), MSD wins on many-distinct-values input (only ~1–2 levels before buckets are singletons). Identify the crossover from your measurements.

Then answer: for a **database index build over 100M 64-bit row IDs**, which would you use and why? (Consider that IDs are near-random → MSD wins; that you can process chunks independently → parallelism is easier with LSD; and that LSD lets you avoid recursion entirely.)

---

## Exercise 8 — Bucket sort assumption audit

Generate 10 datasets of `n = 10⁶` doubles:
1. uniform `[0, 1)`
2. Gaussian `(0, 1)`
3. exponential
4. two-point mixture (90% at 0.1, 10% uniform)
5. uniform on `[0, 10⁻⁶)`
6. all identical
7. sorted
8. sorted descending
9. `√i/n` distributed (concentrated near 0)
10. `1 - √i/n` (concentrated near 1)

For each, report: bucket occupancy histogram (max bucket size), time, and time/Θ(n).

**Expected:** uniform ≈ 1.0×; Gaussian ≈ 2–3×; mixture ≈ 10×; identical ≈ log n factor (with `Arrays.sort` per bucket) or catastrophic (with insertion sort per bucket). Then write one paragraph: *this is why nobody deploys bucket sort without a validated distribution.*

---

## Exercise 9 — Counting sort on non-integer keys

Extend counting sort to:
1. `char[]` — keys are UTF-16 code units. `count` size 65 536. Note this makes counting sort *worse* than comparison sorting for short strings.
2. Small enums — `count` size = enum count. This is the one place counting sort genuinely wins (status codes, board squares, small cardinalities).
3. `String` keys of length ≤ 8 — radix sort by bytes, MSD first, stopping at `SMALL`. Show that it beats `Arrays.sort(String[])` for `n = 10⁶` random 8-char strings by ~3×.

**Then confront the trap:** LSD radix on `String` needs the *longest* string's length for `d`, so a single 1 MB string makes `d` huge. Explain why MSD-with-cutoff is mandatory for variable-length strings, and how MSD handles the terminator (treat a null byte as the smallest digit and stop descending past it).

---

## Exercise 10 — Debugging drills

Each is a plausible implementation. Find the bug and the test that catches it.

1. `for (int i = 0; i < n; i++) out[--count[a[i]]] = a[i];` — inclusive prefix, forward scatter. **Bug:** unstable. Test: stability harness.
2. `int k = max;` instead of `max - min + 1`. **Bug:** massive over-allocation. Test: assert the allocated count size.
3. Radix `for (int shift = 0; shift < 32; shift += 12)` with mask `0xFFF`. Passes at 0, 12, 24 — bits 24–31 only, so bits 12–23 and 24–31 overlap? Check. **Actually:** shifts 0/12/24 with a 12-bit mask cover bits 0–35, and `>>>` masks the shift to 5 bits for `int`, so **shift 24 is fine but the last pass reads bits 24–31 only** — correct but the count array is oversized. Introduce a real bug: use `shift += 11` with a **12-bit** mask → bits 11–21 are never extracted. Test: keys that differ only in bits 11–21.
4. MSD with `if (hi - lo <= SMALL)` but **no** `shift < 0` guard. **Bug:** infinite recursion for identical keys once buckets stop shrinking. Test: all-equal input.
5. Bucket sort with `int idx = (int)((v - min) / w);` and no clamp. **Bug:** `idx == k` for `v == max`. Test: `[1.0, 2.0]` (max lands out of range).

---

## Exercise 11 — Hybrid introsort + radix (the production pattern)

Implement:

```java
static void hybrid(int[] a) {
    // 1. Detect and insertion-sort monotonic runs of length >= RUN
    int i = 0;
    while (i < a.length) {
        int j = i + 1;
        if (a[i] <= a[i+1])  while (j < a.length && a[j-1] <= a[j]) j++;   // ascending run
        else                 while (j < a.length && a[j-1] >= a[j]) j++;   // descending run
        if (j - i >= RUN) insertionSort(a, i, j); else i = j;               // hmm: fix the logic
        else i = j;
    }
    // 2. If the data is now sorted, return. Otherwise radix sort.
    if (isSorted(a)) return;
    RadixSort.sort(a);
}
```

(Your job: write the run-detection loop *correctly* — the sketch above has a bug in the run-length accounting. Then measure the benefit on: sorted input, nearly-sorted input (100 random swaps in a sorted array), and random input.)

**Report:** for sorted input the hybrid is `Θ(n)`; for random input it pays ~10% overhead. Is that trade worth it? Argue it in terms of your actual latency SLO.

---

## Exercise 12 — Parallel radix sort

Partition the array into `p` chunks, radix-sort each chunk in parallel, then `p`-way merge by digit using a counting scatter per pass.

Key question to answer: **does LSD radix parallelise better than MSD?** Justify with the dependency structure. Then implement the parallel version and measure 1/2/4/8 threads on `int[2²⁴]`. Predict the speedup ceiling from Amdahl's law with the serial merge fraction, and compare.

---

## Exercise 13 — Deliverable

`BENCHMARK/RadixCrossover.java`: for `n ∈ {10³, 10⁴, 10⁵, 10⁶, 10⁷}` run counting sort (where legal), LSD radix (`BITS = 8/11/16`), MSD hybrid, bucket sort, `Arrays.sort`, and `Arrays.parallelSort`; print a markdown table with times and a bold row marking the winner. Then answer in writing: **at what `n` does each algorithm become the winner, and which crossover would surprise a reviewer who only knows comparison sorting?**