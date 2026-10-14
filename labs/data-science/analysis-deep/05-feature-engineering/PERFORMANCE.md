# Feature Engineering - Performance Notes

## Complexity (n rows, d features, L levels, w hash width)

- One-hot: O(n) apply, O(n x active) memory sparse (dense O(n x L) - avoid
  dense past dozens of levels).
- Ordinal/target lookup: O(n) average via hashmap, O(L) memory.
- Hashing: O(n) time, O(w) memory, no vocabulary - the scaling winner for
  open vocabularies.
- Scaling/transforms/interactions: O(n x d) time, O(1) extra; single fused
  pass over row arrays.

## Memory shape

Fit accumulators are O(d): sums, counts, per-level sums for target means
(O(L)). Apply streams row-by-row: O(1) working memory. One-hot dense output
is the memory cliff (n x L doubles); keep it sparse or hashed past small L.

## JDK-specific guidance

- `HashMap<String,Integer>` vocabularies beat `List.indexOf` past ~50
  levels; size with expected L to avoid rehashing.
- Fuse per-row transforms (log, product, scale) in one loop pass over
  primitive arrays - fewer passes, better cache behavior.
- `Math.log` is the costliest op here; batch transforms before scaling so
  each value is logged once, then reused.
- Store fitted constants in plain `double` fields of a small holder object:
  no boxing in the apply hot loop.

## Scaling without libraries

Partition by rows for apply (embarrassingly parallel); fit reductions
(sums, per-level sums) via map-reduce over partitions. The parameter object
is the only cross-partition traffic - tiny by design.

## What is NOT claimed here

No throughput numbers: hashing vs lookup speed depends on hardware and key
distribution. The complexities above size the work; benchmark your own
vocabulary sizes.
