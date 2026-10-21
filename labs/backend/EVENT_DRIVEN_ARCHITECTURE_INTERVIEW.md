# Event-Driven Architecture Deep Interview Guide — Wave 6

> Target: 350+ lines covering concepts, technologies (Kafka, RabbitMQ, Cloud Stream, Axon), patterns (Event Sourcing, CQRS, Saga, Outbox), interview questions

---

## 1. Concepts

### Q: Event-driven vs Event Sourcing vs CQRS — what is the difference?

**Answer:**

| Pattern | What It Does | Key Idea |
|---------|-------------|----------|
| **Event-Driven** | Services react to events as they happen | Asynchronous communication, loose coupling |
| **Event Sourcing** | Store state changes as a sequence of events | Current state is derived by replaying events |
| **CQRS** | Separate read and write models | Different data structures for commands vs queries |

**Event-Driven != Event Sourcing:**
- Event-driven: Services publish/consume events. State is stored in current form (not as events).
- Event sourcing: State IS the event log. No current-state table; events are the source of truth.

```java
@EventSourcedAggregate
public class Account {
    @AggregateIdentifier private AccountId id;
    private long balance;

    @CommandHandler
    public Account(OpenAccountCommand cmd) {
        apply(new AccountOpenedEvent(cmd.id(), cmd.initialBalance()));
    }

    @EventSourcingHandler
    public void on(AccountOpenedEvent event) {
        this.id = event.id();
        this.balance = event.initialBalance();
    }
}
```

**Company Frequency:** Netflix (often), Uber (often), Spotify (high)

---

### Q: Event notification vs Event-carried state transfer vs Event sourcing

**Answer:**

| Pattern | Event Contains | Consumer Action | Coupling |
|---------|---------------|-----------------|----------|
| **Event Notification** | Just happened (`orderId: 123`) | Fetch remaining data via API | Loose (consumer fetches) |
| **Event-Carried State Transfer** | All needed data | Use directly, no fetch needed | Tighter (knows schema) |
| **Event Sourcing** | State mutation | Replay events to build state | Tightest (all state from events) |

```java
public record OrderCreatedEvent(String orderId) { }
public record OrderCreatedEvent(String orderId, String customerId, Money total) { }
```

---

### Q: Idempotency and exactly-once processing

**Answer:** Processing the same event multiple times produces the same result.

```java
@Service
public class PaymentConsumer {
    @KafkaListener(topics = "payment-events")
    public void handlePayment(PaymentEvent event) {
        try {
            paymentRepository.insertWithIdempotencyKey(
                new PaymentRecord(event.eventId(), event.orderId(), event.amount()));
        } catch (DuplicateKeyException e) {
            return; // Already processed
        }
    }
}
```

**Exactly-once semantics:**
- Kafka: Idempotent producer + read_committed isolation + transactional API
- RabbitMQ: Publisher confirms + consumer ack + idempotent consumer
- Database: Idempotency key + unique constraint

**Company Frequency:** All companies (universal)

---

### Q: Ordering guarantees, partitions, keys

**Answer:**
- Within a partition: Guaranteed order
- Across partitions: No ordering guarantee
- Key determines partition: Same key -> same partition -> ordered

```java
@Bean
public NewTopic orderEventsTopic() {
    return TopicBuilder.name("order-events")
        .partitions(6).replicas(3)
        .config(TopicConfig.MIN_IN_SYNC_REPLICAS_CONFIG, "2")
        .build();
}

// Producer with key ensures ordering per orderId
kafka.send("order-events", event.orderId(), event);
```

**Company Frequency:** Amazon (high), Netflix (high), Uber (high)

---

## 2. Technologies

### Q: Apache Kafka — topics, partitions, consumer groups

**Answer:**

```
Topic
├── Partition 0 (ordered, immutable)
├── Partition 1
└── Partition 2

Consumer Group
├── Consumer 1 -> Partition 0
└── Consumer 2 -> Partition 1, Partition 2
```

