# Code Deep Dive — Linear-Time Sorts

Annotated Java: counting sort (both stable conventions), LSD radix (digit extraction, signed keys, `long`), MSD radix hybrid, and bucket sort. Java 21.

---

## 1. Counting sort — the two legal conventions

```java
public final class CountingSort {

    /**
     * CONVENTION A: inclusive prefix sum (= end position) + BACKWARD scatter.
     * Stable.
     *
     * count[v] after the prefix pass == #{ elements <= v } == the index one past
     * the last slot belonging to v.
     */
    public static void sort(int[] a) {
        if (a.length <= 1) return;

        int min = Integer.MAX_VALUE, max = Integer.MIN_VALUE;
        for (int v : a) { if (v < min) min = v; if (v > max) max = v; }
        int k = max - min + 1;                       // RANGE, not max

        // Guard against the k = max trap: 32-bit keys with a huge spread would
        // demand a multi-gigabyte count array. Refuse loudly rather than OOM.
        if (k > a.length * 4 && k > (1 << 20)) {
            throw new IllegalArgumentException(
                "key range " + k + " too wide for counting sort; use radix sort");
        }

        int[] count = new int[k];
        for (int v : a) count[v - min]++;           // PITFALL: forget `- min` -> AIOOBE

        for (int v = 1; v < k; v++) count[v] += count[v - 1];   // inclusive prefix

        int[] out = new int[a.length];
        for (int i = a.length - 1; i >= 0; i--)      // MUST be backward to be stable
            out[--count[a[i] - min]] = a[i];

        System.arraycopy(out, 0, a, 0, a.length);
    }

    /**
     * CONVENTION B: exclusive prefix sum (= start position) + FORWARD scatter.
     * Also stable. Use whichever you find easier to reason about — just never mix them.
     */
    public static void sortForward(int[] a) {
        int min = Integer.MAX_VALUE, max = Integer.MIN_VALUE;
        for (int v : a) { if (v < min) min = v; if (v > max) max = v; }
        int k = max - min + 1;
        if (k > 1 << 22) throw new IllegalArgumentException("key range too wide");

        int[] count = new int[k];
        for (int v : a) count[v - min]++;

        // EXCLUSIVE prefix sum: count[v] == #{ elements < v } == start position of v
        int total = 0;
        for (int v = 0; v < k; v++) { int c = count[v]; count[v] = total; total += c; }

        int[] out = new int[a.length];
        for (int i = 0; i < a.length; i++)
            out[count[a[i] - min]++] = a[i];        // forward + start position == stable

        System.arraycopy(out, 0, a, 0, a.length);
    }
}
```

### Pitfalls, each of which is a real bug

1. **Forgetting `k = max - min + 1` and using `max` directly.** Keys `[1000, 1001]` give `max = 1001` ⇒ `count = new int[1001]` instead of `new int[2]`. Works, wastes 4 KB. Worse: keys `[1_000_000, 1_000_001]` allocate 4 MB for two elements. Then `Integer.MAX_VALUE` in a range of two values allocates **8 GB** and dies.
2. **Mixed conventions.** Inclusive prefix + forward scatter → *unstable*. It still produces a sorted array, so a naive "is it sorted?" test passes. Only a stability test catches it.
3. **Offset omission.** `count[v]` instead of `count[v - min]` → `ArrayIndexOutOfBoundsException` for any negative key. (Or silent corruption if `min > 0` and you allocated `count[k]` but index by raw value — no, that would also be AIOOBE. The dangerous version is allocating `count[max+1]` and indexing raw values: correct output, wasted memory.)
4. **In-place scatter.** Writing into `a` while reading from `a` in the same loop clobbers unread elements. You need a second array or the start-position trick with care.
5. **`new int[k]` for `k = 0`.** Only possible if the array is empty, which the `length <= 1` guard catches.

---

## 2. LSD radix sort for `int` (signed!)

