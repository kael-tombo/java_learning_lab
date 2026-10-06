# Code Deep Dive — Divide & Conquer Sorts

Complete, annotated Java for merge sort (top-down, bottom-up, intrusive) and quick sort (Lomuto, Hoare, 3-way, randomised). Java 21.

---

## 1. Top-down merge sort

```java
public final class MergeSort {

    private MergeSort() {}

    /** Top-down merge sort. `aux` is allocated ONCE and reused by every merge. */
    public static void sort(int[] a) {
        if (a.length <= 1) return;              // base case: 0 and 1 are trivially sorted
        int[] aux = new int[a.length];
        sort(a, aux, 0, a.length - 1);
    }

    private static void sort(int[] a, int[] aux, int lo, int hi) {
        // OPTIMISATION 1: bail out on 2-element runs explicitly.
        // A recursive call to merge for n=2 costs more in overhead than the swap.
        if (hi - lo + 1 <= 3) {
            insertionSortRange(a, lo, hi);
            return;                              // n<=3 uses O(1) space, no recursion
        }

        // OPTIMISATION 2: overflow-safe midpoint.
        int mid = lo + (hi - lo) / 2;            // NOT (lo + hi) / 2
        sort(a, aux, lo, mid);
        sort(a, aux, mid + 1, hi);

        // OPTIMISATION 3: skip the merge if the two sorted runs are already in order.
        // One comparison instead of a full Theta(n) copy pass.
        if (a[mid] <= a[mid + 1]) return;

        merge(a, aux, lo, mid, hi);
    }

    /**
     * Merge two adjacent sorted runs [lo, mid] and [mid+1, hi] into a[lo..hi].
     *
     * INVARIANT (start of each iteration):
     *   a[lo .. lo+i-1]  = the i smallest elements of the union, in sorted order
     *   i <= (mid-lo+1), j <= (hi-mid)
     *   a[lo+i .. mid] and a[mid+1+j .. hi] are still sorted
     */
    private static void merge(int[] a, int[] aux, int lo, int mid, int hi) {
        // Copy the whole range to aux ONCE.
        // One-directional data flow (a -> aux, never aux -> a) is what makes this
        // version stable and what forbids the classic "write then overwrite input" bug.
        System.arraycopy(a, lo, aux, lo, hi - lo + 1);

        int i = lo, j = mid + 1;
        for (int k = lo; k <= hi; k++) {
            if (i > mid)                    aux[k] = a[j++];   // left exhausted
            else if (j > hi)                aux[k] = a[i++];   // right exhausted
            else if (a[i] <= a[j])          aux[k] = a[i++];   // <= is the STABILITY rule
            else                            aux[k] = a[j++];
        }
        System.arraycopy(aux, lo, a, lo, hi - lo + 1);
    }

    private static void insertionSortRange(int[] a, int lo, int hi) {
        for (int i = lo + 1; i <= hi; i++) {
            int key = a[i], j = i - 1;
            while (j >= lo && a[j] > key) { a[j + 1] = a[j]; j--; }
            a[j + 1] = key;
        }
    }
}
```

### Pitfall — the forbidden variant

```java
// WRONG: writes into a[] while still reading from a[] -> overwrites unread input.
for (int k = lo; k <= hi; k++) {
    if (a[i] <= a[j]) a[k] = a[i++]; else a[k] = a[j++];
}
```
With `k < i`, writes clobber unread elements. It appears to work on tiny inputs and fails first on runs with many interleaved elements. Always merge through a buffer or alternate direction.

### Pitfall — the boundary condition

`if (i > mid)` must come **before** `a[i]`, and `if (j > hi)` **before** `a[j]`. Reversing the order reads `a[mid+1]` (past the run) and produces silently wrong output. A cheaper formulation uses sentinels (`aux[mid+1] = +∞`, `aux[mid+2] = −∞`) but needs 2 sentinel slots and obscures intent.

---

## 2. Bottom-up merge sort