```java
@Component
public class OrderConsumer {
    @KafkaListener(topics = "orders", groupId = "order-processor")
    public void consume(ConsumerRecord<String, Order> record, Acknowledgment ack) {
        try {
            processOrder(record.value());
            ack.acknowledge();
        } catch (RetryableException e) {
            // Will retry
        } catch (FatalException e) {
            kafkaTemplate.send("orders-dlq", record.key(), record.value());
            ack.acknowledge();
        }
    }
}
```

**Company Frequency:** All companies (universal)

---

### Q: RabbitMQ — exchanges, bindings, queues

**Answer:**

| Type | Routing | Use Case |
|------|---------|----------|
| **Direct** | Exact routing key | Task distribution |
| **Topic** | Pattern match | Pub-sub with routing |
| **Fanout** | All queues bound | Broadcast |
| **Headers** | Headers match | Complex routing |

```java
@Bean
public DirectExchange orderExchange() {
    return new DirectExchange("order.exchange");
}

@Bean
public Queue orderQueue() {
    return QueueBuilder.durable("order.queue")
        .deadLetterExchange("order.dlx")
        .deadLetterRoutingKey("order.dead")
        .build();
}

@Bean
public Binding orderBinding() {
    return BindingBuilder.bind(orderQueue())
        .to(orderExchange())
        .with("order.created");
}
```

**Company Frequency:** Amazon (medium), Google (medium), smaller companies (high)

---

### Q: Spring Cloud Stream — functional programming model

**Answer:**

```java
@SpringBootApplication
public class EventProcessingApplication {

    @Bean
    public Consumer<OrderCreatedEvent> handleOrderCreated() {
        return event -> orderService.process(event);
    }

    @Bean
    public Function<OrderCreatedEvent, PaymentRequestEvent> processPayment() {
        return event -> new PaymentRequestEvent(
            event.orderId(), event.customerId(), event.amount());
    }
}
```

```yaml
spring:
  cloud:
    stream:
      bindings:
        handleOrderCreated-in-0:
          destination: order-events
          group: order-service-group
        processPayment-in-0:
          destination: order-events
        processPayment-out-0:
          destination: payment-requests
      kafka:
        binder:
          brokers: kafka:9092
```

**Company Frequency:** Netflix (often), Google (medium), Pivotal (high)

---

### Q: Axon Framework — Aggregate, Command Handler, Event Handler, Saga

**Answer:**

```java
@Aggregate
public class OrderAggregate {
    @AggregateIdentifier private String orderId;
    private OrderStatus status;

    @CommandHandler
    public OrderAggregate(CreateOrderCommand cmd) {
        apply(new OrderCreatedEvent(cmd.orderId(), cmd.items()));
    }

    @EventSourcingHandler
    public void on(OrderCreatedEvent event) {
        this.orderId = event.orderId();
        this.status = OrderStatus.CREATED;
    }
}

@Saga
public class OrderFulfillmentSaga {
    @Autowired private transient CommandGateway commandGateway;

    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void on(OrderCreatedEvent event) {
        commandGateway.send(new ReserveInventoryCommand(event.orderId(), event.items()));
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void on(InventoryReservedEvent event) {
        commandGateway.send(new ProcessPaymentCommand(event.orderId(), event.total()));
    }

    @EndSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void on(PaymentProcessedEvent event) {
        commandGateway.send(new ConfirmOrderCommand(event.orderId()));
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void on(InventoryReserveFailedEvent event) {
        commandGateway.send(new CancelOrderCommand(event.orderId()));
        SagaLifecycle.end();
    }
}
```

**Company Frequency:** Axon/Pivotal (essential), financial companies (high)

---

## 3. Patterns

### Q: Event sourcing with Spring Boot (full example)

**Answer:**

```java
@Repository
public class EventStore {
    private final JdbcTemplate jdbc;
    private final ObjectMapper mapper;

    public void save(String aggregateId, int version, Object event) {
        jdbc.update(
            "INSERT INTO events (aggregate_id, version, event_type, event_data, created_at) VALUES (?, ?, ?, ?, ?)",
            aggregateId, version, event.getClass().getName(),
            mapper.writeValueAsString(event), Instant.now());
    }

    public List<Object> load(String aggregateId) {
        return jdbc.query(
            "SELECT event_type, event_data FROM events WHERE aggregate_id = ? ORDER BY version ASC",
            rs -> {
                List<Object> events = new ArrayList<>();
                while (rs.next()) {
                    Class<?> type = Class.forName(rs.getString("event_type"));
                    events.add(mapper.readValue(rs.getString("event_data"), type));
                }
                return events;
            }, aggregateId);
    }
}
```

