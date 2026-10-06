# 02 — Divide & Conquer Sorts

<div align="center">

**Merge Sort · QuickSort · 3-Way QuickSort · Intrusive & Bottom-Up Variants**

</div>

---

## Learning Objectives

- Derive the merge sort recurrence `T(n) = 2T(n/2) + Θ(n)` and apply the Master theorem
- Explain why merge sort is *not* in-place while quick sort is
- Prove the quick sort expected bound with a random-pivot argument
- Diagnose worst-case inputs for naive pivot selection and defend with randomisation
- Explain the 3-way partition and its effect on duplicate-heavy data
- Decide between top-down, bottom-up, and in-place variants from memory constraints

## Prerequisites

- Recursion and divide-and-conquer (lab `09-divide-and-conquer`)
- Comparison lower bound `⌈log₂ n!⌉` (see `01-comparison-sorts`)
- Java recursion, generics, `System.arraycopy`

## Estimated Time

- **Theory**: 120 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| Divide | Split the problem into two (or three) roughly equal subproblems |
| Conquer | Recursively solve the subproblems |
| Combine | Merge the sub-solutions in Θ(n) — the sorting analogue of the divide-and-conquer pattern |
| Merge | The linear-time step: repeatedly take the smaller head of two sorted runs |
| Pivot | The partition key that splits quick sort into left/right |
| Partition | The linear step that places elements relative to the pivot |
| Lomuto vs Hoare | The two dominant partition schemes and their constant factors |
| 3-way partition | `< pivot`, `= pivot`, `> pivot` — collapses duplicate-heavy inputs to Θ(n) |
| Intrusive linked list | The memory-free merge sort; moves *pointers* not elements |
| Run | A maximal already-ascending subsequence — the atom of bottom-up merge sort |
| Stability | Merging with `<=` on the left run preserves order; using `<` does not |

## Complexity Snapshot

| Algorithm | Best | Average | Worst | Space | Stable | Adaptive |
|-----------|------|---------|-------|-------|--------|----------|
| Merge sort (top-down, array) | Θ(n log n) | Θ(n log n) | Θ(n log n) | Θ(n) | Yes | No |
| Merge sort (intrusive list) | Θ(n log n) | Θ(n log n) | Θ(n log n) | O(1) | Yes | No |
| Bottom-up merge sort | Θ(n log n) | Θ(n log n) | Θ(n log n) | Θ(n) | Yes | No |
| Quick sort (random pivot) | Θ(n log n) | Θ(n log n) | Θ(n²) | Θ(log n) | No | No |
| Quick sort (median-of-3) | Θ(n log n) | Θ(n log n) | Θ(n²) | Θ(log n) | No | No |
| 3-way quick sort (random) | Θ(n log n) | Θ(n log n) | Θ(n) w/ many dups | Θ(log n) | No | No |
| Quick sort (stable variant) | — | Θ(n log n) | Θ(n log n) | Θ(n) | Yes | No |

## Algorithms Covered

### Merge Sort
- **Mechanism:** split at `mid = lo + (hi-lo)/2`, sort both halves, merge.
- **Invariant at merge:** both halves are sorted; `lo..mid` and `mid+1..hi`.
- **Why Θ(n log n) worst case:** the recurrence has no "lucky" base case — every split is exact.
- **Why stable:** compare `left[i] <= right[j]`; using `<` inverts equal pairs.
- **Optimisation:** skip merge if `a[mid] <= a[mid+1]` (already in order) — "natural merge".

### Quick Sort
- **Mechanism:** choose pivot, partition, recurse on both sides.
- **Invariant at partition return:** every `a[i]` for `i < p` satisfies `a[i] <= a[p]`; every `a[j] > p` satisfies `a[j] >= a[p]`.
- **Lomuto:** single forward scan, last element as pivot, `p` ends at the final position.
- **Hoare:** bidirectional scan, fewer swaps (~3× fewer than Lomuto), but pivot lands *between* positions.
- **Pivot choices:** first/last (Terrible, adversarial), middle, median-of-3 (kills presorted input), median-of-9, ninther (Java's old `Arrays.sort`), random.

### 3-Way Quick Sort (Dutch National Flag)
- **Mechanism:** `[lt | = | gt]` invariant with `<`, `==`, `>` regions maintained during one scan.
- **Why it matters:** with `d` distinct values, 3-way quicksort runs in Θ(d log d) after an O(n) scan — it self-tunes when the value domain is small.
- **Invariant:** `a[lo..lt-1] < v`, `a[lt..gt] == v`, `a[gt+1..hi] > v`.

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/divide-conquer-sorts/` | Java implementations |
| `src/test/java/com/alglab/divide-conquer-sorts/` | JUnit 5 tests |
| `SOLUTION/` | Worked exercise solutions |
| `TESTS/` | Edge-case suites (n=0, n=1, all-equal, presorted) |
| `BENCHMARK/` | Comparison-sort timing harness |
| `MINI_PROJECT/` | Sort visualiser with partition highlights |
| `REAL_WORLD_PROJECT/` | External merge sort over on-disk chunks |
| `CHALLENGE/` | Parallel merge sort, string merge sort |
| `DIAGRAMS/` | Split/merge recursion trees |