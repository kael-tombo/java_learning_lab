# Code Deep Dive — Matrix Chain & String DP

Annotated Java for all six problems. Java 21.

---

## 1. Matrix chain multiplication

```java
public final class MatrixChain {

    /** Returns the minimum scalar-multiplication count for A0 * A1 * ... * A(n-1). */
    public static int minCost(int[] d) {
        int n = d.length - 1;                 // d has n+1 entries
        if (n <= 1) return 0;

        // cost[i][j] for 0 <= i <= j < n.  Diagonal stays 0.
        long[][] cost = new long[n][n];
        long[] h = java.util.Arrays.stream(cost).mapToLong(r -> Long.MAX_VALUE / 4).toArray();
        for (int[] r : cost) java.util.Arrays.fill(r, (int) 0);

        // Fill by INCREASING INTERVAL LENGTH. This is required, not stylistic.
        for (int len = 2; len <= n; len++) {
            for (int i = 0; i + len - 1 < n; i++) {
                int j = i + len - 1;
                long best = Long.MAX_VALUE / 4;
                for (int k = i; k < j; k++) {
                    // rows of (A_i..A_k) = d[i], cols = d[k+1];  A_i..A_j has cols d[j+1]
                    long c = cost[i][k] + cost[k + 1][j] + (long) d[i] * d[k + 1] * d[j + 1];
                    if (c < best) best = c;
                }
                cost[i][j] = best;
            }
        }
        return (int) cost[0][n - 1];
    }
```

**Cleaner version without the stream gymnastics:**

```java
public static long minCost(int[] d) {
    int n = d.length - 1;
    if (n <= 1) return 0;
    final long INF = Long.MAX_VALUE / 4;

    long[][] cost = new long[n][n];
    for (long[] row : cost) Arrays.fill(row, INF);
    for (int i = 0; i < n; i++) cost[i][i] = 0;

    for (int len = 2; len <= n; len++)
        for (int i = 0; i + len - 1 < n; i++) {
            int j = i + len - 1;
            for (int k = i; k < j; k++) {
                long c = cost[i][k] + cost[k + 1][j] + (long) d[i] * d[k + 1] * d[j + 1];
                if (c < cost[i][j]) cost[i][j] = c;
            }
        }
    return cost[0][n - 1];
}
```

### Pitfall 1 — dimension indices off by one

`d` has `n+1` entries: `d[i]` is the number of **rows** of `A_i`, and `d[i+1]` its **columns**.

- The result matrix of `(A_i..A_k)` is `d[i] × d[k+1]`. ✔
- The cost of multiplying `(A_i..A_k) × (A_{k+1}..A_j)` is `d[i] · d[k+1] · d[j+1]`. ✔

Using `d[k]` or `d[j]` gives plausible-looking wrong answers because the array bounds are still valid. **Verify against the worked example in Exercise 1.**

### Pitfall 2 — `int` overflow

`d[i]·d[k+1]·d[j+1]` overflows `int` for `d` values in the hundreds. With `d = {10,100,5,50}` the maximum intermediate is `100·50·50 = 250 000` — fine. With `d = {1000, 1000, 1000}` you get `10⁹` per multiply and `10¹²` over 1000 multiplies ⇒ **`long` is mandatory.** Cast *before* multiplying: `(long) d[i] * d[k+1] * d[j+1]`.

### Pitfall 3 — wrong fill order

```java
for (int i = 0; i < n; i++)                       // WRONG: i ascending
    for (int j = i + 1; j < n; j++)               //         j ascending
        for (int k = i; k < j; k++)
            dp[i][j] = min(dp[i][j], dp[i][k] + dp[k+1][j] + cost);
```

`dp[i][k]` with `k < j` has **not** been computed yet (it comes later in the `j` loop). Result: `dp[i][k]` is `INF` and the answer is wrong (or `INF`-contaminated). **The order must be by increasing interval length, or `i` descending with `j` ascending.**

### Reconstructing the parenthesisation

