# Performance

## Persistent vs Mutable

| Operation | Mutable ArrayList | Persistent List |
|-----------|------------------|-----------------|
| Add | O(1) amortized | O(1) |
| Get by index | O(1) | O(n) |
| Iterate all | O(n) | O(n) |
| Thread safety | Requires sync | Inherently safe |

## Benchmark (10^6 operations)

| Structure | Time | Memory |
|-----------|------|--------|
| ArrayList | 20ms | 8MB |
| PersistentList | 30ms | 16MB (with sharing) |
| Copy on write | 500ms | 80MB (no sharing) |

Structural sharing makes persistent structures memory-efficient.
