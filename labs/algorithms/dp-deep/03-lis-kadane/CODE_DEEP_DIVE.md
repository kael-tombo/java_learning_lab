# Code Deep Dive — LIS & Kadane

Annotated Java. Java 21.

---

## 1. The `Θ(n²)` LIS DP — the oracle

```java
/** dp[i] = LIS length ENDING AT i. */
public static int lisDp(int[] a) {
    int n = a.length;
    int[] dp = new int[n];
    int best = 0;
    for (int i = 0; i < n; i++) {
        dp[i] = 1;
        for (int j = 0; j < i; j++)
            if (a[j] < a[i]) dp[i] = Math.max(dp[i], dp[j] + 1);   // STRICT <
        best = Math.max(best, dp[i]);
    }
    return best;
}
```

**Why the state is "ending at `i`":** it is what makes the transition a clean inner loop over `j < i`. The alternative state ("LIS within `a[0..i]`") has the same answer but a different (worse) recurrence and **cannot be reconstructed** without extra bookkeeping.

---

## 2. Patience sorting — `Θ(n log n)`

```java
public static int lisLength(int[] a) {
    if (a.length == 0) return 0;
    int[] tails = new int[a.length];      // tails[k] = min tail of a length-(k+1) increasing subseq
    int length = 0;
    for (int x : a) {
        // lowerBound = FIRST index with tails[p] >= x  => STRICTLY increasing.
        // Using upperBound here would compute the longest NON-DECREASING subsequence.
        int lo = 0, hi = length;
        while (lo < hi) {
            int mid = lo + ((hi - lo) >>> 1);
            if (tails[mid] < x) lo = mid + 1; else hi = mid;
        }
        tails[lo] = x;                     // overwrite: a SMALLER tail is strictly better
        if (lo == length) length++;
    }
    return length;
}

/** Non-decreasing variant -- ONE comparison changes. */
public static int lndsLength(int[] a) {
    int[] tails = new int[a.length];
    int length = 0;
    for (int x : a) {
        int lo = 0, hi = length;
        while (lo < hi) {
            int mid = lo + ((hi - lo) >>> 1);
            if (tails[mid] <= x) lo = mid + 1; else hi = mid;      // <= instead of <
        }
        tails[lo] = x;
        if (lo == length) length++;
    }
    return length;
}
```

### Pitfall 1 — `tails` is NOT an LIS

```java
int[] a = {1, 4, 2, 3, 0};
// tails evolves: [1] -> [1,4] -> [1,2] -> [1,2,3] -> [0,2,3]
// length = 3, and [0,2,3] is NOT a subsequence of a (positions 4, 2, 3 are not increasing).
```

**Never return or print `tails`.** If you need the sequence, use the `prev` version below.

### Pitfall 2 — `>=` vs `>` in the binary search

`if (tails[mid] < x) lo = mid + 1; else hi = mid;` finds the first `≥ x` — correct for strict LIS. Changing `<` to `<=` computes the non-decreasing variant **silently**. Your test data must contain duplicates to catch it.

---

## 3. Reconstruction

```java
public record Result(int length, int[] indices, int[] values) {}

public static Result lis(int[] a) {
    int n = a.length;
    if (n == 0) return new Result(0, new int[0], new int[0]);

    int[] tails = new int[n];      // VALUES
    int[] tailsIdx = new int[n];   // the index in a that produced each tails entry
    int[] prev = new int[n];       // PITFALL: -1 means "no predecessor"
    Arrays.fill(prev, -1);

    int length = 0;
    for (int i = 0; i < n; i++) {
        int lo = 0, hi = length;
        while (lo < hi) {
            int mid = lo + ((hi - lo) >>> 1);
            if (tails[mid] < a[i]) lo = mid + 1; else hi = mid;
        }
        // READ tails[lo-1] and tailsIdx[lo-1] BEFORE writing tails[lo].
        // (Here they are different arrays so order does not matter -- but if you
        //  stored both in one record array it WOULD.)
        if (lo > 0) prev[i] = tailsIdx[lo - 1];
        tails[lo] = a[i];
        tailsIdx[lo] = i;
        if (lo == length) length++;
    }

    int[] idx = new int[length];
    int cur = tailsIdx[length - 1];
    for (int k = length - 1; k >= 0; k--) { idx[k] = cur; cur = prev[cur]; }

    int[] vals = new int[length];
    for (int k = 0; k < length; k++) vals[k] = a[idx[k]];
    return new Result(length, idx, vals);
}
```

**Pitfall 3 — `prev` must be initialised to `-1`.** Java zero-initialises `int[]`, so an uninitialised `prev[0]` is `0`, and reconstruction loops forever. Symptom: a hang, or an `ArrayIndexOutOfBoundsException` at index 0.