```java
public static int[][] splits(int[] d) {
    int n = d.length - 1;
    long[][] cost = new long[n][n];
    int[][] split = new int[n][n];
    for (long[] row : cost) Arrays.fill(row, Long.MAX_VALUE / 4);
    for (int i = 0; i < n; i++) cost[i][i] = 0;

    for (int len = 2; len <= n; len++)
        for (int i = 0; i + len - 1 < n; i++) {
            int j = i + len - 1;
            for (int k = i; k < j; k++) {
                long c = cost[i][k] + cost[k + 1][j] + (long) d[i] * d[k + 1] * d[j + 1];
                if (c < cost[i][j]) { cost[i][j] = c; split[i][j] = k; }
            }
        }
    return split;
}

public static void printParenthesisation(int[][] split, int i, int j, StringBuilder sb) {
    if (i == j) { sb.append('A').append(i); return; }
    int k = split[i][j];
    sb.append('(');
    printParenthesisation(split, i, k, sb);
    printParenthesisation(split, k + 1, j, sb);
    sb.append(')');
}
```

**Verify** with `d = {10,100,5,50}`: the output must be `(A0(A1A2)A3)` or equivalent with cost `20 000`.

---

## 2. Palindrome partitioning

```java
public record Partition(String text, int cuts, List<String> pieces) {}

public static Partition minCuts(String s) {
    int n = s.length();
    if (n == 0) return new Partition("", 0, List.of());
    if (n == 1) return new Partition(s, 0, List.of(s));

    // pal[i][j] = true iff s[i..j] is a palindrome.  Theta(n^2) precompute.
    boolean[][] pal = new boolean[n][n];
    for (int i = n - 1; i >= 0; i--)
        for (int j = i; j < n; j++)
            pal[i][j] = s.charAt(i) == s.charAt(j) && (j - i <= 1 || pal[i + 1][j - 1]);
    // i DESCENDING so pal[i+1][j-1] is ready. j ascending is fine.
    // PITFALL: pal[i+1][...] needs i+1 <= n-1; guarded by j - i <= 1 short-circuit.

    int[] dp = new int[n + 1];
    int[] from = new int[n + 1];
    Arrays.fill(dp, Integer.MAX_VALUE);
    dp[0] = 0;
    for (int i = 1; i <= n; i++)
        for (int j = 0; j < i; j++)
            if (pal[j][i - 1] && dp[j] != Integer.MAX_VALUE && dp[j] + 1 < dp[i]) {
                dp[i] = dp[j] + 1;
                from[i] = j;
            }

    // reconstruct
    List<String> pieces = new ArrayList<>();
    for (int i = n; i > 0; i = from[i]) pieces.add(s.substring(from[i], i));
    Collections.reverse(pieces);
    return new Partition(s, dp[n], pieces);
}
```

**Pitfall 1 — `pal[i+1][j-1]` when `j - i < 2`.** The short-circuit `j - i <= 1` handles it. Without it you read `pal[n][...]` for `i = n-1` ⇒ `ArrayIndexOutOfBoundsException`.

**Pitfall 2 — the loop direction.** `i` must be **descending** so `pal[i+1][j-1]` is already computed. With `i` ascending you read `false` everywhere and the answer is `n-1` (every character its own piece).

**Pitfall 3 — memory.** `boolean[n][n]` for `n = 10⁵` is **10 GB.** The `Θ(n²)` time means the problem is not feasible at that size anyway, but you should cap `n` and say so.

### The `Θ(n)`-space variant (centre expansion)

```java
public static int minCutsO1Space(String s) {
    int n = s.length();
    if (n <= 1) return 0;
    int[] dp = new int[n + 1];
    Arrays.fill(dp, Integer.MAX_VALUE);
    dp[0] = 0;

    for (int centre = 0; centre < 2 * n - 1; centre++) {
        int l = centre / 2, r = (centre + 1) / 2;
        for (; l >= 0 && r < n && s.charAt(l) == s.charAt(r); l--, r++) {
            // s[l..r] is a palindrome -> the piece ending at r starts at l
            if (dp[l] != Integer.MAX_VALUE) dp[r + 1] = Math.min(dp[r + 1], dp[l] + 1);
        }
    }
    return dp[n] - 1 < 0 ? 0 : dp[n] - 1;
}
```

Same `Θ(n²)` time, `Θ(n)` space. **Every palindrome is visited exactly once** by its centre, so the total work is the number of palindromes, `≤ n(n+1)/2`.

