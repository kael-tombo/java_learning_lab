# Code Deep Dive — Order Statistics

Annotated Java: quickselect (3-way + randomised), median-of-medians, Fenwick tree k-th, bounded-heap top-k, and streaming selection. Java 21.

---

## 1. Quickselect — production shape

```java
public final class QuickSelect {

    private static final ThreadLocalRandom RND = ThreadLocalRandom.current();

    /**
     * Returns the k-th SMALLEST element (0-based rank). PARTITIONS a[] in place.
     * a[0..k] <= result <= a[k..n-1] afterwards.
     */
    public static int select(int[] a, int k) {
        if (k < 0 || k >= a.length) throw new IndexOutOfBoundsException("rank " + k);
        int lo = 0, hi = a.length - 1;

        while (lo < hi) {
            int p = partition3Way(a, lo, hi);   // 3-way handles duplicates in O(1)
            if (p == k) return a[k];
            if (p < k) lo = p + 1;              // discard [lo, p] -- guaranteed <= answer
            else hi = p - 1;                    // discard [p, hi] -- guaranteed >= answer
        }
        return a[lo];
    }

    /**
     * 3-way (Dutch national flag) partition.
     * Returns j such that a[lo..j-1] < pivot == a[j..gt], a[gt+1..hi] > pivot.
     */
    private static int partition3Way(int[] a, int lo, int hi) {
        // RANDOM PIVOT: not the first/last/median-of-3. Randomisation is the only
        // defence against a pre-computed adversarial input.
        int v = a[lo + RND.nextInt(hi - lo + 1)];

        int lt = lo, gt = hi, i = lo;
        // INVARIANT: a[lo..lt-1] < v ; a[lt..gt] == v ; a[gt+1..hi] > v
        while (i <= gt) {
            int c = Integer.compare(a[i], v);
            if (c < 0)      swap(a, lt++, i++);   // both advance
            else if (c > 0) swap(a, i, gt--);      // PITFALL: i must NOT advance
            else            i++;
        }
        // a[lt..gt] is already in final position -- skip it entirely
        return lt + (gt - lt) / 2;                 // a pivot INSIDE the equal block
    }

    private static void swap(int i, int j) { if (i == j) return; int t = a_i_j_swap; }
}
```

**Corrected `swap`:**

```java
private static void swap(int[] a, int i, int j) {
    if (i == j) return;                    // avoid a pointless write
    int t = a[i]; a[i] = a[j]; a[j] = t;
}
```

### Why 3-way, not 2-way

With `d` distinct values, 3-way quickselect's expected comparisons are `Θ(n log d)`; 2-way is `Θ(n)` expected for a single selection on *distinct* data but **`Θ(n²)` on all-equal data** (every partition splits `(0, n-1)`). 3-way turns the all-equal case into a single linear pass.

### Why the pivot returned is `lt + (gt - lt) / 2` and not `lt`

If the target rank `k` lies inside the equal block `[lt, gt]`, any index in that block works — and returning the *middle* means the caller's `if (p == k)` is often false but `p < k` or `p > k` correctly narrows by a lot. Returning `lt` would also be correct; the middle is a small constant-factor win.

### Stack safety

Quickselect uses a `while` loop, so the stack is `O(1)` regardless of pivot quality. If you write it recursively, you **must** recurse on the smaller side:

```java
private static int selectRec(int[] a, int lo, int hi, int k) {
    while (lo < hi) {
        int p = partition(a, lo, hi);
        if (p == k) return a[p];
        int smallLo = Math.min(lo, p - 1), smallHi = Math.min(hi, p - 1);
        if (smallHi - smallLo < hi - lo - (Math.max(lo, p+1) - Math.max(hi, p+1))) {
            selectRec(a, smallLo, smallHi, k);
            lo = p + 1;
        } else {
            selectRec(a, Math.max(lo, p + 1), hi, k);
            hi = p - 1;
        }
    }
    return a[lo];
}
```

The cleanest version uses `if (p - lo < hi - p) { recurse left; lo = p+1; } else { recurse right; hi = p-1; }`.

---

## 2. Median of medians

