# CODE_DEEP_DIVE — Dynamic Programming Track
> Java implementation + pitfalls. Track `dynamic-programming`.

## Canonical: memo → tabulation → compression
```java
import java.util.*;
public final class Memo {
    // Top-down: grid paths with obstacles
    public static int paths(int[][] g) {
        int[][] memo = new int[g.length][g[0].length];
        for (int[] r : memo) Arrays.fill(r, -1);
        return dfs(g, 0, 0, memo);
    }
    static int dfs(int[][] g, int i, int j, int[][] memo) {
        if (i >= g.length || j >= g[0].length || g[i][j] == 1) return 0;
        if (i == g.length - 1 && j == g[0].length - 1) return 1;
        if (memo[i][j] != -1) return memo[i][j];
        return memo[i][j] = dfs(g, i + 1, j, memo) + dfs(g, i, j + 1, memo);
    }
    // Bottom-up with 1D compression (no obstacles)
    public static int pathsTab(int m, int n) {
        int[] dp = new int[n];
        Arrays.fill(dp, 1);
        for (int i = 1; i < m; i++)
            for (int j = 1; j < n; j++) dp[j] += dp[j - 1];
        return dp[n - 1];
    }
    // Coin min-coins bottom-up
    public static int minCoins(int[] coins, int amount) {
        int INF = 1 << 28;
        int[] dp = new int[amount + 1];
        Arrays.fill(dp, INF); dp[0] = 0;
        for (int a = 1; a <= amount; a++)
            for (int c : coins)
                if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);
        return dp[amount] >= INF ? -1 : dp[amount];
    }
}
```

## Pitfalls table
| Pitfall | Symptom | Fix |
|---|---|---|
| Incomplete memo key | wrong reuse | include all varying params |
| Missing base case | StackOverflow | bases before recursion |
| -1 sentinel collision | false hits | separate visited[][] or null-box |
| int overflow counts | negatives | long/BigInteger |
| Forward 0/1 loop | item reuse | descending capacity |
| Deep chain recursion | StackOverflow | iterative table |
| Compressed + reconstruct | impossible | keep parent table |
| Obstacle ignored | overcount | zero blocked cells |
| Coin order dupes | double-count ways | coins-outer discipline |
| No fuzz | hidden base bug | brute n≤12 harness |

## Testing
- Fuzz memo vs brute on grids ≤ 4×4 with random obstacles.
- Fuzz minCoins vs BFS on small amounts.
- Assert tabulation == memo on 200 random cases.

## Performance notes
- int[][] beats Map for dense states; Map for sparse.
- Row-major loops; pre-size; avoid boxing.
- Convert hot memoized paths to tables before shipping.

## Review checklist
- [ ] Keys complete. [ ] Bases tested. [ ] Fuzz green.
- [ ] Compression safe. [ ] Overflow guarded.