**Pitfall:** the answer is `dp[n] - 1` because `dp` counts *pieces*, not cuts. Returning `dp[n]` is the classic off-by-one.

---

## 3. Word break

```java
/** Existence only. Theta(n^2) with a HashSet, or Theta(n*L) with a trie. */
public static boolean wordBreak(String s, Set<String> dict, int maxLen) {
    int n = s.length();
    boolean[] can = new boolean[n + 1];
    can[0] = true;
    for (int i = 1; i <= n; i++)
        for (int j = Math.max(0, i - maxLen); j < i; j++)
            // PITFALL: s.substring(j, i) inside the loop is Theta(i-j) -> Theta(n^3) overall.
            if (can[j] && dict.contains(s.substring(j, i))) { can[i] = true; break; }
    return can[n];
}
```

The `substring` cost is real: for `n = 5000` the naive version is `Θ(n³) = 1.25·10¹¹` character copies.

### The `Θ(n·L)` trie version

```java
public static boolean wordBreakTrie(String s, Trie trie) {
    int n = s.length();
    boolean[] can = new boolean[n + 1];
    can[0] = true;
    for (int i = 0; i < n; i++) {
        if (!can[i]) continue;
        Trie.Node node = trie.root;
        for (int j = i; j < n; j++) {
            node = node.next[s.charAt(j)];
            if (node == null) break;                 // no word extends this far
            if (node.terminal) can[j + 1] = true;
        }
    }
    return can[n];
}
```

`Θ(n·L)` where `L` is the longest word — each walk is `Θ(L)` with `O(1)` per character.

### The `Θ(S + n)` Aho–Corasick version — the right algorithm

```java
public static boolean wordBreakAho(String s, List<String> dict) {
    AhoCorasick ac = new AhoCorasick(dict);
    int n = s.length();
    boolean[] can = new boolean[n + 1];
    can[0] = true;

    for (int end = 1; end <= n; end++) {
        // Feed s[end-1] to the automaton and collect the lengths of all words ending at end-1
        ac.feed(s.charAt(end - 1));
        for (int len : ac.matchedLengthsNow()) {
            if (can[end - len]) { can[end] = true; break; }
        }
    }
    return can[n];
}
```

**`Θ(S + n + matches)`** instead of `Θ(n²)`. For `n = 10⁴` and `|dict| = 10⁴` with mean length 8, that is `Θ(10⁵)` instead of `Θ(10⁸)` — a **1000×** improvement, and the correct algorithm for a large dictionary.

---

## 4. All segmentations

```java
public static List<String> segmentations(String s, Set<String> dict, int maxLen) {
    int n = s.length();
    @SuppressWarnings("unchecked") List<String>[] ways = new List[n + 1];
    ways[0] = new ArrayList<>(List.of(""));
    for (int i = 1; i <= n; i++) {
        ways[i] = new ArrayList<>();
        for (int j = Math.max(0, i - maxLen); j < i; j++) {
            if (ways[j].isEmpty()) continue;
            String piece = s.substring(j, i);
            if (dict.contains(piece))
                for (String pre : ways[j]) ways[i].add(pre.isEmpty() ? piece : pre + " " + piece);
        }
    }
    return ways[n];
}
```

**Pitfall — exponential blow-up.** For `s = "aaaa…a"` with a dictionary of all lengths, the count is `2^{n-1}`. **The output bound is unavoidable**, but production code must cap it:

```java
private static final int MAX_OUT = 1000;
...
if (ways[i].size() > MAX_OUT) throw new IllegalStateException("too many segmentations at " + i);
```

**Failing to cap it is a denial-of-service bug**, not a performance bug — a 40-character all-`a` string with `{"a","aa","aaa","aaaa"}` produces `2³⁹ ≈ 5·10¹¹` segmentations.

---

## 5. String metrics (`Θ(nm)` per pair)

