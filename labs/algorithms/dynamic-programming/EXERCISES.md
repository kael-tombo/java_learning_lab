# EXERCISES — Dynamic Programming Track
> Implement + trace + edge cases (Java templates). Track `dynamic-programming`.

## E1. Memoized fib
```java
import java.util.*;
public class E1 {
    static Map<Integer, Long> memo = new HashMap<>();
    public static long fib(int n) {
        if (n <= 1) return n;
        return memo.computeIfAbsent(n, k -> fib(k - 1) + fib(k - 2));
    }
}
```
- Trace: fib(5) hits/misses. Edge: n=0, negative (reject), overflow at n≈93.

## E2. Grid paths memoized
```java
public class E2 {
    // TODO: f(i,j) with obstacles; memo[i][j] = -1 unknown
    // Edge: blocked start/end, 1×N grid
}
```

## E3. Coin change (min coins + count ways)
```java
public class E3 {
    // TODO: minCoins memoized; ways with coin-order to avoid dupes
    // Edge: amount=0 (0 coins, 1 way), impossible => -1
}
```

## E4. Climbing stairs + house robber
```java
public class E4 {
    // TODO: f(n)=f(n-1)+f(n-2); robber cur=max(prev, prevPrev+x)
    // Edge: single house, all zeros
}
```

## E5. Memo → tabulation conversion
```java
public class E5 {
    // TODO: rewrite E2 bottom-up; then 1D compression; assert equal on fuzz
    // Edge: dimension swap correctness
}
```

## E6. Reconstruction (one optimal path)
```java
public class E6 {
    // TODO: parent pointers during tabulation; walk back from goal
    // Edge: ties (any valid), unreachable goal
}
```

## Edge-case checklist
- [ ] Base cases first. [ ] Memo key complete (all varying params).
- [ ] long for counts. [ ] Depth guard.

## Trace template
| step | state | decision | invariant holds? |
|---|---|---|---|
| 1 | init | base | yes |

## Review rubric
- [ ] All 6 compile + pass fixtures. [ ] Trace tables filled.
- [ ] Complexity stated per exercise. [ ] One pitfall noted each.
