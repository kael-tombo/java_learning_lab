# EXERCISES — Advanced Algorithms Deep Track
> Implement + trace + edge cases (Java templates). Track `advanced-algo-deep`.

## E1. Bit-subset DP (TSP over 12 cities)
```java
public class E1 {
    // dp[mask][i] = min cost visiting mask ending at i
    public static int tsp(int[][] w) {
        int n = w.length, N = 1 << n;
        int[][] dp = new int[N][n];
        for (int[] r : dp) java.util.Arrays.fill(r, 1 << 28);
        dp[1][0] = 0;
        for (int mask = 1; mask < N; mask++)
            for (int i = 0; i < n; i++) {
                if ((mask & (1 << i)) == 0) continue;
                for (int j = 0; j < n; j++) {
                    if ((mask & (1 << j)) != 0) continue;
                    int nm = mask | (1 << j);
                    dp[nm][j] = Math.min(dp[nm][j], dp[mask][i] + w[i][j]);
                }
            }
        int ans = 1 << 28;
        for (int i = 1; i < n; i++) ans = Math.min(ans, dp[N-1][i] + w[i][0]);
        return ans;
    }
}
```
- Trace: n=3 hand-run table. Edge: n=1, asymmetric weights.

## E2. Miller-Rabin + Pollard Rho harness
```java
public class E2 {
    static long mul(long a, long b, long m) {
        return java.math.BigInteger.valueOf(a).multiply(
            java.math.BigInteger.valueOf(b)).mod(
            java.math.BigInteger.valueOf(m)).longValue();
    }
    // TODO: modPow, isProbablePrime bases {2,3,5,7,11} deterministic < 2^64
    // TODO: pollardRho(n) with Floyd cycle + random polynomial
}
```
- Edge: Carmichael 561, even n, n < 2.

## E3. Aho-Corasick matcher
```java
public class E3 {
    // TODO: trie nodes with goto/fail/output; build fail via BFS
    // search(text): walk automaton, emit matches
}
```
- Trace: patterns {he, she, his}. Edge: overlapping matches, empty pattern.

## E4. Convex hull (Monotone chain)
```java
public class E4 {
    // TODO: sort by x; cross(o,a,b) <= 0 pop for lower/upper hull
    // Edge: collinear points, duplicates, n < 3
}
```

## E5. Parallel prefix + Karger step
```java
public class E5 {
    // TODO: ForkJoin parallel prefix (up-sweep/down-sweep)
    // TODO: one Karger contraction step with union-find
    // Edge: single element, disconnected graph
}
```

## E6. Greedy set-cover with ratio log
```java
public class E6 {
    // TODO: greedy max-uncovered pick; assert |cover| <= H(d)*OPT on fixtures
    // Edge: empty universe, duplicate sets
}
```

## Edge-case checklist
- [ ] n=0/1 handled. [ ] overflow guarded (long/BigInteger).
- [ ] randomized seeds fixed for repro. [ ] parallel threshold tuned.

## Trace template
| step | state | decision | invariant holds? |
|---|---|---|---|
| 1 | init | base | yes |

## Review rubric
- [ ] All 6 compile + pass fixtures. [ ] Trace tables filled.
- [ ] Complexity stated per exercise. [ ] One pitfall noted each.
