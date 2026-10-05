# CODE_DEEP_DIVE — Advanced Sorting (Quick + Merge)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.*;
public final class AdvSort { // O(n log n) avg; O(n²) quick-worst
    public static void quick(int[] a) { shuffle(a); q(a, 0, a.length - 1); } // O(n log n) exp
    private static void q(int[] a, int lo, int hi) { // T(n)=T(k)+T(n-k)+O(n)
        if (lo >= hi) return;                          // O(1) base
        int p = partition(a, lo, hi);                  // O(hi-lo) scan
        q(a, lo, p - 1); q(a, p + 1, hi);              // recurse halves (avg)
    }
    private static int partition(int[] a, int lo, int hi) { // Lomuto O(n)
        int pv = a[hi], i = lo;                        // O(1)
        for (int j = lo; j < hi; j++)                  // n-1 iters
            if (a[j] < pv) swap(a, i++, j);            // O(1) each
        swap(a, i, hi); return i;                       // pivot final
    }
    public static void mergeSort(int[] a) { int[] t = new int[a.length]; m(a, t, 0, a.length); } // O(n log n), O(n) aux
    private static void m(int[] a, int[] t, int lo, int hi) { // T=2T(n/2)+O(n)
        if (hi - lo < 2) return;                        // O(1)
        int mid = (lo + hi) >>> 1;                     // O(1) overflow-safe
        m(a, t, lo, mid); m(a, t, mid, hi);            // halves
        merge(a, t, lo, mid, hi);                      // O(n) combine
    }
    private static void merge(int[] a, int[] t, int lo, int mid, int hi) {
        System.arraycopy(a, lo, t, lo, hi - lo);       // O(n) copy
        int i = lo, j = mid, k = lo;                   // O(1)
        while (i < mid && j < hi) a[k++] = t[i] <= t[j] ? t[i++] : t[j++]; // O(n)
        while (i < mid) a[k++] = t[i++];               // drain O(n)
        while (j < hi) a[k++] = t[j++];                // drain
    }
    private static void swap(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }
    private static void shuffle(int[] a) { Random r = new Random(42); for (int i = a.length - 1; i > 0; i--) swap(a, i, r.nextInt(i + 1)); } // O(n)
}
```

## 2. Complexity Annotations (per line)
- `shuffle` O(n): derandomizes worst case (prob 1/n!).
- `partition` Θ(hi-lo): single pass, O(1) extra.
- `q` avg depth O(log n) w.h.p.; worst O(n) without shuffle.
- `merge` Θ(n) time, temp array O(n) total (allocated once — amortized).
- Overall quick avg Θ(n log n) / worst Θ(n²); merge Θ(n log n) worst.

## 3. Pitfalls (5 + fixes)
1. No shuffle + sorted input → quick O(n²). Fix: shuffle or median-of-3.
2. `(lo+hi)/2` overflow → use `>>>1` / `lo+(hi-lo)/2`.
3. Lomuto worst on duplicates → 3-way partition (Dutch flag).
4. Recursing larger half first → stack O(n); recurse smaller first + tail loop → O(log n).
5. `<=` vs `<` in merge flips stability — use `<=` to keep stable.

## 4. Micro-Opts
- Insertion cutoff `n<16` inside `q`/`m` (fewer calls, better cache).
- `Arrays.sort` (TimSort) for objects; `DualPivotQuicksort` for primitives — stdlib wins.

## 5. Test Snippets
```java
int[] a = {5,2,4,6,1,3}; AdvSort.quick(a); assert Arrays.equals(a, new int[]{1,2,3,4,5,6});
int[] b = {}; AdvSort.mergeSort(b); assert b.length == 0; // empty
int[] c = {2,2,2}; AdvSort.quick(c); // duplicates
```

## 6. Checklist
- [ ] Shuffle present + commented. [ ] Cutoff noted. [ ] Stability documented.
- [ ] Sorted/reverse/duplicate benchmarks (see MINI_PROJECT).
