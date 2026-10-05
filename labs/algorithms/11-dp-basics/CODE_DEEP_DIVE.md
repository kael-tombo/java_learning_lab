# CODE_DEEP_DIVE — DP Basics (Three Fib Forms)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.Arrays;
public final class DPBasics { // naive O(φⁿ); memo/tab O(n); opt O(1) space
    public static long naive(int n) { // Θ(φⁿ) — teaching/demo only
        if (n <= 1) return n;            // O(1) base
        return naive(n - 1) + naive(n - 2); // T(n-1)+T(n-2)+O(1)
    }
    public static long memo(int n) { // O(n) states × O(1)
        long[] m = new long[n + 1]; Arrays.fill(m, -1); // O(n) init; -1 safe (fib≥0)
        return dfs(n, m);               // O(n)
    }
    private static long dfs(int n, long[] m) { // stored=final invariant
        if (n <= 1) return n;           // O(1)
        if (m[n] != -1) return m[n];    // O(1) reuse — the whole trick
        return m[n] = dfs(n - 1, m) + dfs(n - 2, m); // compute once O(1)+recurse
    }
    public static long tab(int n) { // O(n) time, O(1) space
        if (n <= 1) return n;           // O(1)
        long a = 0, b = 1;              // O(1) dp[i-2],dp[i-1]
        for (int i = 2; i <= n; i++) { long c = a + b; a = b; b = c; } // O(n) adds
        return b;                       // dp[n]
    }
    public static long mod(int n, long M) { // O(n) word ops under mod
        if (n <= 1) return n;           // O(1)
        long a = 0, b = 1;              // O(1)
        for (int i = 2; i <= n; i++) { long c = (a + b) % M; a = b; b = c; } // mod per add
        return b;                       // O(1)
    }
}
```

## 2. Complexity Annotations
- `naive`: tree nodes ~φⁿ; depth n (stack also O(n)).
- `memo`: n+1 fills, each O(1); recursion depth n (overflow >~10⁴).
- `tab`/`mod`: loop n−1 adds, 2 words; mod keeps word-size O(1).

## 3. Pitfalls (5 + fixes)
1. `int` fib(47) overflow → long (to 92) then mod/BigInteger.
2. Sentinel `-1` collides if answers can be −1 → boolean[] computed.
3. `ways(0)=0` off-by-one → define 1 (empty way), test 0/1.
4. Deep memo (n=10⁵) StackOverflow → tab/loop.
5. `%` once at end overflows → mod per addition (distributive).

## 4. Micro-Opts
- Fast doubling O(log n) for huge n (mod); matrix exponentiation alternative.

## 5. Test Snippets
```java
assert DPBasics.memo(10) == 55 && DPBasics.tab(10) == 55;
assert DPBasics.memo(0) == 0 && DPBasics.tab(1) == 1;
assert DPBasics.mod(100, 1_000_000_007L) == 354224848L;
```

## 6. Checklist
- [ ] Three forms + mod. [ ] Sentinel/base comments. [ ] Depth warning.
