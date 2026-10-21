# Performance: Cassandra NoSQL

## Performance Characteristics

### Benchmark Results

| Operation | P50 Latency | P99 Latency | Throughput |
|-----------|-------------|-------------|------------|
| Single node read | 0.5ms | 2ms | 100,000+ |
| Cross-node lookup | 2ms | 15ms | 25,000 |
| Scatter-gather (4 nodes) | 8ms | 60ms | 5,000 |
| Rebalance (100GB/node) | - | - | 15 min |
| Bulk insert (10K batch) | 500ms | 2s | 20,000 |

### Bottleneck Analysis

#### 1. Network Latency
- Cross-node operations add 1-5ms per network hop
- Scatter-gather is limited by the slowest node
- Solution: Colocate related data, minimize cross-node queries

#### 2. Lock Contention
- Read-write locks serialize topology changes
- High read loads can starve writes
- Solution: Striped locks, copy-on-write for ring state

#### 3. Hash Computation
- Cryptographic hashes (SHA-256) add 1-5μs per operation
- At 100K ops/sec, this becomes 100-500ms of CPU time
- Solution: Use MurmurHash3 for non-security applications

#### 4. Serialization Overhead
- Java serialization: ~10MB/s
- JSON (Jackson): ~50MB/s
- Protocol Buffers: 200MB/s+

### Optimization Techniques

#### Algorithm Optimization
1. Cache ring state: Read-only copy with atomic swap on update
2. Lazy virtual node computation: Compute on first access
3. Bloom filters: For cross-node query pruning

#### Concurrency Optimization
1. Virtual threads (Java 21) for I/O-bound operations
2. Staged event-driven architecture
3. Batched operations for bulk processing

#### Memory Optimization
1. Object pooling to reduce GC pressure
2. Off-heap buffers for large data
3. Compact data structures (arrays over collections)

### Monitoring

#### Key Metrics
- Per-node QPS and latency percentiles
- Skew factor (data distribution balance)
- Cache hit ratio
- Connection pool utilization
- Error rate by operation type

#### Alerting Thresholds
- Skew factor > 0.3
- P99 latency > 50ms
- Error rate > 1%
- Connection pool > 80% utilization
- Any node > 70% capacity

### Scalability Testing

#### Linear Scalability Test
Start with 1 node, measure throughput. Double nodes, verify throughput doubles.
Expected: > 90% linear scaling up to 16 nodes.

#### Hotspot Test
Send 90% of traffic to 10% of keys. Measure latency degradation.
Expected: < 2x P99 latency increase under hotspot conditions.
