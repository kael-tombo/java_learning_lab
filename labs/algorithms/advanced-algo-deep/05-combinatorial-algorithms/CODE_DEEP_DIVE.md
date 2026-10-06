# Code Deep Dive — Combinatorial Algorithms

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
public final class Combinatorics {
    public static long binom(int n, int k) {
        if (k < 0 || k > n) return 0;
        long res = 1;
        for (int i = 1; i <= k; i++) res = res * (n - k + i) / i;   // exact: each step integral
        return res;
    }

    public static long catalan(int n) { return binom(2*n, n) / (n + 1); }

    public static long surjections(int n, int k) {
        long total = 0;
        for (int i = 0; i <= k; i++) {
            long term = binom(k, i) * pow(k - i, n);
            total += (i % 2 == 0) ? term : -term;
        }
        return total;
    }

    private static long pow(long a, int e) { long r = 1; while (e-- > 0) r *= a; return r; }

    public static long stirling2(int n, int k) {
        long[] dp = new long[k + 1];
        dp[0] = 1;
        for (int i = 1; i <= n; i++)
            for (int j = Math.min(i, k); j >= 1; j--)
                dp[j] = j * dp[j] + dp[j - 1];
        return dp[k];
    }

    /** Enumerate every submask of m. */
    public static void submasks(int m) {
        for (int s = m; ; s = (s - 1) & m) {
            // process s
            if (s == 0) break;
        }
    }
}
```

## Pitfalls

- Computing n! first overflows even for modest n — use the multiplicative binomial loop or Pascal.
- Off-by-one in Catalan indexing: C_n counts n pairs of parentheses.
- Inclusion–exclusion has 2^k terms; it is only practical for small k.
- Meet-in-the-middle trades a 2^{n/2} space blow-up for the time win.
- In the Stirling table, update row entries from high k to low k, or the previous row is overwritten.
- The submask loop must use s=(s-1)&M, not s-1, or it leaves the mask and visits wrong subsets.

## Why the bounds hold

- **Binomial via Pascal**: Θ(n·k) time, Θ(k) — rolling row.
- **Catalan closed form**: Θ(n) time, Θ(1) — one binomial computation.
- **S(n,k) Pascal-style**: Θ(n·k) time, Θ(k) — rolling row.
- **Inclusion–exclusion, k props**: Θ(2^k) time, Θ(k) — only for small k.
- **Meet in the middle**: Θ(2^{n/2}·n) time, Θ(2^{n/2}) — halves the exponent.
- **Submask enumeration, all masks**: Θ(3^k) time, Θ(1) — amortised over masks.

## Takeaway

# Theory — Combinatorial Algorithms
