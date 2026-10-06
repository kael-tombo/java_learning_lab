# Code Deep Dive — Binary Search Variants

The four forms you should be able to write from memory, plus predicate search, galloping, and rotated search. Java 21.

---

## 1. The two-loop form — memorise this

```java
/** Smallest index i with a[i] >= key, or a.length if none. */
public static int lowerBound(int[] a, int key) {
    int lo = 0, hi = a.length;              // half-open [lo, hi)
    while (lo < hi) {                        // <, not <= : [lo,hi) may become empty
        int mid = lo + ((hi - lo) >>> 1);    // overflow-safe; mid is ALWAYS in [lo, hi-1]
        if (a[mid] < key) lo = mid + 1;      // a[mid] and everything left of it is too small
        else hi = mid;                       // a[mid] could BE the answer -> keep it
    }
    return lo;
}

/** Smallest index i with a[i] > key, or a.length if none. */
public static int upperBound(int[] a, int key) {
    int lo = 0, hi = a.length;
    while (lo < hi) {
        int mid = lo + ((hi - lo) >>> 1);
        if (a[mid] <= key) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

/** Exact index or -1. Built from lowerBound so there is only ONE search routine to get right. */
public static int indexOf(int[] a, int key) {
    int i = lowerBound(a, key);
    return (i < a.length && a[i] == key) ? i : -1;
}

/** ALL occurrences of key — impossible to express with a single exact-match search. */
public static int[] allIndicesOf(int[] a, int key) {
    int from = lowerBound(a, key);
    int to   = upperBound(a, key);
    if (from == to) return new int[0];        // empty: note from == to, not from > to
    int[] out = new int[to - from];
    for (int k = 0; k < out.length; k++) out[k] = from + k;
    return out;
}

/** Count occurrences of key. */
public static int countOf(int[] a, int key) { return upperBound(a, key) - lowerBound(a, key); }

/** Insert at the sorted position (overwrites whatever was there). */
public static void insertSorted(int[] a, int key) {
    int i = lowerBound(a, key);
    System.arraycopy(a, i, a, i + 1, a.length - i - 1);
    a[i] = key;
}
```

**Why `>>>` rather than `/ 2`:** for a non-negative `hi - lo` they are identical. `>>>` guards against the pathological case where the subtraction goes negative, producing a huge unsigned value — which fails loudly rather than silently. Consistency matters more than the difference.

**Why `hi = a.length`:** it eliminates the sentinel. Under `lo < hi` we have `mid ≤ hi - 1 ≤ n - 1`, so `a[mid]` is *always* valid. There is no `mid >= a.length` branch to get wrong.

---

## 2. Generic version — write it once

```java
public static <T> int lowerBound(T[] a, T key, Comparator<? super T> cmp) {
    int lo = 0, hi = a.length;
    while (lo < hi) {
        int mid = lo + ((hi - lo) >>> 1);
        if (cmp.compare(a[mid], key) < 0) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

public static <T> int lowerBound(List<T> list, T key, Comparator<? super T> cmp) {
    // PITFALL GUARD: on a LinkedList this is Theta(n) per get(i), so the whole
    // search is Theta(n log n). Require RandomAccess, or refuse.
    if (list instanceof RandomAccess) {
        int lo = 0, hi = list.size();
        while (lo < hi) {
            int mid = lo + ((hi - lo) >>> 1);
            if (cmp.compare(list.get(mid), key) < 0) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }
    throw new UnsupportedOperationException("binary search needs O(1) random access");
}
```

**The `instanceof RandomAccess` check is not paranoia.** `LinkedList.get(i)` is `Θ(i)`, so the search is `Θ(n log n)` — *worse* than `Collections.binarySearch` on a sorted `TreeSet` and much worse than a linear scan for small `n`.

---

## 3. Binary search on the answer

