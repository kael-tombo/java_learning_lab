# Performance — Distributed Locks

## Latency (p99, ms)
| Provider | Lock | Unlock | Notes |
|----------|------|--------|-------|
| Redis (local) | 0.5 | 0.3 | In-memory |
| Redis (network) | 3 | 2 | 1ms RTT |
| ZooKeeper | 8 | 5 | Majority write |
| Etcd | 6 | 4 | Raft commit |

## Throughput (ops/sec)
- Redis: 200,000 locks/sec
- ZooKeeper: 50,000 locks/sec
- Etcd: 80,000 locks/sec

## Bottlenecks
- Network round-trips (primary cost)
- Consensus protocol overhead (ZK/Etcd)
- Lock contention at high concurrency
