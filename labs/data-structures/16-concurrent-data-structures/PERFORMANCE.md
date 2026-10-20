# Performance of Concurrent Data Structures

## Empirical Benchmarks

| Structure | 1 Thread | 4 Threads | 8 Threads |
|-----------|----------|-----------|-----------|
| LockFreeStack | 10M ops/s | 35M ops/s | 60M ops/s |
| SynchronizedStack | 8M ops/s | 8M ops/s | 8M ops/s |
| ConcurrentLinkedQueue | 12M ops/s | 40M ops/s | 70M ops/s |

## Key Insights

- Lock-free structures scale near-linearly with cores
- Lock-based structures bottleneck at lock contention
- CAS operations cost ~10ns on modern hardware
- Context switching costs ~1-10μs
