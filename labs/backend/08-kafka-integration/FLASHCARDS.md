# Flashcards: Distributed Event Bus (Kafka-like) (Lab 08)

> **Instructions:** Cover the answer side, recall from memory, then reveal. Shuffle periodically.

---

## Core Concepts

| # | Question | Answer |
|---|----------|--------|
| 1 | What is a distributed log? | An append-only, totally ordered sequence of records, partitioned for scalability, replicated for fault tolerance. |
| 2 | How does Kafka differ from traditional message queues? | Log retention (not delete-on-consume), ordered per partition, consumer-controlled offset, replayable. |
| 3 | What is a topic? | A named category/feed to which records are published. Split into partitions. |
| 4 | What is a partition? | An ordered, immutable log. Each record has a sequential offset. Partitions enable parallelism. |
| 5 | What is a consumer group? | A set of consumers that jointly consume a topic — each partition consumed by exactly one member. |

---

## Producer / Publishing

| # | Question | Answer |
|---|----------|--------|
| 6 | How does key-based partitioning work? | `partition = hash(key) % partitionCount`. Same key → same partition (ordering guarantee). |
| 7 | What if key is null? | Random partition (round-robin via `ThreadLocalRandom`). |
| 8 | What does `publish()` return? | `RecordMetadata`: offset, partition, timestamp. |
| 9 | Is publish synchronous or async? | Synchronous in this impl (locks, appends, returns). Real Kafka: async with callbacks/Future. |
| 10 | What is `RecordMetadata`? | Record of where message was written: `offset`, `partition`, `timestamp`. |

---

## Consumer / Consumption

| # | Question | Answer |
|---|----------|--------|
| 11 | How does `poll()` work? | Loops assigned partitions, reads from current offset up to `maxRecords`, updates offset. |
| 12 | What is `ConsumerRecord`? | Wrapper: topic, partition, offset, key, value, headers, timestamp. |
| 13 | How does a consumer join a group? | `subscribe()` → `ConsumerGroup.addMember()` → `assignPartitions()` |
| 14 | What triggers rebalancing? | Member joins/leaves (in this impl: on each subscribe). Real Kafka: heartbeat protocol. |
| 15 | How is offset committed? | `commitSync()` writes current offset to `ConsumerGroup.committedOffsets`. |

---

## Offset Management

| # | Question | Answer |
|---|----------|--------|
| 16 | Where are committed offsets stored? | `ConsumerGroup.committedOffsets` map: `topic:partition` → offset. |
| 17 | What happens on consumer restart? | `assignPartitions()` reads `committedOffsets` for assigned partitions, starts from there. |
| 18 | What is `seek()`? | Manually sets offset for a partition: `offset.set(newOffset)`. Enables replay. |
| 19 | What is the difference between `poll()` and `seek()`? | `poll()` reads forward from current offset. `seek()` jumps to arbitrary offset. |
| 20 | What is auto-commit? | Not implemented here. Real Kafka: periodic background commit of offsets. |

---

## Retention & Cleanup

| # | Question | Answer |
|---|----------|--------|
| 21 | What are the two retention dimensions? | Time (`maxAgeMs`) and size (`maxSize` messages). |
| 22 | How does the cleaner work? | Scheduled every 10s: for each partition, drop messages older than `maxAgeMs` or exceeding `maxSize`. |
| 23 | What is `RetentionPolicy.infinite()`? | Both `maxAgeMs` and `maxSize` = `Long.MAX_VALUE` — never deletes. |
| 24 | What is log compaction? | Not implemented. Real Kafka: retain latest value per key (for changelog topics). |
| 25 | Can retention be per-topic? | Yes: `createTopic(name, partitions, retention)` — each topic has its own policy. |

---

## Concurrency & Thread Safety

| # | Question | Answer |
|---|----------|--------|
| 26 | How is partition append synchronized? | `ReentrantLock appendLock` per partition. Serializes appends to same partition. |
| 27 | Why `CopyOnWriteArrayList` for partition log? | Readers (poll) iterate without locking. Writers create new array on append. |
| 28 | How are consumer offsets thread-safe? | `AtomicLong` per `TopicPartitionState`. |
| 29 | Is `ConsumerGroup.members` thread-safe? | Yes: `CopyOnWriteArrayList`. |
| 30 | What about `topics` map? | `ConcurrentHashMap` — thread-safe for topic creation/lookup. |