```java
public static int selectDeterministic(int[] a, int k) {
    int lo = 0, hi = a.length - 1;
    while (hi - lo > 5) {
        int pivot = medianOfMedians(a, lo, hi);
        int p = partition(a, lo, hi, pivot);      // put pivot at its final index
        if (p == k) return a[p];
        if (p < k) lo = p + 1; else hi = p - 1;
    }
    return Arrays.sort(a, lo, hi) == null ? a[lo + (k - lo)] : a[k];   // base: <= 5 elements
}

/** Sorts each 5-group in place, collects medians, recurses on the medians. */
private static int medianOfMedians(int[] a, int lo, int hi) {
    int n = hi - lo + 1;
    int groups = (n + 4) / 5;
    int[] medians = new int[groups];

    for (int g = 0; g < groups; g++) {
        int s = lo + g * 5;
        int e = Math.min(s + 4, hi);
        Arrays.sort(a, s, e + 1);              // 5-element sort: insertion sort in practice
        medians[g] = a[s + (e - s) / 2];        // the group's median
    }
    return selectDeterministic(medians, groups / 2);   // median OF the medians
}

/** Hoare partition by explicit value; returns the index of the first element >= pivot. */
private static int partition(int[] a, int lo, int hi, int pivotValue) {
    int i = lo, j = hi;
    while (i <= j) {
        while (a[i] < pivotValue) i++;
        while (a[j] > pivotValue) j--;
        if (i <= j) { swap(a, i, j); i++; j--; }
    }
    return i;      // a[lo..i-1] < pivot, a[i..hi] >= pivot  (i is the FIRST >= pivot)
}
```

### Pitfalls

1. **`Arrays.sort(a, s, e + 1)` — the `+1`.** Java ranges are `[from, to)`. Getting this wrong sorts the wrong window and *silently* breaks the pivot guarantee, degrading the algorithm to `Θ(n log n)` — or worse.
2. **The base case.** Must sort the final ≤ 5 elements and index by `k - lo`. Writing `return a[k]` also works but is fragile; `k - lo` is correct because `k` is a global rank and the range may not start at 0.
3. **Allocating `int[] medians` per level.** `Θ(log n)` allocations of total size `n/5 + n/25 + ... ≈ n/4`. For `n = 10⁸` that is 100 MB of garbage. Pass a reusable scratch buffer down the recursion, or use a `ThreadLocal` scratch.
4. **Returning `i` vs `j` from the Hoare partition.** This returns `i`, the first index `≥ pivot`. Using the Lomuto `j` convention silently changes which half is discarded.
5. **Measured performance:** ~310 ms vs quickselect's ~55 ms at `n = 10⁶`. It is a *correctness/guarantee* tool, not a speed tool.

---

## 3. Fenwick tree — `Θ(log n)` k-th

```java
public final class Fenwick {
    private final int[] tree;
    private final int n;

    public Fenwick(int[] values) {          // 1-indexed conceptually
        this.n = values.length;
        this.tree = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            tree[i] += values[i - 1];
            int parent = i + (i & -i);      // lowbit
            if (parent <= n) tree[parent] += tree[i];
        }
    }

    /** Prefix sum of values[0..i] inclusive. */
    public int prefixSum(int i) {           // i is 0-BASED
        int s = 0;
        for (int k = i + 1; k > 0; k -= k & -k) s += tree[k];
        return s;
    }

    public void add(int i, int delta) {
        for (int k = i + 1; k <= n; k += k & -k) tree[k] += delta;
    }

    /**
     * Index of the k-th SMALLEST value, k 1-based. Returns -1 if total < k.
     * BINARY LIFTING: one pass down the interval decomposition tree.
     * INVARIANT: idx is the largest index with prefixSum(idx) < k.
     */
    public int findByOrder(int k) {
        if (k < 1 || k > prefixSum(n - 1)) return -1;
        int idx = 0;
        // Start at the largest power of two <= n; each step halves.
        for (int step = Integer.highestOneBit(n); step > 0; step >>>= 1) {
            int next = idx + step;
            if (next <= n && tree[next] < k) {   // the whole block [idx+1..next] is too small
                idx = next;
                k -= tree[next];                 // skip it -- this is the O(log n) trick
            }
        }
        return idx;      // 0-based index of the k-th smallest
    }
}
```

**Pitfalls:**
- `findByOrder` returns a **0-based index** (because `idx` is 0-based), not the value. To get the value you need the original array: `values[findByOrder(k)]`.
- `tree[next] < k` uses `k` **already decremented** by skipped blocks. Forgetting the `k -= tree[next]` line makes it return an index that is too small and produces a plausible-looking wrong answer.
- `Integer.highestOneBit(n)` is `0` for `n = 0`. Guard the constructor.
- **Deletions:** `add(i, -count)` requires non-negative frequencies. A Fenwick cannot represent negative point values without breaking the prefix-sum monotonicity that `findByOrder` relies on.

---

## 4. Bounded-heap top-k

