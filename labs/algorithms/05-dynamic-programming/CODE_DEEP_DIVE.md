# CODE_DEEP_DIVE — Dynamic Programming (Fib/LIS/Knapsack-core)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.Arrays;
public final class DP { // states × transition = cost; memo O(n), tab O(n)/O(1)
    public static long fibTab(int n) { // O(n) time, O(1) space
        if (n <= 1) return n;                    // O(1) base
        long a = 0, b = 1;                       // O(1)
        for (int i = 2; i <= n; i++) { long c = a + b; a = b; b = c; } // O(n)
        return b;                                // O(1)
    }
    public static int lis(int[] a) { // O(n log n) patience; O(n) space
        int[] tails = new int[a.length]; int len = 0; // O(n) aux
        for (int x : a) {                        // O(n) iters
            int i = Arrays.binarySearch(tails, 0, len, x); // O(log n) probe
            if (i < 0) i = -(i + 1);             // O(1) insertion point
            tails[i] = x;                        // O(1)
            if (i == len) len++;                 // O(1) extend
        }
        return len;                              // O(1)
    }
    public static int knap1D(int[] w, int[] v, int W) { // O(nW) time, O(W) space
        int[] dp = new int[W + 1];               // O(W)
        for (int i = 0; i < w.length; i++)       // O(n) items
            for (int c = W; c >= w[i]; c--)      // O(W) DESCENDING (load-bearing)
                dp[c] = Math.max(dp[c], dp[c - w[i]] + v[i]); // O(1)
        return dp[W];                            // O(1)
    }
}
```

## 2. Complexity Annotations
- `fibTab`: n−1 adds; 2 words. Naive would be Θ(φⁿ) — state counting explains gap.
- `lis`: n probes × log n; tails[i] = min tail of length i+1 (invariant).
- `knap1D`: nW updates; descending preserves prev-row semantics; ascending = unbounded bug.

## 3. Pitfalls (5 + fixes)
1. Ascending knapsack loop → silent unbounded. Fix: descending + regression test.
2. 1-D loses reconstruction → keep 2-D/take flags when set needed.
3. `int` overflow (fib/values) → long/mod per add.
4. Wrong bases (`ways(0)=0`) → off-by-one cascade; test 0/1.
5. Cyclic state deps → infinite memo recursion; enforce DAG order.

## 4. Micro-Opts
- Two-row knapsack (reconstruct-lite) vs full table (reconstruct).
- `System.arraycopy` for row copies; cache-friendly W-major loops.

## 5. Test Snippets
```java
assert DP.fibTab(10) == 55;
assert DP.lis(new int[]{10,9,2,5,3,7,101,18}) == 4;
assert DP.knap1D(new int[]{2,3,4}, new int[]{3,4,5}, 5) == 7;
```

## 6. Checklist
- [ ] Direction comment on inner loop. [ ] Overflow policy. [ ] Bases tested.
- [ ] State-count comment (states × t).
