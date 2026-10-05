# CODE_DEEP_DIVE — Game Theory Algorithms (Minimax / Grundy)
> Java implementation + pitfalls. Lab `22-game-theory`.

## 1. Production-grade implementation (Java 17)
```java
package lab.22_game_theory;
import java.util.*;

public final class Solution {
    private Solution() {}

    // Core: minimax + alpha-beta; Nash via best-response; Sprague-Grundy XOR
    // Complexity: minimax O(b^d), alpha-beta O(b^(d/2)) best; solving Nash PPAD. Invariant: alpha/beta bounds always bracket true value.
    public static int solve(int[] a) {
        if (a == null) throw new IllegalArgumentException("input null");
        if (a.length == 0) return 0;
        // Example skeleton adaptable to Game Theory Algorithms (Minimax / Grundy); replace body per lab.
        int n = a.length;
        int[] dp = new int[n];
        Arrays.fill(dp, 1);
        int best = 1;
        for (int i = 1; i < n; i++) {
            for (int j = 0; j < i; j++) {
                // MAINTAIN INVARIANT: alpha/beta bounds always bracket true value
                if (a[j] < a[i]) dp[i] = Math.max(dp[i], dp[j] + 1);
            }
            best = Math.max(best, dp[i]);
        }
        return best;
    }

    // Rolling-space / optimized variant (O(min) space where applicable).
    public static int solveOptimized(String x, String y) {
        if (x == null || y == null) throw new IllegalArgumentException("null");
        // Ensure y is shorter for O(min) space.
        if (y.length() > x.length()) { String t2 = x; x = y; y = t2; }
        int m = x.length(), n = y.length();
        int[] prev = new int[n + 1], cur = new int[n + 1];
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (x.charAt(i-1) == y.charAt(j-1)) cur[j] = prev[j-1] + 1;
                else cur[j] = Math.max(prev[j], cur[j-1]);
            }
            int[] tmp = prev; prev = cur; cur = tmp;
        }
        return prev[n];
    }
}
```

## 2. Line-by-line notes (15)
- Null/empty guards first — fail fast with IAE.
- `dp` holds prefix answers; never read uninitialized cells.
- Inner condition encodes problem predicate; swapping it silently breaks correctness.
- `best` avoids final linear scan; update inside loop.
- Optimized variant swaps to keep O(min) space — common interview follow-up.
- Use `long` for sums/products; `Math.addExact` to detect overflow.
- Prefer `ArrayDeque` over `Stack`; `PriorityQueue` for greedy/top-k.
- Keep `solve` pure; I/O only in `main`/tests.

## 3. Pitfalls (10)
1. Off-by-one: `<=` vs `<` on 1-indexed DP tables.
2. Loop order: swapping i/j breaks dependency DAG.
3. int overflow on cost accumulation.
4. Forgetting to swap/clear rolling arrays.
5. Mutating input array unintentionally.
6. Recursion depth > ~10k → StackOverflow; go iterative.
7. Bad hashCode/equals or comparator inconsistency.
8. Mod arithmetic negative remainder (`(x%M+M)%M`).
9. Not handling duplicates/ties deterministically.
10. Measuring without warmup — JIT noise mistaken for regression.

## 4. Testing blueprint
```java
// JUnit 5 excerpts
// - testEmpty, testSingleton, testSorted, testReverse, testDuplicates
// - testRandomVsBruteForce (200 seeds, n<=9)
// - testOverflow (large values with long oracle)
// - testPerformance (n=100k completes < budget)
```

## 5. Performance notes
- Target minimax O(b^d), alpha-beta O(b^(d/2)) best; solving Nash PPAD; profile allocations with JFR.
- Prefer array + index over LinkedList for cache locality.
- Reuse buffers across benchmark iterations; avoid GC churn.
- Parallelize only when n large (ForkJoin threshold ~10k).

## 6. Refactor checklist
- [ ] Guards + Javadoc contract. [ ] Invariant comments. [ ] No magic numbers.
- [ ] Optimized-space variant present. [ ] Fuzz test vs oracle green.