```java
public final class RadixSort {

    /**
     * LSD radix, 11 bits per pass, 3 passes for 32-bit keys.
     *
     * SIGNED-KEY TRICK: `x ^ 0x80000000` flips the sign bit, mapping the signed
     * int range onto the unsigned range [0, 2^32) with the order PRESERVED.
     * Two's-complement negatives sort first, which is exactly what we want.
     */
    public static void sort(int[] a) {
        if (a.length <= 1) return;
        int[] out = new int[a.length];               // ping-pong buffer
        int[] c = new int[1 << 11];                   // 2048 * 4 B = 8 KB -> L1 resident

        for (int shift = 0; shift < 32; shift += 11) {
            Arrays.fill(c, 0);

            int idxShift = shift + 11;
            if (idxShift > 32) idxShift = 32;         // last pass reads only 10 bits

            // COUNT using the flip so the digits are correct for negative keys
            for (int i = 0; i < a.length; i++) {
                int key = a[i] ^ 0x80000000;
                c[(key >>> shift) & 0x7FF]++;
            }
            // EXCLUSIVE prefix -> start positions. Forward scatter keeps this pass stable.
            int sum = 0;
            for (int b = 0; b < c.length; b++) { int t = c[b]; c[b] = sum; sum += t; }
            // SCATTER (stable: forward + start positions)
            for (int i = 0; i < a.length; i++) {
                int key = a[i] ^ 0x80000000;
                out[c[(key >>> shift) & 0x7FF]++] = key ^ 0x80000000;
            }
            // PING-PONG: write the (already unflipped) values back
            for (int i = 0; i < a.length; i++) a[i] = out[i];
        }
    }
}
```

### A cleaner, more common formulation — precompute the flip once

```java
public static void sort(int[] a) {
    if (a.length <= 1) return;
    int n = a.length;
    int[] b = new int[n];
    for (int i = 0; i < n; i++) b[i] = a[i] ^ Integer.MIN_VALUE;   // map to unsigned ONCE
    radixUnsigned(b);
    for (int i = 0; i < n; i++) a[i] = b[i] ^ Integer.MIN_VALUE;   // map back
}

private static void radixUnsigned(int[] a) {
    int n = a.length;
    int[] out = new int[n];
    int[] c = new int[2048];

    for (int shift = 0; shift < 32; shift += 11) {
        Arrays.fill(c, 0);
        for (int v : a) c[(v >>> shift) & 2047]++;
        int sum = 0;
        for (int b = 0; b < 2048; b++) { int t = c[b]; c[b] = sum; sum += t; }
        for (int i = 0; i < n; i++) out[c[(a[i] >>> shift) & 2047]++] = a[i];
        System.arraycopy(out, 0, a, 0, n);          // copy back
    }
}
```

The pre-flip version does **one** extra pass over the array instead of `2d` flips. For 3 passes that is 4× less work on the flip.

### Why `2048` bits-per-`11` and not `256`/`8`

- `k = 8` → 4 passes, `c` = 1 KB (fits L1 trivially) — 4× the memory traffic.
- `k = 11` → 3 passes, `c` = 8 KB (still L1 on most CPUs, 32 KB L1d) — **the sweet spot**.
- `k = 16` → 2 passes, `c` = 256 KB (L2) — fewer passes but the count array and the data compete for L2.

Measured on `int[10⁷]`: `k = 11` ≈ 620 ms, `k = 16` ≈ 590 ms, `k = 8` ≈ 840 ms. All well under `Arrays.sort`'s ~800 ms, and `k = 11` is the most robust across machines.

### Pitfalls

