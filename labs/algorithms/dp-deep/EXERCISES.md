# EXERCISES — DP Deep Track
> Implement + trace + edge cases (Java templates). Track `dp-deep`.

## E1. 0/1 knapsack (1D compression)
```java
public class E1 {
    public static int knapsack(int[] w, int[] v, int W) {
        int[] dp = new int[W + 1];
        for (int i = 0; i < w.length; i++)
            for (int c = W; c >= w[i]; c--)   // backward = 0/1 reuse guard
                dp[c] = Math.max(dp[c], dp[c - w[i]] + v[i]);
        return dp[W];
    }
}
```
- Trace: w={2,3,4}, W=5. Edge: W=0, item heavier than W.

## E2. LCS + reconstruction
```java
public class E2 {
    // TODO: dp[m+1][n+1]; match => dp[i-1][j-1]+1 else max of neighbors
    // TODO: backtrack with parent move table to rebuild one LCS
    // Edge: empty string, all-match, no-match
}
```

## E3. LIS O(n log n) + Kadane
```java
import java.util.*;
public class E3 {
    // TODO: tails + lowerBound for strictly increasing LIS length
    // TODO: Kadane with start/end indices; all-negative edge
}
```

## E4. Matrix chain + interval DP
```java
public class E4 {
    // TODO: dp[len][i]; try splits k; Knuth opt[k] narrowing (advanced)
    // Edge: n=1 (0 cost), n=2
}
```

## E5. Tree DP (reroot diameter / knapsack)
```java
public class E5 {
    // TODO: post-order dp[u]; combine children; second pass for reroot
    // Edge: chain (deep recursion → iterative), star
}
```

## E6. Digit DP counting
```java
public class E6 {
    // TODO: memo[pos][sum][tight]; count numbers <= X with digit-sum S
    // Edge: X=0, leading zeros policy
}
```

## Edge-case checklist
- [ ] Empty inputs. [ ] Backward loop for 0/1. [ ] Forward for unbounded.
- [ ] int vs long totals. [ ] Reconstruction tested.

## Trace template
| step | state | decision | invariant holds? |
|---|---|---|---|
| 1 | init | base | yes |

## Review rubric
- [ ] All 6 compile + pass fixtures. [ ] Trace tables filled.
- [ ] Complexity stated per exercise. [ ] One pitfall noted each.
