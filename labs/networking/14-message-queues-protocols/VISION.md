# VISION — Message Queues & Protocols: Decoupling Under Failure
> Where this lab takes you: from "Kafka handles it" to choosing delivery semantics you can defend and sizing a backlog honestly.

## The Arc
1. **The queue as a shock absorber** — rate mismatches, burst absorption, and when decoupling is a mistake.
2. **Broker models** — queues vs logs, routing, consumer groups, and rebalancing.
3. **Delivery semantics** — at-most-once, at-least-once, exactly-once, and the cost ladder.
4. **Protocol fit** — AMQP, MQTT, Kafka protocol, and what each is actually for.
5. **Operations** — backpressure, lag as a leading indicator, poison messages, and DLQs.

## Milestones (checkable)
- [ ] M1: explain why a queue improves stability and what failure mode it can introduce.
- [ ] M2: implement consumer group rebalancing and explain the stop-the-world cost.
- [ ] M3: implement idempotent consumption and prove at-least-once delivery is safe.
- [ ] M4: design a DLQ policy that does not silently discard data.
- [ ] M5: choose a protocol for three concrete workloads and defend each choice.

## Core Competencies
- Broker models: classic queues vs partitioned logs, and the operational differences.
- Delivery semantics as a cost ladder, with idempotency as the practical enabler.
- Consumer group mechanics, rebalancing, and lag as a leading indicator.
- Backpressure, poison message handling, and DLQ hygiene.

## Anti-Goals
- "Exactly-once" claimed without naming the boundaries of the guarantee.
- Retrying forever with no DLQ and no visibility.
- Choosing Kafka because it is popular rather than because the workload is a log.

## Interview Lens
- "Your consumer fell behind 4 hours. Explain what happened and what you do now."
- "Exactly-once sounds great. What does it actually require?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: broker mechanics, delivery semantics, rebalancing.
- Wk2 QUIZ/FLASHCARDS to 90%+; lag and backpressure experiments.
- Wk3 MINI_PROJECT with a reliable consumer, DLQ, and idempotency.
- Wk4 REAL_WORLD_PROJECT: a messaging backbone for a real estate.

## Done = You Can
- Choose a broker, a protocol, and a delivery semantic per workload, and explain the
  trade-offs in terms an on-call engineer can act on.