```java
/**
 * String edit distance with SEPARABLE costs.
 *   deleteCost(x), insertCost(y), substituteCost(x, y)
 */
public static int stringDistance(char[] x, char[] y,
                                 ToIntFunction<Character> del,
                                 ToIntFunction<Character> ins,
                                 ToIntBiFunction<Character, Character> sub) {
    int n = x.length, m = y.length;
    int[] dp = new int[m + 1];
    for (int j = 1; j <= m; j++) dp[j] = dp[j - 1] + ins.applyAsInt(y[j - 1]);   // E[0][j]

    for (int i = 1; i <= n; i++) {
        int diag = dp[0];
        dp[0] = dp[0] + del.applyAsInt(x[i - 1]);                                // E[i][0]
        for (int j = 1; j <= m; j++) {
            int up = dp[j];                                                       // E[i-1][j]
            int s = (x[i-1] == y[j-1]) ? 0 : sub.applyAsInt(x[i-1], y[j-1]);
            dp[j] = Math.min(Math.min(up + del.applyAsInt(x[i-1]),
                                       dp[j-1] + ins.applyAsInt(y[j-1])),
                             diag + s);
            diag = up;
        }
    }
    return dp[m];
}
```

**Pitfall — recomputing the cost inside the inner loop.** `del.applyAsInt(x[i-1])` is loop-invariant in `j`; hoist it:

```java
int d = del.applyAsInt(x[i - 1]);               // once per row
int c = Math.min(up + d, dp[j-1] + ins.applyAsInt(y[j-1]));
```

For a lambda-based cost this is a **2× speedup** and it makes the code clearer.

### The Penney-game matrix

```java
/** M[i][j] = distance(suffix of X of length |X|-i, prefix of Y of length j). */
public static int[][] overlapMatrix(String X, String Y) {
    int n = X.length(), m = Y.length();
    int[][] M = new int[n + 1][m + 1];
    for (int i = 0; i <= n; i++)
        for (int j = 0; j <= m; j++) {
            int len = Math.min(n - i, j);
            M[i][j] = stringDistance(
                X.substring(i, i + len).toCharArray(),
                Y.substring(0, len).toCharArray(),
                c -> 1, c -> 1, Character::compare);
        }
    return M;
}
```

**Cost:** `Θ(n²m²)` for the whole matrix (`n·m` entries, each an `Θ(len²)` DP). For `n = m = 20` that is `160 000` DP cells × 400 = manageable; for `n = m = 40` it is `Θ(10⁸)` — a few seconds.

**Use `long` distances** — with `substituteCost = |x−y|` and codes up to 127, a distance can exceed `int` for long strings.

---

## 6. RNA folding (Nussinov)

```java
/** Bases: A pairs U, C pairs G. Returns the max number of nested, disjoint pairs. */
public static int maxPairs(char[] seq) {
    int n = seq.length;
    final int[][] dp = new int[n][n];
    // dp[i][j] = max pairs in seq[i..j].  Diagonal and below = 0.

    for (int len = 2; len <= n; len++)
        for (int i = 0; i + len - 1 < n; i++) {
            int j = i + len - 1;
            int best = dp[i + 1][j];                          // i unpaired
            for (int k = i; k <= j - 2; k++)
                if (pairable(seq[i], seq[k]))
                    best = Math.max(best, 1 + dp[i + 1][k - 1] + dp[k + 1][j]);
            dp[i][j] = best;
        }
    return dp[0][n - 1];
}

private static boolean pairable(char a, char b) {
    return (a == 'A' && b == 'U') || (a == 'U' && b == 'A')
        || (a == 'C' && b == 'G') || (a == 'G' && b == 'C');
}
```

### Pitfall 1 — `dp[i+1][k-1]` when `k == i+1`

`k - 1 == i`, and `dp[i+1][i]` is `0` by the `i > j` convention — the array is `n × n` with the lower triangle untouched (zeros). ✔ **This is the one place where the "empty interval" convention must be `0` by initialisation, not by an explicit check.** Writing `dp = new int[n+1][n+1]` with `1`-based indices also works but shifts every index.

### Pitfall 2 — fill order

`len` **increasing** is required: `dp[i+1][k-1]` has length `k−i−1 < len` ✔ and `dp[k+1][j]` has length `j−k < len` ✔.

Using `i` descending, `j` ascending also works (both sub-intervals have a larger `i` or a smaller `j`). Using `i` ascending, `j` descending **does not**.

### Pitfall 3 — `int` overflow

