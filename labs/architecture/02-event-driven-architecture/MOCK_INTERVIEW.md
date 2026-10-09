# Mock Interview: Event-Driven Architecture

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Design an order processing system using events

**Interviewer**: "Design an order processing system. Walk me through your event-driven approach."

**Candidate**: "I'll model the order lifecycle as a series of domain events. Each service reacts to events it cares about and emits events for things that happen within its domain."

**Interviewer**: "What are the key events in the order lifecycle?"

**Candidate**: "The core events: OrderPlaced, PaymentReceived, InventoryReserved, OrderShipped, OrderDelivered. Each event represents a meaningful state change that other services can react to."

**Interviewer**: "Walk me through the flow."

**Candidate**: "The Order Service receives a place-order request. It validates the order, saves it, and emits an OrderPlaced event on Kafka. The Payment Service subscribes to OrderPlaced, processes the payment, and emits PaymentProcessed. The Inventory Service subscribes to PaymentProcessed, reserves inventory, and emits InventoryReserved. The Shipping Service picks up InventoryReserved, creates a shipment, and emits OrderShipped."

**Interviewer**: "What happens if payment fails?"

**Candidate**: "The Payment Service emits a PaymentFailed event. Any service that needs to compensate can react. The Inventory Service releases the temporary hold. The Order Service updates the order status to 'failed'. The Notification Service sends the customer a failure notification."

**Interviewer**: "How do you handle event ordering within a single order?"

**Candidate**: "Critical question. Kafka partitions by order ID guarantee ordering for a single order's events. Each service processes events for the same order on the same partition. If event processing fails, we retry within the partition, maintaining order. If processing consistently fails, we dead-letter to a separate topic for manual intervention."

**Interviewer**: "What about exactly-once processing between services?"

**Candidate**: "The key is idempotency. Each event has a unique ID. Each consumer tracks processed event IDs in its database. If it receives a duplicate event, it skips processing. This gives us at-least-once delivery with idempotent processing — effectively exactly-once."

**Interviewer**: "How do you handle schema evolution? Events change over time."

**Candidate**: "I'd use a Schema Registry with Avro or Protobuf. Each event has a schema version. The registry enforces backward compatibility — you can add fields but not remove or rename. Consumers can handle multiple schema versions. This prevents a producer from breaking consumers."

**Interviewer**: "How do you test an event-driven system?"

**Candidate**: "Three levels: (1) Unit test each event handler in isolation with mocked producers. (2) Integration test the event flow — produce an event and verify the eventual state change across services. (3) Consumer-driven contract tests — each consumer defines the event shape it expects, and producers must not break those contracts."

**Interviewer**: "What monitoring is critical for event-driven systems?"

**Candidate**: "Consumer lag is the most important metric — are consumers keeping up with producers? Event processing latency — how long between event production and consumption? Dead letter queue depth — how many events failed processing? And event throughput — are we approaching capacity limits?"

---

## Key Takeaways

- Events are business facts, not implementation details
- Idempotency is mandatory for reliable event processing
- Schema Registry prevents integration failures
- Testing event flows requires consumer-driven contracts
- Monitor consumer lag and dead letter queues proactively

---

## Evaluation Criteria

The interviewer assesses:
- **Architecture thinking**: Clear decomposition into meaningful boundaries
- **Trade-off awareness**: Understanding of when this pattern helps vs hurts
- **Failure handling**: Proactive identification of failure modes
- **Operational maturity**: Discussion of monitoring, deployment, and operations
- **Communication**: Ability to explain complex concepts clearly


## Staff+ Level Expectations

At the staff+ level, the interviewer expects you to:
- Challenge their assumptions and ask clarifying questions
- Discuss organizational implications (team boundaries, Conway's Law)
- Address data consistency challenges proactively
- Consider migration and evolution strategy
- Discuss cost and operational trade-offs
- Connect technical decisions to business outcomes

## Common Follow-Up Questions

1. ""How would this design change at 100x scale?"" — Discuss partitioning, caching, read replicas
2. ""How do you handle schema evolution?"" — Backward compatibility, versioning, migration strategies
3. ""Whats the biggest risk in this architecture?"" — Identify the weakest link and mitigation
4. ""How would you migrate from the current system?"" — Strangler Fig, feature toggles, parallel run
5. ""How do you test this system?"" — Unit, integration, contract, and end-to-end testing strategies

## Key Takeaways

This mock interview demonstrates the depth of discussion expected at staff+ level. The interviewer is not looking for a single ""correct"" answer but rather evaluating your thought process, trade-off awareness, and ability to communicate complex architectural decisions clearly.

