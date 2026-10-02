# Quiz: Distributed Event Bus (Kafka-like) (Lab 08)

**Topic:** Distributed Log/Event Bus with Kafka-like Semantics  
**Difficulty:** Medium  
**Time Limit:** 15 minutes

---

## Questions

### 1. Core Concept
What is the primary data structure in the `DistributedEventBus`?
- A) A single queue per topic
- B) Topics with multiple partitions, each an ordered log
- C) A pub/sub tree with wildcards
- D) A key-value store with TTL

### 2. Partitioning
How does `publish()` determine which partition a message goes to?
- A) Round-robin across partitions
- B) `key.hashCode() % partitionCount` (key-based)
- C) Random partition
- D) Based on message size

### 3. Consumer Groups
What is the purpose of a consumer group?
- A) To allow multiple consumers to each get all messages
- B) To parallelize consumption — each partition consumed by one group member
- C) To broadcast messages to all consumers
- D) To prioritize certain consumers

### 4. Offset Management
How does a consumer track its position?
- A) Server tracks it automatically
- B) Consumer stores offset locally in `TopicPartitionState.offset`
- C) Offset embedded in message
- D) Timestamp-based seeking only

### 5. Rebalancing
When `assignPartitions()` runs, how are partitions distributed?
- A) Each consumer gets equal number of partitions
- B) Sticky assignment (minimize movement)
- C) Random assignment
- D) By partition key hash

### 6. Retention
What two retention policies are supported?
- A) Time-based and count-based
- B) Time-based and size-based
- C) Count-based and size-based
- D) Time-based only

### 7. Message Structure
What fields does a `Message` contain?
- A) key, value, timestamp
- B) key, value, headers, timestamp
- C) key, value, partition, offset
- D) value, timestamp, checksum

### 8. Delivery Semantics
What delivery guarantee does the implementation provide?
- A) At-most-once
- B) At-least-once
- C) Exactly-once
- D) Best-effort

### 9. Seek/Replay
How does `seek()` enable replay?
- A) Deletes messages before offset
- B) Sets consumer's offset to arbitrary position
- C) Re-publishes messages from offset
- D) Creates new consumer group

### 10. Concurrency
What protects partition append?
- A) `ConcurrentHashMap`
- B) `ReentrantLock` per partition
- C) `synchronized` on topic
- D) No locking needed

---

## Answers

| # | Answer | Explanation |
|---|--------|-------------|
| 1 | **B** | Topics have multiple partitions; each partition is an ordered, append-only log (`CopyOnWriteArrayList<Message>`). |
| 2 | **B** | Key-based partitioning: `Math.abs(key.hashCode()) % partitionCount`. Null key → random partition. |
| 3 | **B** | Consumer group enables parallel consumption: each partition assigned to exactly one member. |
| 4 | **B** | `TopicPartitionState` holds `AtomicLong offset` per partition per consumer. Updated on `poll()`. |
| 5 | **A** | Simple round-robin: `partitionsPerConsumer = partitionCount / members.size()`. Not sticky. |
| 6 | **B** | `RetentionPolicy` has `maxAgeMs` (time) and `maxSize` (count). Cleaner enforces both. |
| 7 | **B** | `Message` record: `key`, `value`, `headers` (Map), `timestamp`. |
| 8 | **B** | At-least-once: consumer polls → processes → `commitSync()`. If crash before commit, re-process. |
| 9 | **B** | `seek(topic, partition, offset)` sets `offset` in `TopicPartitionState`. Next `poll()` reads from there. |
| 10 | **B** | Each `Partition` has `ReentrantLock appendLock` for thread-safe append. |

---

## Scoring

| Score | Level |
|-------|-------|
| 9-10 | Expert — Kafka internals master |
| 7-8 | Proficient — Solid distributed log understanding |
| 5-6 | Developing — Review partitioning and consumer groups |
| <5 | Beginner — Re-read LEETCODE_SOLUTION and test cases |

---

## Further Study

- Read `MOCK_INTERVIEW.md` (if exists)
- Study Kafka protocol, log compaction, transactional producer
- Explore: Kafka Streams, ksqlDB, exactly-once semantics
- Practice: Add compression, schema registry, mirror maker