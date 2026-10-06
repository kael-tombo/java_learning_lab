# CODE_DEEP_DIVE — DP Optimizations

## 1. Monotone deque — sliding-window minimum

```java
package com.alglab.dpop;

public final class WindowMin {
    private final int[] a;
    private final int w;
    private WindowMin(int[] a, int w) { this.a = a; this.w = w; }

    /** min of a[i-w+1..i] for every i, Θ(n) amortised. w >= 1. */
    public int[] min(int w) {
        int n = a.length;
        int[] out = new int[n];
        int[] dq = new int[n];          // ring-free: indices 0..n-1, head/tail ints
        int head = 0, tail = 0;         // deque holds dq[head..tail)
        for (int i = 0; i < n; i++) {
            // 1) evict indices outside the window  (front)
            while (head < tail && dq[head] <= i - w) head++;
            // 2) insert i, popping dominated entries from the back
            while (head < tail && a[dq[tail - 1]] >= a[i]) tail--;
            dq[tail++] = i;
            // 3) the front is the window minimum
            out[i] = a[dq[head]];
        }
        return out;
    }
}
```

**Line-by-line costs:** step 1 pops each index at most once over the run (amortised `O(1)`),
step 2 likewise, step 3 is `O(1)`. Total `Θ(n)` — but note the `while` loops, so a *single*
iteration can pop many entries. That is exactly what makes the bound amortised.

**The `>=` in step 2 is load-bearing.** Using `>` keeps the *oldest* of equal values, which is
also correct for the min but wastes deque space; `>=` keeps the newest, which expires later and
is strictly better for future windows.

## 2. Rolling-row DP with a windowed transition

```java
/** min cost to make s a subsequence-free windowed edit distance. Θ(nm), was Θ(nmW). */
public static int windowedEdit(String a, String b, int w) {
    int n = a.length(), m = b.length();
    int[] prev = new int[m + 1], cur = new int[m + 1];
    int[] dq  = new int[m + 1];                  // deque of column indices, by value
    int[] val = new int[m + 1];                  // parallel value array (avoid re-reading prev[])
    for (int j = 0; j <= m; j++) prev[j] = j;

    for (int i = 1; i <= n; i++) {
        int head = 0, tail = 0;
        cur[0] = i;
        // seed the deque with column 0 so the first window is non-empty
        dq[tail] = 0; val[tail] = prev[0]; tail++;
        for (int j = 1; j <= m; j++) {
            // window is [max(0, j-w), j-1] over PREV row
            while (head < tail && dq[head] < j - w) head++;
            int insert = j - 1;
            while (head < tail && val[tail - 1] >= prev[insert]) tail--;
            dq[tail] = insert; val[tail] = prev[insert]; tail++;
            int skip = val[head];                // O(1) windowed term
            int sub  = prev[j - 1] + (a.charAt(i-1) == b.charAt(j-1) ? 0 : 1);
            int del  = cur[j - 1] + 1;
            cur[j] = Math.min(sub, Math.min(del, skip));
        }
        int[] t = prev; prev = cur; cur = t;     // swap, do not copy — Θ(1)
    }
    return prev[m];
}
```

**Two micro-optimisations worth naming:** the parallel `val[]` array avoids an indirection into
`prev[]` inside the pop loop (better cache locality, and it keeps the loop branch-free of array
bounds checks after JIT warm-up); the row swap avoids an `O(m)` copy.

## 3. Knuth optimisation — interval DP

```java
/** min cost to merge stones i..j where a merge of size s costs s*s. Θ(n²) via Knuth. */
public static long[][] knuthMerge(long[] prefix) {
    int n = prefix.length - 1;                  // prefix[k] = sum of first k
    long[][] D  = new long[n + 2][n + 2];
    int[][]  opt = new int[n + 2][n + 2];
    for (int i = 1; i <= n; i++) { D[i][i] = 0; opt[i][i] = i; }   // base: opt defined

    for (int L = 2; L <= n; L++) {              // increasing interval length
        for (int i = 1; i + L - 1 <= n; i++) {
            int j = i + L - 1;
            long best = Long.MAX_VALUE; int bestK = -1;
            // THE KNUTH RANGE — replace [i, j-1] with [opt[i][j-1], opt[i+1][j]]
            int lo = Math.max(i, opt[i][j - 1]);
            int hi = Math.min(j - 1, opt[i + 1][j]);
            for (int k = lo; k <= hi; k++) {
                long c = D[i][k] + D[k + 1][j] + w(i, j, prefix);
                if (c < best) { best = c; bestK = k; }
            }
            D[i][j] = best; opt[i][j] = bestK;
        }
    }
    return D;
}

private static long w(int i, int j, long[] S) {
    long len = S[j] - S[i - 1];
    return len * len;                            // (j-i+1)^2 — convex in length ⇒ Knuth holds
}
```

