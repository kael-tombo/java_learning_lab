# CODE_DEEP_DIVE — DP Deep Track
> Java implementation + pitfalls. Track `dp-deep`.

## Canonical: knapsack + LCS + LIS
```java
public final class Dp {
    public static int knapsack01(int[] w, int[] v, int W) {
        int[] dp = new int[W + 1];
        for (int i = 0; i < w.length; i++)
            for (int c = W; c >= w[i]; c--)
                dp[c] = Math.max(dp[c], dp[c - w[i]] + v[i]);
        return dp[W];
    }
    public static int lcs(String a, String b) {
        int[] prev = new int[b.length() + 1], cur = new int[b.length() + 1];
        for (int i = 1; i <= a.length(); i++) {
            for (int j = 1; j <= b.length(); j++)
                cur[j] = a.charAt(i-1) == b.charAt(j-1)
                    ? prev[j-1] + 1 : Math.max(prev[j], cur[j-1]);
            int[] t = prev; prev = cur; cur = t;
        }
        return prev[b.length()];
    }
    public static int lis(int[] a) {
        int[] tails = new int[a.length]; int len = 0;
        for (int x : a) {
            int lo = 0, hi = len;
            while (lo < hi) {
                int mid = (lo + hi) >>> 1;
                if (tails[mid] < x) lo = mid + 1; else hi = mid;
            }
            tails[lo] = x; if (lo == len) len++;
        }
        return len;
    }
    public static int kadane(int[] a) {
        int cur = a[0], best = a[0];
        for (int i = 1; i < a.length; i++) {
            cur = Math.max(a[i], cur + a[i]); best = Math.max(best, cur);
        }
        return best;
    }
}
```

## Tree + digit sketches
```java
// Tree DP: dfs(u,parent); merge child knapsacks descending k.
// Digit DP: dfs(pos,tight,sum) with memo[pos][sum] only when tight==0.
// Pitfall: memoizing tight==1 states leaks bound-specific answers.
```

## Pitfalls table
| Pitfall | Symptom | Fix |
|---|---|---|
| Forward 0/1 loop | item reused, inflated value | iterate c descending |
| Unbounded backward loop | undercount | iterate ascending |
| int overflow totals | negative answers | long + addExact |
| dp[0] wrong base | off-by-one cascade | identity base + test |
| Full 2D kept needlessly | OOM | rolling rows (value-only) |
| Reconstruction from compressed | impossible | keep parent table |
| Recursion depth (tree/chain) | StackOverflow | iterative or bigger stack |
| Tight memo leak | wrong counts | memo only tight=0 |
| Leading-zero mishandle | over/under count | explicit started flag |
| Knuth without proof | wrong opt | verify monotonicity first |

## Testing
- Fuzz knapsack vs brute force n ≤ 15, all W.
- Fuzz LCS vs brute on tiny alphabets.
- Digit DP vs brute count on X ≤ 2000.

## Performance notes
- Row-major loops for cache; int[] over List<Integer>.
- Pre-size arrays; avoid boxing in hot transitions.
- Parallelize independent test cases, not inner DP loops.

## Review checklist
- [ ] Loop directions correct. [ ] Bases tested. [ ] Fuzz green.
- [ ] Compression safe. [ ] Overflow guarded.
