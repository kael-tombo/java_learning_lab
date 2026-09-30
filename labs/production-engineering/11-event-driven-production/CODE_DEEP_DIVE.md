# CODE DEEP DIVE: Event-Driven & Kafka Production Engineering
## Lab 11 | Production Engineering Academy — Top 0.0001% Engineering

---

## Pattern 1: Production Kafka Consumer — Non-Blocking Retry + DLQ

```java
package com.learning.production.lab11;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.listener.ContainerProperties;
import org.springframework.kafka.listener.DeadLetterPublishingRecoverer;
import org.springframework.kafka.listener.DefaultErrorHandler;
import org.springframework.kafka.support.serializer.ErrorHandlingDeserializer;
import org.springframework.kafka.support.serializer.JsonDeserializer;
import org.springframework.util.backoff.ExponentialBackOff;
import java.util.HashMap;
import java.util.Map;

@Configuration
@EnableKafka
public class ProductionKafkaConsumerConfig {

    @Bean
    public ConsumerFactory<String, Object> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG,
                "kafka-broker-1:9092,kafka-broker-2:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processing-v2");

        // ── 1. Cooperative Sticky Assignor ─────────────────────────────────────
        // Default EagerAssignor: ALL consumers pause on ANY join/leave event.
        // CooperativeStickyAssignor: only the migrated partition pauses — others keep polling.
        props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
                "org.apache.kafka.clients.consumer.CooperativeStickyAssignor");

        // ── 2. Poll interval tuning (prevents false heartbeat eviction) ─────────
        // If onEvent() logic can take up to 5 minutes (e.g., calls slow downstream),
        // set MAX_POLL_INTERVAL_MS > worst-case processing time.
        // Rule: MAX_POLL_INTERVAL_MS > p99.9 processing time × MAX_POLL_RECORDS
        props.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 600_000); // 10 min
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG,    50);       // 50 × p99.9

        // ── 3. Manual offset management ─────────────────────────────────────────
        // NEVER use auto-commit in financial systems — records are lost on crash
        // between auto-commit interval and processing completion.
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG,  false);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG,  "earliest");

        // ── 4. Resilient deserialization (poison pill protection) ───────────────
        // Without ErrorHandlingDeserializer, a single malformed message blocks
        // the entire partition forever (consumer throws, retries same offset).
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG,
                ErrorHandlingDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG,
                ErrorHandlingDeserializer.class);
        props.put(ErrorHandlingDeserializer.KEY_DESERIALIZER_CLASS,
                StringDeserializer.class);
        props.put(ErrorHandlingDeserializer.VALUE_DESERIALIZER_CLASS,
                JsonDeserializer.class);
        props.put(JsonDeserializer.TRUSTED_PACKAGES, "com.learning.domain.*");

        return new DefaultKafkaConsumerFactory<>(props);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, Object> kafkaListenerContainerFactory(
            ConsumerFactory<String, Object> consumerFactory,
            KafkaTemplate<String, Object> kafkaTemplate) {

        ConcurrentKafkaListenerContainerFactory<String, Object> factory =
                new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);

        // Concurrency = number of partitions on the topic (max useful parallelism)
        factory.setConcurrency(4);
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.RECORD);

        // ── 5. Non-blocking retry with exponential backoff + DLQ ────────────────
        // DefaultErrorHandler replaces deprecated SeekToCurrentErrorHandler.
        // Key: backoff is PER-PARTITION — other partitions continue processing.
        ExponentialBackOff backOff = new ExponentialBackOff(500L, 2.0);
        backOff.setMaxAttempts(3); // 500ms → 1s → 2s → DLQ

        // DLQ topic = original topic + ".DLT" (e.g., "orders.DLT")
        DeadLetterPublishingRecoverer recoverer =
                new DeadLetterPublishingRecoverer(kafkaTemplate);
        DefaultErrorHandler errorHandler = new DefaultErrorHandler(recoverer, backOff);

        // ── 6. Non-retryable exceptions → straight to DLQ (no backoff wasted) ──
        errorHandler.addNotRetryableExceptions(
                org.apache.kafka.common.errors.SerializationException.class,
                com.fasterxml.jackson.core.JsonParseException.class
                // Add: NullPointerException if payload is always expected non-null
        );

        factory.setCommonErrorHandler(errorHandler);
        return factory;
    }
}
```

