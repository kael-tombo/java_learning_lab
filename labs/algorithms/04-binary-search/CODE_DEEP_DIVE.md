# CODE_DEEP_DIVE — Binary Search
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.*;
public final class BinarySearch { // O(log n) time, O(1) space iterative
    public static int search(int[] a, int key) { // half-open [lo,hi)
        int lo = 0, hi = a.length;               // O(1) init; invariant: key in [lo,hi) if present
        while (lo < hi) {                        // ≤ ⌊log n⌋+1 iters
            int mid = (lo + hi) >>> 1;           // O(1) overflow-safe
            if (a[mid] == key) return mid;       // hit
            else if (a[mid] < key) lo = mid + 1; // discard left (sortedness)
            else hi = mid;                       // discard right
        }
        return -(lo + 1);                        // miss: insertion encoding (Arrays parity)
    }
    public static <T> int search(T[] a, T key, Comparator<? super T> c) { // generic O(log n) probes
        int lo = 0, hi = a.length;               // O(1)
        while (lo < hi) {                        // O(log n)
            int mid = (lo + hi) >>> 1;           // O(1)
            int cmp = c.compare(a[mid], key);    // O(1) comparator cost × probes
            if (cmp == 0) return mid;            // O(1)
            else if (cmp < 0) lo = mid + 1;      // O(1)
            else hi = mid;                       // O(1)
        }
        return -(lo + 1);                        // O(1)
    }
    public static int lowerBound(int[] a, int key) { // first ≥ key; no early return
        int lo = 0, hi = a.length;               // O(1)
        while (lo < hi) { int mid = (lo + hi) >>> 1; if (a[mid] < key) lo = mid + 1; else hi = mid; }
        return lo;                               // O(log n)
    }
}
```

## 2. Complexity Annotations
- Recurrence `T(n)=T(n/2)+O(1)` → Θ(log n); space O(1) iterative.
- Comparator version multiplies probe cost: `O(log n × cmp)`.
- `lowerBound` same bound, returns first-hit (duplicates-safe).

## 3. Pitfalls (5 + fixes)
1. `(lo+hi)/2` overflows → `>>>1` / `lo+(hi-lo)/2`.
2. Closed `[lo,hi]` + `mid±1` off-by-one → half-open preferred.
3. Unsorted input → silent wrong answer; assert sorted in tests.
4. Comparator ≠ sort order → same class of bug; reuse one comparator.
5. Any-hit vs first-hit confusion → specify; use lowerBound for first.

## 4. Micro-Opts
- Branchless probe for huge arrays (rare); branch prediction usually fine.
- `Arrays.binarySearch` for stdlib parity (same miss encoding).

## 5. Test Snippets
```java
assert BinarySearch.search(new int[]{1,3,5,7,9}, 7) == 3;
assert BinarySearch.search(new int[]{}, 1) < 0; // empty miss
assert BinarySearch.lowerBound(new int[]{2,2,2,2}, 2) == 0; // duplicates
assert BinarySearch.search(new int[]{1,3,5}, 6) == -4; // insert 3
```

## 6. Checklist
- [ ] Overflow-safe mid. [ ] Half-open + miss encoding. [ ] Duplicate policy tested.
- [ ] Sorted precondition asserted.
