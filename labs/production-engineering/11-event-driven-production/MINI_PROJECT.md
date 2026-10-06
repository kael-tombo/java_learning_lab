# Lab 11: Event-Driven Architecture & Kafka in Production — Mini Project

## Project: `EventLab` — An Order Pipeline with Provable Delivery Guarantees

**Time**: 12–16 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, Spring Kafka, Kafka (KRaft, single node via Testcontainers or docker-compose), PostgreSQL, Avro + Schema Registry, Debezium or a hand-rolled outbox relay, Micrometer/Prometheus

Build an order pipeline that survives every failure mode in this lab, and *prove* each guarantee with a test rather than an assertion.

---

## Part 1 — Topology

```
[orders-api]  --(POST /orders)--> [orders DB: orders + outbox]
                                     |
                                     v
                              [outbox-relay] --produce--> Kafka: order-events (3 partitions, Avro)
                                                       |
              +----------------------+---------------------+-------------------+
              v                      v                     v                   v
      [inventory-svc]        [billing-svc]         [search-indexer]    [audit-archiver]
      (idempotent, 2 parts)  (idempotent)          (idempotent)        (idempotent, DLT)
```

Plus a deliberately broken topic for the schema-evolution exercises.

---

## Part 2 — Producer and consumer baselines

### 2.1 Safe producer

```yaml
# application.yml
spring:
  kafka:
    producer:
      acks: all                      # strongest; the default of "1" can lose records
      retries: 2147483647
      properties:
        enable.idempotence: true     # duplicate suppression per partition
        max.in.flight.requests.per.connection: 5
        linger.ms: 20
        batch.size: 65536
        compression.type: lz4
        delivery.timeout.ms: 120000
        request.timeout.ms: 30000
    template:
      observation-enabled: true
```

```java
@Component
class OrderEventPublisher {
    private final KafkaTemplate<String, OrderEvent> kafka;
    private final SchemaRegistry registry;

    public void publish(String orderId, OrderEvent event) {
        // key = aggregate id => per-order ordering inside one partition
        kafka.send("order-events", orderId, event)
            .whenComplete((result, ex) -> {
                if (ex != null) metrics.counter("publish.failed").increment();
                else metrics.counter("publish.ok").increment();
            });
    }
}
```

**Verify**: `kafka-configs.sh --describe --entity-type brokers` is not enough — assert the *producer* config with `kafka-console-consumer` output and a deliberate broker restart test in Part 6.

### 2.2 Consumer with correct commit discipline

```java
@KafkaListener(topics = "order-events", groupId = "inventory-svc",
               containerFactory = "pauseAndCommitFactory")
public void onOrderEvent(ConsumerRecord<String, OrderEvent> record,
                         Acknowledgment ack) {
    // 1. dedupe FIRST, in the same transaction as the effect
    if (!dedupe.markSeen(record.topic(), record.partition(), record.offset())) {
        ack.acknowledge();
        return;
    }
    // 2. do the work
    inventory.reserve(record.key(), record.value());
    // 3. then commit
    ack.acknowledge();
}
```

```java
@Bean
ConcurrentKafkaListenerContainerFactory<String, OrderEvent> pauseAndCommitFactory(
        ConsumerFactory<String, OrderEvent> cf, ContainerProperties props) {
    var f = new ConcurrentKafkaListenerContainerFactory<String, OrderEvent>();
    f.setConsumerFactory(cf);
    props.setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);
    props.setMaxPollInterval(Duration.ofMinutes(10));        // > worst-case batch time
    props.setMaxPollRecords(200);
    f.setCommonErrorHandler(new DefaultErrorHandler(
        new DeadLetterPublishingRecoverer(kafkaTemplate,
            (r, e) -> new TopicPartition(r.topic() + ".DLT", r.partition())),
        new FixedBackOff(1_000L, 4)));                        // 4 retries, 1 s apart, then DLT
    return f;
}
```

Consumer factory, tuned and *justified in a comment*:

```java
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 200);
props.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 600_000);   // 10 min: 200 × 800 ms = 160 s worst case
props.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 45_000);
props.put(ConsumerConfig.GROUP_INSTANCE_ID_CONFIG, "inventory-1");  // static membership: no rebalance on restart
props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
```

### 2.3 Idempotent consumer

```java
@Repository
class ProcessedEvents {
    /** Business key, so redelivery from ANY topic/offset is suppressed. */
    @Modifying
    @Query(value = """
        INSERT INTO processed_events (event_id, consumer_group, processed_at)
        VALUES (:eventId, :group, now())
        ON CONFLICT (event_id, consumer_group) DO NOTHING
        """, nativeQuery = true)
    int markProcessed(@Param("eventId") String eventId, @Param("group") String group);
}

@Service
class DedupeService {
    @Transactional
    public boolean firstTime(String eventId, String group) {
        return repo.markProcessed(eventId, group) == 1;   // 1 = inserted, 0 = already seen
    }
}
```

Every consumer method runs inside one `@Transactional` boundary that contains both the dedupe insert and the state change — otherwise a crash between them leaves you either double-processing or falsely-suppressed.

**Deliverable**: `CONSUMER_DESIGN.md` — commit discipline, dedup key choice, dedup TTL (bounded by the maximum redelivery window, not by retention), and the transaction boundary, with the reasoning for each.

---

## Part 3 — Transactional outbox

### 3.1 Schema

```sql
CREATE TABLE outbox (
  id            BIGSERIAL PRIMARY KEY,
  aggregate_id  TEXT NOT NULL,
  event_type    TEXT NOT NULL,
  payload       BYTEA NOT NULL,             -- Avro/JSON encoded
  headers       JSONB NOT NULL DEFAULT '{}',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at  TIMESTAMPTZ,
  attempts      INT NOT NULL DEFAULT 0
);
CREATE INDEX ON outbox (id) WHERE published_at IS NULL;   -- partial index: the relay's hot path
CREATE INDEX ON outbox (published_at) WHERE published_at IS NOT NULL;  -- for pruning
```

### 3.2 Write side (same transaction as the state change)

```java
@Service
@RequiredArgsConstructor
class OrderService {
    private final OrderRepository orders;
    private final OutboxRepository outbox;

    @Transactional
    public Order place(CreateOrder cmd) {
        Order order = orders.save(Order.from(cmd));
        outbox.insert(order.getId().toString(), "OrderCreated",
                      avroSerializer.toBytes(OrderCreatedEvent.of(order)), headers(cmd));
        return order;      // the event is committed atomically with the state — no dual-write gap
    }
}
```

### 3.3 Relay

```java
@Component
@RequiredArgsConstructor
class OutboxRelay {
    @Scheduled(fixedDelayString = "${outbox.poll-interval-ms:200}")
    @Transactional
    public void relay() {
        List<OutboxRow> batch = outbox.lockNextBatch(BATCH_SIZE);   // SELECT ... FOR UPDATE SKIP LOCKED
        for (OutboxRow row : batch) {
            try {
                kafkaTemplate.send(TOPIC, row.aggregateId(), row.payload()).get(SEND_TIMEOUT);
                outbox.markPublished(row.id());
            } catch (Exception e) {
                outbox.recordFailure(row.id(), e.getMessage());   // attempts++ ; give up -> alert, do NOT drop
            }
        }
    }
}
```

`lockNextBatch` matters: `FOR UPDATE SKIP LOCKED` lets multiple relay instances run without double-sending each row, and without blocking each other.

### 3.4 Prove the dual-write problem is gone

Test: kill the Kafka broker mid-relay, then restart it. Assert:
- No order exists in the DB without an outbox row.
- Every outbox row is eventually published exactly once *or* published more than once (at-least-once — state this, do not pretend otherwise).
- Consumers produce exactly one effect (dedupe working).

**Deliverable**: `OUTBOX_REPORT.md` with the failure-injection results and the measured publication lag (p50/p99 from `created_at` to `published_at`).

---

## Part 4 — Failure injection

### 4.1 Rebalance storm

