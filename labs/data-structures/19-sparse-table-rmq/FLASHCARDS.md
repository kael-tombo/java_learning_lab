## Front: What is a sparse table?
Back: Precomputed table for O(1) range queries on static arrays. O(n log n) space.

## Front: What operations support O(1) sparse table queries?
Back: Idempotent operations (min, max, gcd). Non-idempotent sum: O(log n).

## Front: What is the disjoint sparse table?
Back: Variant supporting non-idempotent operations in O(1) using prefix/suffix blocks.

## Front: When should you use a sparse table vs segment tree?
Back: Sparse table: static data, O(1) queries, many queries. Segment tree: dynamic updates.
