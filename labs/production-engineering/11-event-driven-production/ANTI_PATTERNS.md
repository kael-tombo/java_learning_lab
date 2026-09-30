# ANTI-PATTERNS: Event-Driven & Kafka Architecture
## Lab 11 | Production Engineering Academy — Top 0.0001% Engineering

---

## Anti-Pattern 1: Dual-Write (DB + Kafka in Separate Transactions)

### The Mistake
```java
@Transactional
public void createOrder(OrderRequest req) {
    orderRepository.save(new Order(req)); // DB write commits
    kafkaTemplate.send("orders", req.toJson()); // Kafka write — separate network call
}
```

### Why It Fails — Two Distinct Crash Scenarios

**Scenario A (Event Lost)**: DB transaction commits. Network to Kafka drops. Event never published.
Downstream billing and inventory never see the order — customer charged, product never shipped.

**Scenario B (Phantom Event)**: `kafkaTemplate.send()` succeeds. DB transaction rolls back on
a constraint violation (duplicate order ID). Kafka consumers charge the customer for an order
that does not exist in the database.

### The Fix: Transactional Outbox Pattern
Write the business entity AND an `OutboxEvent` row in the same ACID transaction.
Debezium CDC reads the DB WAL and forwards the event to Kafka — atomically and in order.

---

## Anti-Pattern 2: Hot Partition Key (Data Skew)

### The Mistake
```java
// BAD: 90% of customers are "US" — 90% of traffic hashes to one partition
kafkaTemplate.send("orders", order.getCountryCode(), orderPayload);
```

### Why It Fails
- Partition hash = `murmurhash(countryCode) % numPartitions`.
- "US" → always Partition 3 → 90,000 msg/s.
- Partitions 0, 1, 2 → 500 msg/s each (idle consumers waste capacity).
- Consumer on Partition 3 hits CPU ceiling → consumer lag grows → SLA breach.

### The Fix
Use high-cardinality composite keys (`customerId`, `orderId`):
```java
// HIGH ENTROPY: orderId (UUID) distributes uniformly across all partitions
kafkaTemplate.send("orders", order.getOrderId().toString(), orderPayload);
```
Verify distribution with:
```bash
kafka-log-dirs.sh --bootstrap-server kafka:9092 \
  --topic orders --describe | grep "size" | sort -t: -k2 -n
```

---

## Anti-Pattern 3: Ignoring `max.poll.interval.ms` — Infinite Rebalance Loop

### The Mistake
```java
@KafkaListener(topics = "orders")
public void processOrder(OrderEvent event) {
    // Calls a slow downstream REST API with no timeout set
    inventoryClient.checkStock(event.getItems()); // Can block for 30+ seconds
}
```
Default `max.poll.interval.ms = 300,000` (5 min). Default `max.poll.records = 500`.
If 500 records × 1s/record = 500s > 300s, the consumer is evicted, triggering a rebalance.
The rebalance revokes partitions → consumer rejoins → evicted again → infinite loop.

### The Fix
```java
// Option A: Reduce records per poll so total processing < interval
props.put(MAX_POLL_RECORDS_CONFIG, 10);         // 10 × 1s = 10s < 300s
// Option B: Increase interval to cover worst-case processing
props.put(MAX_POLL_INTERVAL_MS_CONFIG, 600_000); // 10 min
// Option C: Process async (commit offset AFTER async result)
// Use AckMode.MANUAL_IMMEDIATE + CompletableFuture
```

---

## Anti-Pattern 4: Schema Evolution Breaking Consumers (No Schema Registry)

### The Mistake
```java
// Producer v1 publishes:
record OrderEvent(String orderId, double amount) {}

// Producer team adds a field in v2 — no coordination with consumers
record OrderEvent(String orderId, double amount, String currency) {}  // NEW FIELD
```
Consumer using `ObjectMapper` with `FAIL_ON_UNKNOWN_PROPERTIES = true` throws
`UnrecognizedPropertyException` on every v2 message → consumer lag spikes → DLQ floods.

### The Fix
1. Register schemas in **Confluent Schema Registry** with compatibility mode `BACKWARD`:
   - Consumers on v1 can read v2 messages (new fields must have defaults).
   - Producers cannot remove existing fields without bumping compatibility mode.
2. Configure Jackson:
```java
objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
```
3. Use Avro or Protobuf — both have built-in forward/backward compatibility rules.

---

## Anti-Pattern 5: Using Kafka as a Database (Long Retention + Random Reads)

### The Mistake
```java
// Treating Kafka as a query-able store
kafkaAdminClient.listOffsets(...); // Scan topic to find order by customerId
```
Kafka log is an append-only sequential structure. There is no index. Finding one record
requires scanning all segments → O(N) I/O → unacceptable for production query patterns.

### The Fix
- **Event Sourcing**: Replay topic into a materialized view in PostgreSQL or Redis.
- **Kafka Streams**: Use `KTable` (RocksDB-backed) for stateful aggregations.
- **CQRS**: Separate write model (Kafka) from read model (database projection).

---

## Anti-Pattern 6: Not Handling Poison Pills — Partition Stuck Forever

