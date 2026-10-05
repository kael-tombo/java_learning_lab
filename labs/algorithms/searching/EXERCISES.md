# EXERCISES — Searching Track
> Implement + trace + edge cases (Java templates). Track `searching`.

## E1. lowerBound / upperBound (half-open)
```java
public class E1 {
    // first i with a[i] >= x in [0,n]
    public static int lowerBound(int[] a, int x) {
        int lo = 0, hi = a.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (a[mid] < x) lo = mid + 1; else hi = mid;
        }
        return lo;
    }
    // TODO: upperBound (first > x); exact hit = lb if a[lb]==x
}
```
- Trace: a=[1,2,2,5], x=2. Edge: empty, all-less, all-greater, duplicates.

## E2. Rotated array search
```java
public class E2 {
    // TODO: while lo<hi: if a[mid] vs a[hi-1] decide sorted half; test membership
    // Edge: no rotation, n=1, duplicates (shrink hi on tie)
}
```

## E3. Peak element
```java
public class E3 {
    // TODO: if a[mid] < a[mid+1] lo=mid+1 else hi=mid; return lo
    // Edge: strictly increasing/decreasing, n=1
}
```

## E4. Answer-search (ship capacity / koko)
```java
public class E4 {
    // TODO: lo=max, hi=sum; predicate fits(cap); binary search first true
    // Edge: single pile, huge values (long sums)
}
```

## E5. Exponential + interpolation
```java
public class E5 {
    // TODO: exponential probe bound, then binary within [b/2, min(b,n))
    // TODO: interpolation mid = lo + (x-a[lo])*(hi-lo)/(a[hi]-a[lo])
    // Edge: unbounded/streaming, uniform vs skewed data
}
```

## E6. Fuzz harness
```java
import java.util.*;
public class E6 {
    // TODO: 10k random sorted arrays; assert lb/ub vs linear scan
    // TODO: rotated + peak fuzz vs brute
}
```

## Edge-case checklist
- [ ] Empty/singleton. [ ] Duplicates. [ ] Overflow-safe mid.
- [ ] Predicate monotonic proof. [ ] long sums.

## Trace template
| step | state | decision | invariant holds? |
|---|---|---|---|
| 1 | init | base | yes |

## Review rubric
- [ ] All 6 compile + pass fixtures. [ ] Trace tables filled.
- [ ] Complexity stated per exercise. [ ] One pitfall noted each.
