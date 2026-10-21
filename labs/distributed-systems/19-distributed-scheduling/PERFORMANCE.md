# Performance — Distributed Scheduling

## Scheduling Overhead
| Operation | Latency |
|-----------|---------|
| Cron evaluation | < 0.1ms |
| Job store save | 5-10ms (DB) |
| Leader election | 50-200ms |
| Partition rebalance | 100-500ms |

## Scalability
| Nodes | Jobs | Schedule precision |
|-------|------|-------------------|
| 1 | 1000 | < 1s |
| 3 | 10,000 | < 2s |
| 10 | 100,000 | < 5s |

## Bottlenecks
- Database writes (job store operations)
- Leader election (consensus overhead)
- Job startup time (JVM warmup, class loading)
- Cron evaluation for complex expressions
