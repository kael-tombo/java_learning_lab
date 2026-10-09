# Mock Interview: Event-Driven Architecture Deep Dive

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Designing a real-time analytics pipeline

**Interviewer**: "Design a real-time analytics pipeline that tracks user behavior (page views, clicks, purchases) and aggregates metrics in near real-time."

**Candidate**: "I'd build an event-driven pipeline using Kafka for ingestion and stream processing for aggregation. The architecture: Event Producers → Kafka → Stream Processor → Sink to databases."

**Interviewer**: "Walk me through the event flow."

**Candidate**: "The web and mobile clients emit events (PageViewed, ItemClicked, PurchaseCompleted) through an Event Ingestion API. The API writes events to Kafka topics partitioned by event type. A Flink/KSQL stream processor consumes the events, aggregates them into metrics (page views per minute, conversion rate, revenue per hour), and writes the aggregated results to a time-series database for querying."

**Interviewer**: "How do you handle event schema evolution?"

**Candidate**: "Schema Registry with Avro or Protobuf. Each event type has a registered schema with a version. The ingestion API validates events against the schema before writing to Kafka. Consumers read the schema ID from the event and deserialize accordingly. Backward compatibility — adding optional fields — doesn't break existing consumers. Breaking changes require a new event type."

**Interviewer**: "How do you handle late-arriving events?"

**Candidate**: "In stream processing, events are processed within a 'window' — e.g., a tumbling window of 1 minute for page view counts. Events arriving late can either be dropped (simplest), included if they fall within a grace period (say, 5 minutes), or trigger a recalculation. For the analytics pipeline, I'd use a grace period of 5 minutes with a 'lateness' metric tracked."

**Interviewer**: "How do you guarantee exactly-once processing?"

**Candidate**: "Kafka's exactly-once semantics combined with idempotent sinks. The stream processor reads from Kafka with an exactly-once source, processes, and writes to a sink that supports idempotent operations — or uses a transactional approach where the processor writes its results to Kafka (exactly-once sink) which is then read by a downstream sink connector. This eliminates duplicates."

**Interviewer**: "What about data retention?"

**Candidate**: "Kafka topics have retention policies. Raw events are retained for 30 days (for replay, debugging, historical analysis). Aggregated metrics are retained longer — 90 days in the time-series DB with downsampling to hourly/daily granularity for older data. A data lifecycle policy automatically handles archival and deletion."

**Interviewer**: "How do you scale this pipeline?"

**Candidate**: "Kafka partitions enable parallelism. More partitions mean more consumers can process in parallel. The stream processor's parallelism matches the partition count. For higher throughput: increase Kafka partitions, increase stream processor parallelism, ensure the sink database can handle the write throughput. Auto-scaling based on consumer lag — if lag increases, add more processors."

**Interviewer**: "How do you monitor pipeline health?"

**Candidate**: "Critical metrics: (1) Consumer lag — is processing keeping up with production? (2) Event throughput — events per second per topic. (3) Processing latency — time from event production to availability in the sink. (4) Error rate — events that failed processing. (5) Schema compatibility — mismatches between producers and consumers. Alert on lag exceeding 10 minutes or error rate > 1%."

---

## Key Takeaways

- Kafka provides durable, ordered event storage for real-time pipelines
- Schema Registry ensures compatibility between producers and consumers
- Windowed aggregations handle time-based analytics
- Exactly-once processing is achievable with Kafka's transactional API
- Monitor consumer lag as the primary health metric

---

## Evaluation Criteria

The interviewer assesses:
- **Architecture thinking**: Clear decomposition into meaningful boundaries
- **Trade-off awareness**: Understanding of when this pattern helps vs hurts
- **Failure handling**: Proactive identification of failure modes
- **Operational maturity**: Discussion of monitoring, deployment, and operations
- **Communication**: Ability to explain complex concepts clearly


## Staff+ Level Expectations

At the staff+ level, the interviewer expects you to:
- Challenge their assumptions and ask clarifying questions
- Discuss organizational implications (team boundaries, Conway's Law)
- Address data consistency challenges proactively
- Consider migration and evolution strategy
- Discuss cost and operational trade-offs
- Connect technical decisions to business outcomes

## Common Follow-Up Questions

1. ""How would this design change at 100x scale?"" — Discuss partitioning, caching, read replicas
2. ""How do you handle schema evolution?"" — Backward compatibility, versioning, migration strategies
3. ""Whats the biggest risk in this architecture?"" — Identify the weakest link and mitigation
4. ""How would you migrate from the current system?"" — Strangler Fig, feature toggles, parallel run
5. ""How do you test this system?"" — Unit, integration, contract, and end-to-end testing strategies

## Key Takeaways

This mock interview demonstrates the depth of discussion expected at staff+ level. The interviewer is not looking for a single ""correct"" answer but rather evaluating your thought process, trade-off awareness, and ability to communicate complex architectural decisions clearly.

