# Code Deep Dive — LCS & Edit Distance

Annotated Java: full-table, rolled, Hirschberg, bit-parallel, Damerau/OSA, Myers's diff, banded. Java 21.

---

## 1. Reference implementations (write these first, always)

```java
public final class Seq {

    // ---------- LCS: full table. The correctness oracle for everything else. ----------
    public static int[][] lcsTable(byte[] a, byte[] b) {
        int n = a.length, m = b.length;
        int[][] L = new int[n + 1][m + 1];        // boundary row/col are 0
        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= m; j++)
                L[i][j] = (a[i - 1] == b[j - 1])
                        ? L[i - 1][j - 1] + 1      // take the diagonal: provably optimal
                        : Math.max(L[i - 1][j], L[i][j - 1]);
        return L;
    }

    // ---------- LCS: rolled, Theta(min(n,m)) space ----------
    public static int lcsLen(byte[] a, byte[] b) {
        if (a.length < b.length) { byte[] t = a; a = b; b = t; }   // b is the SHORTER one
        int n = a.length, m = b.length;
        int[] dp = new int[m + 1];                // one row

        for (int i = 1; i <= n; i++) {
            int diagonal = 0;                     // L[i-1][0] -- always 0 for LCS
            dp[0] = 0;                             // L[i][0] = 0
            for (int j = 1; j <= m; j++) {
                int up = dp[j];                   // L[i-1][j] -- MUST save before overwriting
                dp[j] = (a[i - 1] == b[j - 1])
                        ? diagonal + 1
                        : Math.max(dp[j], dp[j - 1]);
                diagonal = up;                     // becomes L[i][j-1] for the next j
            }
        }
        return dp[m];
    }

    // ---------- Levenshtein: rolled ----------
    public static int editDistance(byte[] a, byte[] b) {
        if (a.length < b.length) { byte[] t = a; a = b; b = t; }
        int n = a.length, m = b.length;
        int[] dp = new int[m + 1];
        for (int j = 0; j <= m; j++) dp[j] = j;    // E[0][j] = j -- NON-ZERO boundary

        for (int i = 1; i <= n; i++) {
            int diagonal = dp[0];                  // E[i-1][0] = i-1
            dp[0] = i;                             // E[i][0] = i  <-- the LCS/E difference
            for (int j = 1; j <= m; j++) {
                int up = dp[j];                    // E[i-1][j]
                int cost = (a[i - 1] == b[j - 1]) ? 0 : 1;
                dp[j] = Math.min(Math.min(up + 1, dp[j - 1] + 1), diagonal + cost);
                diagonal = up;
            }
        }
        return dp[m];
    }
}
```

### The three boundaries, side by side

| | `dp[0]` before the outer loop | `dp[0]` at the start of each row |
|---|---|---|
| LCS | `0` | `0` |
| Levenshtein | `j` (`E[0][j] = j`) | **`i`** (`E[i][0] = i`) |

**Forgetting the `dp[0] = i` in Levenshtein** makes it compute something LCS-shaped. Symptom: `editDistance("abc", "") == 0`.

**Forgetting the `diagonal = up` save** gives the correct first row and garbage afterwards — the single most common bug in this family.

---

## 2. LCS reconstruction

```java
/** Backtrack the full table into an alignment. */
public record Aln(byte[] a, byte[] b, byte[] aOps, byte[] bOps) {}   // 'M','-','+' per column

public static Aln align(byte[] a, byte[] b) {
    int n = a.length, m = b.length;
    int[][] L = lcsTable(a, b);

    byte[] ao = new byte[n + m], bo = new byte[m + n];
    int pa = n + m - 1, pb = m + n - 1, i = n, j = m;

    while (i > 0 && j > 0) {
        if (a[i - 1] == b[j - 1]) {              // MATCH (greedy diagonal is optimal)
            ao[pa--] = 'M'; bo[pb--] = 'M'; i--; j--;
        } else if (L[i - 1][j] >= L[i][j - 1]) {  // tie-break: prefer DELETING from a.
                                                 // The other choice gives an equally long
                                                 // alignment; this one is stable for diffing.
            ao[pa--] = '-'; bo[pb--] = ' '; i--;
        } else {
            ao[pa--] = ' '; bo[pb--] = '+'; j--;
        }
    }
    while (i > 0) { ao[pa--] = '-'; bo[pb--] = ' '; i--; }
    while (j > 0) { ao[pa--] = ' '; bo[pb--] = '+'; j--; }
    return new Aln(a, b, ao, pb1(ao, pa + 1, n + m), pb1(bo, pb + 1, n + m));
}
```

