# EXERCISES: Event-Driven & Kafka Engineering
## Lab 11 | Production Engineering Academy — Top 0.0001% Engineering

---

## Exercise 1: Non-Blocking Retry & DLQ Consumer

**Objective**: Build a production-hardened Kafka consumer that survives poison pills, retries
transient failures with exponential backoff, and advances partition offsets without blocking.

### Setup
```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka-test</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>kafka</artifactId>
    <scope>test</scope>
</dependency>
```

### Tasks
1. Start an embedded Kafka using `@EmbeddedKafka(partitions = 3, topics = {"orders", "orders.DLT"})`.
2. Configure `ProductionKafkaConsumerConfig` with `ErrorHandlingDeserializer` and `DeadLetterPublishingRecoverer`.
3. Publish 5 test records to `orders`:
   - Record A: Valid `OrderEvent` JSON.
   - Record B: `{"orderId": null, "amount": "INVALID_NUMBER"}` — triggers `JsonParseException`.
   - Record C: Valid `OrderEvent` JSON.
   - Record D: Triggers a transient `RuntimeException` on first 2 attempts (use a counter).
   - Record E: Valid `OrderEvent` JSON.

4. **Acceptance Criteria**:
   - Records A, C, E: processed exactly once.
   - Record B: routed to `orders.DLT` within 500ms (non-retryable).
   - Record D: succeeds on attempt 3 (after 500ms + 1s backoff). NOT routed to DLQ.
   - No record is stuck waiting behind another — verify by asserting C is consumed before D retries complete.

### Verification
```java
// Use ConsumerRecord headers to verify DLQ metadata
ConsumerRecord<String, byte[]> dlqRecord = dlqConsumer.poll(Duration.ofSeconds(5))
    .records("orders.DLT").iterator().next();
assertThat(new String(dlqRecord.headers().lastHeader("kafka_dlt-exception-message").value()))
    .contains("JsonParseException");
```

---

## Exercise 2: Transactional Outbox with Atomicity Verification

**Objective**: Prove that order + outbox row are atomically written, and that a transaction rollback
leaves no orphaned events in the outbox table.

### Tasks
1. Create `Order` entity and `OutboxEvent` entity sharing the same PostgreSQL database (use Testcontainers `PostgreSQLContainer`).
2. Implement `OrderService.createOrder()` writing both in a single `@Transactional` method.
3. **Test A — Happy path**: Create a valid order. Assert `outbox_events` contains exactly 1 row with `event_type = 'ORDER_CREATED'` and `aggregate_id = order.getId()`.
4. **Test B — Rollback atomicity**: Configure a `@Transactional` method to throw `DataIntegrityViolationException` after inserting the order but before returning. Assert:
   - `orders` table has 0 rows.
   - `outbox_events` table has 0 rows.
   - *(If 1 row exists in `outbox_events` but 0 in `orders` → you have the dual-write bug.)*

5. **Test C — Async poller**: Implement a `@Scheduled(fixedDelay = 100)` poller using
   `SELECT ... FOR UPDATE SKIP LOCKED`. Assert that within 500ms of order creation, the
   corresponding Kafka record appears on the `outbox.Order` topic.

---

## Exercise 3: Full Saga Orchestration — Happy Path + Compensation

**Objective**: Implement a 3-step saga (inventory → payment → ship) with compensating transactions
when payment fails.

### Tasks
1. Create 3 embedded Kafka topics: `inventory-commands`, `inventory-events`, `payment-commands`, `payment-events`, `order-events`.
2. Implement `OrderFulfilmentSagaOrchestrator` as a `@KafkaListener`.
3. Implement stub handlers for inventory and payment that publish results to their event topics.

4. **Test A — Happy path**:
   - Publish `OrderCreatedEvent` to `outbox.Order`.
   - Assert sequence: `ReserveInventoryCommand` → `InventoryReservedEvent` → `ChargePaymentCommand` → `PaymentChargedEvent` → `ShipOrderCommand` → order status `SHIPPED`.

5. **Test B — Payment failure + compensation**:
   - Configure payment stub to publish `PaymentFailedEvent`.
   - Assert: `ReleaseInventoryCommand` is published to `inventory-commands` (compensation).
   - Assert: `OrderCancelledEvent` published with reason `PAYMENT_FAILED`.
   - Assert: No `ShipOrderCommand` ever published (compensation short-circuits).

6. **Verify idempotency**: Replay the `OrderCreatedEvent` twice. Assert saga executes only once (idempotency key check).

---

## Exercise 4: LMAX Disruptor Benchmark — False Sharing vs Padded

**Objective**: Empirically measure the performance difference between a false-sharing `OrderEvent`
and a cache-line padded version using JMH.

### Setup
```xml
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-core</artifactId>
    <version>1.37</version>
</dependency>
```

### Tasks
1. Create two `OrderEvent` variants:
   - `UnpaddedOrderEvent`: fields `long orderId, double price, long volume` (48 bytes — fits in one cache line but shared with the Sequence counter).
   - `PaddedOrderEvent`: same fields + `@Contended` annotation (or manual `long p1..p7` padding to 128 bytes).