```bash
# Slow the downstream so processing exceeds max.poll.interval.ms
docker compose exec postgres psql -c "ALTER SYSTEM SET statement_timeout='900ms';"
./run-load.sh 5000      # events/sec
```

Watch: lag climbing, consumer CPU ~0, `Rebalance` in the logs.

| Fix | Config | Poll cycle | Storm resolved? |
|---|---|---|---|
| none | 500 records × 800 ms | 400 s > 300 s | no |
| A | `max.poll.records=100` | 80 s | yes |
| B | `max.poll.interval.ms=900000` | 400 s < 900 s | yes (but 15-min crash window) |
| C | pause/commit/resume + `max.poll.records=500` | independent | yes (preferred) |

**Deliverable**: the table above, filled from measurements, with the trade-off of B called out.

### 4.2 Poison message

Publish a deliberately malformed event:

```bash
kafka-console-producer.sh --topic order-events --property "parse.key=true" --property "key.separator=|"
# emit OrderCreated with totalAmount = -999999 and an unknown currency code
```

Verify:
1. It retries 4 times, then lands in `order-events.DLT`.
2. The DLT record contains: original payload, original topic/partition/offset, exception class, attempt count, timestamp, correlation id, headers.
3. **The partition keeps moving** — subsequent valid messages are processed.
4. Alerting on DLT rate catches it in minutes; alerting on depth alone takes hours (compute both numbers).

**Deliverable**: `DLT_SPEC.md` plus the measured `detection_latency = DLT_depth / DLT_rate` for both alert strategies.

### 4.3 Hot partition

```java
// Drive 80% of traffic through one key.
for (int i = 0; i < 80_000; i++) kafka.send("order-events", "hot-key", event);
```

Measure per-partition rate, then fix with salting:

```java
String salted = orderId + "-" + ThreadLocalRandom.current().nextInt(16);  // sacrifices per-key ordering
```

State the trade-off explicitly: **salting trades ordering for parallelism**. Where ordering is required, do not salt — split the stream or add partitions on a new topic.

**Deliverable**: `SKEW_REPORT.md` with the per-partition table before and after.

---

## Part 5 — Schema evolution with Avro + Registry

```java
@Configuration
class AvroConfig {
    @Bean
    ProducerFactory<String, GenericRecord> avroFactory() {
        var props = new HashMap<String, Object>();
        props.put(AbstractKafkaSchemaSerDeConfig.SCHEMA_REGISTRY_URL_CONFIG, "http://registry:8081");
        props.put(AbstractKafkaSchemaSerDeConfig.SPECIFIC_AVRO_READER_CONFIG, false);
        return new DefaultKafkaProducerFactory<>(props);
    }
}
```

Registry settings:

```properties
# compatibility=BACKWARD_TRANSITIVE for a topic with multiple reader versions
order-events.compatibility.level=FULL_TRANSITIVE
```

Exercise these changes against the registry and record the verdict for each:

| Change | Expected | Why |
|---|---|---|
| Add field `channel` with default `"web"` | compatible | readers tolerate it |
| Remove field `couponCode` | **incompatible** | old data lacks nothing, but new data breaks forward readers |
| Rename `couponCode` → `promoCode` | **incompatible** | it is remove + add |
| `totalAmount: int` → `long` | **incompatible** (FULL) | type change |
| `int` → `long` with a default | **incompatible** (FULL) | promote types do not unify |
| Make optional field required | **incompatible** | old records lack it |
| Add enum symbol `PARTIALLY_SHIPPED` | compatible for writers | document that readers must tolerate unknown symbols |
| Add a new topic field `null` for a primitive | **incompatible** | primitives cannot be null |

Then demonstrate the safe alternative for a rename:

```java
@AvroName("promoCode")                        // keep the wire name, change the Java name
String promoCode;
// deprecated accessor retained so old consumers still compile
@Deprecated public String couponCode() { return promoCode; }
```

**Deliverable**: `SCHEMA_MATRIX.md` with the measured verdicts and the schema id at which each version became the writer schema.

---

## Part 6 — Chaos tests (run each and record the outcome)