**Schema:**
```sql
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    aggregate_id VARCHAR(255) NOT NULL,
    version INT NOT NULL,
    event_type VARCHAR(500) NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(aggregate_id, version)
);
```

**Company Frequency:** Financial services (high), retail (medium)

---

### Q: Outbox pattern — reliable event publishing

**Answer:**
Problem: Dual-write (DB + message broker) is not atomic.

Solution: Write event to outbox table in same DB transaction. A separate process reads and publishes.

```java
@Service
public class OrderService {
    @Transactional
    public void createOrder(CreateOrderRequest req) {
        Order order = orderRepository.save(new Order(req));
        outboxRepository.save(new OutboxMessage(
            UUID.randomUUID().toString(),
            "OrderCreated",
            objectMapper.writeValueAsString(new OrderCreatedEvent(order.getId())),
            Instant.now()));
    }
}

@Component
public class OutboxPublisher {
    @Scheduled(fixedDelay = 1000)
    @Transactional
    public void publishOutbox() {
        List<OutboxMessage> messages = outboxRepository.findTop100ByPublishedFalseOrderByCreatedAt();
        for (OutboxMessage msg : messages) {
            try {
                kafka.send(msg.getTopic(), msg.getPayload()).get(5, TimeUnit.SECONDS);
                msg.setPublished(true);
                outboxRepository.save(msg);
            } catch (Exception e) {
                log.error("Failed to publish: {}", msg.getId(), e);
            }
        }
    }
}
```

**Company Frequency:** All companies (universal pattern)

---

### Q: Dead letter queue handling

**Answer:**

```java
@Bean
public DeadLetterPublishingRecoverer recoverer(KafkaTemplate<String, Object> template) {
    return new DeadLetterPublishingRecoverer(template,
        (record, ex) -> new TopicPartition(record.topic() + ".DLT", record.partition()));
}

@Bean
public DefaultErrorHandler errorHandler(DeadLetterPublishingRecoverer recoverer) {
    DefaultErrorHandler handler = new DefaultErrorHandler(
        recoverer, new FixedBackOff(1000L, 3L));
    handler.addNotRetryableExceptions(NonRecoverableException.class);
    return handler;
}

@KafkaListener(topics = "orders.DLT")
public void handleDeadLetter(ConsumerRecord<String, String> record) {
    log.error("DLQ message: key={}, value={}", record.key(), record.value());
    alertService.alert("DLQ: orders topic has dead letters");
}
```

---

### Q: Schema evolution — Avro, Protobuf, JSON Schema

**Answer:**

| Format | Schema Registry | Compatibility | Performance | Size |
|--------|----------------|--------------|-------------|------|
| **Avro** | Confluent Schema Registry | BACKWARD, FORWARD, FULL, NONE | Fast, binary | Small |
| **Protobuf** | Buf, Confluent | Same (wire compat in .proto) | Fastest, binary | Small |
| **JSON Schema** | Schema Registry | Flexible | Slower, text | Large |

**Avro evolution rules (BACKWARD compatible):**
- Add field with default: OK
- Remove field that had default: OK
- Widen type (int -> long): OK
- Remove field without default: BREAKING
- Rename field: BREAKING

**Company Frequency:** Confluent (essential), Netflix (often), Google (Protobuf)

---

## 4. Interview Questions

### Q: When should you use events vs REST APIs?

**Answer:**
Events (Async) when:
- Loose coupling required
- Multiple services need to react
- Processing can be deferred
- High scalability/throughput needed
- System must handle failures gracefully

REST (Sync) when:
- Immediate response needed
- Simple request-response flow
- Only one service needs the data
- Strong consistency required
- Operations are idempotent queries

