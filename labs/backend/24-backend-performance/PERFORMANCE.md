# Performance: Performance Optimization (Meta!)

Key metrics to measure:
- p50/p95/p99 latency
- Throughput (requests/second)
- Error rate
- GC pause time and frequency
- Connection pool utilization
- Cache hit ratio
- CPU/memory/disk/network utilization

Optimization priorities:
1. Database queries (most common bottleneck)
2. Network calls (external API latency)
3. Serialization/deserialization
4. Logging I/O
5. GC overhead
