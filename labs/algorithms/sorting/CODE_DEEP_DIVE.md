# CODE_DEEP_DIVE — Sorting Track
> Java implementation + pitfalls. Track `sorting`.

## Canonical: Hoare + 3-way + quickselect
```java
import java.util.concurrent.ThreadLocalRandom;
public final class Quick {
    public static void sort(int[] a) { qs(a, 0, a.length); }
    static void qs(int[] a, int lo, int hi) {
        while (hi - lo > 16) {                 // insertion cutoff
            int[] eq = partition3(a, lo, hi);  // [lt, gt) equals
            if (eq[0] - lo < hi - eq[1]) { qs(a, lo, eq[0]); lo = eq[1]; }
            else { qs(a, eq[1], hi); hi = eq[0]; }
        }
        insertion(a, lo, hi);
    }
    // returns [lt, gt): equals region
    static int[] partition3(int[] a, int lo, int hi) {
        int pivot = a[lo + ThreadLocalRandom.current().nextInt(hi - lo)];
        int lt = lo, i = lo, gt = hi;
        while (i < gt) {
            if (a[i] < pivot) { swap(a, lt++, i++); }
            else if (a[i] > pivot) { swap(a, --gt, i); }
            else i++;
        }
        return new int[]{lt, gt};
    }
    static void insertion(int[] a, int lo, int hi) {
        for (int i = lo + 1; i < hi; i++) {
            int x = a[i], j = i - 1;
            while (j >= lo && a[j] > x) { a[j + 1] = a[j]; j--; }
            a[j + 1] = x;
        }
    }
    static void swap(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }
    public static int select(int[] a, int k) {
        int lo = 0, hi = a.length;
        while (true) {
            int[] eq = partition3(a, lo, hi);
            if (k < eq[0]) hi = eq[0];
            else if (k >= eq[1]) lo = eq[1];
            else return a[k];
        }
    }
}
```

## Pitfalls table
| Pitfall | Symptom | Fix |
|---|---|---|
| Fixed pivot | O(n²) on sorted | random/median-of-3/shuffle |
| Lomuto duplicates | quadratic | 3-way partition |
| Unbounded recursion | StackOverflow | smaller-first + loop |
| No cutoff | slow tiny ranges | insertion ≤16 |
| Unstable assumed | order bugs | tie-break or stable sort |
| Comparator overflow | wrong order | Integer.compare, no subtraction |
| k unchecked | AIOOBE | range-check k |
| Shared Random contention | slowdown | ThreadLocalRandom |
| Benchmark sorted-only | false confidence | random/dupes/reverse mix |
| select mutates | caller surprise | document or copy |

## Testing
- Fuzz vs Arrays.sort on 10k arrays incl. sorted/rev/dupes/empty.
- Quickselect vs sorted[k] for random k.
- Assert stack depth O(log n) via counter on adversarial input.

## Performance notes
- Sequential scans → cache-friendly; Hoare halves swaps.
- Parallelize at ≥10k partitions via ForkJoin.
- Dual-pivot (JDK) for primitives; TimSort for objects.

## Review checklist
- [ ] Pivot randomized. [ ] 3-way regions. [ ] Fuzz green.
- [ ] Cutoff present. [ ] Depth bounded.
