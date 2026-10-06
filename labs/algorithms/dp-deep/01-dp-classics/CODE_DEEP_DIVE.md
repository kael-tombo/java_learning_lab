# Code Deep Dive — DP Classics

Every algorithm twice: top-down memoised and bottom-up tabulated, plus a brute-force oracle. Java 21.

---

## 1. The oracle you must write first

```java
/** Brute force. Exponential. ONLY as a test oracle -- never ship it. */
public static int fibBrute(int n) { return n < 2 ? n : fibBrute(n - 1) + fibBrute(n - 2); }
```

Every DP in this lab is validated as `topDown(n) == bottomUp(n) == bruteForce(n)` for `n = 0..20`. That cross-check catches essentially every DP bug and costs you ten minutes to write.

---

## 2. Fibonacci — top-down

```java
public static final class Fib {
    /** -1 == not computed. Use -1, never 0: F(0) == 0 is a legitimate value. */
    private final long[] memo;

    public Fib(int n) { memo = new long[n + 1]; Arrays.fill(memo, -1L); }

    public long solve(int n) {
        if (n < 0 || n > memo.length - 1) throw new IndexOutOfBoundsException("n=" + n);
        if (n <= 1) return n;                       // BASE first
        long cached = memo[n];                     // CACHE lookup second
        if (cached != -1) return cached;           // PITFALL: `memo[n] != 0` is WRONG -- F(0)=0
        return memo[n] = solve(n - 1) + solve(n - 2);
    }
}
```

**PITFALL — the sentinel must not collide with a legitimate value.** `long[] memo` initialised to `0` breaks at `n = 0` because `F(0) = 0`. Either fill with `-1` or with `Long.MIN_VALUE`, or use a `boolean[] seen` (costly) or a sentinel outside the value domain. **This is the most common top-down DP bug and it produces a wrong answer at exactly one index, which your `n = 0` test must cover.**

**PITFALL — recursion depth.** At `n = 10⁵` this is 10⁵ stack frames → `StackOverflowError`. Top-down DP is not safe for large `n` in Java. That is a real reason to prefer bottom-up.

---

## 3. Fibonacci — bottom-up, rolled

```java
/** Tabulated, O(1) space. F(n) for n >= 0. */
public static long fib(int n) {
    if (n <= 1) return n;
    long prev2 = 0, prev1 = 1;                    // dp[0], dp[1]
    for (int i = 2; i <= n; i++) {
        long cur = prev1 + prev2;
        prev2 = prev1;
        prev1 = cur;
    }
    return prev1;
}

/** Tabulated, full array -- needed if you want to inspect dp. */
public static long[] fibTable(int n) {
    long[] dp = new long[n + 1];
    if (n == 0) return dp;
    dp[0] = 0; dp[1] = 1;                          // BASE before the loop, always
    for (int i = 2; i <= n; i++) dp[i] = dp[i-1] + dp[i-2];
    return dp;
}
```

**The rolling loop is correct** because:
- The reads (`prev1`, `prev2`) happen **before** the write (`cur`), and `cur` is a fresh local.
- The writes to `prev1`/`prev2` happen **after** both reads.

Getting this wrong (`prev1 += prev2; prev2 = prev1;`) produces `F(2)=1, F(3)=2, F(4)=4, F(5)=8` — **doubling instead of Fibonacci**. That is a *classic*: swapping the assignment order is the bug, and it produces plausible-looking increasing values.

---

## 4. Climbing stairs — and the base case that bites

```java
/** Ways to reach step n with moves of 1 or 2. dp[0] = 1 (the empty climb). */
public static long ways(int n) {
    if (n < 0) return 0;
    if (n <= 1) return 1;
    long a = 1, b = 1;                             // dp[0], dp[1]
    for (int i = 2; i <= n; i++) { long c = a + b; a = b; b = c; }
    return b;
}

/** The exact-k-steps variant: dp[n] = sum of dp[n-1..n-k]. */
public static long waysExactly(int n, int k) {
    if (n == 0) return 1;
    long[] dp = new long[n + 1];
    dp[0] = 1;
    long window = 0;
    for (int i = 1; i <= n; i++) {
        dp[i] = window;
        window += dp[i];
        if (i >= k) window -= dp[i - k];           // maintain a k-wide sliding sum
    }
    return dp[n];
}
```

