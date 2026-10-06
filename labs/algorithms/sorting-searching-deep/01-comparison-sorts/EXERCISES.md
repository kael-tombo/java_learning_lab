# Exercises — Comparison Sorts

Every exercise: **implement in Java**, **trace by hand**, **then hit the edge cases**. Java 21, package `com.alglab.comparison`. Put solutions in `SOLUTION/`, tests in `TESTS/`.

---

## Exercise 1 — Insertion sort with a shift counter

Implement `int insertionSortWithShifts(int[] a)` returning the number of element *moves* into an empty slot performed by the inner loop.

```java
public static int insertionSortWithShifts(int[] a) {
    int moves = 0;
    for (int i = 1; i < a.length; i++) {
        int key = a[i], j = i - 1;
        while (j >= 0 && a[j] > key) { a[j + 1] = a[j]; j--; moves++; }
        a[j + 1] = key;
    }
    return moves;
}
```

**Trace** `[5, 2, 4, 6, 1, 3]`:

| i | key | values shifted | moves so far |
|---|-----|----------------|--------------|
| 1 | 2 | 5 | 1 |
| 2 | 4 | 5 | 2 |
| 3 | 6 | — | 2 |
| 4 | 1 | 6, 4, 2, 5 | 6 |
| 5 | 3 | 4, 5 | 8 |

Total = 8 = number of inversions in the original array. Verify by counting inversions with the O(n²) double loop — they must match for every input.

**Edge cases:** `[]` → 0. `[1]` → 0. `[2,1]` → 1. `[1,2]` → 0 (best case Θ(n)). `[3,2,1]` → 3.

---

## Exercise 2 — Prove insertion sort is stable

Implement `boolean isStableInsertion(int[] a)` by tagging each element with its original index, sorting, and checking the tags of equal keys are increasing. Confirm it returns `true` for 1000 random small arrays (values drawn from a 5-element alphabet so ties are frequent).

Then implement selection sort with the *same* tagging and show it returns `false` on some input. Find the smallest such input by brute force over all arrays of length ≤ 5.

**Hint:** the smallest witness is 4 elements, e.g. `[2a, 2b, 1, 3]` — with tags `a < b`, selection sort moves the `2b` to index 0.

---

## Exercise 3 — Selection sort swap counting

Implement `int selectionSortCountingSwaps(int[] a)` and prove the answer is always `≤ n - 1`.

**Trace** `[29, 10, 14, 37, 13]` → 4 swaps; `[1,2,3,4,5]` → 0 swaps; `[5,4,3,2,1]` → 2 swaps. Find an input with exactly `n-1` swaps and describe it: it is one where every element of the suffix is smaller than the prefix minimum, i.e. `a[i]` is never already the min of `a[i..n-1]`.

---

## Exercise 4 — Bubble sort invariant instrumentation

Instrument bubble sort to assert after every outer pass that `a[end+1..n-1]` is non-decreasing.

```java
assert sortedSuffix(a, end + 1) : "pass " + end + " broke the suffix invariant";
```

**Trace** `[5, 1, 4, 2, 8]`, pass 1 (end = 4): swaps at i=0 and i=2 → `[1,4,2,5,8]`. Suffix `a[5..]` is empty, trivially sorted. Pass 2 (end = 3): swap at i=1 → `[1,2,4,5,8]`, suffix `a[4..4] = 8` sorted. Pass 3 (end = 2): no swap → early exit.

**Edge case to find:** an input where the `!swapped` early exit saves the most work — `[1..n]` sorted: 1 comparison set of `n-1` comparisons total instead of `n(n-1)/2`.

---

## Exercise 5 — Cocktail shaker on turtles

Generate the "turtle" input `[1, 2, ..., k, n, n-1, ..., k+1]` (a sorted small run followed by a descending large run) and instrument standard bubble sort vs cocktail shaker to count comparisons.

| n | bubble comparisons | shaker comparisons |
|---|--------------------|--------------------|
| 100 | ~4950 | ~300 |
| 1000 | ~499500 | ~2500 |

