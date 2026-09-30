# EXERCISES: Event-Driven & Kafka Engineering
## Lab 11 | Production Engineering Academy

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
