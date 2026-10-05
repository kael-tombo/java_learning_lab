# CODE_DEEP_DIVE — Divide and Conquer (Merge/Count + Power)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
public final class DC { // merge T=2T(n/2)+O(n) → O(n log n); pow O(log n)
    public static long inversions(int[] a) { // Θ(n log n) counting
        int[] t = new int[a.length];         // O(n) buffer once
        return sortCount(a, t, 0, a.length); // O(n log n)
    }
    private static long sortCount(int[] a, int[] t, int lo, int hi) { // recurrence core
        if (hi - lo < 2) return 0;           // O(1) base
        int mid = (lo + hi) >>> 1;           // O(1)
        long c = sortCount(a, t, lo, mid) + sortCount(a, t, mid, hi); // 2T(n/2)
        return c + mergeCount(a, t, lo, mid, hi); // +Θ(n)
    }
    private static long mergeCount(int[] a, int[] t, int lo, int mid, int hi) { // Θ(n)
        System.arraycopy(a, lo, t, lo, hi - lo); // O(n)
        int i = lo, j = mid, k = lo; long inv = 0; // O(1)
        while (i < mid && j < hi)        // O(n)
            if (t[i] <= t[j]) a[k++] = t[i++]; // O(1)
            else { a[k++] = t[j++]; inv += mid - i; } // cross inversions
        while (i < mid) a[k++] = t[i++]; // drain
        while (j < hi) a[k++] = t[j++];  // drain
        return inv;                      // O(1)
    }
    public static long pow(long x, long e) { // T(e)=T(e/2)+O(1) → O(log e)
        if (e == 0) return 1;                // O(1)
        long h = pow(x, e / 2);              // halve
        long r = h * h;                      // O(1)
        return (e % 2 == 0) ? r : r * x;     // O(1)
    }
}
```

## 2. Complexity Annotations
- `sortCount`: per level n work × log n levels; buffer reused (not per call).
- Cross term `mid−i` counts all skipped left elements (sorted halves invariant).
- `pow`: halving + O(1) combine; iterative avoids depth log e anyway.

## 3. Pitfalls (5 + fixes)
1. Buffer per recursion → O(n log n) space. Fix: allocate once, pass down.
2. `<=` vs `<` changes inversion definition → document pairs counted.
3. `int` inversion count overflows (n=10⁵ → ~5·10⁹) → long.
4. `(lo+hi)/2` overflow → `>>>1`.
5. `pow` negative exponent → define throw or inverse (document).

## 4. Micro-Opts
- Insertion cutoff n<32 skips recursion; parallel halves via ForkJoin (span log²n).

## 5. Test Snippets
```java
assert DC.inversions(new int[]{2,3,8,6,1}) == 5;
assert DC.pow(2, 10) == 1024;
```

## 6. Checklist
- [ ] Buffer-once. [ ] long counts. [ ] Cutoff noted.
