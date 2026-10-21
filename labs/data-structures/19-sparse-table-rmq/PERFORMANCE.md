# Performance

| n | Preprocess | Query (min) | Memory |
|---|-----------|-------------|--------|
| 10^3 | 10μs | 50ns | 40KB |
| 10^5 | 2ms | 50ns | 4MB |
| 10^6 | 30ms | 50ns | 80MB |
| 10^7 | 400ms | 50ns | 1.6GB |

Segment tree query for comparison: ~200ns
Sparse table is ~4x faster for queries but uses more memory.