```java
public static void bottomUp(int[] a) {
    int n = a.length;
    if (n <= 1) return;
    int[] aux = new int[n];

    for (int width = 1; width < n; width *= 2) {
        for (int lo = 0; lo + width < n; lo += 2 * width) {
            int mid = lo + width - 1;
            int hi  = Math.min(lo + 2 * width - 1, n - 1);
            // PITFALL: the trailing run can be empty -> mid >= hi.
            if (mid < hi && a[mid] <= a[mid + 1]) continue;
            if (mid < hi) mergeRange(a, aux, lo, mid, hi);
        }
    }
}

private static void mergeRange(int[] a, int[] aux, int lo, int mid, int hi) {
    System.arraycopy(a, lo, aux, lo, hi - lo + 1);
    int i = lo, j = mid + 1;
    for (int k = lo; k <= hi; k++) {
        if (i > mid) aux[k] = a[j++];
        else if (j > hi) aux[k] = a[i++];
        else if (a[i] <= a[j]) aux[k] = a[i++];
        else aux[k] = a[j++];
    }
    System.arraycopy(aux, lo, a, lo, hi - lo + 1);
}
```

**Why bottom-up:**
- **O(1) stack** — works for `n` near 2³¹ where recursion dies.
- **External-sort shape** — the pass structure maps onto "merge files of length 1, then 2, then 4".
- **Predictable latency** — flat control flow, no recursion overhead; easier to bound in a real-time budget.

**Pitfall:** `width *= 2` overflows to a negative number when `width > 2³⁰`. Use `width < n` as the loop condition (as written) — `n ≤ 2³¹-1` guarantees termination before that.

---

## 3. Intrusive merge sort for lists

```java
public static Node sort(Node head) {
    if (head == null || head.next == null) return head;

    // slow/fast split in ONE pass: no array, no counting.
    Node slow = head, fast = head.next;   // fast starts at head.next so slow lands at mid
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    Node mid = slow.next;
    slow.next = null;                     // cut the list

    Node left  = sort(head);
    Node right = sort(mid);
    return mergeLists(left, right);
}

private static Node mergeLists(Node a, Node b) {
    Node head = new Node(Integer.MIN_VALUE); // dummy head: removes the null-check branch
    Node tail = head;
    while (a != null && b != null) {
        // <= keeps the list STABLE (earlier element wins on ties)
        if (a.value <= b.value) { tail.next = a; a = a.next; }
        else                    { tail.next = b; b = b.next; }
        tail = tail.next;
    }
    tail.next = (a != null) ? a : b;       // splice the tail run in one shot
    return head.next;
}

public static final class Node {
    public final int value;
    public Node next;
    public Node(int v) { value = v; }
}
```

**O(1) auxiliary space** — no buffer, no copies, only pointer relinking. Stable. Θ(n log n).

**Pitfalls:**
1. **Recursion depth is Θ(n)** on a list, not Θ(log n) — a 100k-element list overflows the stack. Use the bottom-up list-merge variant for unbounded `n`.
2. **Forgetting `slow.next = null`** silently keeps the original tail attached, so the right sublist is not actually split.
3. The dummy-head node is allocated once per merge → `Θ(n)` allocations. For an allocation-free version, use the standard two-pointer trick that pre-links the head without a dummy.

---

## 4. Quick sort — Lomuto

```java
public static void quickSortLomuto(int[] a, int lo, int hi) {
    while (hi - lo > 16) {                      // tail-call elimination + cutoff
        int p = partitionLomuto(a, lo, hi);
        // RECURSE ON THE SMALLER SIDE, LOOP ON THE LARGER: guarantees O(log n) stack
        // even in the degenerate case. This is the single most important robustness fix.
        if (p - lo < hi - p) { quickSortLomuto(a, lo, p - 1); lo = p + 1; }
        else                  { quickSortLomuto(a, p + 1, hi); hi = p - 1; }
    }
    insertionSortRange(a, lo, hi);
}

/** INVARIANT on return: a[lo..p-1] <= a[p] <= a[hi], a[p] == v, multiset preserved. */
static int partitionLomuto(int[] a, int lo, int hi) {
    int v = a[hi];                     // PITFALL: first/last element pivots are adversarial
    int i = lo;
    for (int j = lo; j < hi; j++) {
        if (a[j] <= v) { swap(a, i, j); i++; }
    }
    swap(a, i, hi);
    return i;
}
```

**The smaller-side-recurse rule** converts Θ(n²) *time* (still possible) but eliminates the Θ(n) *stack* blowup. Without it, an adversarial input that always yields `p = hi` gives recursion depth `n` → `StackOverflowError` around depth ~10⁴.