**The one line that makes it fast:** `int lo = opt[i][j-1]; int hi = opt[i+1][j];`. Everything
else is identical to the naive version. If you ever find yourself writing `for (int k = i; k < j; k++)`
inside a Knuth-optimised loop, the optimisation has been defeated.

**Off-by-one discipline:** `opt[i][i] = i` even though the split range for `[i,i]` is empty —
you never use it, but you must initialise it so `opt[i+1][j]` is not `0` (which would give
`hi = 0` and an empty search range, silently returning `MAX_VALUE`).

## 4. Divide & conquer optimisation

```java
/** D[j] = min_{i<j} (D[i] + C(j) - C(i)), assuming C convex. Θ(n log n). */
public static long[] dncOptimised(long[] C) {
    int n = C.length - 1;
    long[] D = new long[n + 1];
    int[] opt = new int[n + 1];
    for (int j = 1; j <= n; j++) D[j] = Long.MAX_VALUE;
    D[0] = 0;
    // fill one row (here: a single 1-D "row") by divide & conquer
    compute(n, 0, 0, n - 1, D, opt, C);
    return D;
}

private static void compute(int n, int i, int L, int R, long[] D, int[] opt, long[] C) {
    if (L > R) return;
    int mid = (L + R) >>> 1;
    int lo = (mid == 0) ? 0 : opt[L - 1];
    int hi = Math.min(mid - 1, (R == n - 1) ? n - 1 : opt[R + 1]);
    long best = Long.MAX_VALUE; int bestK = lo;
    for (int k = lo; k <= hi; k++) {
        long c = D[k] + C[mid] - C[k];
        if (c < best) { best = c; bestK = k; }
    }
    D[mid] = best; opt[mid] = bestK;
    compute(n, i, L, mid - 1, D, opt, C);        // left: hi bounded by opt[mid]
    compute(n, i, mid + 1, R, D, opt, C);        // right: lo bounded by opt[mid]
}
```

**Why `compute` recurses *after* setting `opt[mid]`:** both children read `opt[mid]` as a search
bound, so `mid` must be finalised first. Recursing before is a stale-read bug.

## 5. SMAWK — row minima of a totally monotone implicit matrix

```java
public interface Matrix { int get(int row, int col); }

/** Row-minimum column indices of a totally monotone matrix, Θ(n) evaluations. */
public static int[] smawk(Matrix m, int rows, int cols) {
    int[] ans = new int[rows];
    int[] reduced = reduce(m, rows, cols);
    interpolate(m, ans, 0, rows - 1, reduced, 0, reduced.length - 1);
    return ans;
}

/** Column reduction: discard columns that cannot be a row minimum. Halves the columns. */
private static int[] reduce(Matrix m, int rows, int[] cols) {
    // Build a stack of surviving columns (Monge/total-monotonicity dependent).
    int[] stack = new int[cols.length];
    int size = 0;
    for (int c : cols) {
        if (size == 0) { stack[size++] = c; continue; }
        int last = stack[size - 1];
        int better = totalMonotoneMin(m, last, c, rows) ? c : last;   // see note
        if (better == c && size > 0) {
            // c dominates `last` on some row ⇒ `last` is safe to discard
            if (!strictlyWorseEverywhere(m, last, c, rows)) size--;
            stack[size++] = c;
        }
    }
    int[] out = new int[size];
    System.arraycopy(stack, 0, out, 0, size);
    return out;
}
```

**Honest caveat (and this matters).** SMAWK's `reduce` step is subtle: it maintains a stack of
columns and pops while the new column is "better" for the relevant row range. A correct
implementation needs the row-range bookkeeping that is easy to get wrong. **Prefer the monotone
optima version below unless profiling demands SMAWK.**

## 6. Monotone-opt pointer walk (the practical alternative)

```java
/** opt[j] is non-decreasing ⇒ a single forward pointer suffices. Θ(n) total. */
public static long[] monotoneOpt(long[] A, long[] B) {
    int n = A.length;
    long[] D = new long[n];
    int[] opt = new int[n];
    int k = 0;
    for (int j = 1; j < n; j++) {
        // advance while the NEXT split beats the current one
        while (k + 1 < j && A[k + 1] + B[j] <= A[k] + B[j]) k++;
        D[j] = A[k] + B[j];
        opt[j] = k;
    }
    return D;
}
```

`k` increases monotonically from `0` to at most `n`, so the inner `while` executes `≤ n` times
in total across the whole loop. This is the same amortisation shape as the deque, and in
practice it captures most of SMAWK's benefit for a fraction of the bug surface.

## 7. In-place DP: choosing the sweep direction