```java
/**
 * k SMALLEST elements, in ASCENDING order, without touching the input.
 * Uses a MAX-heap so the REJECTION test is O(1).
 */
public static <T> List<T> kSmallest(Iterable<T> src, int k, Comparator<? super T> cmp) {
    if (k <= 0) return List.of();
    Comparator<T> reverse = cmp.reversed();          // MAX-heap of the k best
    PriorityQueue<T> heap = new PriorityQueue<>(Math.max(1, k), reverse);
    for (T x : src) {
        if (heap.size() < k) heap.offer(x);
        else if (cmp.compare(x, heap.peek()) < 0) {  // O(1) reject for most elements
            heap.poll();                              // O(log k)
            heap.offer(x);                            // O(log k)
        }
    }
    List<T> out = new ArrayList<>(heap);
    Collections.sort(out, cmp);                       // drain: n log n for the SMALL set
    return out;
}

/** k LARGEST elements -- MIN-heap of size k (the mirror image). */
public static <T> List<T> kLargest(Iterable<T> src, int k, Comparator<? super T> cmp) {
    PriorityQueue<T> heap = new PriorityQueue<>(Math.max(1, k), cmp);   // min-heap
    for (T x : src) {
        if (heap.size() < k) heap.offer(x);
        else if (cmp.compare(x, heap.peek()) > 0) { heap.poll(); heap.offer(x); }
    }
    return new ArrayList<>(heap);
}
```

**The one design decision that matters:** the heap's ordering must be the *opposite* of the "keep" predicate, so that the element most likely to be rejected is `peek()` and the rejection test is `O(1)`.

| Goal | Heap type | Rejection test |
|------|-----------|---------------|
| k smallest | **max**-heap | `x >= peek()` → reject (the current worst of the k best) |
| k largest | **min**-heap | `x <= peek()` → reject |

Getting this backwards gives a `Θ(log k)` cost for every element instead of `Θ(1)`, which is a 10–20× slowdown at `k = 10⁶`.

**`PriorityQueue` is not iterable in sorted order** — you must either `poll()` all `k` elements (`Θ(k log k)`) or copy and sort (`Θ(k log k)` but with better constants for small `k`). For `k` small relative to `n`, copy-and-sort is fine.

---

## 5. Streaming selection without a stream buffer

```java
/** k-th smallest of a one-shot stream, O(k) memory, Theta(n log k). */
public static <T> T kthSmallestStreaming(Iterator<T> src, int k, Comparator<? super T> cmp) {
    if (k <= 0) throw new IllegalArgumentException("k");
    PriorityQueue<T> heap = new PriorityQueue<>(k, cmp.reversed());   // max-heap of size k
    while (src.hasNext()) {
        T x = src.next();
        if (heap.size() < k) heap.offer(x);
        else if (cmp.compare(x, heap.peek()) < 0) { heap.poll(); heap.offer(x); }
    }
    if (heap.size() < k) throw new IllegalArgumentException("stream shorter than k");
    return heap.peek();                            // the max of the k smallest == the k-th smallest
}
```

**The neat trick:** with a max-heap of exactly the `k` smallest elements, `peek()` **is** the `k`-th smallest. No extra extraction needed.

### Reservoir sampling (for a random *sample*, not an order statistic)

```java
/** Uniform random sample of size k from a stream, O(k) memory, ONE pass. */
public static <T> List<T> reservoirSample(Iterator<T> src, int k, Random rnd) {
    List<T> reservoir = new ArrayList<>(k);
    int seen = 0;
    while (src.hasNext()) {
        T x = src.next();
        if (seen < k) reservoir.add(x);
        else {
            int j = rnd.nextInt(seen + 1);        // uniform in [0, seen]
            if (j < k) reservoir.set(j, x);       // reservoir[j] = x
        }
        seen++;
    }
    return reservoir;
}
```

**Invariant:** after `seen` items, `reservoir` is a uniformly random `k`-subset of them. Proof sketch: item `seen+1` enters with probability `k/(seen+1)` (the `j < k` test) and each of the `k` slots is equally likely — exactly matching a uniform draw.

**Cost:** `Θ(n)` expected, `O(k)` memory. **Note:** reservoir sampling gives a random *sample*, so you can estimate percentiles but not compute the exact median unless you sort the reservoir (`O(k log k)`) and accept the sampling error.

---

## 6. Weighted order statistics

```java
/** Weighted k-th: pick x minimizing the total weight strictly below x. */
public static int weightedSelect(int[] value, long[] weight, long target) {
    int n = value.length;
    // Requires value[] sorted (or sort pairs first)
    long acc = 0;
    for (int i = 0; i < n; i++) {
        long w = weight[i];
        if (target < acc + w) return i;
        acc += w;
    }
    return n - 1;
}
```

Linear after a sort. **The real version** partitions on `weight` prefix sums like quickselect partitions on values — `Θ(n)` expected without the sort. Used in weighted percentiles (a latency sample where some requests were retried and count double).

---

## 7. Parallel selection