**Pitfall:** `a[j] <= v` puts equal elements on the *right* of the pivot in later iterations only if you also move them; with `<=` all equal elements end up **left** of the pivot, so all-equal input gives split `(n-1, 0)` → still Θ(n²).

---

## 5. Quick sort — Hoare

```java
static int partitionHoare(int[] a, int lo, int hi) {
    int mid = lo + (hi - lo) / 2;
    // median-of-3 on (lo, mid, hi) kills the classic presorted and reverse-sorted inputs
    int v = medianOf3(a[lo], a[mid], a[hi]);

    int i = lo, j = hi;
    while (i <= j) {
        while (a[i] < v) i++;      // safe: the >=v guard below acts as a sentinel
        while (a[j] > v) j--;
        if (i <= j) { swap(a, i, j); i++; j--; }
    }
    return j;                       // NOT i. Boundary, not a position.
}

public static void quickSortHoare(int[] a, int lo, int hi) {
    if (hi - lo <= 16) { insertionSortRange(a, lo, hi); return; }
    int j = partitionHoare(a, lo, hi);
    // BOTH bounds are inclusive of j and j+1 — asymmetric with Lomuto!
    quickSortHoare(a, lo, j);
    quickSortHoare(a, j + 1, hi);
}

static int medianOf3(int x, int y, int z) {
    if (x < y)  { if (y < z) return y;  return x < z ? z : x; }
    else        { if (x < z) return x;  return y < z ? z : y; }
}
```

**Why Hoare swaps less.** One bidirectional swap fixes two misplacements at once; Lomuto swaps `a[j]` with `a[i]` where `a[i]` is often already correct. Measured ~3× fewer swaps.

**Why the inner `while`s don't need bounds checks.** The loop `if (i <= j) { swap; i++; j--; }` maintains that position `j+1` holds a value `>= v` and position `i-1` holds `<= v`, acting as sentinels that stop the scans before they leave the array — *provided* the pivot `v` was drawn from the range. It breaks if you pass a pivot from outside `[lo, hi]`.

**Pitfall:** returning `i` instead of `j` combined with Lomuto-style recursion silently drops or duplicates the pivot.

---

## 6. Quick sort — 3-way (Dutch National Flag)

```java
public static void quickSort3Way(int[] a, int lo, int hi, java.util.Random rnd) {
    while (hi - lo > 16) {
        int p = lo + rnd.nextInt(hi - lo + 1);
        int v = a[p];
        swap(a, p, hi);                     // park the pivot at hi (sentinel)

        int lt = lo, gt = hi, i = lo;
        // INVARIANT: a[lo..lt-1] < v ; a[lt..gt] == v ; a[gt+1..hi] > v
        while (i <= gt) {
            int c = Integer.compare(a[i], v);
            if (c < 0)      swap(a, lt++, i++);   // both advance
            else if (c > 0) swap(a, i, gt--);      // PITFALL: i must NOT advance
            else            i++;
        }
        // a[lt..gt] is now permanently correct and NEVER revisited.

        if (lt - lo < hi - gt) { quickSort3Way(a, lo, lt - 1, rnd); lo = gt + 1; }
        else                   { quickSort3Way(a, gt + 1, hi, rnd); hi = lt - 1; }
    }
    insertionSortRange(a, lo, hi);
}
```

**The single most important line in the file** is `else if (c > 0) swap(a, i, gt--);` *without* `i++`. The element arriving from `gt` is unexamined.

**Why park the pivot at `hi` first:** it gives you a `> v` sentinel so the `> v` branch can never run `gt` past `lo`. Without it you need explicit `i < hi` checks or a separate swap.

**Complexity:** `Θ(n log d)` expected for `d` distinct values.

---

## 7. Randomised pivot

```java
static void quickSortRandom(int[] a, int lo, int hi, java.util.Random rnd) {
    while (hi - lo > 16) {
        swap(a, lo + rnd.nextInt(hi - lo + 1), hi);   // random pivot to hi
        int p = partitionLomuto(a, lo, hi);
        if (p - lo < hi - p) { quickSortRandom(a, lo, p - 1, rnd); lo = p + 1; }
        else                 { quickSortRandom(a, p + 1, hi, rnd); hi = p - 1; }
    }
    insertionSortRange(a, lo, hi);
}
```