```java
/**
 * Smallest x in [lo, hi] for which f(x) is true, or hi+1 if f is never true.
 * Requires: f monotone non-decreasing (false...false,true...true).
 */
public static int firstTrue(int lo, int hi, IntPredicate f) {
    int result = hi + 1;                       // sentinel: "no true exists"
    while (lo <= hi) {
        int mid = lo + ((hi - lo) >>> 1);
        if (f(mid)) { result = mid; hi = mid - 1; }   // remember it, look for a smaller one
        else lo = mid + 1;
    }
    return result;
}

/**
 * Smallest x in [0, hi] for which f(x) is true, assuming f(hi) IS true.
 * No sentinel needed. Note the UPWARD-biased midpoint.
 */
public static int minFeasible(int hi, IntPredicate f) {
    int lo = 0;
    while (lo < hi) {
        int mid = lo + ((hi - lo + 1) >>> 1);   // the +1 biases UP: guarantees progress
        if (f(mid)) lo = mid;
        else hi = mid - 1;
    }
    return lo;
}

/** Largest x in [lo, hi] with f(x) true, assuming f(lo) IS true. */
public static int maxFeasible(int lo, int hi, IntPredicate f) {
    while (lo < hi) {
        int mid = lo + ((hi - lo) >>> 1);      // downward bias
        if (f(mid)) lo = mid + 1;              // hmm: see note
        else hi = mid;
    }
    return lo - 1;
}
```

**Pitfall in `maxFeasible`:** the correct body is

```java
public static int maxFeasible(int lo, int hi, IntPredicate f) {
    while (lo < hi) {
        int mid = lo + ((hi - lo + 1) >>> 1);   // UPWARD bias, matching minFeasible
        if (f(mid)) lo = mid; else hi = mid - 1;
    }
    return lo;
}
```

Both `minFeasible` and `maxFeasible` are the *same* loop; only the interpretation of `[lo, hi]` differs (both answer the "first true" question). Write one and call it twice.

**The infinite loop to know about:**

```java
// BROKEN: with hi == lo + 1, mid == lo, and if f(lo) is true, lo never changes.
int mid = lo + ((hi - lo) >>> 1);   // no +1
if (f(mid)) lo = mid; else hi = mid - 1;
```

Symptom: hangs on small ranges. Fix: `((hi - lo + 1) >>> 1)`.

### A worked example — minimum speed

```java
static double minSpeed(double[] times) {   // times[i] = your finish time at speed times[i]
    return minFeasible(times.length - 1, i -> times[i] <= 0.0);
}
```
Predicate `f(i) = times[i] ≤ T` is monotone **decreasing** in `i` here, so the first-true form needs the boolean inverted: `f(i) = times[i] > T`. Write the predicate so it is non-decreasing; the search itself is convention-blind.

---

## 4. Galloping / exponential search

```java
/**
 * Index of key in a sorted array, or -(insertionPoint) - 1 (Arrays contract).
 * Theta(log k) where k is the distance from a[0] to the answer.
 */
public static int gallopSearch(int[] a, int key) {
    int n = a.length;
    if (n == 0) return -1;

    int lo = 0;
    if (a[0] >= key) return a[0] == key ? 0 : -1;   // handle the head first

    // Phase 1: exponential probe. Bound the answer from above.
    int bound = 1;
    while (bound < n && a[bound] < key) bound <<= 1;    // 1, 2, 4, 8, ... PITFALL: bound <<= 1
    // PITFALL: `bound <<= 1` overflows to a negative number for bound > 2^30.
    //           Guard with `bound < n` FIRST (as written) or use `bound *= 2` with the
    //           same guard. `bound = n - bound` style clamping is the other fix.

    lo = bound >>> 1;                               // answer is in [lo, min(bound, n))
    int hi = Math.min(bound, n) - 1;

    // Phase 2: ordinary binary search inside the window.
    while (lo <= hi) {
        int mid = lo + ((hi - lo) >>> 1);
        if (a[mid] < key) lo = mid + 1;
        else if (a[mid] > key) hi = mid - 1;
        else return mid;
    }
    return -1;
}
```

**Overflow-safe version of the probe:**

```java
int bound = 1;
while (bound < n && a[bound] < key) bound = bound > (n >> 1) ? n : bound << 1;
```

**`Arrays.binarySearch` on a chunked index:**