```java
/** FORWARD sweep is safe: min(D[i][j-1], D[i-1][j] + c) */
public static int inPlaceForward(int[] a, int c) {
    int n = a.length;
    int[] D = new int[n];
    for (int j = 1; j < n; j++) D[j] = D[j - 1];
    for (int i = 1; i < n; i++) {
        for (int j = 1; j < n; j++)
            D[j] = Math.min(D[j - 1], D[j] + c);   // D[j-1] is now row i; D[j] is still row i-1
    }
    return D;
}

/** BACKWARD sweep is required: max(D[i][j-1], D[i-1][j-1]) — a forward sweep is WRONG. */
public static int inPlaceBackward(int[] a, int c) {
    int n = a.length;
    int[] D = new int[n];
    for (int j = 1; j < n; j++) D[j] = D[j - 1];
    for (int i = 1; i < n; i++)
        for (int j = n - 1; j >= 1; j--)
            D[j] = Math.max(D[j - 1], D[j - 1] + c);
    return D;
}
```

The second example is the trap: `D[j−1]` on the right-hand side *must* be row `i−1`, but in a
forward sweep it has already been overwritten with row `i`. No exception is thrown — the array
indices are all valid. **This is the single most common silent-wrong-answer bug in DP
optimisation.** Always verify an in-place version against a two-row reference.

## 8. Bitset subset sum

```java
/** reachable[s] for s in 0..S. Θ(n·S/64) word-ops. */
public static long[] subsetSum(long[] items, int S) {
    int words = (S >>> 6) + 1;
    long[] bits = new long[words];
    bits[0] = 1L;                                          // sum 0 reachable
    for (long v : items) {
        if (v > S) continue;
        int wShift = (int) (v >>> 6), bShift = (int) (v & 63);
        // in-place: walk words DOWN so each item is used at most once (0/1 knapsack)
        for (int i = words - 1; i >= wShift; i--) {
            long shifted = bits[i - wShift] << bShift;
            if (bShift != 0 && i - wShift - 1 >= 0)
                shifted |= bits[i - wShift - 1] >>> (64 - bShift);   // carry across word boundary
            bits[i] |= shifted;
        }
    }
    return bits;
}
```

**Three things to get right:** the `>>> (64 - bShift)` carry (Java's shift distance is mod 64, so
`bShift == 0` must be special-cased — `>>> 64` is `>>> 0`, a silent bug); the **descending** word
loop for 0/1 knapsack (ascending would reuse the item, giving unbounded behaviour); and masking
off bits above `S` in the final word.

## 9. Pitfalls (8 + fixes)

1. **Stale `opt[mid]` in D&C** — recurse *after* assigning, never before.
2. **Uninitialised `opt[i][i]`** — default `0` gives an empty search range and `MAX_VALUE`.
3. **Forward sweep on a `j−1`-previous-row recurrence** — silently wrong. Use two rows.
4. **`bShift == 0` in the bitset carry** — `>>> 64 == >>> 0`. Special-case it.
5. **Ascending word loop in 0/1 bitset knapsack** — reuses items; you get the unbounded answer.
6. **Deque used on a non-monotone comparison** — wrong minimum, no warning.
7. **Knuth conditions assumed but unverified** — wrong answers on instances where `w` violates
   the quadratic inequality. Test on small `n` against brute force.
8. **SMAWK on a merely-monotone (not totally monotone) matrix** — wrong row minima, no crash.

## 10. Micro-optimisations

- Swap rows by reference (`int[] t = prev; prev = cur; cur = t;`) instead of `System.arraycopy`.
- Flatten `int[][]` to a single `int[]` with `idx = i * stride + j` for cache locality.
- Precompute `w(i,j)` where it does not depend on `k` (it usually doesn't) — hoist it out of
  the `k` loop entirely.
- Replace the deque's `val[]` parallel array with an index into a packed long to halve the
  array traffic.
- Use `Long.MAX_VALUE / 4` rather than `Long.MAX_VALUE` as `-∞` so adding `w` cannot overflow.
- For very large `S` in bitset DP, split the bitset into cache-sized blocks (e.g. 32 KB) and
  process items block-by-block to stay in L1/L2.

## 11. Checklist

- [ ] Deque: front-evict then back-pop then query — in that order.
- [ ] Deque: only valid when the comparison order is fixed and monotone.
- [ ] Knuth: both conditions verified on the actual cost function.
- [ ] Knuth: `opt[i][i]` initialised; search range clamped with `Math.max`/`Math.min`.
- [ ] D&C: `opt[mid]` assigned before recursing; bounds clamped.
- [ ] In-place: sweep direction justified by "what row does each read find?"
- [ ] Bitset: `bShift == 0` special-cased; descending loop; tail bits masked.
- [ ] Every optimisation cross-validated against the naive version on random `n ≤ 12`.