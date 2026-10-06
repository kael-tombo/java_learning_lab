# Exercises — Bit Sort & Search

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.bitops`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Bit-trick table, verified

Implement each from memory, then verify against a reference. Report `Θ(1)` status.

| expression | purpose | reference to check against |
|-----------|---------|---------------------------|
| `x & -x` | isolate lowest set bit | loop counting trailing zeros |
| `x & (x-1)` | clear lowest set bit | — |
| `x ^ (x-1)` | lowest set bit + everything below | — |
| `x & (x+1)` | clear the lowest run of 1s | — |
| `x \| (x+1)` | set the lowest 0 bit | — |
| `x > 0 && (x & (x-1)) == 0` | power of two | `Long.bitLength` |
| `Integer.bitCount(x)` | popcount | `Integer.bitCount` (it IS the reference) |
| `31 - Integer.numberOfLeadingZeros(x)` | highest set bit | `Integer.highestOneBit` |
| `Long.numberOfTrailingZeros(x)` | lowest set bit index | loop |
| `x ^ y` then `numberOfTrailingZeros` | first differing bit | loop |

**Then fill in the boundary table** for `{0, 1, -1, 2, MAX_VALUE, MIN_VALUE, 0x55555555, 0xAAAAAAAA, 1<<16}` and **find every entry where the expression does something surprising.** (Hint: `-MIN_VALUE == MIN_VALUE`, so `MIN_VALUE & -MIN_VALUE == MIN_VALUE`, not a single bit.)

---

## Exercise 2 — Trace branchless partition

Partition `[5, 2, 7, 1, 6, 3]` on bit 1 (value 2) using the branchless form. Fill in the table:

| `j` | `a[j]` | `a[j] & 2` | `set` | `mask` | `a[m]` | `diff` | swap? | `a` after | `m` |
|-----|--------|-----------|-------|--------|--------|--------|-------|-----------|-----|
| 0 | 5 | 0 | 0 | 0 | 5 | 0 | no | 5 2 7 1 6 3 | 0 |
| 1 | 2 | 2 | 1 | -1 | | | | | |
| 2 | 7 | | | | | | | | | |
| 3 | 1 | | | | | | | | | |
| 4 | 6 | | | | | | | | | |
| 5 | 3 | | | | | | | | | |

**Verify** the result has bit 1 clear in `[lo, m)` and set in `[m, hi)`. Then re-run on bit 0 and bit 2.

**Now the branchy version** — do the same trace but write down the *predicted* branch outcome at each step and mark the ones a predictor would get wrong. Count them: this is the misprediction count you are saving.

---

## Exercise 3 — Bitwise sort, traced

Sort `[3, 1, 4, 1, 5, 9, 2, 6]` with `BitSort`. Work with the flipped values (`^ Integer.MIN_VALUE`) — for positive inputs that adds `0x80000000`, so the *unsigned* ordering is unchanged and you can just sort the positive values MSB-first.

Level `b=2` (bit 2, value 4):

| `j` | `a[j]` | bit 2 | `a[m]` | swap? | array | `m` |
|-----|--------|-------|--------|-------|-------|-----|
| 0 | 3 | 0 | | | | |
| 1 | 1 | 0 | | | | |
| 2 | 4 | 1 | | | | |
| 3 | 1 | 0 | | | | |
| 4 | 5 | 1 | | | | |
| 5 | 9 | 0 | | | | |
| 6 | 2 | 0 | | | | |
| 7 | 6 | 1 | | | | |

Continue through bits 1 and 0 (with the `SMALL = 16` cutoff meaning you would actually stop at level 0 and insertion-sort — do the trace for the `SMALL = 0` case to see the full tree).

**Then:** count comparisons. The answer is **zero** — the bitwise sort uses no comparisons at all. Verify with a counter and report the number of bit tests (= `Σ n/2^b ≈ 2n` for a balanced tree).

---

## Exercise 4 — Branchless vs branchy vs Arrays.sort

Benchmark on `int[10⁶]`, `int[10⁷]`:
- `BitSort` branchless
- `BitSort` branchy
- `Arrays.sort`
- `Arrays.parallelSort`

Report ns/element and mispredicted-branch counts (via `perf stat -e branch-misses` if available, or by estimating from the time difference).

**Then answer in writing:**
1. Does branchless beat branchy? By how much? (Expect 1.3–2×.)
2. Does either beat `Arrays.sort`? Why not? (It is **intrinsified** dual-pivot quicksort — see `Code Deep Dive`.)
3. **At what input distribution would branchless win by the most?** (A random distribution maximises branch entropy. Try: all-equal, sorted, 2 distinct values, organ-pipe.)

---

## Exercise 5 — Bit trie: build, find, ceiling, floor

Build a trie over `{0, 1, 5, 6, 9, 13, 100, 1000, -1, Integer.MIN_VALUE, Integer.MAX_VALUE}`.

**Draw the first 6 levels.** Then verify:
- `find(k)` for every `k` in `[-10, 1020]` matches a `HashMap` reference.
- `ceiling(k)` matches a brute-force linear scan for every `k` in `[-10, 1020]`.
- `floor(k)` likewise.
- **Signed ordering:** trie order is unsigned. Verify that `find(-1)` and `find(Integer.MAX_VALUE)` both work, and that an *ordered iteration* (in-order DFS) yields the **unsigned** order — which is why you must flip before inserting if you want signed order.

**The `ceiling` bug hunt:** implement two variants:
- A: remember the *shallowest* candidate.
- B: remember the *last* candidate found.
Find the smallest key set where they disagree, and explain why A is correct.

---

## Exercise 6 — Trie memory measurement

Insert `n = 10⁵`, `10⁶` random `int`s into (a) a plain trie, (b) a `HashMap`. Report heap usage after a `System.gc()`.

| `n` | plain trie MB | HashMap MB | ratio |
|-----|--------------|------------|-------|
| 10⁴ | | | |
| 10⁵ | | | |
| 10⁶ | | | |

Then **implement a Patricia (compressed) trie** — skip single-child chains, store `skipBits` per node — and re-measure. Verify it uses `≤ 2n` nodes and still answers `find`/`ceiling` in `Θ(log n)`.

**Answer in writing:** at what `n` does the plain trie become unusable, and what is the practical mitigation for a range-query use case? (Sort once + binary search is `Θ(n log n)` build, `Θ(log n)` query, `4n` bytes.)

---

## Exercise 7 — Bitset set algebra benchmark

Build `BitSet64` and a `HashSet<Integer>`; benchmark for `n = 10⁴ … 10⁷`:

| operation | `n = 10⁴` | `10⁵` | `10⁶` | `10⁷` |
|-----------|-----------|--------|--------|--------|
| `intersect` bitset | | | | |
| `intersect` HashSet | | | | |
| `cardinality` bitset | | | | |
| `cardinality` HashSet | | | | |
| iterate all set bits | | | | |

**Find the sparsity crossover**: for sets with `n/1000` elements, which wins? Verify the theory (`Θ(n/w)` bitset vs `Θ(|A|)` hash set) and state the crossover density.

Then add the **two-level summary** and show `firstSet()` becomes `Θ(1)`.

---

## Exercise 8 — Morton codes and the GPU pattern

1. Encode `n = 10⁶` random points in `[0, 2²¹)²` by Morton code. Sort. Report encoding time, sort time, and the ratio of "adjacent in space" pairs to "adjacent in code" pairs (this is the locality metric).

2. Run 1 000 rectangle queries. For each, report: candidates examined by the binary-search range, true positives, and the **false-positive ratio**.

3. Compare against a naive scan of all points.

**Answer in writing:** for what query shape is Morton competitive with a scan? (Very selective queries — a small rectangle. For a query covering half the space, the binary search returns `Θ(n)` candidates and Morton is a pure loss.)

4. **Decode** the code back with `compactBy2` and verify you recover `(x, y)` for all `10⁶` points.

5. Implement a **Hilbert curve** (`d2xy`/`xy2d` from the standard Skilling algorithm) and compare the false-positive ratio and the average jump length against Morton.

---

## Exercise 9 — Held–Karp on `n ≤ 16`

Implement the exact TSP with:
1. `int[] dp` over masks — `Θ(2ⁿ n²)` time, `Θ(2ⁿ)` space (no `from` array).
2. Bit-parallel subset iteration using `for (int m = mask; m != 0; m &= m - 1)`.

For a random 16-city instance, verify the result matches a brute-force permutation search (`16! = 2·10¹³` — too slow, so use `n = 10` and compare against `10! = 3.6·10⁶`).

**Then report** memory and time for `n = 18`, `20`, `22`, `24` and extrapolate where it breaks.

**Finally:** implement the Held–Karp **bounded-memory variant** (Savitch-style / meet-in-the-middle over the "half the cities" split) and note its `Θ(2^{n/2})` space and `Θ(2^{n/2} n²)` time — enough for `n ≈ 30`. Why does this not contradict the `Θ(n! )` lower bound for TSP? (Because TSP has no known `n^{Ω(n)}` lower bound; the exact algorithm is `Θ(2ⁿ)` — this is the strongest evidence that "TSP needs factorial time" is a *belief* about the complexity *class*, not a theorem.)

---

## Exercise 10 — Debugging drills

1. `BitSort.sort` without the `^ Integer.MIN_VALUE` flip on inputs containing negatives — what does it produce for `[-1, 0, 1]`?
2. `partitionBit` with `int mask = set;` instead of `-set` — find a failing input.
3. `partitionBit` with `m += 1 - set;` — find a failing input.
4. `Bits.lowestSetBit(0)` → returns 32. Write the line of code that would then index `a[32]` and crash.
5. `1 << 31` — why does this not compile, and what are the two correct ways?
6. `numberOfTrailingZeros` used to find the *highest* set bit — what's wrong?
7. `spreadBy2` with one mask step missing — which bits get corrupted, and does `demorton2` still invert it? (It should **not**, which is a good self-check.)
8. Submask enumeration with `if (s == 0) break;` moved *after* the `s = (s-1) & k` update — what happens?

---

## Exercise 11 — Deliverable

`MINI_PROJECT/BitVisualizer.java`: a console tool that
- takes a 64-bit word and prints its bit layout with field annotations;
- runs the branchless partition on a small array and prints the `set`/`mask`/`diff` values per step;
- renders a Morton-code visualisation of a small point set as ASCII (the Z-curve);
- draws a bit trie for a small key set.

Then `BENCHMARK/BitRace.java` producing a markdown table: branchy vs branchless partition vs `Arrays.sort` vs radix sort vs counting sort, across input densities `{100%, 50%, 2 distinct, 10⁶ distinct}`, at `n ∈ {10⁴, 10⁶, 10⁷}`.

**Answer in writing:** at what point does the *bitwise* approach stop being worth it, and what property of the input (density, width, or distribution) is the deciding factor?