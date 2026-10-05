# EXERCISES — Sorting Track
> Implement + trace + edge cases (Java templates). Track `sorting`.

## E1. Hoare quicksort (smaller-first recursion)
```java
import java.util.concurrent.ThreadLocalRandom;
public class E1 {
    public static void sort(int[] a) { qs(a, 0, a.length); }
    static void qs(int[] a, int lo, int hi) {
        while (hi - lo > 1) {
            int p = partition(a, lo, hi);
            if (p - lo < hi - p) { qs(a, lo, p); lo = p; }
            else { qs(a, p, hi); hi = p; }
        }
    }
    static int partition(int[] a, int lo, int hi) {
        int pivot = a[lo + ThreadLocalRandom.current().nextInt(hi - lo)];
        int i = lo - 1, j = hi;
        while (true) {
            do i++; while (a[i] < pivot);
            do j--; while (a[j] > pivot);
            if (i >= j) return j + 1;
            int t = a[i]; a[i] = a[j]; a[j] = t;
        }
    }
}
```
- Trace: [5,1,4,2,3]. Edge: sorted, reverse, all equal, empty.

## E2. 3-way Dutch-flag
```java
public class E2 {
    // TODO: lt/lo, i, gt/hi regions; <p swap front; >p swap back
    // Edge: all-equal O(n); two values; single distinct
}
```

## E3. Quickselect kth smallest
```java
public class E3 {
    // TODO: partition; recurse side with k; median-of-3 + cutoff to insertion
    // Edge: k=0/min, k=n-1/max, duplicates
}
```

## E4. Insertion cutoff + shuffling
```java
public class E4 {
    // TODO: cutoff ~8-16 to insertion sort; pre-shuffle or random pivot
    // Edge: tiny n, nearly sorted (cutoff still helps)
}
```

## E5. Stability/secondary-key exercise
```java
public class E5 {
    // TODO: show quicksort instability on (key,id) pairs; fix via comparator tie-break
    // Edge: all keys equal (3-way shines)
}
```

## E6. Fuzz harness
```java
import java.util.*;
public class E6 {
    // TODO: 10k random arrays (sorted/rev/dupes); assert vs Arrays.sort
    // TODO: quickselect vs sorted[k]
}
```

## Edge-case checklist
- [ ] Empty/singleton. [ ] All equal. [ ] Sorted/reverse.
- [ ] Duplicates heavy. [ ] Stack bound.

## Trace template
| step | state | decision | invariant holds? |
|---|---|---|---|
| 1 | init | base | yes |

## Review rubric
- [ ] All 6 compile + pass fixtures. [ ] Trace tables filled.
- [ ] Complexity stated per exercise. [ ] One pitfall noted each.
