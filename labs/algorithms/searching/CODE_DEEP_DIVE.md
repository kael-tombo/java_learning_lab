# CODE_DEEP_DIVE — Searching Track
> Java implementation + pitfalls. Track `searching`.

## Canonical: bounds + rotated + peak + answer-search
```java
public final class Search {
    public static int lowerBound(int[] a, int x) {
        int lo = 0, hi = a.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;   // overflow-safe
            if (a[mid] < x) lo = mid + 1; else hi = mid;
        }
        return lo;
    }
    public static int upperBound(int[] a, int x) {
        int lo = 0, hi = a.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (a[mid] <= x) lo = mid + 1; else hi = mid;
        }
        return lo;
    }
    public static int rotated(int[] a, int x) {
        int lo = 0, hi = a.length - 1;
        while (lo <= hi) {
            int mid = (lo + hi) >>> 1;
            if (a[mid] == x) return mid;
            if (a[lo] <= a[mid]) {                    // left sorted
                if (a[lo] <= x && x < a[mid]) hi = mid - 1;
                else lo = mid + 1;
            } else {                                  // right sorted
                if (a[mid] < x && x <= a[hi]) lo = mid + 1;
                else hi = mid - 1;
            }
        }
        return -1;
    }
    public static int peak(int[] a) {
        int lo = 0, hi = a.length - 1;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (a[mid] < a[mid + 1]) lo = mid + 1; else hi = mid;
        }
        return lo;
    }
}
```

## Pitfalls table
| Pitfall | Symptom | Fix |
|---|---|---|
| (lo+hi)/2 overflow | negative mid, AIOOBE | >>>1 shift |
| Closed-interval ±1 | missed ends/infinite | half-open discipline |
| mid never advances | infinite loop | ensure lo or hi moves past mid |
| Unsorted input | wrong answer | validate or sort first |
| Rotated duplicates | wrong half | shrink hi on a[lo]==a[mid] |
| Predicate not monotonic | garbage bound | prove + unit-test predicate |
| long sums in int | overflow capacity | long lo/hi/sums |
| Arrays.binarySearch misuse | misread negative | insertion point = -(r)-1 |
| NaN doubles | unordered | avoid or total-order comparator |
| Recursive depth worry | frames (minor) | iterative version |

## Testing
- Fuzz bounds vs linear scan, 10k random arrays (empty/dupes/extremes).
- Fuzz rotated vs linear indexOf; peak: verify a[p] ≥ neighbors.
- Answer-search: brute predicate over small ranges.

## Performance notes
- Binary jumps are cache-hostile; Eytzinger layout for huge static arrays.
- Interpolation for uniform; branchless mid for tight loops.
- Batch: sort once, then q×log n queries.

## Review checklist
- [ ] Mid overflow-safe. [ ] Interval discipline. [ ] Fuzz green.
- [ ] Predicate proved. [ ] Contract of binarySearch respected.