```java
// Chunk index: each chunk holds 1024 sorted ints.
int chunk = gallopSearch(chunkOffsets, target);          // O(log chunks)
int within = Arrays.binarySearch(chunks.get(chunk), target, 0, 1024);   // O(log 1024)
```

This is the actual pattern used in columnar scan engines (ClickHouse, Velox, Arrow): one gallop over chunk metadata, then one binary search inside the selected chunk. It is `Θ(log chunks + log chunkSize)`, and each term is small.

---

## 5. Rotated sorted array

```java
/** Sorted ascending, rotated by an unknown amount. Returns index or -1. */
public static int searchRotated(int[] a, int key) {
    int lo = 0, hi = a.length - 1;                // inclusive: we return a real index
    while (lo <= hi) {
        int mid = lo + ((hi - lo) >>> 1);
        if (a[mid] == key) return mid;

        if (a[lo] <= a[mid]) {                    // [lo, mid] is sorted
            if (a[lo] <= key && key < a[mid]) hi = mid - 1;
            else lo = mid + 1;
        } else {                                  // [mid, hi] is sorted
            if (a[mid] < key && key <= a[hi]) lo = mid + 1;
            else hi = mid - 1;
        }
    }
    return -1;
}

/** Index of the rotation point (the minimum). Requires STRICTLY increasing input. */
public static int findRotationPoint(int[] a) {
    int lo = 0, hi = a.length - 1;
    while (lo < hi) {
        int mid = lo + ((hi - lo) >>> 1);
        if (a[mid] > a[hi]) lo = mid + 1;         // rotation is strictly inside (mid, hi]
        else hi = mid;                            // rotation is at or before mid
    }
    return lo;
}

/** WITH duplicates: O(n) worst case is unavoidable, so shrink both ends on ties. */
public static int searchRotatedWithDups(int[] a, int key) {
    int lo = 0, hi = a.length - 1;
    while (lo <= hi) {
        int mid = lo + ((hi - lo) >>> 1);
        if (a[mid] == key) return mid;
        if (a[lo] == a[mid] && a[mid] == a[hi]) { lo++; hi--; continue; }  // THE DUP HANDLER
        if (a[lo] <= a[mid]) {
            if (a[lo] <= key && key < a[mid]) hi = mid - 1; else lo = mid + 1;
        } else {
            if (a[mid] < key && key <= a[hi]) lo = mid + 1; else hi = mid - 1;
        }
    }
    return -1;
}
```

**The duplicate handler is mandatory.** Without it, `[1,1,1,1,2,1]` searching for `2` sends `hi = mid - 1` repeatedly and returns `-1` — a wrong answer that a sortedness test cannot catch.

**Information-theoretic note:** on all-equal input, no algorithm can do better than `Θ(n)` — the answer's position carries `log n` bits and each comparison yields at most 1 bit about it while all values are equal. So `Θ(n)` is *correct*, not a failure.

---

## 6. Binary search on a sorted matrix / k-th smallest

```java
/** K-th smallest in a sorted ROW of a matrix sorted by: rows asc, cols asc. */
public static int kthSmallestMatrix(int[][] m, int k) {
    int lo = 0, hi = m.length - 1;
    while (lo < hi) {                                // predicate search over ROWS
        int mid = lo + ((hi - lo) >>> 1);
        if (rowMax(m, mid) < k) lo = mid + 1;         // fewer than k elements in rows <= mid
        else hi = mid;
    }
    return kthInRow(m[lo], k);
}

private static int rowMax(int[][] m, int r) {
    int c = m[r].length - 1;
    while (c > 0 && m[r][c - 1] > m[r][c]) c--;       // find the end of the row's run
    return c + 1;
}
```

**Cost:** `Θ(log(rows) · log(cols))`. This is the correct shape — `log R` outer steps × `log n` inner cost — and it is why "binary search on the answer" is often described as `Θ(log² n)` for two-dimensional problems.

**The general form of this technique**, worth internalising:

```java
/** K-th smallest of a stream that cannot be re-read. */
static int kthSmallestStream(int[] a, int k) {
    int lo = Integer.MIN_VALUE, hi = Integer.MAX_VALUE;
    while (lo < hi) {
        int mid = lo + ((hi - lo) >>> 1);               // careful: hi-lo overflows int!
        if (countLessOrEqual(a, mid) < k) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}
```