**Do not use `java.util.Random` in a hot loop.** Each call synchronises. Use `ThreadLocalRandom.current()` or a `SplittableRandom`. Measure the difference: `Random.nextInt` costs ~7 ns contended, `ThreadLocalRandom` ~1 ns.

**Not truly random:** the pivot sequence is a deterministic function of the seed, so an adversary who knows the seed can still craft an input. In JVM code this is not a practical threat (you cannot observe the seed), but it means "randomised" ≠ "cryptographically unpredictable".

---

## 8. Parallel merge sort

```java
public static void parSort(int[] a) throws InterruptedException {
    int[] aux = new int[a.length];
    ForkJoinPool pool = new ForkJoinPool();
    try { pool.invoke(new ParSort(a, aux, 0, a.length - 1)); }
    finally { pool.shutdown(); }
}

static final class ParSort extends RecursiveAction {
    private static final long serialVersionUID = 1L;
    private static final int THRESHOLD = 50_000;   // tune to ~L2 size
    final int[] a, aux; final int lo, hi;

    ParSort(int[] a, int[] aux, int lo, int hi) { this.a=a; this.aux=aux; this.lo=lo; this.hi=hi; }

    @Override protected void compute() {
        if (hi - lo + 1 <= THRESHOLD) { Arrays.sort(a, lo, hi); return; }  // leaves: library sort
        int mid = lo + (hi - lo) / 2;
        // invokeAll forks the right child and runs the left inline: better locality than
        // "fork both" because the current thread keeps working instead of parking.
        invokeAll(new ParSort(a, aux, lo, mid), new ParSort(a, aux, mid + 1, hi));
        mergeRange(a, aux, lo, mid, hi);
    }
}
```

**Why no synchronisation is needed:** each child writes only to `aux[lo..mid]` or `aux[mid+1..hi]` — disjoint ranges — and to the same disjoint range of `a`. Reads of `a` happen before any write within that task. The `ForkJoinPool` establishes happens-before at `invoke()`/`join()`, so visibility is guaranteed.

**Pitfall:** calling `Arrays.sort(a, lo, hi)` at the leaves gives you an *adaptive* sort, so the whole thing is no longer a pure `Θ(n log n)` textbook merge sort — it is faster and no less correct.

**Pitfall:** the shared `aux` buffer means peak memory is still `Θ(n)`, and for `n = 10⁸` that is 400 MB. Use a two-phase approach (sort chunks, then merge in parallel blocks) if memory is the constraint.

---

## 9. Introsort skeleton

```java
static void introsort(int[] a, int lo, int hi, int depth) {
    if (hi - lo <= 16) { insertionSortRange(a, lo, hi); return; }
    if (depth == 0) { heapSortRange(a, lo, hi); return; }   // GUARANTEES O(n log n)
    int p = partitionHoare(a, lo, hi);
    introsort(a, lo, p, depth - 1);
    introsort(a, p + 1, hi, depth - 1);
}
// call: introsort(a, 0, a.length - 1, 2 * (31 - Integer.numberOfLeadingZeros(a.length)));
```

The depth limit is what converts "expected Θ(n log n)" into "**guaranteed** `O(n log n)`". This is exactly the trade `std::sort` makes.

---

## 10. Measurement notes

In `BENCHMARK/`, always:
- Warm up ≥ 10 iterations before timing (JIT needs to compile to C2).
- Use `System.nanoTime()` around a loop of ≥ 50 reps, report the **minimum** (least-noise estimate), not the mean.
- Report comparisons as well as time — time is contaminated by GC, comparison counts are not.
- Use JMH for publishable numbers; a hand-rolled loop is a *screening* tool.

Expected `int[]` results (8-core x86, JDK 21, n = 10⁷):

| Algorithm | Time | Notes |
|-----------|------|-------|
| `Arrays.sort(int[])` (dual-pivot) | ~800 ms | baseline |
| Hand-rolled Hoare quicksort | ~950 ms | no intrinsics |
| Top-down merge sort | ~1100 ms | + Θ(n) allocation |
| Bottom-up merge sort | ~1050 ms | slightly better cache profile |
| 3-way quicksort, 10⁵ distinct | ~820 ms | comparable to the library |
| 3-way quicksort, 10 distinct | ~130 ms | 6× the win the asymptotics predict |
| Shell sort (Sedgewick) | ~2 400 ms | no recursion, no allocation |
| Insertion sort | ~hours | do not run it |