```java
public static int medianParallel(int[] a) throws InterruptedException {
    int n = a.length;
    if (n == 0) throw new IllegalArgumentException();
    int p = Math.min(Runtime.getRuntime().availableProcessors(), 64);
    if (p == 1 || n < 1 << 20) return QuickSelect.select(a, n / 2);

    // 1. Each thread takes the local median of its block.
    int[] blockMedians = new int[p];
    CountDownLatch done = new CountDownLatch(p);
    for (int t = 0; t < p; t++) {
        final int id = t;
        new Thread(() -> {
            int lo = id * (n / p), hi = (id + 1) * (n / p) - 1;
            blockMedians[id] = QuickSelect.select(a, lo, (hi - lo) / 2);
            done.countDown();
        }).start();
    }
    done.await();

    // 2. Median of the p block medians -> a pivot with >= n/(2p) elements on each side.
    int pivot = QuickSelect.select(blockMedians, p / 2);

    // 3. Global count of elements < pivot.
    int[] cnt = new int[1];
    for (int t = 0; t < p; t++) {
        final int id = t;
        new Thread(() -> {
            int lo = id * (n / p), hi = (id + 1) * (n / p) - 1;
            for (int i = lo; i <= hi; i++) if (a[i] < pivot) cnt[0]++;
        }).start();
    }
    // ...join...

    int rank = cnt[0];
    if (rank == n / 2) return pivot;
    // 4. The answer lives in ONE block; find it with a local quickselect.
    for (int t = 0; t < p; t++) {
        int lo = t * (n / p), hi = (t + 1) * (n / p) - 1;
        int below = 0;
        for (int i = lo; i <= hi; i++) if (a[i] < pivot) below++;
        if (rank < below) return QuickSelect.select(a, lo + (rank - (rank - below)), lo + below - 1);
        rank -= below;
    }
    return pivot;
}
```

### Pitfalls that are structural, not typos

1. **`int[] cnt` incremented from several threads is not atomic.** Use `LongAdder`, `AtomicInteger`, or an `int[]` with one slot per thread. The sketch above is wrong as written and is fixed by giving each thread its own counter.
2. **The pivot guarantee.** A block median has ≥ half its block on each side, so the global pivot has ≥ `n/(2p)` elements on each side — good enough for `Θ(n)` work, but it does **not** give a `Θ(log n)`-depth bound. Depth is `Θ(n/p + p)`.
3. **Each thread's quickselect partitions its own block** — disjoint, no synchronisation needed. But step 3's *count* pass reads the whole array while no writes occur, so it is safe.
4. **`Runtime.availableProcessors()` in a container** reflects the cgroup quota on modern JDKs, but not always. Read it once and log it; do not call it in a loop.

---

## 8. What to actually use in Java

```java
// Single value, array disposable:
int kth = com.carrotsearch.hppc.IntArrays.select(a, k);   // hppc
// or, with no dependency:
int kth = select(a, k);                                    // your own

// k smallest of a collection -- Guava:
List<T> out = com.google.common.collect.Lists.partition(sorted, k).get(0);

// Percentiles over primitives -- fastutil:
int[] sorted = IntArrays.quickSort(IntArrays.asList(a).toIntArray());
int p95 = sorted[(int) (0.95 * sorted.length)];

// Everything else:
Arrays.sort(a);
int p95 = a[(int) (0.95 * a.length)];
```

**Measure before you optimise.** At `n = 10⁶`, `Arrays.sort` is ~75 ms and quickselect is ~50 ms — a 1.5× wall-clock win, not the 8× the comparison count suggests, because quickselect is memory-bound and sorting's merges are sequential. The 8× only materialises at `n ≥ 10⁸`, where the array no longer fits in cache for *either* algorithm but quickselect touches fewer bytes.

---

## 9. Verification suite

```java
static void fuzz() {
    Random rnd = new Random(7);
    for (int t = 0; t < 100_000; t++) {
        int n = rnd.nextInt(60);
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = rnd.nextInt(6);      // heavy duplicates
        if (n == 0) continue;
        int[] ref = a.clone(); Arrays.sort(ref);
        for (int k = 0; k < n; k++) {
            assert select(a.clone(), k) == ref[k] : "select failed at k=" + k;
            assert selectDeterministic(a.clone(), k) == ref[k] : "MoM failed at k=" + k;
        }
    }
}

static void testStackSafety() {
    // Adversarial for first/last pivot: if you use a non-randomised pivot,
    // 200_000 sorted elements overflow the stack with the recursive version.
    int[] sorted = new int[200_000];
    for (int i = 0; i < sorted.length; i++) sorted[i] = i;
    assert select(sorted.clone(), 100_000) == 100_000;
}
```

The `a.clone()` in the fuzz loop is not paranoia — several of the algorithms mutate the input in place, and *sharing* it across `k` values is exactly the bug the "input is destroyed" caveat warns about. A fuzz test that passes because it accidentally tests an already-partitioned array tells you nothing.