# CODE_DEEP_DIVE — Digit DP

## 1. Canonical implementation: count ≤ N with digit sum = S

```java
package com.alglab.digitdp;

public final class DigitSumCount {
    private final int d;              // number of digits
    private final int[] n;            // n[i] = i-th digit of N, MSB first

    private DigitSumCount(long bound) {
        String s = Long.toString(bound);
        this.d = s.length();          // N = 0 → d = 1  (critical: never 0)
        this.n = new int[d];
        for (int i = 0; i < d; i++) n[i] = s.charAt(i) - '0';
    }

    /** count of x in [0, bound] with digitSum(x) == target. Θ(d · target · 10) */
    public static long count(long bound, int target) {
        if (target < 0 || target > 9 * String.valueOf(bound).length()) return 0L; // prune early
        DigitSumCount self = new DigitSumCount(bound);
        long[][] memo = new long[self.d + 1][target + 1];
        return self.memo(0, 0, true, memo);
    }

    // memo[pos][sum] : only the tight==true slice is cached — see note below
    private long memo(int pos, int sum, boolean tight, long[][] m) {
        if (sum > target) return 0;                       // monotone → prune
        if (pos == d) return sum == target ? 1 : 0;       // terminal
        if (tight && m[pos][sum] >= 0) return m[pos][sum];
        int hi = tight ? n[pos] : 9;                      // the bound flag's only job
        long ans = 0;
        for (int x = 0; x <= hi; x++) ans += memo(pos + 1, sum + x, tight && x == n[pos], m);
        if (tight) m[pos][sum] = ans;
        return ans;
    }
}
```

**The one-line takeaway:** `int hi = tight ? n[pos] : 9;` *is* the bound. Everything else is
bookkeeping.

## 2. Rolling-array version (Θ(K) space)

```java
/** iterative, two arrays: only Θ(target) space regardless of d */
public static long countIterative(long bound, int target) {
    String s = Long.toString(bound);
    int d = s.length();
    long[] cur = new long[target + 1], next = new long[target + 1];
    cur[0] = 1;                                            // empty prefix, sum 0, tight
    for (int pos = 0; pos < d; pos++) {
        Arrays.fill(next, 0L);
        int digitN = s.charAt(pos) - '0';
        for (int sum = 0; sum <= target; sum++) {
            long waysTight = cur[sum];
            long waysFree = free[sum];                     // see two-flag version below
            if (waysTight == 0 && waysFree == 0) continue;
            int hiTight = digitN, hiFree = 9;
            for (int x = 0; x <= hiTight; x++)
                if (sum + x <= target) next[sum + x] += waysTight;
            for (int x = 0; x <= hiFree; x++)
                if (sum + x <= target) next[sum + x] += waysFree;
        }
        System.arraycopy(next, 0, cur, 0, target + 1);
    }
    return cur[target];
}
```

Keep `curTight[]` and `curFree[]` **separate** — merging them into one array requires remembering,
per cell, which `tight` value produced it. Separate arrays make the two-phase transition
obvious: the tight array only extends up to `n[pos]`, the free array up to `9`.

## 3. Value-carrying (counting → summing)

```java
/** Σ x for x in [0, bound] with digitSum(x) == target. Θ(d · target · 10) */
public static long sumValues(long bound, int target) {
    String s = Long.toString(bound);
    int d = s.length();
    long[] cT = new long[target + 1], cF = new long[target + 1];
    long[] sT = new long[target + 1], sF = new long[target + 1];
    long[] nT = new long[target + 1], nF = new long[target + 1];
    long[] nS = new long[target + 1], nF2 = new long[target + 1];   // sum-of-squares
    cT[0] = 1;
    for (int pos = 0; pos < d; pos++) {
        Arrays.fill(nT, 0); Arrays.fill(nF, 0);
        Arrays.fill(nS, 0); Arrays.fill(nF2, 0);
        Arrays.fill(nX, 0); Arrays.fill(nY, 0);
        int digitN = s.charAt(pos) - '0';
        for (int sum = 0; sum <= target; sum++) {
            // tight branch
            for (int x = 0; x <= digitN && sum + x <= target; x++) {
                int t = sum + x;
                nT[t]  += cT[sum];
                nS[t]  += 10L * sT[sum] + (long) x * cT[sum];   // p → 10p + x
                nX[t]  += 100L * qT[sum] + 20L * x * sT[sum] + (long) x * x * cT[sum];
            }
            // free branch (identical, hi = 9)
            for (int x = 0; x <= 9 && sum + x <= target; x++) { /* ... */ }
        }
        cT = nT; cF = nF; sT = nS; sF = nF2; qT = nX; qF = nY;
    }
    return sT[target] + sF[target];
}
```