**Writing back-to-front into fixed-size arrays and trimming the offset** is the standard trick; writing front-to-front requires a length estimate first, which is an extra pass.

**PITFALL — LCS reconstruction is only valid if you always take the diagonal on a match.** If you take `max(L[i-1][j], L[i][j-1])` even when `a[i-1] == b[j-1]`, you may produce an alignment *shorter* than `L[n][m]` (the diagonal is provably ≥ the others, but only by induction over the whole table, and a hand-written backtracker that prefers "up" can drift). Assert `alignment length == L[n][m]`.

---

## 3. Hirschberg's linear-space LCS

```java
/**
 * LCS with reconstruction in Theta(min(n,m)) space.
 * NOTE: this version splits ONLY A, giving Theta(nm log n) time in the worst case.
 *       See the next method for the Theta(nm) version.
 */
public static byte[] lcsHirschberg(byte[] a, byte[] b) {
    if (a.length == 0) return new byte[0];
    if (b.length == 0) return new byte[0];
    if (a.length == 1) { return (indexOfByte(b, a[0]) >= 0) ? a.clone() : new byte[0]; }

    int mid = a.length >>> 1;
    int[] fwd = lcsLengthsForward(a, 0, mid, b);       // fwd[j] = LCS(a[0..mid),  b[0..j))
    int[] bwd = lcsLengthsBackward(a, mid, a.length, b); // bwd[j] = LCS(a[mid..n),  b[j..m))

    int best = -1, split = 0;
    for (int j = 0; j <= b.length; j++) {
        int v = fwd[j] + bwd[j];
        if (v > best) { best = v; split = j; }          // FIRST maximum: deterministic
    }
    byte[] left  = lcsHirschberg(Arrays.copyOfRange(a, 0, mid), Arrays.copyOfRange(b, 0, split));
    byte[] right = lcsHirschberg(Arrays.copyOfRange(a, mid, a.length), Arrays.copyOfRange(b, split, b.length));
    return concat(left, right);
}

/** Forward rolled LCS lengths: result[j] = LCS(a[lo..hi), b[0..j)). */
private static int[] lcsLengthsForward(byte[] a, int lo, int hi, byte[] b) {
    int[] dp = new int[b.length + 1];
    for (int i = lo; i < hi; i++) {
        int diag = 0;
        for (int j = 1; j <= b.length; j++) {
            int up = dp[j];
            dp[j] = (a[i] == b[j - 1]) ? diag + 1 : Math.max(dp[j], dp[j - 1]);
            diag = up;
        }
    }
    return dp;
}

/** Backward rolled LCS lengths: result[j] = LCS(a[lo..hi), b[j..m)). */
private static int[] lcsLengthsBackward(byte[] a, int lo, int hi, byte[] b) {
    int[] dp = new int[b.length + 1];
    for (int i = hi - 1; i >= lo; i--) {
        int diag = 0;
        for (int j = b.length - 1; j >= 0; j--) {
            int down = dp[j];
            dp[j] = (a[i] == b[j]) ? diag + 1 : Math.max(dp[j], dp[j + 1]);
            diag = down;
        }
    }
    return dp;
}
```

### The `Θ(nm)` version — alternate which string you split

```java
/** Splits the LONGER string each time so BOTH dimensions halve -> Theta(nm). */
public static byte[] lcsHirschbergFast(byte[] a, byte[] b) {
    if (a.length == 0 || b.length == 0) return new byte[0];
    if (a.length == 1) return (indexOfByte(b, a[0]) >= 0) ? a.clone() : new byte[0];
    if (b.length == 1) return (indexOfByte(a, b[0]) >= 0) ? b.clone() : new byte[0];

    // Split whichever is LONGER. This is the whole difference between nm and nm log n.
    if (a.length >= b.length) {
        int mid = a.length >>> 1;
        int[] fwd = lcsLengthsForward(a, 0, mid, b);
        int[] bwd = lcsLengthsBackward(a, mid, a.length, b);
        int split = argMax(fwd, bwd);
        return concat(lcsHirschbergFast(Arrays.copyOfRange(a, 0, mid), Arrays.copyOfRange(b, 0, split)),
                      lcsHirschbergFast(Arrays.copyOfRange(a, mid, a.length), Arrays.copyOfRange(b, split, b.length)));
    } else {
        // symmetric, splitting B
        int mid = b.length >>> 1;
        int[] fwd = lcsLengthsBackward(b, 0, mid, a);      // NOTE the axes swap
        int[] bwd = lcsLengthsForward(b, mid, b.length, a);
        int split = argMax(fwd, bwd);
        return concat(lcsHirschbergFast(Arrays.copyOfRange(a, 0, split), Arrays.copyOfRange(b, 0, mid)),
                      lcsHirschbergFast(Arrays.copyOfRange(a, split, a.length), Arrays.copyOfRange(b, mid, b.length)));
    }
}
```

