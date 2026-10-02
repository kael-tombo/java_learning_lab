# Exercises: Distributed Event Bus (Kafka-like) (Lab 08)

**Prerequisites:** Read `LEETCODE_SOLUTION.md`  
**Difficulty:** Progressive (Easy → Medium → Hard)

---

## Exercise 1: Message Compression (Easy)

### Task
Add compression support for messages (Snappy, Zstd, GZIP).

### Requirements
```java
public enum CompressionType {
    NONE, SNAPPY, ZSTD, GZIP
}

public record ProducerConfig(
    CompressionType compression,
    int batchSize,
    long lingerMs
) {}

// In publish():
// 1. Accumulate messages in memory buffer per partition
// 2. When batchSize or lingerMs reached, compress batch
// 3. Write compressed batch as single "message set"
// 4. Store compression type in message headers
```

### Test Case
```java
@Test
void testCompression() {
    var bus = new DistributedEventBus();
    bus.createTopic("compressed", 1, RetentionPolicy.infinite());
    
    // Publish 1000 small messages with compression
    // Verify disk/memory usage < uncompressed
    // Verify consumers can decompress
}
```

---

## Exercise 2: Producer Batching & Async Send (Easy)

### Task
Make `publish()` asynchronous with batching (like Kafka's `linger.ms` and `batch.size`).

### Requirements
```java
public class AsyncProducer {
    private final DistributedEventBus bus;
    private final Map<String, PartitionBuffer> buffers = new ConcurrentHashMap<>();
    
    public CompletableFuture<RecordMetadata> send(String topic, String key, String value) {
        // Add to buffer for topic+partition
        // Schedule flush if lingerMs exceeded
        // Return future completed on flush
    }
    
    private void flush(String topic) { ... }
}

// PartitionBuffer: accumulates messages, compresses, sends in batch
```

### Test Case
```java
@Test
void testAsyncBatching() throws Exception {
    var producer = new AsyncProducer(bus, ProducerConfig.builder()
        .batchSize(100)
        .lingerMs(10)
        .build());
    
    // Send 500 messages rapidly
    // Verify they're batched (fewer actual appends)
    // Verify all futures complete
}
```

---

## Exercise 3: Consumer Fetch Optimization (Medium)

### Task
Optimize `poll()` with fetch sessions and incremental fetch (like Kafka's Fetch API v3+).

### Requirements
```java
// Current: polls all assigned partitions every call
// Optimized:
// - Track which partitions have data available (via metadata)
// - Only fetch from partitions with new data
// - Support incremental fetch: resume from last fetched offset
// - Fetch response includes: partition, highWatermark, records, nextFetchOffset

public record FetchResult(
    Map<Integer, PartitionData> partitions,
    long throttleTimeMs
) {}

public record PartitionData(
    long highWatermark,
    long lastStableOffset,
    List<ConsumerRecord> records,
    long nextFetchOffset
) {}
```

### Test Case
```java
@Test
void testFetchOptimization() {
    // Produce to 2 partitions
    // Consumer polls
    // Verify only partition with data returns records
    // Verify highWatermark returned for lag monitoring
}
```

---

## Exercise 4: Log Compaction (Medium)

### Task
Implement log compaction — retain only the latest value for each key.

### Requirements
```java
public class CompactionManager {
    private final DistributedEventBus bus;
    
    public void compact(String topic) {
        Topic t = bus.getTopic(topic);
        for (Partition p : t.partitions) {
            // Build Map<key, Message> keeping latest by offset
            // Replace partition log with compacted entries
            // Preserve order of latest values
        }
    }
    
    // Background job: run compaction periodically
    // Only for topics with cleanup.policy=compact
}
```

### Test Case
```java
@Test
void testLogCompaction() {
    bus.createTopic("compacted", 1, RetentionPolicy.infinite());
    
    // Same key, multiple updates
    bus.publish("compacted", "user-1", "name=Alice");
    bus.publish("compacted", "user-1", "name=Bob");
    bus.publish("compacted", "user-1", "name=Carol");
    
    bus.compact("compacted");
    
    // Only "name=Carol" should remain for key "user-1"
    var consumer = bus.createConsumer("g1");
    consumer.subscribe("compacted");
    var records = consumer.poll("compacted", 10, 1000);
    assertEquals(1, records.size());
    assertEquals("name=Carol", records.get(0).value());
}
```

---

## Exercise 5: Transactional Producer (Medium)

### Task
Add transactional producer support for exactly-once semantics.

### Requirements
```java
public class TransactionalProducer {
    private final String transactionalId;
    private final DistributedEventBus bus;
    private TransactionState state = TransactionState.IDLE;
    private final List<PendingSend> pending = new ArrayList<>();
    
    public void initTransactions() { ... }
    public void beginTransaction() { ... }
    public void send(String topic, String key, String value) { ... }
    public void commitTransaction() { ... }
    public void abortTransaction() { ... }
}

// Transaction log: separate internal topic
// Commit marker: special message marking transaction committed/aborted
// Consumer: reads only committed transactions (isolation.level=read_committed)
```

### Test Case
```java
@Test
void testTransactionalSend() {
    var txProducer = new TransactionalProducer("tx-1", bus);
    txProducer.initTransactions();
    
    txProducer.beginTransaction();
    txProducer.send("topic", "k1", "v1");
    txProducer.send("topic", "k2", "v2");
    txProducer.commitTransaction();
    
    // Verify both messages visible to read_committed consumer
    // Verify aborted transaction messages NOT visible
}
```

---

## Exercise 6: Schema Registry Integration (Medium)

### Task
Integrate a schema registry (Avro/Protobuf) for message validation and evolution.

### Requirements
```java
public interface SchemaRegistry {
    int register(String subject, Schema schema);  // Returns schema ID
    Schema getById(int id);
    Schema getLatest(String subject);
    boolean isCompatible(String subject, Schema schema); // BACKWARD, FORWARD, FULL
}

// Producer: serialize with schema ID prefix (Confluent wire format: magic byte + schema ID)
// Consumer: deserialize using schema from registry
// Config: auto.register.schemas, use.latest.version
```

### Test Case
```java
@Test
void testSchemaEvolution() {
    // Register v1 schema: { name: string }
    // Produce with v1
    // Register v2 schema: { name: string, email: string } (backward compatible)
    // Produce with v2
    // Consumer with v1 schema reads v2 message (ignores email)
    // Consumer with v2 schema reads v1 message (email = null)
}
```

---

## Exercise 7: Replication & ISR (Hard)

### Task
Implement partition replication with In-Sync Replicas (ISR) and leader election.

### Requirements
```java
public class ReplicatedPartition {
    private final int partitionId;
    private final List<Replica> replicas; // One leader, N followers
    private final Set<Replica> isr;       // In-sync replicas
    
    // Leader appends to local log, replicates to ISR followers
    // Follower: fetch from leader, ack when replicated
    // If follower lags > replica.lag.time.max.ms → remove from ISR
    // If leader fails → controller elects new leader from ISR
}

public enum ReplicaState { LEADER, FOLLOWER, OBSERVER }
```

### Test Case
```java
@Test
void testReplication() {
    // Create topic with replication.factor=3
    // Verify 3 replicas, 1 leader
    // Kill leader
    // Verify new leader elected from ISR
    // Verify no data loss (acks=all)
}
```

---

## Exercise 8: Consumer Group Protocol (Hard)

### Task
Implement full Kafka consumer group protocol (JoinGroup, SyncGroup, Heartbeat).

### Requirements
```java
public class GroupCoordinator {
    // Manages group metadata, generation, protocol
    // JoinGroup: members send metadata (subscription, assignor)
    // Leader (chosen by coordinator) runs assignment
    // SyncGroup: leader sends assignment to coordinator, members fetch
    // Heartbeat: members send periodically, detect failures
}

// Assignors: Range, RoundRobin, Sticky, CooperativeSticky
// Rebalance protocol: PrepareJoin -> JoinGroup -> SyncGroup
// Static membership: memberId persists across restarts
```

### Test Case
```java
@Test
void testConsumerGroupProtocol() {
    // Start 3 consumers in same group
    // Verify JoinGroup -> SyncGroup sequence
    // Verify partition assignment
    // Kill one consumer -> heartbeat timeout -> rebalance
    // Verify remaining consumers get reassigned partitions
}
```

---

## Exercise 9: Tiered Storage (Hard)

### Task
Implement tiered storage — offload old log segments to remote storage (S3/GCS).

### Requirements
```java
public class TieredStorageManager {
    private final RemoteStorage remote; // S3, GCS, etc.
    private final long localRetentionMs; // Keep recent locally
    
    public void offload(String topic, int partition, long beforeOffset) {
        // 1. Identify segments fully before beforeOffset
        // 2. Upload segment files to remote storage
        // 3. Delete local segment files
        // 4. Update partition metadata: segment -> remote URI
    }
    
    // Fetch: if offset in local, read local; else fetch from remote
    // Compaction: can compact remote segments
}
```

### Test Case
```java
@Test
void testTieredStorage() {
    // Produce 10GB of data
    // Configure local retention = 1GB
    // Trigger offload
    // Verify local < 1GB, remote has rest
    // Consume old data -> fetched from remote transparently
}
```

---

## Exercise 10: Kafka Streams-like DSL (Hard)

### Task
Build a stream processing DSL on top of the event bus (filter, map, join, aggregate).

### Requirements
```java
public interface KStream<K, V> {
    KStream<K, V> filter(Predicate<Record<K,V>> predicate);
    <K2, V2> KStream<K2, V2> map(KeyValueMapper<K,V,K2,V2> mapper);
    <K2, V2> KStream<K2, V2> flatMap(KeyValueMapper<K,V,Iterable<Record<K2,V2>>> mapper);
    KStream<K, V> peek(Consumer<Record<K,V>> action);
    
    <V2> KStream<K, V2> mapValues(ValueMapper<V,V2> mapper);
    <VO> KTable<K, VO> groupByKey().aggregate(Initializer<VO>, Aggregator<K,V,VO>);
    
    <K2, V2> KStream<K, Tuple2<V, V2>> join(
        KStream<K, V2> other,
        ValueJoiner<V, V2, Tuple2<V, V2>> joiner,
        JoinWindows windows
    );
}

public interface KTable<K, V> { ... }
```

### Test Case
```java
@Test
void testStreamProcessing() {
    // Source: orders topic
    // Filter: orders > $100
    // Map: enrich with customer info (join with customers table)
    // Aggregate: count orders per customer per hour
    // Sink: output to alerts topic
    
    // Verify end-to-end processing
    // Verify exactly-once semantics
}
```

---

## Solutions

See `SOLUTIONS.md` for reference implementations.

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1 | 15 | Compression reduces size, decompression works |
| 2 | 20 | Async send batches, futures complete correctly |
| 3 | 25 | Fetch optimization reduces unnecessary polls |
| 4 | 30 | Compaction retains latest per key |
| 5 | 40 | Transactions commit/abort, isolation works |
| 6 | 35 | Schema registry validates, evolution works |
| 7 | 60 | Replication + ISR + leader election |
| 8 | 60 | Full group protocol with rebalance |
| 9 | 50 | Tiered offload + transparent fetch |
| 10 | 80 | DSL compiles to executable topology |

**Total: 415 points**

---

## Next Steps

1. Run tests: `mvn test`
2. Study Kafka Protocol Guide, Kafka Streams DSL
3. Explore: Kafka Connect, ksqlDB, MirrorMaker
4. Read: "Kafka: The Definitive Guide" (O'Reilly)
5. Practice: Build a real-time analytics pipeline