**Pitfall 4 — `tailsIdx[length-1]` is the *last* slot written**, which is the index of the element that achieved the maximum length. **Not** `a[length-1]`. These differ routinely.

---

## 4. Max-sum increasing subsequence — Fenwick

```java
/** best[i] = maximum SUM of an increasing subsequence ending at i. Theta(n log n). */
public static int maxSumIncreasing(int[] a) {
    int n = a.length;
    if (n == 0) return 0;

    // Coordinate-compress values to 1..sigma so the Fenwick is dense.
    int[] sorted = a.clone(); Arrays.sort(sorted);
    int[] rank = new int[n];
    for (int i = 0; i < n; i++) rank[i] = lowerBound(sorted, a[i]) + 1;

    int sigma = sorted.length;
    int[] bit = new int[sigma + 1];          // Fenwick storing the MAX best[] per rank
    int best = Integer.MIN_VALUE;
    for (int i = 0; i < n; i++) {
        // Query ranks STRICTLY BELOW rank[i] -- so this is a STRICTLY increasing subsequence.
        int q = queryMax(bit, rank[i] - 1);
        int cur = (q == Integer.MIN_VALUE) ? a[i] : q + a[i];
        updateMax(bit, rank[i], cur);
        best = Math.max(best, cur);
    }
    return best == Integer.MIN_VALUE ? 0 : best;
}

private static int queryMax(int[] bit, int i) {
    int r = Integer.MIN_VALUE;
    for (; i > 0; i -= i & -i) r = Math.max(r, bit[i]);
    return r;
}

private static void updateMax(int[] bit, int i, int v) {
    for (; i < bit.length; i += i & -i) bit[i] = Math.max(bit[i], v);
}
```

**Pitfall 5 — `queryMax(bit, rank[i] - 1)` vs `queryMax(bit, rank[i])`.** The `-1` enforces strictness. Using `rank[i]` lets an element extend itself (`a[i] + best[i]` with `j = i`), producing nonsense.

**Pitfall 6 — coordinate compression must handle duplicates.** `lowerBound(sorted, a[i]) + 1` maps all equal values to the *same* rank, which is required for strictness. Using a de-duplicated index or `upperBound` changes the semantics.

**Pitfall 7 — negative `a`.** With all-negative input, `best[i] = a[i] + max(0, ...)` is negative, so `best` initialised to `0` returns `0`. Use `Integer.MIN_VALUE` and the sentinel check above.

---

## 5. Kadane — the three-state version

```java
/** Non-empty maximum contiguous subarray. O(1) space. */
public static long maxSubarray(int[] a) {
    if (a.length == 0) throw new IllegalArgumentException("empty");
    long total = 0;
    long best  = Long.MIN_VALUE;    // PITFALL: NOT 0 -- that breaks all-negative input
    long cur   = 0;
    for (int x : a) {
        total += x;
        cur = Math.max(x, cur + x); // extend the running subarray, or restart at x
        best = Math.max(best, cur);
    }
    return best;
}

/** Relaxed version: allows the empty subarray, so all-negative input returns 0. */
public static long maxSubarrayRelaxed(int[] a) {
    long best = 0, cur = 0;
    for (int x : a) { cur = Math.max(0, cur + x); best = Math.max(best, cur); }
    return best;
}

/** Prefix-sum cross-check -- must equal maxSubarray(). */
public static long maxSubarrayPrefixSweep(int[] a) {
    long p = 0, minP = 0, best = Long.MIN_VALUE;
    for (int x : a) { p += x; best = Math.max(best, p - minP); minP = Math.min(minP, p); }
    return best;
}
```

### Pitfalls

1. **`best = 0`** → returns `0` for `[-3, -1, -2]` instead of `-1`. **This is the single most common Kadane bug.**
2. **`cur` initialised to `0` with `cur = Math.max(x, cur + x)`** is fine (first iteration gives `max(x, x) = x`). But `cur = Math.max(0, cur + x)` is the *relaxed* variant and will give `0` for all-negative.
3. **Returning `best` vs `cur`** — `best` is the answer, `cur` is the best subarray *ending here*. Printing `cur` is wrong.
4. **Integer overflow** with `int[]` of size `10⁶` and values `10⁹`: sum can reach `10¹⁵`. Use `long`.

---

## 6. Circular maximum subarray

```java
public static long maxCircularSubarray(int[] a) {
    if (a.length == 0) throw new IllegalArgumentException("empty");

    long total = 0, maxSum = Long.MIN_VALUE, minSum = Long.MAX_VALUE;
    long curMax = 0, curMin = 0, bestMax = Long.MIN_VALUE, bestMin = Long.MAX_VALUE;

    for (int x : a) {
        total += x;
        curMax = Math.max(x, curMax + x); bestMax = Math.max(bestMax, curMax);
        curMin = Math.min(x, curMin + x); bestMin = Math.min(bestMin, curMin);
    }
    // PITFALL: if bestMax < 0 then ALL elements are negative. The wrapping candidate
    // (total - bestMin) equals 0, which is invalid for the non-empty convention.
    if (bestMax < 0) return bestMax;
    return Math.max(bestMax, total - bestMin);
}
```