**Overflow bug right there:** `hi - lo` overflows for the full `int` range. Use `long`:

```java
long lo = Integer.MIN_VALUE, hi = Integer.MAX_VALUE;
while (lo < hi) {
    long mid = lo + ((hi - lo) >>> 1);
    if (countLessOrEqual(a, (int) mid) < k) lo = mid + 1;
    else hi = mid;
}
return (int) lo;
```

Or — much better — search the **index** space instead of the value space, which avoids the overflow entirely:

```java
static int countLessOrEqual(int[] a, int v) {
    return upperBound(a, v);            // our own utility! O(log n), not O(n)
}
static int kthSmallestViaIndex(int[] a, int k) { return a[lowerBound(a, ...)]; }
```

---

## 7. `Arrays.binarySearch` — the contract

```java
int i = Arrays.binarySearch(a, key);
if (i < 0) {
    i = -i - 1;          // insertion point  (NOT -i + 1, NOT -i - 2)
    // i is in [0, a.length]
}
```

| Fact | Guaranteed? |
|------|-------------|
| `Θ(log n)` on a sorted array | **Yes** |
| `-i - 1` gives the insertion point | **Yes** |
| Which index you get when duplicates exist | **No** — unspecified |
| Works on an unsorted array | **No** — silently returns garbage |
| `int[]` keys can be `long` | **No** — no such overload |
| Search ordering matches sort ordering | **Your** responsibility |

**Trap:** sorting by `id` then `Arrays.binarySearch(a, name, byName)`. No exception, no warning, wrong answer. Extract the comparator to a constant used by both.

**Trap:** `Arrays.binarySearch(long[] a, int key)` does not exist; you must either use `int[]` or `Arrays.binarySearch(a, 0, n, (long) key)`. Passing a `long` that does not fit an `int` is a silent truncation if you cast.

---

## 8. Pitfall: signed/unsigned digit search

When searching inside a `long` packed with `(value << 32) | index`, comparing `a[mid] < key` compares the **whole** packed `long`, which is correct for ordering *and* gives you stability for free — provided the value is shifted left enough that the index cannot overflow into the value's bits:

```java
// Requires value < 2^(64 - 32) = 2^32. Use << 20 if you need 20-bit indices (n < 10^6).
long packed = ((long) value << 20) | index;
int i = Arrays.binarySearch(packed, ((long) target << 20));   // any index < 2^20 works
```

**Trap:** `<< 32 | index` puts the index in the *sign* half for negative values, breaking the ordering. Verify your shift width against `log₂(maxN) + 1`.

---

## 9. Test harness (write this first — it finds all of the above)

```java
static void fuzz() {
    Random rnd = new Random(42);
    for (int trial = 0; trial < 200_000; trial++) {
        int n = rnd.nextInt(40);
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = rnd.nextInt(8);      // many duplicates
        int[] sorted = a.clone(); Arrays.sort(sorted);

        for (int key = -1; key <= 8; key++) {
            int lb = lowerBound(a.clone() , key);
            int ub = upperBound(a.clone(), key);

            // 1. lb is the first index >= key
            assert (lb == n || sorted[lb] >= key) : "lowerBound too big";
            // 2. everything before lb is < key
            for (int i = 0; i < lb; i++) assert sorted[i] < key : "lb too small";
            // 3. ub is the first index > key
            assert (ub == n || sorted[ub] > key) : "upperBound too big";
            // 4. count matches a linear count
            assert ub - lb == (int) Arrays.stream(a).filter(v -> v == key).count();
            // 5. indexOf agrees with Arrays.binarySearch on PRESENCE
            assert (indexOf(a.clone(), key) >= 0)
                == Arrays.binarySearch(sorted, key) >= 0;
        }
    }
}
```

**Why clone the array:** `lowerBound` does not modify it, so you don't strictly need to — but if you are also testing `insertSorted` you do. Being explicit catches accidental mutation, which is a real bug source in generic binary search helpers.