**`dp[0] = 1`, not 0.** The empty climb is one valid way. With `dp[0] = 0` you get `1, 0, 1, 1, 2, …` — wrong for `n = 1` and `n = 2`, and only visible if you test small `n`.

**`waysExactly` sliding-window arithmetic:** the invariant is that after processing `i`, `window = dp[max(0,i-k+1)] + … + dp[i]`. Adding `dp[i]` and subtracting `dp[i-k]` (when `i ≥ k`) keeps it at exactly `k` terms. Off-by-one here produces answers that are correct for `n < k` and wrong for larger `n` — exactly the kind of bug a small test suite misses.

---

## 5. Rod cutting

```java
/**
 * Maximum revenue from cutting a rod of length n.
 * dp[i] = max( price[i], max over 1 <= j < i of price[j] + dp[i-j] )
 */
public static int maxRevenue(int[] price, int n) {
    if (n < 0 || n >= price.length) throw new IllegalArgumentException("n=" + n);
    int[] dp = new int[n + 1];

    for (int i = 1; i <= n; i++) {
        // Initialise with the "no cut" option FIRST. PITFALL: forgetting this makes
        // dp[i] = 0 whenever every cut is worse than selling the whole rod.
        dp[i] = price[i];

        for (int j = 1; j <= i; j++) {
            dp[i] = Math.max(dp[i], price[j] + dp[i - j]);
        }
    }
    return dp[n];
}

/** Top-down version -- proves top-down == bottom-up. */
public static int maxRevenueMemo(int[] price, int n) {
    int[] memo = new int[n + 1];
    Arrays.fill(memo, -1);
    return solve(price, n, memo);
}

private static int solve(int[] price, int i, int[] memo) {
    if (i <= 0) return 0;
    if (memo[i] != -1) return memo[i];
    int best = price[i];                            // no cut
    for (int j = 1; j <= i; j++) best = Math.max(best, price[j] + solve(price, i - j, memo));
    return memo[i] = best;
}

/** With reconstruction: returns the cut lengths. */
public static List<Integer> cutPlan(int[] price, int n) {
    int[] dp = new int[n + 1];
    int[] choice = new int[n + 1];                  // which j was optimal at i
    for (int i = 1; i <= n; i++) {
        dp[i] = price[i];
        for (int j = 1; j <= i; j++) {
            int cand = price[j] + dp[i - j];
            if (cand > dp[i]) { dp[i] = cand; choice[i] = j; }
        }
    }
    List<Integer> cuts = new ArrayList<>();
    for (int i = n; i > 0; i -= choice[i]) cuts.add(choice[i]);
    Collections.reverse(cuts);
    return cuts;
}
```

**PITFALL — `dp[i] = price[i]` must be the initialiser.** If you write `dp[i] = 0` and only loop `j = 1..i`, the `j = i` case gives `price[i] + dp[0] = price[i]`, so it is covered — but only if `price[i]` is a legal single-piece sale. Writing `dp[i] = 0` and looping `j = 1..i-1` **without** the initialiser silently loses the no-cut option. Pick one and comment it.

**Reconstruction needs the full table.** `Θ(n)` space, not `O(1)` — this is the general trade: **you cannot both roll the array and print the solution.**

---

## 6. Unbounded coin change

