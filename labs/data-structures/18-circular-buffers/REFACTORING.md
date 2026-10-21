# Refactoring

1. Power-of-2 capacity for fast modulo
2. Lock-free for SPSC using volatile
3. Cache-line padding to avoid false sharing
4. Batch read/write for throughput
5. Add memory-mapped persistence
6. Implement as Disruptor-style ring buffer
