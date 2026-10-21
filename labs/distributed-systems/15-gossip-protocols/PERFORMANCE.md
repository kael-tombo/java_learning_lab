# Performance — Gossip Protocols

## Convergence Time
| N (nodes) | Fan-out | Rounds | Time (100ms/round) |
|-----------|---------|--------|-------------------|
| 100 | 3 | 5 | 500ms |
| 1,000 | 3 | 7 | 700ms |
| 10,000 | 3 | 9 | 900ms |
| 100,000 | 3 | 11 | 1.1s |
| 1,000,000 | 3 | 13 | 1.3s |

## Bandwidth
- Per round: f * message_size bytes per node
- With f=3, msg=1KB: 3KB/round/node
- For 1000 nodes: 3MB total per round

## Memory
- Member list: N * sizeof(member) bytes
- Message store: configured retention
- Typically < 100MB for 10,000 nodes