### Pitfalls in Hirschberg

1. **`split` off by one.** `fwd[j]` is `LCS(A1, B[0..j))` so `j` is a **count**, and the subproblems are `B[0, split)` and `B[split, m)`. Using `B[0, split-1]` loses a character. Verify the returned LCS length against `lcsLen(a, b)` in a test.

2. **`argMax` tie-break.** Taking the *first* maximum makes the algorithm deterministic; taking the last makes it favour splitting `B` earlier. Either is correct; pick one and write it down so diffs are reproducible.

3. **Quadratic recursion depth is fine, linear is not.** Depth is `Θ(log n)` because you always halve. The `Arrays.copyOfRange` allocations are `Θ(n)` total per level ⇒ `Θ(n log n)` allocations overall. Pass ranges instead of copying if allocation pressure matters.

4. **`argMax` over `fwd + bwd` requires both arrays of length `m+1`** with `bwd[m] = 0` and `fwd[0] = 0`. Off-by-one in either boundary breaks the base cases.

---

## 4. Bit-parallel LCS

```java
/**
 * Bit-parallel LCS for m <= 64 in a single word. Hyyro/Crochemore formulation.
 * Theta(n * m / w) word operations.
 */
public static long lcsBitParallel(byte[] a, byte[] b) {
    final int m = b.length;
    if (m > 64) throw new IllegalArgumentException("single-word version needs m <= 64; see multiWord()");

    // M[c] = bit j set iff b[j] == c. 256 longs for a byte alphabet.
    long[] M = new long[256];
    for (int j = 0; j < m; j++) M[b[j] & 0xFF] |= 1L << j;

    long V = 0;
    for (int i = 0; i < a.length; i++) {
        long u = V | M[a[i] & 0xFF];
        V = (V << 1) | 1;                 // shift breakpoints, add the boundary bit at 0
        V = u & ~(u - V);                 // THE operation: borrow propagation finds next matches
    }
    return Long.bitCount(V);              // the LCS length IS the popcount of the final row
}
```

**PITFALL 1 — the alphabet.** `M` indexed by `b[j] & 0xFF` works for bytes. For `char`, use `M = new long[65536]` = **512 KB** — which defeats the space advantage entirely. For Unicode text, compress the alphabet first (map distinct characters to `0..σ-1`) or use `HashMap<Long,Long>` for the masks.

**PITFALL 2 — `m = 64` and `1L << 63`.** `1L << j` for `j = 63` sets the sign bit; `u - V` then involves a negative `V` and the borrow semantics change. Two options: limit to `m ≤ 63`, or use `unsigned` comparisons carefully. **Test `m = 63` and `m = 64` explicitly.**

**PITFALL 3 — validating against the scalar DP is mandatory.** Bit tricks fail silently on off-by-ones in the mask construction. Fuzz with random `(a, b)` including `m = 0`, `m = 1`, `m = 63`, `m = 64`, and single-character alphabets.

### Multi-word version (m > 64)

```java
public static long lcsBitParallelMulti(byte[] a, byte[] b) {
    final int m = b.length, words = (m + 63) >>> 6;
    long[][] M = new long[256][words];
    for (int j = 0; j < m; j++) M[b[j] & 0xFF][j >>> 6] |= 1L << (j & 63);

    long[] V = new long[words];
    for (int i = 0; i < a.length; i++) {
        long[] Mc = M[a[i] & 0xFF];
        long carry = 1;                       // the "| 1" boundary bit goes into word 0 only
        for (int w = 0; w < words; w++) {
            long u = V[w] | Mc[w];
            long shifted = (V[w] << 1) | carry;
            carry = V[w] >>> 63;               // propagate the shifted-out bit into the next word
            // The SUBTRACTION must borrow across words: do it manually.
            long borrow = 0;
            long newV = 0;
            for (int bit = 0; bit < 64; bit++) {
                long ub = (u >>> bit) & 1;
                long vb = (shifted >>> bit) & 1;
                long bb = borrow;
                long diff = ub - vb - bb;
                newV |= ((diff & 1) << bit);
                borrow = (diff < 0) ? 1 : 0;
            }
            V[w] = u & ~newV;
        }
    }
    long total = 0;
    for (long w : V) total += Long.bitCount(w);
    return total;
}
```

