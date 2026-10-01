# Exercises — Linear Searching

1. **Basic scan** — Implement `int linearSearch(int[] a, int target)` returning the first index or -1. Test on `{4,2,7,1,9}`, target 1 and 42.
2. **Count comparisons** — Instrument your scan to return the comparison count. Verify average ≈ n/2 over all present targets in a 100-element array.
3. **Sentinel version** — Implement sentinel linear search (save last element, overwrite with target, scan without bounds check, restore). Benchmark vs plain loop on 1M elements.
4. **Peak by scan** — Implement O(n) peak finding (return any `i` with `a[i] >` neighbors, edges compare one neighbor). Compare result with the `FindPeakElement` binary search in LEETCODE_SOLUTION.md on `{1,2,1,3,5,6,4}`.
5. **When-linear-wins analysis** — Time `Arrays.sort` + `Arrays.binarySearch` vs plain linear scan for a single query on n = 100, 10_000, 1_000_000 random ints. Write a 5-line conclusion stating the crossover point on your machine.