---

## Delivery Semantics

| # | Question | Answer |
|---|----------|--------|
| 31 | What is at-least-once? | Message processed ≥1 time. Achieved by: process → commit offset. Crash before commit → reprocess. |
| 32 | What is at-most-once? | Commit offset → process. Crash after commit → message lost. |
| 33 | What is exactly-once? | Requires idempotent processing + transactional write (process + commit in same transaction). |
| 34 | How to achieve exactly-once in this impl? | Add `transactionalId` to producer, use `initTransactions()`, `beginTransaction()`, `send()`, `commitTransaction()`. |
| 35 | What is the role of `isolation.level`? | `read_committed` = only read transactionally committed messages. `read_uncommitted` = all. |

---

## Rebalancing

| # | Question | Answer |
|---|----------|--------|
| 36 | What is the rebalance protocol? | 1. Members join group 2. Leader (coordinator) assigns partitions 3. Members revoke old, consume new. |
| 37 | How does this impl handle rebalance? | `assignPartitions()` called on subscribe. Simple static assignment: `partitionCount / members`. |
| 38 | What is sticky partitioning? | Minimize partition movement during rebalance (cooperative sticky assignor). Not implemented here. |
| 39 | What happens to in-flight records during rebalance? | Consumer should finish processing, commit, then revoke. Not handled in this impl. |
| 40 | What is the "rebalance storm"? | Frequent rebalances due to heartbeat timeouts. Fix: tune `session.timeout.ms`, `heartbeat.interval.ms`. |

---

## Performance & Scaling

| # | Question | Answer |
|---|----------|--------|
| 41 | How to increase throughput? | More partitions (parallelism), batch produces, compression (snappy/zstd), larger fetch sizes. |
| 42 | What is the latency vs throughput tradeoff? | `linger.ms` > 0 batches sends (higher throughput, higher latency). `fetch.min.bytes` similar for consumer. |
| 43 | How does partition count affect consumer scaling? | Max consumers in group = partition count. More partitions = more parallelism. |
| 44 | What is the "hot partition" problem? | Skewed key distribution → one partition gets disproportionate load. Fix: better key, more partitions. |
| 45 | How to handle backpressure? | Consumer `max.poll.records`, `max.poll.interval.ms`, pause/resume partitions. |

---

## Quick Reference: Key Classes

| Class | Responsibility |
|-------|----------------|
| `DistributedEventBus` | Main facade: topics, producers, consumers, retention |
| `Topic` | Name, partition count, retention policy, list of partitions |
| `Partition` | Ordered log (`CopyOnWriteArrayList<Message>`), append lock |
| `Consumer` | Subscribe, poll, commit, seek, close |
| `ConsumerGroup` | Manages members, committed offsets, partition assignment |
| `Message` | Key, value, headers, timestamp |
| `RecordMetadata` | Append result: offset, partition, timestamp |

---

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Too few partitions | Can't scale consumers | Plan for peak parallelism |
| Null keys | Random distribution, no ordering | Use meaningful keys |
| No offset commit | Reprocessing on restart | Commit after successful processing |
| Large messages | Broker/network pressure | Compress, use chunking, or external store |
| Unbounded retention | Disk exhaustion | Set time/size limits |
| Single consumer group for all | Coupling, blast radius | Separate groups per application |

---

## Real Kafka Features Not Implemented

| Feature | Description |
|---------|-------------|
| **Replication** | ISR (in-sync replicas), leader election, acks=all |
| **Log Compaction** | Retain latest per key for changelog topics |
| **Transactions** | Exactly-once across multiple partitions |
| **Schema Registry** | Avro/Protobuf schema validation & evolution |
| **Consumer Heartbeats** | Detect failures, trigger rebalance |
| **Tiered Storage** | Offload old segments to S3/GCS |
| **KRaft** | Kafka metadata in Kafka (no ZooKeeper) |