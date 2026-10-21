# Performance — Distributed Queues

## Throughput (messages/sec)
| System | Single partition | 10 partitions | 100 partitions |
|--------|-----------------|---------------|----------------|
| In-memory | 1M/s | 10M/s | 50M/s |
| Pulsar | 100K/s | 1M/s | 10M/s |
| SQS | 10K/s | 100K/s | N/A (auto-scale) |

## Latency (p99)
| System | Without load | Under load (90%) |
|--------|-------------|------------------|
| In-memory | 0.1ms | 1ms |
| Pulsar | 5ms | 50ms |
| SQS | 20ms | 200ms |

## Scaling
- Partitions increase parallelism, not latency
- More consumers than partitions wastes resources
- Pulsar supports dynamic topic partitioning (split)