### Why `AckMode.RECORD` vs `AckMode.BATCH` Matters

| AckMode | Offset committed after | Risk on crash |
|---|---|---|
| `MANUAL_IMMEDIATE` | Explicit `ack.acknowledge()` call | Safest — developer controls commit point |
| `RECORD` | Each record is processed | Re-processes last record on restart |
| `BATCH` | Full poll batch processed | Re-processes entire last batch on crash |
| `AUTO` (never use) | Fixed time interval | Loses records between commit and crash |

> **Production rule**: Use `MANUAL_IMMEDIATE` for financial transactions. Use `BATCH` for
> high-throughput analytics where at-least-once re-processing is acceptable.

---

## Pattern 2: Transactional Outbox with Debezium CDC

### 2.1 The Outbox Entity (Same DB Transaction as the Business Entity)

```java
package com.learning.production.lab11;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "outbox_events",
       indexes = @Index(name = "idx_outbox_processed", columnList = "processed, created_at"))
public class OutboxEvent {

    @Id
    private UUID id;

    @Column(nullable = false)
    private String aggregateType;  // e.g., "Order"

    @Column(nullable = false)
    private String aggregateId;    // e.g., order UUID

    @Column(nullable = false)
    private String eventType;      // e.g., "ORDER_CREATED"

    @Column(columnDefinition = "TEXT", nullable = false)
    private String payload;        // JSON domain event

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private boolean processed = false;  // For polling-based fallback

    @Version
    private Long version;              // Optimistic lock — prevents double-publish

    public OutboxEvent() {}

    public OutboxEvent(String aggregateType, String aggregateId,
                       String eventType, String payload) {
        this.id            = UUID.randomUUID();
        this.aggregateType = aggregateType;
        this.aggregateId   = aggregateId;
        this.eventType     = eventType;
        this.payload       = payload;
        this.createdAt     = Instant.now();
    }
    // getters/setters omitted for brevity
}
```

### 2.2 Service Layer — Atomic DB + Outbox Write

```java
@Service
@Transactional
public class OrderService {

    private final OrderRepository orderRepository;
    private final OutboxEventRepository outboxRepository;
    private final ObjectMapper objectMapper;

    public OrderService(OrderRepository orderRepository,
                        OutboxEventRepository outboxRepository,
                        ObjectMapper objectMapper) {
        this.orderRepository = orderRepository;
        this.outboxRepository = outboxRepository;
        this.objectMapper = objectMapper;
    }

    public Order createOrder(OrderRequest req) throws JsonProcessingException {
        // ── Both writes in ONE ACID transaction ──────────────────────────────────
        // If the JVM crashes after save(order) but before save(outboxEvent),
        // the DB rolls back BOTH — no phantom order, no missing event.
        Order order = orderRepository.save(new Order(req));

        OrderCreatedEvent domainEvent = new OrderCreatedEvent(
            order.getId(), order.getCustomerId(),
            order.getTotal(), Instant.now()
        );

        outboxRepository.save(new OutboxEvent(
            "Order",
            order.getId().toString(),
            "ORDER_CREATED",
            objectMapper.writeValueAsString(domainEvent)
        ));

        return order;
        // Transaction commits here — both rows visible to Debezium WAL reader
    }
}
```

### 2.3 Debezium CDC Connector Configuration (PostgreSQL WAL)

```json
{
  "name": "outbox-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres-primary",
    "database.port":     "5432",
    "database.user":     "debezium",
    "database.password": "secret",
    "database.dbname":   "orders_db",
    "database.server.name": "orders-pg",
    "table.include.list": "public.outbox_events",

    "transforms": "outbox",
    "transforms.outbox.type":
        "io.debezium.transforms.outbox.EventRouter",
    "transforms.outbox.table.field.event.id":      "id",
    "transforms.outbox.table.field.event.key":     "aggregate_id",
    "transforms.outbox.table.field.event.payload": "payload",
    "transforms.outbox.route.by.field":            "aggregate_type",
    "transforms.outbox.route.topic.replacement":
        "outbox.${routedByValue}",

    "publication.name": "dbz_publication",
    "slot.name":        "debezium_outbox_slot",

    "heartbeat.interval.ms": "5000",
    "snapshot.mode": "never"
  }
}
```