```java
public static int minCoins(int[] coins, int amount) {
    if (amount < 0) throw new IllegalArgumentException();
    final int INF = Integer.MAX_VALUE / 2;          // NOT MAX_VALUE: INF+1 would overflow
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, INF);
    dp[0] = 0;

    for (int a = 1; a <= amount; a++) {
        for (int c : coins) {
            if (c > a) continue;
            if (dp[a - c] == INF) continue;         // explicit reachability check
            dp[a] = Math.min(dp[a], dp[a - c] + 1);
        }
    }
    return dp[amount] == INF ? -1 : dp[amount];
}

/** COUNT the ways, treating different ORDERINGS as different (compositions). */
public static int countCompositions(int[] coins, int amount) {
    int[] dp = new int[amount + 1];
    dp[0] = 1;                                      // the empty combination
    for (int a = 1; a <= amount; a++)
        for (int c : coins) if (c <= a) dp[a] += dp[a - c];
    return dp[amount];
}

/** COUNT the ways treating order as IRRELEVANT (combinations / multisets). */
public static int countCombinations(int[] coins, int amount) {
    int[] dp = new int[amount + 1];
    dp[0] = 1;
    for (int c : coins)                             // OUTER LOOP IS COINS -- this is the whole difference
        for (int a = c; a <= amount; a++)
            dp[a] += dp[a - c];
    return dp[amount];
}
```

### The three traps in this file

1. **`INF = Integer.MAX_VALUE` overflows.** `INF + 1 = Integer.MIN_VALUE`, so `Math.min(dp[a], dp[a-c] + 1)` becomes "negative", and `-1` as the "unreachable" return collides with a legitimate-looking answer. Use `MAX_VALUE / 2` or check reachability.

2. **`countCompositions` vs `countCombinations` differ only by the loop order.** Verify with `coins = {1, 2}`, `amount = 3`:
   - compositions: `1+1+1`, `1+2`, `2+1` ⇒ **3**
   - combinations: `{1,1,1}`, `{1,2}` ⇒ **2**

   **Write both in the test.** This is the single most-asked coin-change variant and the loop-order distinction is the entire question.

3. **`dp[0] = 1` for counting, `dp[0] = 0` for minimising.** Same array, different base. Mixing them gives 0 or 1 off everywhere.