**The bit-by-bit borrow loop is O(64) per word — you have just thrown away most of the speedup.** That is why production bit-parallel LCS caps at `m ≤ 64` per chunk or uses `Long.reverseBytes`-based borrow tricks that are considerably more delicate. **Honest conclusion: implement the single-word version and use it only for `m ≤ 64`.**

---

## 5. Damerau / OSA

```java
/** Optimal String Alignment (restrictions ON): each substring edited at most once. */
public static int osa(byte[] a, byte[] b) {
    if (a.length < b.length) { byte[] t = a; a = b; b = t; }
    int n = a.length, m = b.length;
    int[][] d = new int[n + 1][m + 1];
    for (int i = 0; i <= n; i++) d[i][0] = i;
    for (int j = 0; j <= m; j++) d[0][j] = j;

    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= m; j++) {
            int cost = (a[i - 1] == b[j - 1]) ? 0 : 1;
            d[i][j] = Math.min(Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1), d[i - 1][j - 1] + cost);
            // TRANSPOSE: the (i-2, j-2) cell
            if (i > 1 && j > 1 && a[i - 1] == b[j - 2] && a[i - 2] == b[j - 1]) {
                d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1);
            }
        }
    return d[n][m];
}
```

**Why this needs the full table (or two rolled rows):** the transpose term reads `d[i-2][j-2]`, two rows back. Rolling to one row silently reads garbage.

**Two rows works:**

```java
int[] prevPrev = null, prev = null, cur = null;
for (int i = 1; i <= n; i++) {
    cur = new int[m + 1];
    cur[0] = i;
    for (int j = 1; j <= m; j++) { /* uses prev[j-1], prev[j], cur[j-1], prevPrev[j-2] */ }
    prevPrev = prev; prev = cur;
}
```

**Verify `osa("ca", "ac") == 1`** (Levenshtein gives 2) and `osa("ab", "ba") == 1`.

**Name it correctly in your code.** `osa` is *not* true Damerau-Levenshtein (which needs the Lowrance–Wagner `lastRow`/`lastCol` arrays to allow unrestricted edits), and OSA is **not a metric**:

```
osa("CA", "AC") = 1
osa("AC", "AB") = 1
osa("CA", "AB") = 3   >  1 + 1     <-- triangle inequality VIOLATED
```

If you feed OSA distances into a BK-tree or a "near-duplicate detector" with a threshold, **you will get wrong answers.** Use true Levenshtein or unrestricted Damerau there.

---

## 6. Myers's `O(ND)` diff

```java
/**
 * Myers' O(ND) shortest edit script. D = edit distance.
 * Returns the D-path as a list of (diagonal, move) in reverse.
 */
public record Script(int aStart, int aEnd, int bStart, int bEnd, boolean diagonal) {}

public static List<Script> myersDiff(byte[] a, byte[] b, int maxD) {
    int n = a.length, m = b.length;
    int max = n + m;
    int offset = max;
    boolean[] done = new boolean[2 * max + 1];
    int[] v = new int[2 * max + 1];

    for (int d = 0; d <= Math.min(maxD, max); d++) {
        for (int k = -d; k <= d; k += 2) {
            int i;
            if (k == -d || (k != d && v[k - 1 + offset] < v[k + 1 + offset])) {
                i = v[k + 1 + offset];          // DOWN (insert)
            } else {
                i = v[k - 1 + offset] + 1;      // RIGHT (delete)
            }
            int j = i - k;
            while (i < n && j < m && a[i] == b[j]) { i++; j++; }   // the SNAKE
            v[k + offset] = i;
            done[k + offset] = true;
            if (i >= n && j >= m) return trace(a, b, v, d, k, offset);
        }
    }
    return List.of();       // exceeded maxD: caller must fall back to the O(nm) DP
}
```