> **Critical**: Replication slot `debezium_outbox_slot` holds WAL segments until Debezium reads
> them. If the Kafka Connect cluster goes down for hours, PostgreSQL WAL disk fills up → DB crash.
> **Monitor** `pg_replication_slots` lag bytes with Prometheus + alert at 5 GB.

---

## Pattern 3: Saga Orchestration — Distributed Transaction Without 2PC

```java
package com.learning.production.lab11;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * Saga Orchestrator for Order Fulfilment.
 *
 * Step sequence (happy path):
 *   ORDER_CREATED → ReserveInventory → INVENTORY_RESERVED
 *                                    → ChargePayment → PAYMENT_CHARGED
 *                                                    → ShipOrder → ORDER_SHIPPED
 *
 * Compensating transactions (rollback path):
 *   PAYMENT_FAILED → ReleaseInventory → INVENTORY_RELEASED → ORDER_CANCELLED
 */
@Component
public class OrderFulfilmentSagaOrchestrator {

    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final SagaStateRepository sagaRepository;

    public OrderFulfilmentSagaOrchestrator(KafkaTemplate<String, Object> kafkaTemplate,
                                           SagaStateRepository sagaRepository) {
        this.kafkaTemplate = kafkaTemplate;
        this.sagaRepository = sagaRepository;
    }

    // ── Step 1: Start the saga when an order is created ───────────────────────
    @KafkaListener(topics = "outbox.Order", groupId = "saga-orchestrator")
    @Transactional
    public void onOrderCreated(OrderCreatedEvent event) {
        // Persist saga state so orchestrator survives crashes
        sagaRepository.save(new SagaState(event.orderId(), SagaStep.RESERVE_INVENTORY));

        kafkaTemplate.send("inventory-commands",
            event.customerId(),
            new ReserveInventoryCommand(event.orderId(), event.items())
        );
    }

    // ── Step 2: Inventory reserved → charge payment ───────────────────────────
    @KafkaListener(topics = "inventory-events", groupId = "saga-orchestrator")
    @Transactional
    public void onInventoryEvent(InventoryEvent event) {
        SagaState state = sagaRepository.findByOrderId(event.orderId());

        if (event instanceof InventoryReservedEvent reserved) {
            state.advance(SagaStep.CHARGE_PAYMENT);
            sagaRepository.save(state);
            kafkaTemplate.send("payment-commands",
                reserved.customerId(),
                new ChargePaymentCommand(reserved.orderId(), reserved.total())
            );
        } else if (event instanceof InventoryFailedEvent failed) {
            // No inventory → cancel saga immediately (no compensation needed yet)
            state.advance(SagaStep.CANCELLED);
            sagaRepository.save(state);
            kafkaTemplate.send("order-events",
                failed.orderId(),
                new OrderCancelledEvent(failed.orderId(), "OUT_OF_STOCK")
            );
        }
    }

    // ── Step 3: Payment result → ship or compensate ───────────────────────────
    @KafkaListener(topics = "payment-events", groupId = "saga-orchestrator")
    @Transactional
    public void onPaymentEvent(PaymentEvent event) {
        SagaState state = sagaRepository.findByOrderId(event.orderId());

        if (event instanceof PaymentChargedEvent) {
            state.advance(SagaStep.SHIP_ORDER);
            sagaRepository.save(state);
            kafkaTemplate.send("shipping-commands",
                event.orderId(),
                new ShipOrderCommand(event.orderId())
            );
        } else if (event instanceof PaymentFailedEvent failed) {
            // COMPENSATING TRANSACTION: release the reserved inventory
            state.advance(SagaStep.COMPENSATING_RELEASE_INVENTORY);
            sagaRepository.save(state);
            kafkaTemplate.send("inventory-commands",
                failed.orderId(),
                new ReleaseInventoryCommand(failed.orderId())
            );
        }
    }
}
```

### Why Not 2-Phase Commit (2PC)?

