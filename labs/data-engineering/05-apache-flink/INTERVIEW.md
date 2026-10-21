# Apache Flink Interview Questions

## Beginner
**Q**: What is the difference between Flink and Spark Streaming?
**A**: Flink is true streaming (processes each event as it arrives), while Spark Streaming uses micro-batching (processes events in small batches). Flink has superior event-time handling and state management.

## Intermediate
**Q**: How does exactly-once work in Flink?
**A**: Flink uses distributed snapshots (checkpoints) aligned with barriers in the data stream. Combined with idempotent or transactional sinks, this provides exactly-once guarantees.

## Advanced
**Q**: How would you handle out-of-order events with large latencies?
**A**: Use allowed lateness with side outputs for very late events. Configure watermarks with generous bounded-out-of-orderness. Use a two-stage processing model where initial results are produced and corrected as late data arrives.