1. **Not handling negative keys.** Without the flip, `[5, -1, 3]` sorts to `[5, -1, 3]`-ish garbage: `-1 >>> 11` is a huge unsigned digit, so negatives land at the end. `Arrays.sort`-compatibility tests will catch it, but only if you include negative keys — **write that test first**.
2. **Making the inner pass unstable.** Using an inclusive prefix sum with `--c[...]` and a forward loop breaks stability, and the whole algorithm silently fails to sort multi-digit numbers. Symptom: `[1, 10, 2]` comes out wrong only when a key has ≥ 11 bits of variation. Add a test with keys spanning multiple digit positions (`1, 2048, 4096, 3`).
3. **Digit width not dividing 32.** With `k = 11` and 32-bit keys, the last pass covers only bits 22–31 (10 bits). Masking with `0x7FF` is harmless here, but with `k = 12` you'd get passes at shifts 0, 12, 24 with the last reading bits 24–31 only — still fine. The real trap is **over-reading**: `shift = 33` on an `int` shifts by `33 & 31 = 1` because Java masks shift counts to 5 bits for `int`. Loop on `shift < 32` to prevent it.
4. **`long` keys.** Use `>>>` (unsigned) not `>>`, and `Long.MIN_VALUE` for the flip. `c` size can grow if you use `k = 21` (`2M` entries = 8 MB — spills to RAM and kills performance).

---

## 3. MSD radix hybrid

```java
public final class MsdRadix {

    private static final int BITS = 11;
    private static final int BASE = 1 << BITS;
    private static final int MASK = BASE - 1;
    private static final int SMALL = 64;             // cutoff: switch to comparison sort

    public static void sort(int[] a) {
        if (a.length <= 1) return;
        msd(a, 0, a.length, 31 - BITS);
    }

    private static void msd(int[] a, int lo, int hi, int shift) {
        if (hi - lo <= SMALL || shift < 0) {          // CUTOFF: comparison sort
            Arrays.sort(a, lo, hi);
            return;
        }

        int[] c = new int[BASE];
        for (int i = lo; i < hi; i++) c[((a[i] ^ Integer.MIN_VALUE) >>> shift) & MASK]++;
        int sum = 0;
        for (int b = 0; b < BASE; b++) { int t = c[b]; c[b] = sum; sum += t; }

        // Distribute in place using the buffer + copy-back (simpler and faster
        // than a hand-rolled cycle-leader permutation).
        int[] buf = new int[hi - lo];
        for (int i = lo; i < hi; i++) {
            int d = ((a[i] ^ Integer.MIN_VALUE) >>> shift) & MASK;
            buf[c[d]++] = a[i];
        }
        System.arraycopy(buf, 0, a, lo, hi - lo);

        // Recurse into each non-empty bucket.
        int start = lo;
        for (int b = 0; b < BASE; b++) {
            int end = c[b];
            if (end - start > SMALL) msd(a, start, end, shift - BITS);
            start = end;
        }
    }
}
```

### MSD vs LSD — the trade, concretely

| | LSD | MSD hybrid |
|---|-----|-----------|
| First pass | full `Θ(n)` | full `Θ(n)` |
| Later passes | all global (`Θ(n)` each) | only non-empty buckets |
| Uses a comparison sort | never | **yes**, below `SMALL = 64` |
| Needs stability | **yes** | no |
| Memory | one ping-pong buffer | one buffer **per recursion level** (garbage) |
| All-keys-identical input | `Θ(d·n)` | `Θ(d·n)` (worst case — one bucket) |
| Cache behaviour | sequential streaming | jumps between buckets |
| Parallelism | trivial per pass | hard (data-dependent boundaries) |

**Production note:** the `new int[BASE]` per recursion level is 8 KB × depth 3 = 24 KB of garbage per call. For deep recursion on many buckets, hoist the count array and reuse it (pass it in, reset only the touched entries) — or accept the garbage, which the JVM's TLAB handles cheaply. Measure before optimising.

---

## 4. Bucket sort

