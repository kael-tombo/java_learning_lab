# Architecture

Sparse tables are typically used as a component within larger systems:
`
QueryProcessor
  → SparseTable (static data)
  → SegmentTree (dynamic data)
  → CacheLayer (LRU for hot ranges)
`

Design decisions:
- Use sparse table when data is static and queries are frequent
- Combine with segment tree for data that has both static and dynamic portions
- Use disjoint sparse table for non-idempotent operations on static data
