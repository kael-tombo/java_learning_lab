# Mini Project — Event-Driven Architecture

## Goal

Build an event-driven system where multiple services communicate through
events rather than direct calls, demonstrating loose coupling, event
propagation, and independent consumer evolution.

## Requirements

### Event Bus
- Implement a simple in-memory or file-based event bus
- Support publish/subscribe semantics
- Events carry: event ID, type, timestamp, payload, correlation ID

### Producer Service: Order Service
- Emits events: `OrderCreated`, `OrderCancelled`, `OrderShipped`
- Does not know about consumers
- Persists events before publishing (outbox pattern)

### Consumer Services
1. **Inventory Service** — listens to `OrderCreated`, reserves stock
2. **Notification Service** — listens to all order events, sends notifications
3. **Analytics Service** — listens to all events, updates dashboards

## Technical Specifications

1. **Event design**
   - Events are immutable facts with unique IDs
   - Include timestamp and correlation ID for tracing
   - Use a consistent serialization format (JSON)

2. **Delivery semantics**
   - At-least-once delivery
   - Consumers must be idempotent
   - Handle poison messages (dead letter queue)

3. **Decoupling**
   - Producers have zero knowledge of consumers
   - New consumers can be added without changing producers
   - Consumers process events at their own pace

4. **Error handling**
   - Failed consumer processing retries with backoff
   - Dead letter queue for unprocessable events
   - Consumer health monitoring

## Steps

1. Design event schema and base event class
2. Implement event bus with pub/sub
3. Build Order Service with event publishing
4. Implement Inventory Service consumer
5. Implement Notification Service consumer
6. Implement Analytics Service consumer
7. Add idempotency handling to all consumers
8. Add dead letter queue for failed events
9. Write tests for event flow and failure scenarios

## Acceptance Criteria

- [ ] Order Service emits events without knowing consumers
- [ ] All three consumers receive and process events
- [ ] Duplicate events don't cause duplicate processing
- [ ] Failed events go to dead letter queue
- [ ] New consumer can be added without producer changes
- [ ] Events include correlation IDs for tracing

## Stretch Goals

- Implement event replay from a log
- Add event schema versioning
- Implement saga pattern across consumers
- Add metrics for event processing lag