Max pairs is `⌊n/2⌋`, so `int` is fine. But the **MFE variant** with energy terms can go negative and needs `-∞` initialisation, not `0`.

---

## 7. Burst balloons — the same shape with `max`

```java
/** Same interval+split shape as matrix chain, with max instead of min. */
public static int burst(int[] nums) {
    int n = nums.length;
    if (n < 3) return 0;
    int[][] dp = new int[n][n];
    for (int len = 1; len < n; len++)
        for (int i = 0; i + len < n; i++) {
            int j = i + len;
            for (int k = i + 1; k <= j; k++) {
                if (k < n && nums[i] > 0 && nums[j] > 0) continue;   // boundary balloons are free
                dp[i][j] = Math.max(dp[i][j],
                        dp[i][k-1] + dp[k][j] + nums[i] * nums[k] * nums[j]);
            }
        }
    return dp[0][n - 1];
}
```

**Note the structure is identical** to matrix chain — the same `Θ(n³)` interval DP with a split. Only the combine function and the boundary handling differ. **Recognising that is the transferable skill.**

---

## 8. Cross-validation harness

```java
static void fuzz() {
    Random rnd = new Random(2468);
    for (int trial = 0; trial < 20_000; trial++) {
        // --- Matrix chain: enumerate all parenthesisations (Catalan) for n <= 8 ---
        int n = 1 + rnd.nextInt(8);
        int[] d = new int[n + 1];
        for (int i = 0; i <= n; i++) d[i] = 1 + rnd.nextInt(6);
        assert MatrixChain.minCost(d.clone()) == bruteMatrixChain(d.clone(), n);

        // --- Palindrome partitioning: greedy/brute for short strings ---
        String s = randStr(rnd, rnd.nextInt(12), 1 + rnd.nextInt(3));
        assert IntervalDP.minCuts(s).cuts() == bruteMinCuts(s);
        assert IntervalDP.minCutsO1Space(s).cuts() == IntervalDP.minCuts(s).cuts();

        // --- Word break: recursive definition ---
        Set<String> dict = randDict(rnd, s);
        assert IntervalDP.wordBreak(s, dict, s.length() + 1) == bruteWordBreak(s, dict);

        // --- RNA: brute force over pairings for n <= 10 ---
        char[] seq = randRna(rnd, 1 + rnd.nextInt(10));
        assert IntervalDP.maxPairs(seq) == bruteMaxPairs(seq);
    }
}

/** Catalan enumeration. O(4^n) -- only for n <= 8. This is the ORACLE. */
static long bruteMatrixChain(int[] d, int n) {
    if (n == 1) return 0;
    long best = Long.MAX_VALUE / 4;
    for (int k = 0; k < n - 1; k++) {
        long c = bruteMatrixChain(d, k + 1)
               + bruteMatrixChain(Arrays.copyOfRange(d, k + 1, d.length), n - k - 1)
               + (long) d[0] * d[k + 1] * d[n];
        best = Math.min(best, c);
    }
    return best;
}
```

**The Catalan oracle is the highest-value test in this lab.** It validates the fill order, the dimension indices, and the `long` handling all at once, and it is only ~10 lines.

**Use a small alphabet** for palindromes and RNA (3 letters) so ties and repeats are frequent.

---

## 9. What to use in production

```java
// Matrix chain in Java: you probably do NOT need this.
// The JIT + escape analysis inlines small fixed chains at compile time.
// Use the DP when the "matrices" are really strings, trees, or intervals.

// Palindrome partitioning: the Theta(n^2) DP with a precomputed pal table.
// O(n^2) space is fine for n <= 5000 (25 MB). Beyond that the problem is
// inherently quadratic and you should look for a different formulation.

// Word break with a big dictionary: ACROSS -- Aho-Corasick, Theta(S + n).
// Theta(n^2) is a 1000x slowdown at realistic scales.

// RNA folding: this IS what tools do, but they vectorise it.
// A correct Theta(n^3) DP is a baseline, not a solution.
```

**The transferable lesson:** the interval+split DP is a *shape*, and the engineering question is always *"can I precompute the split predicate (→ `Θ(n²)`) or exploit monotonicity of `opt` (→ Knuth/D&C/SMAWK)?"* Lab `08-dp-optimizations` is the systematic answer.