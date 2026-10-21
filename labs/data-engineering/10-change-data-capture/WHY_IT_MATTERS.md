# Why CDC Matters

## Business Impact
- **Real-time**: Sub-second data freshness from source systems
- **Zero Impact**: No load on production databases
- **Complete**: Captures all changes including deletes
- **Reliable**: Exactly-once semantics via Kafka

## Use Cases That Require CDC
| Use Case | Latency Required | CDC Solution |
|----------|-----------------|--------------|
| Real-time analytics | <1 second | Debezium + Kafka |
| Cache invalidation | Milliseconds | Debezium + Kafka Streams |
| Database migration | Minutes | Debezium snapshot + streaming |
| Search indexing | Seconds | Debezium + Elasticsearch sink |
| Audit logging | Seconds | Debezium + S3 sink |

## Key Benefits
- 100x lower latency than batch ETL
- No schema changes required on source
- Captures deletes (impossible with timestamp queries)
- Schema history maintained
