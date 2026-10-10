# Math Foundation: HashMap Internals

## Position arithmetic
- Rule: spreader `h ^ (h >>> 16)` folds high bits down. Masking with `(n-1)` is valid only because capacity stays
  a power of two (array-hashed variants); linked/sorted variants replace the
  mask with a midpoint comparison or key comparison.

## Load and growth
- default capacity 16, load factor 0.75; resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0.
- Amortized put/add is O(1): total copy work over n inserts is the geometric
  series n + n/r + n/r^2 + ... = n·r/(r-1) = O(n) for growth ratio r
  (r=2 hash tables, r=1.5 ArrayList ≈ 3n moves).

## Height / chain bounds
- TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64. Below the treeify threshold, worst-case chain length is O(n);
  above it (tables >= 64), red-black bins cap the per-bucket cost at
  O(log n) with height <= 2·log2(n+1). Sorted trees guarantee O(log n)
  per op by the same bound. Linked index walks cost floor(n/2) comparisons.

## Expected vs worst case
| Case | Hash path | List index | Tree path |
|------|-----------|------------|-----------|
| get (avg) | O(1) | O(n/4) avg walk | O(log n) |
| get (worst) | O(log n) treeified | O(n/2) | O(log n) |
| put amortized | O(1) | O(n/2)+O(1) | O(log n) |

## Worked numbers
- 1M entries, load 0.75: table ~2^21 (2,097,152), mean chain ~0.5.
- 1M-entry ArrayList at 1.5x: ~log_{1.5}(1M/10) ≈ 28 grows, ~3M moves total.
- 1M-node red-black tree: height <= 2·log2(1M) ≈ 40 comparisons worst case.
