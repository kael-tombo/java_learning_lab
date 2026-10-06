# Flashcards — Divide & Conquer Sorts

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | The three phases of a divide-and-conquer sort | **Divide** (cheap split), **Conquer** (recurse to base case), **Combine** (linear merge/partition) |
| 2 | Merge sort recurrence | `T(n) = 2T(n/2) + Θ(n)` |
| 3 | Merge sort via the Master theorem | `a=2, b=2, f(n)=n`; `n^(log_b a) = n`; **Case 2** → `Θ(n log n)` |
| 4 | Merge sort recursion tree shape | `log₂ n` levels, `Θ(n)` total work per level → `Θ(n log n)` |
| 5 | Why does merge sort have no best/worst distinction? | The split is always exact and the merge is always linear — no input can change either |
| 6 | Merge sort's merge precondition | Both halves are individually sorted |
| 7 | Merge sort's merge postcondition | The range is sorted and contains the same multiset of elements |
| 8 | The one-character rule for merge stability | Compare with `<=` (take from the left run on ties); `<` destroys stability |
| 9 | Merge sort space (array version) | `Θ(n)` auxiliary buffer + `Θ(log n)` stack |
| 10 | Merge sort space (intrusive list version) | `O(1)` auxiliary — you relink pointers instead of copying elements |
| 11 | Bottom-up merge sort advantage | **O(1) stack** — safe for n up to 2³¹, and maps onto external/disk merges |
| 12 | Natural merge optimisation | Skip the merge when `a[mid] <= a[mid+1]`; the two sorted runs are already globally ordered |
| 13 | Natural merge sort complexity | Θ(n) presorted, Θ(n log n) random — TimSort's ancestor |
| 14 | Why use `lo + (hi - lo) / 2` instead of `(lo + hi) / 2`? | `(lo + hi)` can overflow `int` for large index spaces |
| 15 | Lomuto partition invariant | `a[lo..p-1] <= pivot == a[p] <= a[hi]` (with `>=` on the right, not `>`) |
| 16 | Why does Lomuto degrade on all-equal input? | Every equal element lands right of the pivot, giving split `(0, n-1)` → `Θ(n²)` |
| 17 | Lomuto vs Hoare swap counts | Hoare does ~3× **fewer** swaps (each swap fixes two misplacements) |
| 18 | Hoare's returned index means | The pivot ends up **between** `j` and `j+1`; recurse `quickSort(lo, j)` and `quickSort(j + 1, hi)` |
| 19 | The classic Hoare recursion bug | Using `lo..j-1` / `j+1..hi` instead of `lo..j` / `j+1..hi` — drops the pivot |
| 20 | Quick sort recurrence | `T(n) = T(k) + T(n-k-1) + Θ(n)`, `k` = size of the left partition |
| 21 | Quick sort worst case and its cause | `Θ(n²)` when `k = 0` every time — presorted input with a last-element pivot |
| 22 | Randomised pivot expected bound | `Θ(n log n)` expected; with probability `≥ 1 - 1/n` it completes in `O(n log n)` |
| 23 | Why does randomisation beat median-of-3? | Randomisation protects against *any* fixed adversarial input; median-of-3 is only a heuristic the adversary can defeat |
| 24 | Expected depth of an element under random pivot | `Θ(log n)` |
| 25 | 3-way partition regions | `[lo, lt-1] < v`, `[lt, gt] == v`, `[gt+1, hi] > v` |
| 26 | 3-way quicksort comparison bound | `Θ(n log d)` where `d` = number of distinct values |
| 27 | The 3-way partition forgotten increment | After `swap(a, i, gt--)` you must **not** advance `i` — the incoming element is unexamined |
| 28 | 3-way quicksort on all-equal input | A single `Θ(n)` pass, zero recursion |
| 29 | Is 3-way quicksort ever worse than 2-way? | Never asymptotically; only ~constant-factor bookkeeping overhead when all values are distinct |
| 30 | Is quicksort stable? | **No** — partition swaps move elements across their equal partners |
| 31 | How to make a "stable quicksort"? | Sort an index array with a comparator that breaks ties by index (costs Θ(n) extra space + indirection) — never used in practice |
| 32 | When must you use merge sort instead of quicksort? | Stability needed, external/disk sorting (sequential I/O), linked lists, or a worst-case guarantee |
| 33 | Why does quicksort beat merge sort in RAM practice? | Cache locality (in-place, sequential access), fewer writes, no allocation |
| 34 | Merge sort's extra write cost | Every element is written twice: `a → aux` and `aux → a` |
| 35 | Merge sort base case | `hi - lo + 1 <= 1` — empty and single-element ranges are sorted |
| 36 | Why do library sorts use insertion sort below ~32–47 elements? | Constant factors beat asymptotics; no recursion/alloc, and n² is tiny |
| 37 | Bottom-up merge sort outer-loop width | `for (width = 1; width < n; width *= 2)`, merging `[lo, lo+width)` with `[lo+width, lo+2*width)` |
| 38 | Bottom-up merge: how to handle an odd trailing run | Clamp `hi` with `Math.min(lo + 2*width - 1, n-1)` and skip if `mid >= hi` |
| 39 | Counting inversions in merge sort | When `a[i] > a[j]`, add `mid - i + 1` — all remaining left elements are > `a[j]` |
| 40 | Max inversions for `n = 10^5` | `n(n-1)/2 = 4 999 950 000` — exceeds `int`, so use `long` |
| 41 | Introsort's shape | Insertion sort for small ranges, quicksort partition, **heap sort fallback** at a depth limit |
| 42 | Introsort's stack guarantee | Depth capped at `2·log₂ n` insertions → `O(log n)` stack |
| 43 | Introsort's time guarantee | `O(n log n)` worst case, because the fallback is heap sort |
| 44 | Fork-join parallel merge sort: why no locks? | Both children write **disjoint** `aux` ranges and read-only `a` ranges — no data race |
| 45 | Amdahl's law cap for parallel merge sort | With a 1% serial merge fraction, speedup ≤ 100× regardless of core count |
| 46 | Parallel merge sort's bottleneck | The final `Θ(n)` merge is inherently serial |
| 47 | What does `Arrays.sort(int[])` use in HotSpot? | Dual-pivot quicksort (with insertion sort under ~47 elements) — *not* merge sort |
| 48 | What does `Arrays.sort(T[])` use? | TimSort — stable, adaptive, merging-based |
| 49 | Merge sort on already-sorted input without the natural-run check | Still full `Θ(n log n)` — merge sort is not adaptive by default |
| 50 | Merge sort on reverse-sorted input | `Θ(n log n)` — no special degradation |
| 51 | Quick sort on reverse-sorted input, last-element pivot | `Θ(n²)` — every partition splits off one element |
| 52 | Quick sort on a "median-of-3 killer" input | `Θ(n²)` even with median-of-3, unless you randomise |
| 53 | Count inversions in the *original* array | Insertion sort's total shift count equals the inversion count |
| 54 | Two merges that must be sequential in external sort | Pass k and pass k+1 of bottom-up merge — each depends on the whole previous pass |
| 55 | External merge sort's real bottleneck | Disk I/O bandwidth, not CPU — choose buffer size = block size |
| 56 | How to detect "already merged" cheaply? | `a[mid] <= a[mid+1]` — one comparison |
| 57 | Sorting a `LinkedList<T>`? | Intrusive merge sort, bottom-up: `O(1)` extra space, Θ(n log n), stable. Random access to a list is `Θ(n)` |
| 58 | Quick sort's memory access pattern | Sequential-ish scans with random-ish swaps — fits `Arrays.sort`'s profile |
| 59 | Merge sort's memory access pattern | Two streams (`a`, `aux`) ping-ponging — 2× the memory traffic |
| 60 | Rule of thumb in Java | `Arrays.sort` for everything; reach for your own only to beat TimSort on a *measured* workload |

## Self-test (one line each)

1. Merge sort's Master-theorem case and result? → **Case 2, `Θ(n log n)`**
2. Why does Lomuto go quadratic on duplicates? → **Equal elements all go right, giving an `(0, n-1)` split every time**
3. `<` vs `<=` in the merge loop — which preserves stability? → **`<=`**
4. 3-way quicksort on `d` distinct values? → **`Θ(n log d)`**
5. Merge sort vs quick sort — the practical tiebreaker? → **Cache locality and no allocation, not asymptotics**