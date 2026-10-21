# CDC Interview Questions

## Beginner
**Q**: What is CDC and why is it useful?
**A**: CDC captures database changes in real-time. It's useful for real-time analytics, cache invalidation, database migrations, and maintaining search indexes with minimal source impact.

## Intermediate
**Q**: Compare log-based CDC with query-based CDC.
**A**: Log-based reads the database transaction log - no source impact, captures all operations (including deletes), sub-second latency. Query-based checks timestamp columns - simpler but higher latency, can't capture deletes, and puts load on the source.

## Advanced
**Q**: Design a CDC pipeline from multiple databases to a data lake.
**A**: Use Debezium connectors for each database type (MySQL/postgres), stream to Kafka topics (one per table), use Kafka Connect S3 sink with Parquet format for the data lake, and Kafka Streams for real-time enrichment and transformations.