| | 2PC | Saga |
|---|---|---|
| **Locks held** | Across all services until all vote | None (each step commits independently) |
| **Failure mode** | Coordinator crash → all services blocked | Failed step triggers compensating transaction |
| **Throughput** | Low (blocking protocol) | High (async, event-driven) |
| **Isolation** | Full ACID | Eventual consistency |
| **Suitable for** | Single-DB + single JVM | Distributed microservices |

---

## Pattern 4: Idempotent Consumer — At-Least-Once Delivery Safety

```java
@Service
public class IdempotentOrderConsumer {

    private final ProcessedEventRepository processedEvents;
    private final OrderRepository orders;

    // ── Exactly-once processing via DB idempotency key ────────────────────────
    @KafkaListener(topics = "orders", groupId = "order-consumer")
    @Transactional
    public void consume(ConsumerRecord<String, OrderCreatedEvent> record) {
        String idempotencyKey = record.topic()
                + "-" + record.partition()
                + "-" + record.offset();

        // ── Check: already processed? ─────────────────────────────────────────
        if (processedEvents.existsById(idempotencyKey)) {
            // Duplicate delivery — safe to skip (Kafka at-least-once guarantee)
            return;
        }

        OrderCreatedEvent event = record.value();

        // ── Business logic ───────────────────────────────────────────────────
        orders.save(new Order(event));

        // ── Mark as processed (same transaction) ─────────────────────────────
        // If JVM crashes here before commit, both writes roll back.
        // Kafka offset NOT committed → message redelivered → idempotency key
        // not yet in DB → processed again safely.
        processedEvents.save(new ProcessedEvent(idempotencyKey, Instant.now()));

        // Offset committed after @Transactional commits (AckMode.RECORD)
    }
}
```

> **Performance note**: The `processed_events` table grows unboundedly. Add a TTL cleanup job:
> ```sql
> DELETE FROM processed_events WHERE processed_at < NOW() - INTERVAL '7 days';
> ```
> Run this as a pg_cron job, not from the Java app (avoid row-level locking on the hot path).

---

## Pattern 5: Reactive Kafka with Back-Pressure (Project Reactor)

```java
package com.learning.production.lab11;

import reactor.core.publisher.Flux;
import reactor.core.scheduler.Schedulers;
import reactor.kafka.receiver.KafkaReceiver;
import reactor.kafka.receiver.ReceiverOptions;
import reactor.kafka.receiver.ReceiverRecord;

import java.time.Duration;
import java.util.Collections;
import java.util.Map;

public class ReactiveKafkaPipeline {

    public static Flux<Void> buildPipeline(Map<String, Object> consumerProps,
                                           OrderProcessor processor) {
        ReceiverOptions<String, byte[]> options = ReceiverOptions
            .<String, byte[]>create(consumerProps)
            .subscription(Collections.singleton("orders"))
            // Back-pressure: only fetch 100 records at a time from Kafka broker
            .maxCommitAttempts(3)
            .commitBatchSize(100);

        return KafkaReceiver.create(options)
            .receive()
            // ── Window into 50ms batches — reduces Kafka offset commits ─────────
            .windowTimeout(100, Duration.ofMillis(50))
            .flatMap(batch -> batch
                // ── Process each record on a bounded elastic scheduler ────────
                // Prevents a slow downstream from blocking the Kafka poll thread
                .publishOn(Schedulers.boundedElastic())
                .concatMap(record -> processRecord(record, processor))
            )
            // ── Error recovery: log and continue (no poison pill blocking) ─────
            .onErrorContinue((err, record) -> {
                System.err.println("Failed to process: " + record + " → " + err.getMessage());
                // In production: send to DLQ here
            });
    }

    private static Flux<Void> processRecord(ReceiverRecord<String, byte[]> record,
                                             OrderProcessor processor) {
        return Flux.fromCallable(() -> {
                processor.process(record.value());
                return record;
            })
            .doOnNext(r -> r.receiverOffset().acknowledge())
            .then()
            .flux();
    }
}
```

### Back-Pressure vs. Pull Model

