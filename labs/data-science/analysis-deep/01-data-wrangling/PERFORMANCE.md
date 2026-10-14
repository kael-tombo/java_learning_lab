# Data Wrangling - Performance Notes

## Complexity per stage (n rows, u unique keys)

- Profiling and missing counts: O(n) time, O(1) extra space.
- Coercion: O(n x L) for max field length L; one exception object per
  reject, so pathological all-reject columns pay allocation cost.
- Dedup: O(n) average time with hashing, O(u) key memory.
- Mean/mode fill: O(n) time. Median fill: O(n log n) for the sort plus an
  O(n) copy when the input must stay unmutated.
- Quartiles: dominated by the same O(n log n) sort.

## Memory shape

Streaming line-by-line keeps O(1) row memory for profiling, coercion, and
dedup-key hashing (keys only). Sorting for median/quartiles needs the full
column in memory: O(n) doubles. On the lab's tiny arrays none of this
matters; the shapes matter when n reaches millions.

## JDK-specific guidance

- Reuse one `StringBuilder` or pre-sized structures in hot loops instead of
  concatenating keys per row.
- Prefer `Arrays.sort` on primitive `double[]` (dual-pivot quicksort, fast
  and in-place) over boxing into `List<Double>` and `Collections.sort`.
- `LinkedHashMap` costs marginally more than `HashMap` per entry; pay it
  only where output order stability is required.
- Exceptions are for rejects, not flow control on mostly-bad data: if over
  half a column rejects, pre-validate characters before `parseDouble`.

## Scaling without libraries

Partition by key hash for parallel dedup (per-partition maps, then merge),
and use single-pass mean/variance accumulation for profiling. Exact median
and quartiles still need the sort; that is the stage to sample or to replace
with a sketch only when exactness is explicitly waived.

## What is NOT claimed here

No wall-clock timings appear because they depend on hardware and JVM flags.
Size the stages by the complexities above and measure on your own workload.
