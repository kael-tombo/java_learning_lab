# Mock Interview: Distributed Log / Event Bus with Kafka Semantics (Lab 08)

**Role:** Senior Backend Engineer
**Duration:** 55 minutes
**Difficulty:** Easy to Medium to Hard

---

## Round 1: Easy Problem Understanding (5 min)

**Interviewer:** Design a distributed log or event bus with Kafka-like semantics. What core concepts must you model?

**Candidate:** The fundamental abstraction is an append-only log. Kafka organizes logs into topics. Each topic has partitions which are the unit of parallelism and ordering. Producers write to partitions optionally keyed for ordering. Consumers read from partitions in consumer groups each partition is consumed by exactly one consumer in a group. The offset tracks how far a consumer has read.

**Interviewer:** Why is the log abstraction so powerful?

**Candidate:** The log turns distributed state into a sequence of immutable events. This enables replay (consumers can rewind to any offset), multiple independent consumers each with their own offset, and decoupling of producers and consumers in time and space. It is the foundation of event-driven architectures, CQRS, and stream processing.

**Interviewer:** What is the difference between a queue and a log?

**Candidate:** A queue removes messages after consumption point-to-point semantics. A log retains messages and allows multiple consumers to read independently at their own pace. In a queue if the consumer crashes the message is lost or needs redelivery. In a log the consumer simply resumes from its last committed offset. The log is the more powerful abstraction and Kafka is often described as a distributed commit log.

---

## Round 2: Medium Partitions and Ordering (10 min)

**Interviewer:** Explain how partitioning works and why ordering is only within a partition.

**Candidate:** Each topic is split into N partitions. When a producer sends a message with a key, hash(key) % N determines the partition. Messages with the same key go to the same partition and are ordered by offset. Cross-partition ordering is not guaranteed. If you need global ordering use a single partition which limits throughput. This trade-off is fundamental partitions enable parallelism at the cost of ordering guarantees.

**Interviewer:** How does consumer group rebalancing work in your design?

**Candidate:** When a consumer joins or leaves a group partitions must be reassigned. My implementation uses a simple assignment: partitionsPerConsumer = totalPartitions / consumers.size(). Each consumer gets a contiguous slice. Kafka uses configurable partition assignors (range, round-robin, or sticky). During rebalancing all consumers in the group stop reading then resume with new assignments. Sticky assignment minimizes partition movement.

**Interviewer:** What is the offset commit semantics at-least-once vs at-most-once vs exactly-once?

**Candidate:** My implementation uses at-least-once by default. The consumer calls commitSync() after processing storing the current offset. If the consumer crashes before committing it re-processes from the last committed offset. For at-most-once commit before processing risk of data loss. Exactly-once requires transactional coordination between the consumer, offset store, and output system using Kafka EOS or idempotent sinks.

---

## Round 3: Medium-Hard Storage and Retention (10 min)

**Interviewer:** How does the log physically store messages? What about retention?

**Candidate:** Internally each partition is a CopyOnWriteArrayList in memory. In production Kafka writes to segmented files on disk each segment is a contiguous byte array. Retention can be time-based (delete messages older than X hours) or size-based (keep last Y bytes). My retention policy uses a background cleaner that periodically truncates the head of the log.

**Interviewer:** How do you handle a consumer that is too slow and the log fills up?

**Candidate:** If the consumer is slower than the producer the log grows until retention limits are hit. Old messages are deleted and the consumer may lose messages when its offset points to a deleted segment. Kafka handles this with log.retention.bytes and log.retention.hours. Consumers should alert when consumer lag (producer offset minus consumer offset) exceeds a threshold. This is a key operational metric.

**Interviewer:** Can you support compaction instead of deletion?

**Candidate:** Yes for compacted topics instead of deleting old messages the log keeps only the latest message for each key. This is useful for key-value state stores like current address of user. Compaction runs in the background scanning segments and keeping only the last entry per key. My implementation only supports time/size-based deletion but can be extended with a compaction strategy.

---

## Round 4: Hard Production Readiness (15 min)

**Interviewer:** How would you make this production-ready? What is missing?

**Candidate:** Several things. Persistence write to disk (WAL) for crash recovery not just in-memory. Replication each partition should be replicated across N brokers using leader/follower with ISR (in-sync replicas). The leader handles all reads and writes followers replicate asynchronously. Leader election via Raft or Kafka own quorum. Consumer rebalancing needs a coordinator. Compression (snappy, zstd) for high-throughput scenarios. A wire protocol (binary protocol over TCP) for clients to connect.

**Interviewer:** How does your publish method compare to Kafka acks setting?

**Candidate:** My publish writes to a single partition immediately. Kafka offers acks=0 (fire-and-forget), acks=1 (leader wrote), and acks=all (all in-sync replicas wrote). My implementation is analogous to acks=1. For acks=all I would need to wait for replication acknowledgments from all ISR replicas before returning the metadata to the producer.

**Interviewer:** How do you handle partition leader failure and election?

**Candidate:** Each partition has a leader and multiple followers (replicas). The leader handles all produce and consume requests. Followers replicate the log from the leader. If the leader fails, one of the in-sync replicas (ISR) is elected as the new leader. The ISR set contains followers that are fully caught up with the leader. If a follower falls too far behind it is removed from ISR. This ensures the new leader has all committed data.

**Interviewer:** How would you implement exactly-once semantics?

**Candidate:** Exactly-once requires: (1) Idempotent producers with a producer ID and sequence number to detect duplicates. (2) Transactional writes that atomically commit to multiple partitions. (3) Consumers that store their offset in the same transaction as their output. Kafka achieves this with the transaction coordinator and the __transaction_state internal topic. The producer sends a BeginTransaction, writes data, and then commits. The consumer reads committed data and stores offsets transactionally.

**Interviewer:** What metrics are critical for operating a Kafka-like system?

**Candidate:** (1) Under-replicated partitions indicates replication lag or leader issues. (2) Consumer lag the difference between the latest offset and the consumer committed offset. (3) Request rate and throughput per broker. (4) Disk usage per partition. (5) Network I/O and bandwidth. (6) Number of active consumer group rebalances high rebalance frequency indicates instability. These are exported via JMX and integrated with monitoring systems.

---

## Round 5: Summary (5 min)

**Interviewer:** Summarize the key design decisions and trade-offs.

**Candidate:** (1) Log as the core abstraction provides replay, decoupling, and multiple consumers. (2) Partitions enable horizontal scaling at the cost of global ordering. (3) Retention-based storage bounds disk usage at the cost of potentially losing old data. (4) At-least-once delivery prioritizes data safety over deduplication. (5) Replication provides durability and availability at the cost of write latency. The log is the most important abstraction in distributed systems after the network itself.