```
Reactive Kafka (pull):          Standard Spring Kafka (push):
  KafkaReceiver ──request(100)──>  Broker   ContainerFactory ──poll()──> Broker
  Broker ──────100 records──────>  Consumer  Broker ──500 records──────> Consumer
  Process batch ─────────────────> Ack       Process each ──────────────> Ack
  request(100) again ────────────>           poll() again immediately──>
                                            (no flow control!)
```

Reactive Kafka propagates back-pressure from the downstream processor back to the Kafka poll
layer — if the processor is slow, fewer records are fetched. Standard Spring Kafka will continue
polling at the configured `max.poll.records` rate, filling the internal queue unboundedly.


---

## Pattern 1: Production Kafka Consumer with Non-Blocking Dead Letter Queue (DLQ)

```java
package com.learning.production.lab11;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.listener.ContainerProperties;
import org.springframework.kafka.listener.DeadLetterPublishingRecoverer;
import org.springframework.kafka.listener.DefaultErrorHandler;
import org.springframework.kafka.support.serializer.ErrorHandlingDeserializer;
import org.springframework.kafka.support.serializer.JsonDeserializer;
import org.springframework.util.backoff.ExponentialBackOff;

import java.util.HashMap;
import java.util.Map;

@Configuration
@EnableKafka
public class ProductionKafkaConsumerConfig {

    @Bean
    public ConsumerFactory<String, Object> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka-broker-1:9092,kafka-broker-2:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processing-v2");

        // 1. Cooperative Sticky Assignor (Eliminates Stop-the-world rebalance storms)
        props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
                "org.apache.kafka.clients.consumer.CooperativeStickyAssignor");

        // 2. Poll pacing to prevent false eviction
        props.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 600_000); // 10 minutes
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 50);          // Max 50 items per poll

        // 3. Offset management: Manual immediate ack
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        // 4. Resilient Deserialization Wrappers (Catches poison pills before listener)
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, ErrorHandlingDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, ErrorHandlingDeserializer.class);
        props.put(ErrorHandlingDeserializer.KEY_DESERIALIZER_CLASS, StringDeserializer.class);
        props.put(ErrorHandlingDeserializer.VALUE_DESERIALIZER_CLASS, JsonDeserializer.class);
        props.put(JsonDeserializer.TRUSTED_PACKAGES, "com.learning.domain.*");

        return new DefaultKafkaConsumerFactory<>(props);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, Object> kafkaListenerContainerFactory(
            ConsumerFactory<String, Object> consumerFactory,
            KafkaTemplate<String, Object> kafkaTemplate) {

        ConcurrentKafkaListenerContainerFactory<String, Object> factory =
                new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);
        factory.setConcurrency(4); // 4 consumer worker threads per container pod
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.RECORD);

        // 5. Non-Blocking Retry with Exponential Backoff + DLQ Recovery
        ExponentialBackOff backOff = new ExponentialBackOff(500L, 2.0); // 500ms, 1s, 2s
        backOff.setMaxAttempts(3);

        DeadLetterPublishingRecoverer recoverer = new DeadLetterPublishingRecoverer(kafkaTemplate);
        DefaultErrorHandler errorHandler = new DefaultErrorHandler(recoverer, backOff);

        // Do NOT retry poison pill serialization errors; send directly to DLQ
        errorHandler.addNotRetryableExceptions(
                org.apache.kafka.common.errors.SerializationException.class,
                com.fasterxml.jackson.core.JsonParseException.class
        );

        factory.setCommonErrorHandler(errorHandler);
        return factory;
    }
}
```

---

## Pattern 2: The Transactional Outbox Entity & Repository

```java
package com.learning.production.lab11;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "outbox_events")
public class OutboxEvent {
    @Id
    private UUID id;

    @Column(nullable = false)
    private String aggregateType;

    @Column(nullable = false)
    private String aggregateId;

    @Column(nullable = false)
    private String eventType;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String payload; // JSON representation of the domain event

    @Column(nullable = false)
    private Instant createdAt;

    public OutboxEvent() {}

    public OutboxEvent(String aggregateType, String aggregateId, String eventType, String payload) {
        this.id = UUID.randomUUID();
        this.aggregateType = aggregateType;
        this.aggregateId = aggregateId;
        this.eventType = eventType;
        this.payload = payload;
        this.createdAt = Instant.now();
    }
    // Getters and Setters
}
```