### The Mistake
```java
@KafkaListener(topics = "orders")
public void processOrder(byte[] payload) {
    Order order = objectMapper.readValue(payload, Order.class); // Throws on malformed JSON
    // Consumer retries this offset forever — partition stuck, lag grows
}
```

### Why It Is Catastrophic
Without `ErrorHandlingDeserializer`, deserialization failure causes the container to:
1. Seek back to the same offset.
2. Re-poll and re-throw infinitely.
3. Block ALL messages behind the poison pill on that partition.

### The Fix
```java
// config: ErrorHandlingDeserializer wraps the real deserializer
// If deserialization fails, the record's value() is null, and
// DeserializationException is stored in the header
props.put(VALUE_DESERIALIZER_CLASS_CONFIG, ErrorHandlingDeserializer.class);

// Handler: send to DLQ immediately (non-retryable)
errorHandler.addNotRetryableExceptions(SerializationException.class);
```

---

## Anti-Pattern 7: Synchronous `kafkaTemplate.send().get()` in the Hot Path

### The Mistake
```java
@PostMapping("/orders")
public ResponseEntity<Order> createOrder(@RequestBody OrderRequest req) {
    Order order = orderService.save(req);
    // BLOCKS the HTTP thread until Kafka broker ACKs! (typically 5-50ms)
    kafkaTemplate.send("orders", order.toJson()).get(5, TimeUnit.SECONDS);
    return ResponseEntity.ok(order);
}
```

### Why It Kills Throughput
Each HTTP thread is held for 5–50ms per Kafka round-trip. With 200 Tomcat threads at 20ms/ack:
`200 threads / 0.02s = 10,000 req/s max throughput` — entirely limited by Kafka ACK latency.

### The Fix
```java
// Fire-and-forget with error callback — non-blocking
ListenableFuture<SendResult<String, Object>> future =
    kafkaTemplate.send("orders", order.toJson());
future.addCallback(
    result -> log.debug("Sent: {}", result.getRecordMetadata().offset()),
    ex     -> dlqService.sendToDlq(order, ex) // compensate on failure
);
return ResponseEntity.ok(order); // Return immediately — don't wait
```

---

## Anti-Pattern 8: Overusing `enable.idempotence=true` Without Understanding the Cost

### The Misconception
Many teams enable `enable.idempotence=true` on Kafka producers thinking it guarantees
exactly-once semantics end-to-end.

### The Reality
Producer idempotence (`enable.idempotence=true`) only prevents **duplicate writes on producer
retry within a single session**. It does NOT protect against:
- Consumer re-processing the same message after a crash (use idempotent consumer).
- Duplicate produces from two producer instances (use Kafka Transactions + `transactional.id`).
- Application-level duplicates from Saga retries (use DB idempotency key).

**Performance cost**: Idempotence requires `acks=all` (all ISR replicas must ACK) and
`max.in.flight.requests.per.connection=5` (enforced). This adds ~2–5ms latency per batch.

### When to Use What

| Guarantee | Mechanism | Latency Cost |
|---|---|---|
| No duplicate produce on retry | `enable.idempotence=true` | ~2ms |
| No duplicate consume on crash | Idempotent consumer (DB key) | ~1ms DB read |
| Exactly-once end-to-end | Kafka Transactions (`transactional.id`) | ~5–20ms |
| Cross-service exactly-once | Saga + compensating transactions | 0 (async) |


---

## Anti-Pattern 1: Dual-Writing (Writing to DB, then Calling Kafka Producer)

### The Mistake
```java
@Transactional
public void createOrder(OrderRequest req) {
    orderRepository.save(new Order(req)); // DB Write
    kafkaTemplate.send("orders", req.toJson()); // External Network Write
}
```

### Why It Fails
1. **Network Crash Scenario**: The database transaction commits successfully, but the network to Kafka drops or Kafka broker rejects the write. The order exists in DB, but the event is never published! Downstream billing and inventory never fulfill the order.
2. **Crash Before Commit**: `kafkaTemplate.send()` succeeds, but the database rolls back on constraint violation or power failure. Downstream consumers charge the customer for an order that does not exist in the database!

### The Correct Production Fix
Use the **Transactional Outbox Pattern**:
Write both the order entity and an `OutboxEvent` entity within the same single ACID database transaction. Read the outbox via Change Data Capture (Debezium) or an async forwarder.

---

## Anti-Pattern 2: Hot Partition Keys (Severe Data Skew)

### The Mistake
Using a coarse or non-uniform partition key, such as `country_code` or `tenant_type`:
```java
// BAD: 90% of customers are in "US"
kafkaTemplate.send("orders", order.getCountryCode(), orderPayload);
```

### Why It Fails
All US transactions hash to the exact same partition (e.g. Partition 3).
- Partition 3 receives 90,000 req/s while Partitions 0, 1, 2 receive 500 req/s.
- The single consumer assigned to Partition 3 experiences massive lag and CPU starvation, while other consumer pods sit idle.

### The Correct Production Fix
Use fine-grained composite partition keys with high entropy, such as `customerId` or `orderId`.