**Test:** `[-1, -2, -3]` → `bestMax = -1 < 0` ⇒ return `-1`. Without the guard: `total = -6`, `bestMin = -6`, `total - bestMin = 0`, `max(-1, 0) = 0`. **Wrong.**

`[1, -2, 3, -2]` → `bestMax = 3`, `bestMin = -2`, `total = 0` ⇒ `max(3, 0-(-2)) = 3`. ✓

---

## 7. Constrained subarray — monotonic deque

```java
/** Maximum sum of a subarray with AT MOST k elements. Theta(n) with a monotonic deque. */
public static long maxSubarrayAtMostK(int[] a, int k) {
    if (k <= 0) throw new IllegalArgumentException("k must be >= 1");
    int n = a.length;

    long[] P = new long[n + 1];
    for (int i = 0; i < n; i++) P[i + 1] = P[i] + a[i];

    // dq holds INDICES into P, with strictly increasing P[dq[0]] < P[dq[1]] < ...
    int[] dq = new int[n + 1];
    int head = 0, tail = 0;
    long best = Long.MIN_VALUE;

    for (int i = 1; i <= n; i++) {
        // Window for a subarray ENDING at i-1 with length <= k is j in [max(0,i-k), i-1].
        // PITFALL: insert i-1 BEFORE querying, and expire j < i-k AFTER.
        while (head < tail && P[dq[tail - 1]] >= P[i - 1]) tail--;   // dominated: later AND <= value
        dq[tail++] = i - 1;

        while (head < tail && dq[head] < i - k) head++;              // outside the window

        // best subarray ending at i-1 = P[i] - min P over the window
        if (head < tail) best = Math.max(best, P[i] - P[dq[head]]);
    }
    return best;
}

/** EXACTLY k elements: Theta(n), no data structure at all. */
public static long maxSubarrayExactlyK(int[] a, int k) {
    if (k <= 0 || k > a.length) throw new IllegalArgumentException("k");
    long sum = 0;
    for (int i = 0; i < k; i++) sum += a[i];
    long best = sum;
    for (int i = k; i < a.length; i++) {
        sum += a[i] - a[i - k];
        best = Math.max(best, sum);
    }
    return best;
}
```

### Pitfalls in the deque version

1. **Insert/query order.** You must push the new index before querying (so the window is `[i-k, i-1]` inclusive of `i-1`) and expire after. Swapping the two lines shifts the window by one and gives wrong answers exactly at length `k`.
2. **`>=` vs `>` in the dominance pop.** Using `>` instead of `>=` keeps equal values in the deque. That is still *correct* (just uses more memory), but with `>=` the deque is strictly increasing, which is the tighter invariant.
3. **Window is `[i-k, i-1]`, not `[i-k+1, i]`** — because `P[i] - P[j]` is the sum of `a[j..i-1]`, whose length is `i - j`. So `length ≤ k ⟺ j ≥ i - k`. **Getting this off by one changes "at most k" into "at most k-1"**, which is invisible unless your test data has all-negative values.
4. **All-negative input:** `best = Long.MIN_VALUE` and the deque holds the maximum `P` (not minimum) because we subtract it. Correct: for `[-5,-5]`, `k=2`, exactly-`k` gives `-10`, at-most-`k` gives `-5`.

---

## 8. Grid LIS — longest increasing path

```java
/** Moves right or down only (and/or diagonally). Theta(mn log n). */
public static int longestIncreasingPath(int[][] g) {
    if (g.length == 0) return 0;
    int n = g.length, m = g[0].length;
    int[] tails = new int[Math.max(n, m) + 1];
    int length = 0;
    for (int r = 0; r < n; r++) {
        for (int c = 0; c < m; c++) {
            int v = g[r][c];
            int lo = 0, hi = length;
            while (lo < hi) { int mid = lo + ((hi - lo) >>> 1); if (tails[mid] < v) lo = mid + 1; else hi = mid; }
            tails[lo] = v;
            if (lo == length) length++;
        }
    }
    return length;
}
```

**This works only for right/down moves** (values along a path are strictly increasing and the path is monotone in the row-major order). If moves include up/left, the same `tails` array is reused with stale entries from different rows and you get wrong answers — use a proper DP over cells instead.

