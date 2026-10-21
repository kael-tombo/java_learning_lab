# Performance — Distributed Monitoring

## Storage Requirements
| Resolution | Retention | Storage per metric |
|------------|-----------|-------------------|
| 15s | 30 days | ~170KB |
| 5min | 6 months | ~50KB |
| 1hour | 3 years | ~25KB |

## Query Performance
| Data size | Prometheus | Thanos | Cortex |
|-----------|-----------|--------|--------|
| 1M series | < 1s | < 1s | < 1s |
| 10M series | 3-5s | 2-4s | 2-3s |
| 100M series | N/A | 10-15s | 8-12s |

## Ingestion Rate
- Single Prometheus: ~1M samples/sec
- Thanos: limited by object store throughput
- Cortex: horizontally scalable ingesters
- OTel Collector: 100K-500K spans/sec per instance