| Test | Action | Success criteria |
|---|---|---|
| T1 | Kill broker mid-relay | no lost order, eventual publication, no double effect |
| T2 | Restart a consumer with `group.instance.id` set | no rebalance storm, lag resumes |
| T3 | Kill a consumer *without* `group.instance.id` | measure rebalance duration and duplicate processing (dedupe must absorb it) |
| T4 | Force a rebalance during processing | no lost offsets (MANUAL_IMMEDIATE + dedupe), no double effect |
| T5 | Expand partitions 3 → 6 on the same topic | ordering lost for ~50% of keys — document it |
| T6 | Truncate retention to 1 hour | demonstrate silent data loss with a 2-hour consumer outage |
| T7 | Poison the consumer's downstream (unavailable DB) | retries → DLT, partition keeps flowing |
| T8 | Fill the broker disk to 99% | observe and document the failure mode |

**Deliverable**: `CHAOS_RESULTS.md` — the table with measured outcomes and any fix required.

---

## Part 7 — Operational dashboard

Grafana panels that answer "is the pipeline healthy?" in 60 seconds:

- Produce rate vs consume rate (per topic), with the difference as lag growth rate.
- Consumer lag by group, and oldest-unconsumed age **compared against retention**.
- Consumer poll rate, poll latency, commit latency, commit failure rate.
- Rebalance count per group (a spike here is an early warning for the storm).
- Processing time per record (p99) vs `max.poll.interval.ms` — the margin is what matters.
- Outbox depth and oldest unpublished row age.
- DLT rate (5 min window) and depth.
- Per-partition rate (skew detection).
- Records per partition per group.

Alerts:

```yaml
- alert: ConsumerRebalanceLoop
  expr: increase(consumer_group_rebalances_total[5m]) > 5
  for: 2m
- alert: LagGrowingFasterThanDrain
  expr: deriv(kafka_consumergroup_lag[10m]) > 0
  for: 15m
- alert: PollIntervalMarginLow
  expr: histogram_quantile(0.99, sum by (le) (rate(consumer_record_processing_seconds_bucket[10m]))) * max_poll_records > max_poll_interval_ms * 0.8
- alert: OutboxBacklogGrowing
  expr: outbox_unpublished_oldest_seconds > 60
- alert: DltFlowing
  expr: increase(dlt_messages_total[5m]) > 500
- alert: RetentionWillExpireUnconsumed
  expr: kafka_consumergroup_oldest_unconsumed_age_seconds > kafka_topic_retention_ms * 0.7
```

The last alert is the one that prevents silent data loss. It is the most valuable line in this lab.

---

## Acceptance Criteria

- [ ] `CONSUMER_DESIGN.md` justifies commit discipline, dedup key, dedup TTL, and transaction boundary.
- [ ] Outbox survives broker failure mid-relay: no lost orders, eventual publication, no double effect. Measured publication lag reported.
- [ ] Rebalance storm reproduced with lag growing and CPU idle; three fixes measured, with the trade-off of each.
- [ ] Poison message → 4 retries → DLT; partition keeps flowing; DLT record contains everything needed to reproduce; detection latency computed for rate-based and depth-based alerting.
- [ ] Hot partition reproduced; salting applied with the ordering trade-off documented.
- [ ] `SCHEMA_MATRIX.md` shows measured verdicts for all 8 changes, including the two that surprise people.
- [ ] All 8 chaos tests run with recorded outcomes.
- [ ] Retention truncation demonstrates silent data loss, and the retention-expiry alert fires before it happens.
- [ ] Dashboard + alerts run live against the lab stack.

---

## Stretch

- Swap the polled relay for Debezium CDC and measure the publication-latency improvement.
- Implement a saga: `OrderCreated` → `PaymentAuthorized` → `InventoryReserved`, with compensating events and a compensating DLT, and measure the partial-saga rate.
- Add a compacted topic holding the current order state per `orderId` (a materialized view for a new consumer), so the new consumer does not have to replay the whole log.
- Model and demonstrate the cost of fan-out by adding an archive consumer group, and show the egress bill increase.
