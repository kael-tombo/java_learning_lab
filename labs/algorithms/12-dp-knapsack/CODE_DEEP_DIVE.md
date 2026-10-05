# CODE_DEEP_DIVE — 0/1 Knapsack (2-D + 1-D + Reconstruct)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.*;
public final class Knapsack { // O(nW) time; O(nW) / O(W) space
    public static int dp2D(int[] w, int[] v, int W) { // value-only via full table
        int n = w.length; int[][] dp = new int[n + 1][W + 1]; // O(nW) space
        for (int i = 1; i <= n; i++)             // O(n) items
            for (int c = 0; c <= W; c++) {       // O(W) capacities
                dp[i][c] = dp[i - 1][c];         // O(1) skip
                if (w[i - 1] <= c)               // O(1) feasible?
                    dp[i][c] = Math.max(dp[i][c], dp[i - 1][c - w[i - 1]] + v[i - 1]); // take
            }
        return dp[n][W];                         // O(1) optimum
    }
    public static int dp1D(int[] w, int[] v, int W) { // O(W) space — value only
        int[] dp = new int[W + 1];               // O(W)
        for (int i = 0; i < w.length; i++)       // O(n)
            for (int c = W; c >= w[i]; c--)      // DESCENDING — prev-row preserved
                dp[c] = Math.max(dp[c], dp[c - w[i]] + v[i]); // O(1)
        return dp[W];                            // O(1)
    }
    public static List<Integer> chosen(int[] w, int[] v, int W) { // needs 2-D walk
        int n = w.length; int[][] dp = new int[n + 1][W + 1]; // rebuild O(nW)
        for (int i = 1; i <= n; i++) for (int c = 0; c <= W; c++) { // same fill
            dp[i][c] = dp[i - 1][c];
            if (w[i - 1] <= c) dp[i][c] = Math.max(dp[i][c], dp[i - 1][c - w[i - 1]] + v[i - 1]);
        }
        List<Integer> out = new ArrayList<>(); int c = W; // backtrack O(n+W)
        for (int i = n; i > 0; i--)              // O(n) steps
            if (dp[i][c] != dp[i - 1][c]) { out.add(i - 1); c -= w[i - 1]; } // took i
        Collections.reverse(out); return out;    // O(n)
    }
}
```

## 2. Complexity Annotations
- States `n(W+1)` × O(1) → Θ(nW) time (pseudo-poly).
- 1-D descending keeps `dp[c−w]` = prev-row (not-yet-overwritten); ascending breaks it.
- Reconstruction O(n+W) walk after O(nW) fill; 1-D alone cannot reconstruct.

## 3. Pitfalls (5 + fixes)
1. Ascending 1-D → unbounded (silent). Fix: descending + direction test.
2. Promising set from 1-D → impossible; keep table/take flags.
3. `w[i]==0,v>0` infinite-feel → pre-take all, exclude from loops.
4. `int` value overflow → long for big sums.
5. Non-integer weights → scale/discretize or FPTAS (DP needs int caps).

## 4. Micro-Opts
- Two-row + bitset take-matrix (memory lite + reconstruct); reachable-set sparse DP.

## 5. Test Snippets
```java
int[] w={2,3,4}, v={3,4,5};
assert Knapsack.dp2D(w,v,5)==7 && Knapsack.dp1D(w,v,5)==7;
assert Knapsack.chosen(w,v,5).equals(List.of(0,1));
```

## 6. Checklist
- [ ] Direction comment. [ ] Reconstruct path. [ ] Zero-weight guard.
