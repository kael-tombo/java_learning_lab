# Math Foundation of Concurrent Data Structures

## Progress Conditions

1. **Wait-Free**: Every thread completes in finite steps (strongest)
2. **Lock-Free**: Some thread always makes progress
3. **Obstruction-Free**: A thread makes progress if run in isolation

## Contention Analysis

Throughput under contention:
- Lock-based: degrades as threads increase (context switching)
- Lock-free: scales better with thread count (no context switching)

## Amdahl's Law

Speedup = 1 / ((1-P) + P/N)
- P = parallel portion
- N = number of processors
- Concurrent data structures maximize P by minimizing serialization
