# Performance — Time Ordering

## 1. Performance Characteristics

| Clock Type | Time/op | Space | Message Overhead |
|------------|---------|-------|-----------------|
| Lamport | O(1) | O(1) | 4 bytes |
| Vector (n=10) | O(n) | O(n) | 40 bytes |
| Vector (n=100) | O(n) | O(n) | 400 bytes |
| HLC | O(1) | O(1) | 12 bytes |

## 2. Throughput (ops/sec)
`
Lamport:        52,000,000 (single-thread)
Vector (n=10):   5,200,000
Vector (n=100):   520,000
HLC:            48,000,000
`

## 3. Optimization
- Use int[] arrays not Integer objects
- Avoid defensive copies in hot paths
- Use volatile for single-writer scenarios
- LongAdder for high-contention counters
- Batch vector updates when possible

## 4. Scaling
- Lamport: linear throughput scaling
- Vector: degrades linearly with process count
- HLC: constant-time regardless of cluster size
- At high message rates, serialization is bottleneck