**The state is a diagonal `k = i - j`, not a grid cell.** That is the entire idea: the furthest-reaching path with `d` edits and `k` diagonal steps is a single number, so each `d`-step touches `d+1` integers instead of `n·m`.

**The snake** (the `while` loop) is where the speed comes from: matching runs are consumed in one go.

**Two things this implementation cannot do:**

1. **Produce a script without a trace.** The `v` array is overwritten every `d`; a real implementation either records parent pointers (memory `Θ(D)`) or replays. The `trace` method is the replay.
2. **Handle large `D`.** `Θ((n+m)·D)` becomes worse than `Θ(nm)` when `D > nm/(n+m) ≈ min(n,m)/2`. **Always cap `maxD`** and fall back:

```java
public static List<Script> diff(byte[] a, byte[] b) {
    // 1. Strip the common prefix and suffix -- O(n+m) and usually removes most of the work.
    int pre = commonPrefix(a, b), suf = commonSuffix(a, b, pre);
    byte[] ac = Arrays.copyOfRange(a, pre, a.length - suf);
    byte[] bc = Arrays.copyOfRange(b, pre, b.length - suf);

    // 2. If either side is empty, there is nothing to do.
    if (ac.length == 0 || bc.length == 0) return List.of();

    // 3. Cap D. past this, Myers is worse than the quadratic DP.
    int cap = Math.max(64, (ac.length + bc.length) / 4);
    List<Script> s = myersDiff(ac, bc, cap);
    if (s.isEmpty()) s = fallbackQuadratic(ac, bc);       // the LCS/Levenshtein backtrack
    return offset(s, pre, suf);
}
```

**The prefix/suffix strip plus the `D` cap is the correct production shape** and is exactly what `git diff` does.

---

## 7. Banded / `k`-mismatch

```java
/** Returns true if editDistance(a, b) <= k. Theta(nk) time, Theta(k) space. */
public static boolean withinK(byte[] a, byte[] b, int k) {
    int n = a.length, m = b.length;
    if (Math.abs(n - m) > k) return false;          // length difference is a lower bound
    int[] dp = new int[2 * k + 3];
    int off = k + 1;
    Arrays.fill(dp, Integer.MAX_VALUE);
    for (int j = 0; j <= Math.min(m, k); j++) dp[off + j] = j;

    for (int i = 1; i <= n; i++) {
        int lo = Math.max(0, i - k), hi = Math.min(m, i + k);
        int diagOld = dp[off + lo - 1 < 0 ? 0 : off + lo - 1];
        for (int j = lo; j <= hi; j++) {
            int idx = off + (j - i);
            int cost = (a[i - 1] == b[j - 1]) ? 0 : 1;
            int v = Math.min(Math.min(
                    (idx + 1 < dp.length) ? dp[idx + 1] + 1 : Integer.MAX_VALUE,
                    dp[idx - 1] + 1),
                    diagOld + cost);
            diagOld = dp[idx];                       // old dp for this idx becomes next diagonal
            dp[idx] = v;
        }
    }
    return dp[off + (m - n)] <= k;
}
```

**The correctness argument:** `E[i][j] ≤ k` implies `|i - j| ≤ k` (you cannot reach a cell whose index difference exceeds the number of edits, since each edit changes `i - j` by at most 1). So only cells in the band `|i-j| ≤ k` can have `E ≤ k`. Cells outside are `∞`.

**Any in-place version of this is subtle** — the `diagOld` juggling is the whole algorithm. Validate against `editDistance(...) <= k` on 10⁵ random cases.

---

## 8. What to use in production

```java
// One-off similarity: Apache Commons Text
int d = LevenshteinDistance.getDefaultInstance().apply(a, b);

// A spell checker: bit-parallel single word over m <= 64 is exactly the right tool
boolean miss = lcsBitParallel(word, dictEntry) < word.length();   // or a proper approx-match

// Large similar files: the Myers hybrid from section 6 -- prefix/suffix strip + D cap + fallback

// Small strings, many comparisons: the rolled Theta(min(n,m))-space DP, it is fast enough

// Massive inputs where even 400 MB is too much: HirschbergFast
```

**The reference `Θ(nm)` DP is not optional.** It is the oracle that validates every one of the six algorithms above, and it is 20 lines. Write it first, fuzz against it, and only then optimise.