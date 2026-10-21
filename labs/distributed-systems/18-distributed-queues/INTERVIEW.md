# Distributed Queues - Interview Preparation

> Key interview questions about distributed queue systems.

---

## Core Interview Questions

### Q1: What are the guarantees offered by different queue systems?
**Answer**: At-most-once: message may be lost, never duplicated (least safe, fastest). At-least-once: message delivered at least once, may be duplicated (safe, needs dedup). Exactly-once: message delivered exactly once (safest, hardest, Kafka with idempotent producer + transactional).

### Q2: How does Kafka achieve ordering within a partition?
**Answer**: Key-based partitioning means all messages with same key go to same partition. Within partition, messages ordered by offset (append-only log). Consumer reads sequentially. No ordering guarantees across partitions. Total order requires single partition (limited parallelism).

### Q3: What is backpressure and how do you handle it?
**Answer**: Consumer cannot process messages as fast as producer. Handling: flow control (push back to producer), bounded queues, rate limiting producers, scaling consumers (increase partition count), circuit breaker (reject new messages), disk-based buffering.

### Q4: Compare SQS vs Kafka vs RabbitMQ
**Answer**: SQS: fully managed, at-least-once, 256KB max, pull-based, auto-scaling. Kafka: persistent log, high throughput, replay, ordered within partition, retention-based. RabbitMQ: flexible routing (topic, direct, fanout), push/pull, broker-based, AMQP.

### Q5: How do you design a priority queue in a distributed system?
**Answer**: Multiple queues (one per priority level), consumers check high-priority first. Or: single queue with priority field, sorted on consume. Kafka: multiple topics (one per priority). Tradeoff: high-priority starvation protection vs complexity.

## Company-Specific Focus

| Company | Queue Focus |
|---------|------------|
| Confluent | "Kafka internals: partitions, ISR, consumer groups" |
| Amazon | "SQS vs Kinesis vs SNS - when to use each" |
| Google | "Pub/Sub: exactly-once delivery evolution" |
| LinkedIn | "Kafka's origin story at LinkedIn" |

## LeetCode Connections

| Problem | # | Queue Concept |
|---------|---|--------------|
| Design Circular Queue | 622 | Bounded queue |
| Design Bounded Blocking Queue | 1188 | Producer-consumer |
| Task Scheduler | 621 | Priority queue scheduling |
| Sliding Window Maximum | 239 | Queue-based stream processing |
| Number of Recent Calls | 933 | Sliding window queue |

## System Design Connections

- **Design a Task Queue**: Redis or RabbitMQ with retry logic
- **Design a Notification System**: Priority queues per channel
- **Design a Stream Processing Pipeline**: Kafka with Spark/Flink
- **Design an Event-Driven Architecture**: Pub/sub with dead letter queues

> **Key Insight**: For Kafka questions, know partition assignment, consumer groups, ISR, and exactly-once semantics intimately.