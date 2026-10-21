# Performance — Distributed Caching

## Latency (p99)
| Operation | Local | Redis (net) | Memcached (net) |
|-----------|-------|-------------|-----------------|
| Get | 0.01ms | 1-3ms | 1-3ms |
| Put | 0.01ms | 1-3ms | 1-3ms |
| Delete | 0.01ms | 1-2ms | 1-2ms |

## Throughput (single node)
- Redis: 100K-200K ops/sec
- Memcached: 200K-500K ops/sec
- Local cache: 10M+ ops/sec

## Cache Sizing Guide
| Workload | Cache Size | Hit Rate |
|----------|-----------|----------|
| Read-heavy (90:10) | 20% of DB | ~95% |
| Write-heavy (50:50) | 10% of DB | ~80% |
| Balanced | 15% of DB | ~90% |
