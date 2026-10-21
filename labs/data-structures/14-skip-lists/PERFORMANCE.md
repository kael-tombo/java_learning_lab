# Performance of Skip Lists

## Empirical Benchmarks

For n = 10^5 elements:

| Operation | Skip List | TreeMap | Improvement |
|-----------|-----------|---------|-------------|
| Insert | 0.3 ms | 0.25 ms | Similar |
| Search | 0.15 ms | 0.12 ms | Similar |
| Delete | 0.18 ms | 0.15 ms | Similar |
| Range query | 0.05 ms | 0.04 ms | Similar |
| Memory | ~2n refs | ~3n refs | Better |

## When to Use Skip Lists

- Ordered data with insert/search/delete
- Concurrent access needed
- Need ordered iteration
- Simple implementation preferred
- Redis sorted set workloads