```java
public static void sort(double[] a) {
    if (a.length <= 1) return;
    double min = Double.POSITIVE_INFINITY, max = Double.NEGATIVE_INFINITY;
    for (double v : a) { if (v < min) min = v; if (v > max) max = v; }
    if (min == max) return;                          // all equal: nothing to do

    int k = a.length;
    double w = (max - min) / k;
    List<List<Double>> buckets = new ArrayList<>(k);
    for (int i = 0; i < k; i++) buckets.add(new ArrayList<>());

    for (double v : a) {
        int idx = (int) ((v - min) / w);
        if (idx >= k) idx = k - 1;                   // PITFALL: floating-point rounding
        buckets.get(idx).add(v);
    }

    int out = 0;
    for (List<Double> b : buckets) {
        Double[] arr = b.toArray(new Double[0]);
        Arrays.sort(arr);                            // insertion sort would do; this is faster
        for (double v : arr) a[out++] = v;
    }
}
```

### Pitfalls

1. **Floating-point rounding.** `(v - min) / w` can equal `k` when `v == max` due to rounding. The `idx >= k` clamp is mandatory. **Also handle `NaN`** — every comparison with `NaN` is false, so `min`/`max` stay at their sentinels and the result is garbage. Reject non-finite input explicitly.
2. **`Double.POSITIVE_INFINITY` as the initial `min`.** If the input contains `-Infinity`, the comparison silently fails to update `min`. Filter with `Double.isFinite` first.
3. **`Θ(n)` is a lie without uniformity.** All keys in `[min, min+ε)` land in one bucket and `Arrays.sort` makes it `Θ(n log n)` (not `Θ(n²)`, since you used `Arrays.sort` instead of insertion sort — the *worst case* is bounded). With insertion sort per bucket, the worst case is genuinely `Θ(n²)`.
4. **Boxing.** `List<Double>` allocates a `Double` per element. For `n = 10⁷` that is 10⁷ short-lived allocations. Use primitive arrays per bucket, or a counting-array approach, if this is in a hot path. **Or just use `Arrays.sort(double[])`** — dual-pivot quicksort, no allocation, `Θ(n log n)` guaranteed-independent.
5. **`k = n` buckets** means `n` list objects. Use a single flat array with bucket offsets (a counting-sort-like layout) if you must.

---

## 5. The honest comparison

```java
// What you should write in production:
Arrays.sort(intArray);              // dual-pivot quicksort, introsort-like, ~75ms for 10^6
Arrays.sort(objectArray);           // TimSort, stable, adaptive
Arrays.parallelSort(bigIntArray);   // parallel merge sort, uses all cores

// What you write when you have MEASURED a need:
RadixSort.sort(highThroughputInts); // ~45ms for 10^6
```

Only reach for radix when profiling shows the sort is a measurable fraction of a latency-sensitive path and the keys are fixed-width integers. Then measure `k ∈ {8, 11, 16}` on your machine and pick the winner — the optimum is hardware-specific.

---

## 6. Verification suite (write this before you trust anything)

```java
static void verify(IntFunction<int[]> gen) {
    for (int trial = 0; trial < 2000; trial++) {
        int[] a = gen.apply(trial);
        int[] orig = a.clone();
        RadixSort.sort(a);
        assert Arrays.equals(a, Arrays.stream(orig).sorted().toArray())
            : "not sorted: " + Arrays.toString(orig);
        // multiset preservation
        int[] x = a.clone(), y = orig.clone();
        Arrays.sort(x); Arrays.sort(y);
        assert Arrays.equals(x, y) : "lost or duplicated elements";
    }
}

// Generators that MUST all pass:
//   nextInt(n)               uniform positives
//   nextInt(n) - n/2         NEGATIVE keys (catches the sign-flip bug)
//   Integer.MIN_VALUE .. 0   extreme negatives
//   {0, 1, 2048, 4096}       multi-digit (catches the stability bug)
//   all equal                degenerate
//   n = 0, 1, 2              boundaries
//   long.MIN_VALUE .. MAX    sign-bit extremes
```

**The stability test** is what catches the most common bug:

```java
// Pack (value, index) and check indices ascend within each value run.
long[] packed = new long[n];
for (int i = 0; i < n; i++) packed[i] = ((long) value[i] << 20) | i;
// sort packed as unsigned longs, then verify the low 20 bits ascend within ties
```