2. Write JMH benchmark:
```java
@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.SECONDS)
@State(Scope.Thread)
public class DisruptorFalseSharingBenchmark {
    private Disruptor<UnpaddedOrderEvent> unpaddedDisruptor;
    private Disruptor<PaddedOrderEvent>   paddedDisruptor;

    @Benchmark
    public void unpaddedRingBuffer(Blackhole bh) {
        long seq = unpaddedDisruptor.getRingBuffer().next();
        try {
            UnpaddedOrderEvent e = unpaddedDisruptor.getRingBuffer().get(seq);
            e.orderId = seq;
            bh.consume(e.price);
        } finally {
            unpaddedDisruptor.getRingBuffer().publish(seq);
        }
    }
    // Mirror for padded variant
}
```

3. Run benchmark: `java -jar target/benchmarks.jar -f 2 -wi 5 -i 10`

4. **Expected outcome**: Padded variant should be 15–40% faster throughput due to eliminated false sharing on the sequence counter.

5. **Extend**: Add a 3rd benchmark with `ProducerType.MULTI` and 4 threads. Measure CAS retry rate using `AtomicLong` and compare with `tryNext(100)` batch claiming.

---

## Exercise 5: Schema Registry — BACKWARD Compatibility Enforcement

**Objective**: Prove that the Schema Registry enforces backward compatibility and rejects incompatible schema changes at CI time.

### Tasks
1. Start Confluent Schema Registry using Testcontainers:
```java
@Container
static SchemaRegistryContainer schemaRegistry = new SchemaRegistryContainer("7.5.0")
    .withKafka(kafkaContainer);
```

2. Register initial `OrderEvent` Avro schema (v1):
```json
{
  "type": "record", "name": "OrderEvent",
  "fields": [
    {"name": "orderId", "type": "string"},
    {"name": "amount",  "type": "double"}
  ]
}
```

3. **Test A — Compatible evolution (BACKWARD)**:
   - Attempt to register v2 with a NEW field `currency` with default `"USD"`.
   - Assert: Registry accepts v2 (default value makes it backward compatible).

4. **Test B — Incompatible evolution**:
   - Attempt to register v3 that REMOVES `amount`.
   - Assert: Registry rejects with `SchemaRegistryException: Incompatible schema`.

5. **Test C — Consumer compatibility**:
   - Produce 100 records using v2 schema.
   - Consume using v1 schema deserializer.
   - Assert: All 100 records consumed successfully (v1 consumer ignores unknown `currency` field).

---

## Exercise 6: Kafka Streams Exactly-Once — Zombie Fencing Under Broker Failover

**Objective**: Prove that `EXACTLY_ONCE_V2` prevents duplicate output after a broker leader failover, and that zombie tasks are fenced.

### Tasks
1. Start a 3-broker Kafka cluster using Testcontainers.
2. Create a Kafka Streams application that reads from `orders-input`, increments a counter per
   `customerId`, and writes the running total to `order-totals`.
3. Configure with `EXACTLY_ONCE_V2`.

4. **Test A — Normal operation**:
   - Produce 1,000 records with 10 unique customer IDs (100 per customer).
   - Assert: `order-totals` contains exactly 100 per customer — no duplicates.

5. **Test B — Broker failover during processing**:
   - Produce 500 records, then trigger leader failover on the input topic partition:
   ```bash
   kafka-leader-election.sh --bootstrap-server broker:9092 --election-type UNCLEAN \
     --topic orders-input --partition 0
   ```
   - Produce remaining 500 records.
   - Assert: `order-totals` still contains exactly 100 per customer (no duplicates from replay).

6. **Test C — Verify fencing log**:
   - Assert that `ProducerFencedException` appears in Kafka Streams logs during the failover.
   - This proves zombie fencing is active — the old task's transaction was aborted.


---

## Exercise 1: Build a Non-Blocking Retry & DLQ Consumer

### Objective
Implement a robust Kafka consumer that survives poison pill messages and retries transient failures across dedicated backoff topics without blocking partition progression.

### Tasks
1. Set up an embedded Kafka broker using `@EmbeddedKafka` or Testcontainers Kafka.
2. Configure Spring Kafka with `ErrorHandlingDeserializer` and `DeadLetterPublishingRecoverer`.
3. Publish 3 test records:
   - Record 1: Valid payment JSON.
   - Record 2: Malformed poison pill JSON (unparseable).
   - Record 3: Valid payment JSON.
4. Verify that:
   - Record 1 processes successfully.
   - Record 2 is automatically routed to `orders-dlq` topic with exception stack trace headers.
   - Record 3 is processed immediately without waiting or getting blocked behind Record 2.

---

## Exercise 2: Implement the Transactional Outbox Pattern

### Tasks
1. Create a Spring Boot transaction that inserts a Customer order and an `OutboxEvent` in a single `@Transactional` method.
2. Throw an unexpected `DataIntegrityViolationException` midway: verify that both order and outbox record roll back atomically.
3. Build an asynchronous poller with `FOR UPDATE SKIP LOCKED` that publishes outbox records to Kafka and marks them as `published = true`.
