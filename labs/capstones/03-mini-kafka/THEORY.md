# Mini Kafka - Theory

## Core Concepts

### 1. TopicPartition 

TopicPartition implements an append-only log with long offsets, key-based compaction using ByteArrayWrapper for binary key comparison, and support for message headers as Map<String,String>.

Key implementation details: the system uses concurrent data structures (ConcurrentHashMap, CopyOnWriteArrayList) for thread safety. Error handling follows fail-fast principles with IllegalArgumentException for validation and IllegalStateException for invalid operations. All components are designed for testability with clear interfaces and dependency injection.

### 2. MessageBroker manages topic creation, partition assignment, produce/consume operations, offset commit/read, and consumer group coordination.

MessageBroker manages topic creation, partition assignment, produce/consume operations, offset commit/read, and consumer group coordination.

Key implementation details: the system uses concurrent data structures (ConcurrentHashMap, CopyOnWriteArrayList) for thread safety. Error handling follows fail-fast principles with IllegalArgumentException for validation and IllegalStateException for invalid operations. All components are designed for testability with clear interfaces and dependency injection.

### 3. ProducerClient supports synchronous (immediate write) and asynchronous (batch + linger) production modes. Batching accumulates records and flushes on batch size or linger timeout.

ProducerClient supports synchronous (immediate write) and asynchronous (batch + linger) production modes. Batching accumulates records and flushes on batch size or linger timeout.

Key implementation details: the system uses concurrent data structures (ConcurrentHashMap, CopyOnWriteArrayList) for thread safety. Error handling follows fail-fast principles with IllegalArgumentException for validation and IllegalStateException for invalid operations. All components are designed for testability with clear interfaces and dependency injection.

### 4. ConsumerClient subscribes to topics, polls for messages with configurable timeout and max poll records, and supports offset commit with auto-offset-reset (earliest/latest).

ConsumerClient subscribes to topics, polls for messages with configurable timeout and max poll records, and supports offset commit with auto-offset-reset (earliest/latest).

Key implementation details: the system uses concurrent data structures (ConcurrentHashMap, CopyOnWriteArrayList) for thread safety. Error handling follows fail-fast principles with IllegalArgumentException for validation and IllegalStateException for invalid operations. All components are designed for testability with clear interfaces and dependency injection.

### 5. ConsumerGroup manages group membership with join/leave, partition assignment with round-robin rebalancing, and leader election.

ConsumerGroup manages group membership with join/leave, partition assignment with round-robin rebalancing, and leader election.

Key implementation details: the system uses concurrent data structures (ConcurrentHashMap, CopyOnWriteArrayList) for thread safety. Error handling follows fail-fast principles with IllegalArgumentException for validation and IllegalStateException for invalid operations. All components are designed for testability with clear interfaces and dependency injection.

### 6. LogSegment stores messages in memory with optional file-based persistence via DataOutputStream. Tracks size in bytes and supports active segment detection.

LogSegment stores messages in memory with optional file-based persistence via DataOutputStream. Tracks size in bytes and supports active segment detection.

Key implementation details: the system uses concurrent data structures (ConcurrentHashMap, CopyOnWriteArrayList) for thread safety. Error handling follows fail-fast principles with IllegalArgumentException for validation and IllegalStateException for invalid operations. All components are designed for testability with clear interfaces and dependency injection.

### 7. OffsetManager persists consumer offsets per group/topic/partition with metadata, supporting reset and delete operations.

OffsetManager persists consumer offsets per group/topic/partition with metadata, supporting reset and delete operations.

Key implementation details: the system uses concurrent data structures (ConcurrentHashMap, CopyOnWriteArrayList) for thread safety. Error handling follows fail-fast principles with IllegalArgumentException for validation and IllegalStateException for invalid operations. All components are designed for testability with clear interfaces and dependency injection.

## Design Principles

The architecture follows SOLID principles with single-responsibility classes, open-for-extension design, and dependency inversion. Thread safety is achieved through immutable records, atomic operations, and synchronized blocks where necessary. All components include comprehensive JUnit 5 test coverage with parameterized tests and edge case handling.

## Performance Characteristics

Operations are O(1) for hash-based lookups, O(log n) for tree-based structures, and O(n) for linear scans. Memory usage is proportional to the number of stored elements with per-entry overhead for indexing structures. Concurrent access patterns use lock striping and non-blocking algorithms where possible to minimize contention.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Monitoring Kafka performance metrics (Datadog, published Apr 6, 2016, updated Feb 2, 2026) — https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/ — Takeaway tied to lab TopicPartition/LogSegment: Kafka's append-only partitioned log is why the lab's offset-per-partition and active-segment tracking matter; monitor log-end vs. committed offset per partition.
- Consumer lag as the key health signal: offsets, fetch purgatory, and rebalance behavior (same Datadog Kafka guide, 2016/2026) — https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/ — Takeaway tied to lab ConsumerClient/ConsumerGroup/OffsetManager: the lab's poll-timeout, max-poll-records, auto-offset-reset, and round-robin rebalance directly control lag; alert lag in time-behind, not just message count.
- Broker health: UnderReplicatedPartitions, ISR shrink/expand, OfflinePartitionsCount, ActiveControllerCount (same Datadog Kafka guide, 2016/2026) — https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/ — Takeaway tied to lab MessageBroker/ProducerClient batching: `UnderReplicatedPartitions > 0` or ISR flapping means produce-with-acks and replication assumptions in the lab no longer hold — investigate before tuning batch/linger.

