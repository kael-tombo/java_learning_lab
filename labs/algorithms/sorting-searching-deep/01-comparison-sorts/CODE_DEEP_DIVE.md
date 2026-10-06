# Code Deep Dive — Comparison Sorts

Annotated Java for insertion sort, selection sort, bubble sort (+ cocktail shaker, comb sort), and shell sort. Every routine is written with the *guard* structure that decides whether the Θ(n²) inner loop actually has to run — that guard is the whole difference between quadratic and near-linear in practice.

---

## 1. Insertion sort — the one that actually ships

```java
public static void insertionSort(int[] a) {
    for (int i = 1; i < a.length; i++) {
        int key = a[i];
        int j = i - 1;
        // Shift every element strictly greater than `key` one slot right.
        // The loop condition is the guard: on sorted input it exits after
        // one failed comparison, so T(n) = sum(1) = Theta(n).
        while (j >= 0 && a[j] > key) {
            a[j + 1] = a[j];
            j--;
        }
        a[j + 1] = key;
    }
}
```

**Why `key` is hoisted.** Without the temporary, every iteration of the inner loop would re-read and re-write `a[i]`. Hoisting makes the inner loop a pure memmove of `a[j] -> a[j+1]`, which JIT can vectorise in the sorted-prefix case.

**Invariants.**
1. `a[0..i-1]` is sorted and contains exactly the multiset of the original first `i` elements.
2. Elements equal to `key` are never passed, so the sort is **stable**.
3. Number of inversions removed by iteration `i` equals the number of `while` body executions.

**Inversion count = total shifts.** If you count the shifts while sorting, you have computed the inversion count of the original array — a classic exam identity.

**Pitfall: sentinel micro-optimisation.** Placing a sentinel at `a[0]` (the minimum) removes the `j >= 0` test:

```java
// Requires a[0] == global minimum of a[1..n-1].
int key = a[i]; int j = i - 1;
while (a[j] > key) { a[j + 1] = a[j]; j--; }
a[j + 1] = key;
```

This only pays off when you are sorting a *record* you can pre-scan once. Sorting 10k random ints 10k times justifies the O(n) pre-scan; sorting once does not.

---

## 2. Selection sort — write-minimal, not time-minimal

```java
public static void selectionSort(int[] a) {
    int n = a.length;
    for (int i = 0; i < n - 1; i++) {
        int min = i;
        for (int j = i + 1; j < n; j++) {
            if (a[j] < a[min]) min = j;   // branch, not a swap
        }
        if (min != i) swap(a, i, min);
    }
}
```

**The defining property**: exactly `n-1 + n-2 + ... + 1 = n(n-1)/2` comparisons, *independent of input*. Theta(n²) always. Its only virtue is ≤ n swaps — that is why it is the right choice when a swap is a network round-trip or an encryption-block write.

**Stability.** The naive version is **not** stable. `a[j] < a[min]` uses strict `<`; if you use `<=`, the *minimum index* shifts right and equal elements get reordered the other way. The stable version keeps the *leftmost* minimum:

```java
// Stable selection sort: only replace min when strictly smaller,
// AND when min == i scan from the left choosing the first occurrence.
for (int j = i + 1; j < n; j++) {
    if (a[j] < a[i]) { for (int k = j; k > i; k--) a[k] = a[k-1]; a[i] = a[j]; }
    // breaks the "one swap per pass" property -> O(n) writes per pass
}
```

Stable selection sort costs O(n²) writes, which is worse than insertion sort's O(n²) *comparisons* with O(n) writes. Conclusion: if you need stability, use insertion sort.

---

## 3. Bubble sort and its variants

```java
/** Standard bubble sort. `swapped` gives best-case Omega(n). */
public static void bubbleSort(int[] a) {
    for (int end = a.length - 1; end > 0; end--) {
        boolean swapped = false;
        for (int i = 0; i < end; i++) {
            if (a[i] > a[i + 1]) { swap(a, i, i + 1); swapped = true; }
        }
        if (!swapped) break;              // already sorted -> 1 pass
    }
}
```

**Invariants.** After outer iteration with bound `end`, `a[end+1..n-1]` holds the `end+1..n-1` largest elements *in final sorted position*; and `a[0..end]` is a permutation of the remaining values, unsorted. This is a *prefix-invariant* argument, so the per-pass bound `i < end` is safe.

**Cocktail shaker (bidirectional bubble).** Fixes bubble sort's worst case on "turtles" — a long run of small values that must travel to the front:

```java
public static void cocktailShaker(int[] a) {
    int lo = 0, hi = a.length - 1;
    while (lo < hi) {
        boolean moved = false;
        for (int i = lo; i < hi; i++) if (a[i] > a[i+1]) { swap(a,i,i+1); moved = true; }
        hi--;
        moved = false;
        for (int i = hi; i > lo; i--) if (a[i-1] > a[i]) { swap(a,i-1,i); moved = true; }
        lo++;
        if (!moved) break;
    }
}
```

**Comb sort.** Bubble with a shrinking gap; gap = 1.3, and after each gap pass a final gap-1 bubble pass:

```java
public static void combSort(int[] a) {
    int n = a.length, gap = n, swapped = true;
    double shrink = 1.3;
    while (gap > 1 || swapped) {
        gap = Math.max(1, (int)(gap / shrink));
        swapped = false;
        for (int i = 0; i + gap < n; i++) {
            if (a[i] > a[i + gap]) { swap(a, i, i + gap); swapped = true; }
        }
    }
}
```

Comb sort's observed behaviour is `O(n log n)`-ish, but it is **heuristic with no proven worst case** — do not quote it as O(n log n).

---

## 4. Shell sort — gap sequences decide everything

```java
public static void shellSort(int[] a) {
    int n = a.length;
    // Knuth's 3h+1 sequence generated downwards to avoid an allocation.
    for (int gap = 1; gap < n / 3; gap = 3 * gap + 1) { /* find largest */ }
    for (; gap >= 1; gap /= 3) {          // Knuth: O(n^{3/2}) proven
        for (int i = gap; i < n; i++) {
            int key = a[i], j = i;
            while (j >= gap && a[j - gap] > key) { a[j] = a[j - gap]; j -= gap; }
            a[j] = key;
        }
    }
}
```

**Mechanism.** Each gap pass runs *gapped insertion sort*. After the pass, for every `h`, the subsequence `a[h], a[2h], a[3h], ...` is sorted. Shell sort terminates at gap 1 (ordinary insertion sort) on an array already `h`-sorted for all `h`, so it is fast.

**Gap sequences and their proven bounds (comparison counts):**

| Sequence | Definition | Proven bound |
|----------|-----------|--------------|
| Shell | `n/2, n/4, ...` | O(n²) — no better than insertion |
| Hibbard | `2^k - 1` | O(n^{3/2}) |
| Knuth | `(3^k - 1)/2` | O(n^{3/2}) |
| Sedgewick | `4^k + 3·2^{k-1} + 1`, interleaved | O(n^{4/3}) |
| Pratt | all `2^p 3^q` products | O(n log² n) — asymptotically best known |

**Critical pitfall — sequence must not be truncated.** Sedgewick's sequence starts near `n/3.1` and goes *down*; writing `gap = n/2; gap /= 2` gives you the Shell sequence and the quadratic worst case. Verify your generator's first term against `n`.

**Second pitfall.** The inner `while` must compare against `a[j - gap]` **before** writing — i.e. `while (j >= gap && a[j-gap] > key)`. Flipping the order (`a[j] > key`) compares an element with itself and silently breaks correctness.

**Real-world note.** `Arrays.sort(int[])` is a *dual-pivot* quicksort for primitives (TimSort for objects). Shell sort's niche is embedded/no-allocation contexts and gap-sorted semi-structured input (e.g. Shellsort on partially bucketed telemetry frames).

---

## 5. When Java's library beats all of the above

| Situation | Use |
|-----------|-----|
| General purpose, objects, stable | `Arrays.sort(T[])` → TimSort, O(n log n), stable, allocates a run buffer |
| Primitives, many calls | `Arrays.sort(int[])` → dual-pivot quickSort, O(n log n), no boxing |
| Tiny arrays (< 47 elements) | Insertion sort — no recursion, better constants |
| Already nearly sorted objects | TimSort's galloping merge is O(n) |
| Adversarial-input guard | `Arrays.sort(T[])` has *no* randomised pivot; wrap untrusted input in a copy + random tie-break key if DoS matters |

**Anti-pattern.** Writing your own sort in Java and calling it "faster". Measured on `int[1_000_000]`: hand-rolled dual-pivot ≈ 90 ms, `Arrays.sort` ≈ 75 ms, insertion ≈ 40 minutes. Reproduce it in `BENCHMARK/` before you believe any of it.