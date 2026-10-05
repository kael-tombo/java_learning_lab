# CODE_DEEP_DIVE — Sorting & Searching Deep Track
> Java implementation + pitfalls. Track `sorting-searching-deep`.

## Canonical: 3-way quick + lowerBound + KMP
```java
import java.util.concurrent.ThreadLocalRandom;
public final class SortSearch {
    public static void quick3(int[] a) { qs(a, 0, a.length); }
    static void qs(int[] a, int lo, int hi) {
        while (hi - lo > 16) {
            int p = a[lo + ThreadLocalRandom.current().nextInt(hi - lo)];
            int lt = lo, i = lo, gt = hi;
            while (i < gt) {
                if (a[i] < p) { int t = a[lt]; a[lt++] = a[i]; a[i++] = t; }
                else if (a[i] > p) { int t = a[--gt]; a[gt] = a[i]; a[i] = t; }
                else i++;
            }
            if (lt - lo < hi - gt) { qs(a, lo, lt); lo = gt; }
            else { qs(a, gt, hi); hi = lt; }
        }
        for (int k = lo + 1; k < hi; k++) {
            int x = a[k], j = k - 1;
            while (j >= lo && a[j] > x) { a[j + 1] = a[j]; j--; }
            a[j + 1] = x;
        }
    }
    public static int lowerBound(int[] a, int x) {
        int lo = 0, hi = a.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (a[mid] < x) lo = mid + 1; else hi = mid;
        }
        return lo;
    }
    public static int[] prefix(String p) {
        int[] pi = new int[p.length()];
        for (int i = 1; i < p.length(); i++) {
            int j = pi[i - 1];
            while (j > 0 && p.charAt(i) != p.charAt(j)) j = pi[j - 1];
            if (p.charAt(i) == p.charAt(j)) j++;
            pi[i] = j;
        }
        return pi;
    }
}
```

## Pitfalls table
| Pitfall | Symptom | Fix |
|---|---|---|
| Fixed pivot | O(n²) sorted | random/median-3 |
| Lomuto dupes | quadratic | 3-way regions |
| Overflow mid | negative index | >>>1 |
| Closed intervals | ±1 bugs | half-open [lo,hi) |
| Unstable assumed | order bugs | tie-break/stable sort |
| KMP fallback wrong | missed matches | pi[j-1] loop |
| RK no verify | false positives | compare on hit |
| Empty pattern | crash | define: match at 0 |
| k range unchecked | AIOOBE | validate select k |
| Counting k huge | OOM | reject/radix fallback |

## Testing
- Fuzz sorts vs Arrays.sort; bounds vs linear scan; KMP vs indexOf loop.
- Adversarial: sorted/reverse/dupes/organ-pipe/empty.
- Benchmark 1k→10M; record cache/branch effects.

## Performance notes
- 3-way + cutoff + smaller-first is the production default.
- Static sorted arrays: Eytzinger for search-heavy loads.
- Parallel sorts at ≥10k via ForkJoin/Arrays.parallelSort.

## Review checklist
- [ ] Pivot randomized. [ ] Mid safe. [ ] Fuzz green.
- [ ] KMP fallback loop. [ ] Stability decision explicit.