Predict the numbers before running. Explain why shaker is Θ(n²) on this input for bubble but only Θ(n) for shaker.

---

## Exercise 6 — Shell sort with three gap sequences

Implement `shellSort(int[] a, int[] gaps)` where `gaps` is given in **descending** order and the last element must be 1. Throw `IllegalArgumentException` otherwise.

Generate gaps for: Shell (`n/2, n/4, ... 1`), Knuth (`3h+1`), Hibbard (`2^k - 1`), Sedgewick (`4^k + 3·2^{k-1} + 1`). Instrument to count comparisons per sequence on:
- random `int[100_000]`
- reverse sorted
- `[1, 5, 3, 9, 2, 7, 4, 8, 6, 5]` pattern, tiled (the classic hard Shell input)

**Predicted order** (random input, n = 10⁵): Sedgewick < Knuth ≈ Hibbard < Shell. On the tiled-pattern input Shell degrades badly — plot the comparison counts as a bar chart in `BENCHMARK/`.

---

## Exercise 7 — Holes, not shifts: a branch-light insertion sort

Rewrite insertion sort so the inner loop is a binary search for the insert position, then `System.arraycopy` the block. Called *binary insertion sort*.

- Complexity becomes Θ(n log n) comparisons but stays Θ(n²) moves.
- **Trace** on `[5, 2, 4, 6, 1]`: for `key=1`, binary search over `[2,4,5,6]` finds pos 0, one `arraycopy` of length 4.
- Compare wall-clock against plain insertion sort on `int[10_000]` — on modern CPUs `arraycopy` (SIMD memcpy) often *wins* despite the worse asymptotics. Report the crossover point.

**Edge case:** duplicates. Binary search must find the **leftmost** insert position to keep stability.

---

## Exercise 8 — Lower bound demonstration

Implement `int countComparisons(int[] a, BiPredicate<Integer,Integer> cmp)` by wrapping the comparison in a lambda that increments a counter. Show empirically that for comparison sorts on `n = 1000` random distinct keys, *every* sort you wrote performs at least `ceil(log2(1000!)) ≈ 8529` comparisons.

Compute `log2(n!)` with `lgamma(n+1) / log(2)` in double precision. For `n = 20`: `log2(20!) ≈ 61.1`, so ≥ 62 comparisons — verify insertion sort performs far more.

**Deliverable:** a table for n = 10, 20, 50, 100 of `log2(n!)` vs your measured comparison counts for insertion, selection, bubble, shell, `Arrays.sort`.

---

## Exercise 9 — Debugging drill: three broken sorts

Each of the three below passes 7/10 random tests. Find the bug in each and write a regression test.

1. **Broken shell sort:** `while (j >= gap && a[j] > key) { a[j] = a[j - gap]; j -= gap; }` — fails on `[5, 4, 3, 2, 1]` with gaps `{4, 2, 1}`? Trace it.
2. **Broken bubble:** loop bound uses `i < end` but the swap test uses `a[i] >= a[i+1]` (non-strict) and `if (!swapped) break;` is placed *before* the inner loop — what happens?
3. **Broken selection:** `if (a[j] <= a[min]) min = j;` — is the result sorted? Is it stable? Which one breaks and why?

---

## Exercise 10 — Deliverable

Build a `SortRace` main class in `BENCHMARK/` that:
1. Generates 8 input distributions (random, sorted, reverse, few-unique, sawtooth, organ-pipe, all-equal, shuffled-with-1-swap).
2. Runs insertion / selection / bubble / shaker / comb / shell / `Arrays.sort` on each.
3. Prints a markdown table of nanoseconds and comparison counts.
4. Flags any case where your hand-rolled sort is slower than `Arrays.sort` and explains why.

**Success criterion:** you can state, from measurements, exactly when a quadratic sort is the *correct* engineering choice (answer: arrays of ≤ 32 elements, or ≤ 2 swaps per element, where constant factors beat asymptotics).