`nX` (sum of squares) uses `(10p + x)² = 100p² + 20px + x²`. **Overflow:** `Σ x²` over
`[0, 10^18]` is `Θ(10^54)` — `long` overflows around `10^19`. Use `BigInteger` or work mod `M`.

## 4. Divisibility with precomputation

```java
/** ways[len][r] = # of length-len digit strings (leading zeros allowed) ≡ r (mod m) */
public static long[][] buildWays(int m, int maxLen) {
    long[][] ways = new long[maxLen + 1][m];
    ways[0][0] = 1;                                              // empty string ≡ 0
    for (int len = 0; len < maxLen; len++)
        for (int r = 0; r < m; r++) {
            if (ways[len][r] == 0) continue;                    // prune empty cells
            for (int x = 0; x <= 9; x++)
                ways[len + 1][(10 * r + x) % m] += ways[len][r];
        }
    return ways;
}

/** count of x in [0, bound] with x % m == 0. Θ(d · 10) with the table */
public static long countDivisible(long bound, int m, long[][] ways) {
    String s = Long.toString(bound);
    long ans = 0;
    int rem = 0;
    for (int pos = 0; pos < s.length(); pos++) {
        int digitN = s.charAt(pos) - '0';
        int rest = s.length() - pos - 1;
        // branch here: choose x < digitN, then the rest is unconstrained
        for (int x = 0; x < digitN; x++)
            ans += ways[rest][((rem * 10) + x) % m];
        // continue tight
        rem = (rem * 10 + digitN) % m;
    }
    return ans + (rem == 0 ? 1 : 0);                            // include bound itself
}
```

Note the `ways[rest][...]` lookup is `O(1)` — the whole suffix collapses to one table read.

## 5. Pitfalls (7 + fixes)

1. **`d = 0` for `N = 0`.** `Long.toString(0)` gives `"0"` → `d = 1`, fine. But `String.valueOf`
   on a `long` built by division can produce `""` → guard `d = max(1, digits)`.
2. **Memoising only the `tight = 1` slice.** Legal and correct *only if* you also memo the
   `tight = 0` slice separately — the value depends on `pos` and `sum` in both slices, so
   cache both or neither. Caching only one and letting the other recompute is not a bug, just
   slower; caching one *table* for both is a bug.
3. **Forgetting `started`.** Counting "digit sum = 3, no two equal adjacent digits ≤ 99" without
   `started` counts `003` and `3` as different paths to the same number. Fix: add the flag, or
   prove the predicate is leading-zero invariant first.
4. **Leading zeros contributing to the sum.** `007` has digit sum 7 by string semantics. Fix:
   `s' = started ? s + x : (x == 0 ? s : x)`.
5. **Caching by `pos` only.** The memo key must include *every* dimension. Missing `tight` in
   the key is the classic bug — you get a value computed for a smaller bound.
6. **`sum > target` not pruned.** Non-terminating `O(d · 10^d)` blowup if `target` is unbounded.
7. **`int` accumulators for sums.** `Σ x` over `[0, 10^18]` is `~5·10^35` — `long` overflows.
   Counts fit `long`; sums need `BigInteger` or modular arithmetic.

## 6. Micro-optimisations

- `System.arraycopy` instead of `Arrays.fill` + loop when swapping buffers.
- `int[]` for `n[]` digits (cache locality); avoid `String.charAt` in the hot loop.
- Short-circuit when `N = 10^k − 1`: the `tight` branch is never taken after `pos = 0`, so the
  whole query is one table lookup.
- Precompute `hiTight`/`hiFree` outside the `sum` loop.
- Unroll the `x` loop for the free branch (`hi = 9` is a compile-time constant).

## 7. Test snippets

```java
// count(0, 0) == 1          — the number 0 itself
// count(9, 0) == 1          — only 0; proves leading zeros do NOT add to sum
// count(99, 18) == 1        — only 99
// count(999, 18) == 55      — a+b+c=18, 0<=a,b,c<=9 (inclusion-exclusion)
// count(10, 1) == 2         — 1 and 10
// countDivisible(20, 5) == 5  — 0,5,10,15,20 (0 counts)
// sumValues(20, 5) == 50     — 0+5+10+15+20
// brute-force cross-check for every N in [0, 5000]
```

## 8. Checklist

- [ ] `d ≥ 1` always. [ ] Memo key includes *all* state dimensions.
- [ ] `started` present iff the predicate is leading-zero sensitive.
- [ ] `sum > target` pruned. [ ] Accumulator width chosen per statistic (count `long`,
      sum `BigInteger`/mod).
- [ ] `tight` update is `tight && (x == n[pos])`, never `x == n[pos]`.
- [ ] Cross-validated against brute force for small `N`.