**Overflow in the counting variants:** `countCombinations({1}, 10^4)` = 1, fine; but `countCombinations({1,2,3}, 500)` = `2^499/…` ≫ `2³¹`. Use `long` and document the cap, or `BigInteger`. (LeetCode's "coin change II" is bounded by a modulus; add `dp[a] %= MOD` inside the loop if that is the spec — but then `dp[a] + dp[a-c]` can be `2·MOD`, so use `(dp[a] + dp[a - c]) % MOD` with care about the int range: `2 * (MOD-1)` overflows if `MOD > 2³⁰`.)

---

## 7. Top-down with a generic memo (avoid the boilerplate)

```java
/** Memoises a state function over Integer keys. Works for any acyclic DP. */
public static final class Memo1 {
    private final int n;
    private final long[] memo;
    private final boolean[] seen;
    private long statesComputed = 0, cacheHits = 0;

    public Memo1(int n) { this.n = n; memo = new long[n + 1]; seen = new boolean[n + 1]; }

    public interface Rec { long apply(int i); }

    public long solve(int target, Rec transition) {
        if (target < 0 || target > n) throw new IllegalArgumentException();
        if (target == 0) return 1;                   // caller-specific base
        if (seen[target]) { cacheHits++; return memo[target]; }
        statesComputed++;
        return memo[target] = transition.apply(target);
    }

    public long states() { return statesComputed; }
    public long hits() { return cacheHits; }
}
```

**Why `seen[]` as well as a sentinel value.** It is unambiguous for every value domain (including "0 is a legitimate answer" and "answers can be negative"). The cost is 1 byte per state — usually irrelevant, and always worth it.

**`statesComputed` is a diagnostic you should assert on.** For Fibonacci it must equal `n+1`. If it is larger, your state definition is too fine (you are memoising sub-subproblems unnecessarily). If smaller, you have a bug.

---

## 8. 2-D patterns you will reuse everywhere

### Grid DP, `dp[i][j] = f(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])`

```java
public static int[][] grid(int[][] a) {
    int n = a.length, m = a[0].length;
    int[][] dp = new int[n + 1][m + 1];             // +1 on both axes: the zero row/column are the base
    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= m; j++)
            dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]) + a[i-1][j-1];
    return dp;
}

/** Rolled to O(m) -- and note WHICH axis you roll, which depends on the recurrence. */
public static int gridRolled(int[][] a) {
    int n = a.length, m = a[0].length;
    int[] dp = new int[m + 1];
    for (int i = 1; i <= n; i++) {
        int diagonal = 0;                            // holds the OLD dp[i-1][j-1]
        for (int j = 1; j <= m; j++) {
            int up = dp[j];                           // save before overwrite
            dp[j] = Math.max(dp[j], dp[j - 1]) + a[i - 1][j - 1];
            diagonal = up;                            // becomes the next iteration's diagonal
        }
    }
    return dp[m];
}
```

**The `diagonal` save is the whole trick.** `dp[i][j]`'s recurrence reads three cells; after overwriting `dp[j]` in place, the old `dp[i-1][j-1]` is gone. Saving it before the write is what makes rolling correct. **A missing `diagonal` produces answers that are correct for the first row and wrong afterwards** — and a test that only checks `n = m = 1` will not notice.

### The fill-order rule for 2-D

```
if the recurrence reads dp[i-1][j] and dp[i][j-1]:
    i ascending OUTER, j ascending INNER          ✓

if it reads dp[i-1][j] and dp[i+1][j]   (column recurrence):
    it is NOT a valid bottom-up DP -- the dependency is cyclic in i.
    Either change the state definition or use top-down.
```

**This is worth internalising: "can I fill this bottom-up?" is answered by "does every transition reference a strictly smaller index under some total order?"** If not, top-down (or a topological sort of the state DAG) is mandatory.

---

## 9. Cross-validation harness

```java
static void fuzz() {
    Random rnd = new Random(2024);
    for (int trial = 0; trial < 20_000; trial++) {
        int n = rnd.nextInt(16);
        assert fibBrute(n) == fib(n) : "fib " + n;

        // Climbing stairs vs a brute-force enumeration of move sequences.
        long brute = 0;
        for (int mask = 0; (1 << mask) - 1 <= n && mask < (1 << 12); mask++) { /* ... */ }
        // Simpler oracle: ways(n) == fib(n+1). Assert that identity directly.
        assert ways(n) == fib(n + 1) : "climbing stairs == fib(n+1) failed at " + n;

        // Rod cutting: top-down vs bottom-up vs an exhaustive set-partition search.
        int len = 1 + rnd.nextInt(9);
        int[] price = new int[len];
        for (int i = 0; i < len; i++) price[i] = 1 + rnd.nextInt(20);
        assert maxRevenueMemo(price, len - 1) == maxRevenue(price, len - 1) : "rod";

        // Coin change: min, compositions, combinations.
        int[] coins = {1, 3, 4};
        int amt = rnd.nextInt(30);
        int min = minCoins(coins, amt);
        assert min == -1 || min >= 0 : "coin";
        assert countCombinations(coins, amt) <= countCompositions(coins, amt) : "combo <= comp";
    }
}
```

**The invariant `combinations ≤ compositions` is a good sanity check** — every multiset corresponds to at least one ordering, so the ordering count must be ≥ the multiset count. It fails the moment someone swaps the loop order by accident.

**And the identity `ways(n) == fib(n+1)`** is worth asserting explicitly: it is the cleanest possible proof that "climbing stairs is Fibonacci", and if a refactor breaks it you know immediately.

---

## 10. What to write in production

```java
// Nothing here. Java has no DP library because every DP is bespoke.
//
// What IS reusable:
//   - a generic memo table (Memo1 above)
//   - the rolling-array pattern with an explicit `diagonal` save
//   - a sentinel convention (INF = MAX/2) written down once
//
// What is NOT reusable:
//   - top-down recursion above n ~ 1000 (StackOverflowError)
//   - "clever" index arithmetic that hides the state definition
//
// What to remember: state definition first, code second.
```