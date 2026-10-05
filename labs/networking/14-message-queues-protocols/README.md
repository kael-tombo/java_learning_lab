# Message Queues & Protocols - README

## Overview
This lab covers message brokers and the protocols that sit on them, with the emphasis on
the decisions that cause incidents: delivery semantics, consumer group behaviour,
backpressure, and poison messages. It also covers protocol selection — AMQP, MQTT, and the
Kafka protocol — because "which broker" is usually the wrong first question.

## Learning Objectives
- Explain when a queue improves stability and when it introduces a failure mode
- Distinguish classic queue brokers from partitioned-log brokers and their trade-offs
- Implement consumer groups, rebalancing, and sticky partition assignment
- Distinguish at-most-once, at-least-once, and effectively-once, and what each costs
- Build an idempotent consumer that makes redelivery safe
- Handle poison messages with DLQ hygiene that does not hide problems
- Select a protocol per workload class and defend the choice
- Alert on consumer lag in a form that prompts the right action

## Prerequisites
- Java 21+
- Familiarity with concurrency and distributed systems basics
- Completed lab 04 (gRPC) is helpful for the delivery-semantics comparison

## Lab Structure

| Directory/File | Description |
|----------------|-------------|
| `src/main/java/` | Broker, group coordinator, idempotent consumer, DLQ |
| `src/test/java/` | Delivery-semantics, rebalancing, and poison-pill tests |
| `MINI_PROJECT/` | RelayLine: broker with groups, semantics, and a real DLQ |
| `REAL_WORLD_PROJECT/` | EventRail: multi-tenant messaging backbone |
| `SOLUTION/` | Solutions to exercises |

## Quick Start

```java
// At-least-once + idempotency = effectively-once, demonstrated under forced duplicates.
repeat(10, () -> consumer.onOrderPlaced(orderPlaced(eventId: "e-42")));
assertThat(payments.chargesActuallyMade()).isEqualTo(1);
assertThat(payments.captureCalls()).isEqualTo(10);
```

## Topics Covered
1. The queue as a shock absorber: rate mismatch, burst absorption, added failure modes
2. Broker models: classic queues vs partitioned logs, retention, and replay
3. Routing: exchanges, topics, filters, and per-tenant isolation
4. Consumer groups: group coordination, rebalancing, sticky assignment, `max.poll.interval`
5. Delivery semantics: at-most-once, at-least-once, exactly-once, effectively-once
6. Idempotency: dedupe registries, downstream idempotency keys, ordering of side effects
7. Failure handling: transient vs permanent errors, DLQ design, poison pills
8. Protocol selection: AMQP, MQTT, Kafka protocol, and workload fit
9. Operations: lag as time-to-clear, rebalance diagnosis, capacity and retention

## Assessment
- Complete the coding exercises in `EXERCISES.md`
- Pass the quiz in `QUIZ.md`
- Submit the mini project
- Complete the real-world project

## Estimated Time
5-6 hours

## References
- Kafka documentation - design, consumer groups, delivery semantics
- RabbitMQ documentation - AMQP, confirms, dead-lettering
- MQTT v5.0 specification (OASIS)
- Ben-Haim & Lyon - Exactly-Once Semantics Are Possible
- Kleppmann - Designing Data-Intensive Applications, chapters 5-7
