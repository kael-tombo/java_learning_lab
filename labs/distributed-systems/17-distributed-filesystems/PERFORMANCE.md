# Performance — Distributed Filesystems

## Throughput (sequential reads)
| System | Single thread | Parallel (10 threads) |
|--------|--------------|----------------------|
| HDFS | 100MB/s | 500MB/s |
| Ceph | 200MB/s | 1GB/s |
| MinIO | 500MB/s | 3GB/s |
| Local disk | 500MB/s | 500MB/s |

## Latency
| Operation | HDFS | Ceph | MinIO |
|-----------|------|------|-------|
| Read (4KB) | 10ms | 5ms | 3ms |
| Write (4KB) | 15ms | 8ms | 5ms |
| List (1000) | 50ms | 20ms | 30ms |

## Scalability
- HDFS: ~10,000 nodes, 100PB
- Ceph: ~10,000 OSDs, exabyte scale
- MinIO: ~100s nodes, petabyte scale
