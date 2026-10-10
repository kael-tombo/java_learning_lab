# Math Foundation: TreeMap / TreeSet

## Red-black height bound
- Five invariants (root black, no double-red, equal black-height h on every
  root-to-leaf path) force: black-height >= height/2, and a tree of black-height
  h holds >= 2^h - 1 black nodes. So height <= 2*log2(n+1) — the whole O(log n)
  guarantee in one inequality.

## Rebalance cost is constant
- fixAfterInsertion: at most 2 rotations + O(log n) recoloring up the path.
- fixAfterDeletion: at most 3 rotations. Search dominates; balancing is cheap.

## Operation costs vs HashMap
| Op | TreeMap | HashMap |
|----|---------|---------|
| get/put/remove | O(log n) | O(1) expected |
| first/lastKey | O(log n), left/right descent | O(n) scan |
| subMap(k1,k2) | O(log n + k) | O(n) + sort |
| ordered iteration | O(n) | O(n) unordered |

## compareTo==0 vs equals
- Identity is comparison-based, not equals-based: a case-insensitive TreeSet
  treats "a" and "A" as one element. Set size then counts equivalence classes,
  and contains() can disagree with equals() — a documented SortedSet wart.

## Worked numbers
- n = 1M: height <= 2*log2(10^6+1) ~= 40 comparisons worst case per op.
- Range of k=1000 in 1M tree: ~20 down + 1000 successor steps = O(log n + k).
- Entry ~48 B (3 refs + key + val + color) vs HashMap node ~32 B + slot.

## Why sorted iteration is free
- In-order walk visits each edge twice: O(n) total for full iteration after
  one O(log n) descent to the leftmost node — no sort pass, no buffer.
- firstKey/lastKey never scan: one root-to-leaf descent each, O(log n), versus
  HashMap's O(n) scan for min/max. That descent is the feature the class sells.
