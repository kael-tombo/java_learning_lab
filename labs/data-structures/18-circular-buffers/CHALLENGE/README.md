# Challenge: Lock-Free Ring Buffer

Implement a lock-free single-producer single-consumer (SPSC) ring buffer.
- No locks, only volatile/atomic
- Memory barrier management
- Cache-line padding for performance
- Benchmark against lock-based version