**The common trap:** a *full* 2-D grid LIS problem (moves in all four directions) is **not** solvable with patience sorting. It is `Θ(mn log(mn))` by reducing to a 1-D LIS over the sorted (value, r+c) ordering, or `Θ(mn)` by the layer-DP for right/down.

---

## 9. Count of LIS

```java
/** Number of distinct longest strictly increasing subsequences. Theta(n log n). */
public static long countLIS(int[] a) {
    int n = a.length;
    if (n == 0) return 0;

    int[] sorted = a.clone(); Arrays.sort(sorted);
    int[] rank = new int[n];
    for (int i = 0; i < n; i++) rank[i] = lowerBound(sorted, a[i]) + 1;

    int sigma = sorted.length;
    int[] len  = new int[sigma + 1];
    long[] cnt = new long[sigma + 1];        // Fenwick storing (maxLen, countAtMaxLen)
    long[] ways = new long[n];

    int L = 0;
    for (int i = 0; i < n; i++) {
        // Query the best (len, count) over ranks STRICTLY BELOW rank[i].
        int qLen = 0; long qCnt = 0;
        for (int j = rank[i] - 1; j > 0; j -= j & -j) {
            if (len[j] > qLen) { qLen = len[j]; qCnt = cnt[j]; }
            else if (len[j] == qLen && len[j] > 0) qCnt += cnt[j];
        }
        ways[i] = (qLen == 0) ? 1 : qCnt;
        int newLen = qLen + 1;

        // Insert (newLen, ways[i]) at rank[i].
        for (int j = rank[i]; j <= sigma; j += j & -j) {
            if (newLen > len[j]) { len[j] = newLen; cnt[j] = ways[i]; }
            else if (newLen == len[j]) cnt[j] += ways[i];
        }
        L = Math.max(L, newLen);
    }

    long total = 0;
    for (int j = 0; j <= sigma; j++) if (len[j] == L) total += cnt[j];
    return total;
}
```

**Pitfall 8 — the Fenwick must store a `(maxLen, count)` pair**, not just a max. Counting LIS requires knowing how many predecessors achieve each length.

**Pitfall 9 — overflow.** The number of LIS can be `C(n, n/2) ≈ 2ⁿ/√n`. For `n = 40` that exceeds `long`. Use `BigInteger` or cap the test size at ~30.

**Pitfall 10 — the `else if (len[j] == qLen && len[j] > 0)` clause.** If `len[j] == 0` (nothing inserted), you must **not** add its count, because the count at length 0 is 0 and adding 0 is fine, but if you initialise `cnt[0]` wrongly you double-count.

---

## 10. Cross-validation harness

```java
static void fuzz() {
    Random rnd = new Random(31337);
    for (int trial = 0; trial < 100_000; trial++) {
        int n = rnd.nextInt(14);
        int[] a = new int[n];
        int alpha = 1 + rnd.nextInt(5);              // 1..5 values => LOTS of duplicates
        for (int i = 0; i < n; i++) a[i] = rnd.nextInt(alpha);

        // --- LIS ---
        int oracle = lisDp(a.clone());
        assert lisLength(a.clone()) == oracle : "LIS";
        assert lndsLength(a.clone()) == lndsDp(a.clone()) : "LNDS";
        Result r = lis(a.clone());
        assert r.length() == oracle : "LIS recon length";
        assert isStrictlyIncreasing(r.values()) : "LIS recon is increasing";
        assert isSubsequence(a, r.indices()) : "LIS recon indices valid";
        assert countLIS(a.clone()) <= bruteForceCountLIS(a) : "countLIS";

        // --- Kadane ---
        long k = maxSubarray(a.clone());
        assert k == bruteForceMaxSubarray(a) : "kadane";
        assert k == maxSubarrayPrefixSweep(a.clone()) : "prefix sweep";
        assert maxSubarrayRelaxed(a.clone()) == Math.max(0, k) : "relaxed";

        // --- Circular ---
        long circ = maxCircularSubarray(a.clone());
        assert circ >= k : "circular >= normal";
        assert circ == bruteForceCircular(a) : "circular";

        // --- Constraints ---
        for (int kk = 1; kk <= Math.max(1, n); kk++) {
            assert maxSubarrayAtMostK(a.clone(), kk) == bruteAtMostK(a, kk) : "atMostK";
            if (kk <= n) assert maxSubarrayExactlyK(a.clone(), kk) == bruteExactlyK(a, kk) : "exactlyK";
        }
    }
}
```

**Use a small alphabet (1–5 values).** With 14 elements drawn from 5 values you get enormous numbers of ties, which is exactly where `lowerBound` vs `upperBound`, the Fenwick's `rank-1`, and the dominance pops in the deque all break.

**The `isSubsequence` check is the one that catches the "tails is not an LIS" bug** — checking that the returned *values* increase is not enough, because a non-subsequence can still be increasing.