**Company context:** Amazon uses internal REST APIs extensively (API mandate). Netflix prefers async events. Google uses mix with gRPC streaming.

---

### Q: How do you guarantee event delivery?

**Answer:**
Layered approach:
1. Transactional outbox (DB as reliable store)
2. Idempotent producer (Kafka config)
3. acks=all (broker-level)
4. Consumer manual commit
5. Idempotent consumer (de-duplication)
6. DLQ (final safety net)

```java
// Kafka — wait for acknowledgment
kafkaTemplate.send("orders", event).addCallback(
    result -> log.info("Sent: offset={}", result.getRecordMetadata().offset()),
    failure -> log.error("Failed to send", failure));

// Manual offset commit
@KafkaListener(topics = "orders")
public void consume(ConsumerRecord<String, Order> record, Acknowledgment ack) {
    try {
        process(record.value());
        ack.acknowledge(); // Only commit on success
    } catch (Exception e) {
        // Retry or DLQ
    }
}
```

---

### Q: How do you handle event schema evolution?

**Answer:**
1. Use a schema registry (Confluent, Buf, Apicurio)
2. Define compatibility rules: BACKWARD, FORWARD, FULL, NONE
3. Never delete fields, only add optional ones with defaults
4. Version events explicitly (schemaVersion header)
5. Dual-write during migration (publish both v1 and v2)

```java
@Component
public class OrderEventProcessor {
    @KafkaListener(topics = "orders")
    public void handle(ConsumerRecord<String, byte[]> record,
                       @Header("schemaVersion") Integer version) {
        switch (version != null ? version : 1) {
            case 1 -> processV1(deserializeV1(record.value()));
            case 2 -> processV2(deserializeV2(record.value()));
            default -> throw new UnsupportedSchemaException("Version: " + version);
        }
    }
}
```

---

### Q: What is the difference between Kafka and RabbitMQ?

**Answer:**

| Aspect | Kafka | RabbitMQ |
|--------|-------|----------|
| Model | Pull-based (consumer polls) | Push-based (broker pushes) |
| Ordering | Per-partition guaranteed | Per-queue (single consumer) |
| Retention | Time/size-based (replayable) | Deleted after ack |
| Throughput | Very high (100k+/s per partition) | Medium (10k-20k/s) |
| Latency | Higher (batch/pull) | Lower (immediate push) |
| Routing | Topic + partition key | Exchange + binding keys |
| Replay | Yes (by offset/timestamp) | No (re-publish required) |
| Consumer Groups | Native (shared partition load) | Manual (competing consumers) |
| Use Case | Event sourcing, stream processing | Task queues, RPC, pub-sub |

Choose Kafka: High throughput, event sourcing, long retention, stream processing.
Choose RabbitMQ: Complex routing, low latency, task queues, small-medium throughput.

**Company frequency:** Every company asks this question.

---

### Q: Design an event-driven order processing system

**Answer:**
```
Client -> API Gateway -> Order Service
                             |
                    (Transactional Outbox)
                             |
                     Kafka: OrderCreated
                        /     |       \
              Payment Svc  Inventory  Shipping
                  |            |           |
           PaymentOK      Reserved     Shipped
                        \
                     Saga Coordinator
                    /                  \
           Order confirmed    Compensation on failure
```

**Components:**
1. Order Service: REST endpoint, writes order + outbox event transactionally
2. Kafka: Event backbone (OrderCreated topic)
3. Payment Service: Listens, processes payment, publishes PaymentApproved/Rejected
4. Inventory Service: Listens, reserves stock, publishes Reserved/Failed
5. Saga Coordinator: Tracks state, triggers compensation on failure
6. Dead Letter Queue: Captures failed events for manual reprocessing

**Key design decisions:**
- Partition by orderId for ordering
- At-least-once delivery with idempotent consumers
- Transactional outbox for reliable publishing
- Separate DLQ per service
- Retry with exponential backoff before DLQ

---

> End of EVENT_DRIVEN_ARCHITECTURE_INTERVIEW.md
> Total: covering concepts, technologies, patterns, interview questions
