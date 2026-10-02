# THEORY — Message Queues & Protocols (lab14)

## 1. The queue as a shock absorber

Synchronous calls couple producer speed to consumer speed — one slow
consumer back-pressures the world. A queue decouples in time (buffer
spikes), in availability (consumer down → messages wait), and in scale
(add consumers, not bigger servers). The three patterns from the mock:
**pub/sub** (every consumer gets everything), **work queue / competing
consumers** (each message once, load shared), **request/reply**
(correlation ID over a temp reply queue) — plus **fanout/direct/topic**
routing and the **dead-letter queue** where poison messages go for
autopsy instead of infinite redelivery.

## 2. Broker vs log: RabbitMQ vs Kafka

Same word "queue", opposite philosophies. **RabbitMQ** (AMQP): smart
broker, dumb consumer — push-based, rich routing (direct/topic/fanout/
headers), per-message ACKs, ideal for task distribution and complex
routing. **Kafka**: dumb broker, smart consumer — pull-based partitioned
append-only log, 100K msg/s per partition, replayable, compactable.
Choose broker for routing intelligence, log for throughput + replay
(event sourcing, audit). Many estates run both, bridged at a gateway.

## 3. Delivery semantics cost ladder

**At-most-once** (no ACK/retry — telemetry), **at-least-once** (ACK +
retry — duplicates possible — task processing), **exactly-once**
(transactions + dedup + idempotency — financial-grade, highest cost).
Kafka's version: idempotent producer + transactional API + offset
management. MQTT's version: QoS 2 four-step handshake. There is no free
exactly-once — only paid-for.

## 4. Protocol fit: AMQP vs MQTT vs Kafka

AMQP: feature-rich enterprise routing, persistent, heavier — complex
workflows. MQTT: 2-byte header, QoS 0/1/2, last-will — constrained IoT
devices. Kafka: durable high-throughput log — data lakes/streaming
analytics, hungrier hosts. Canonical edge pattern: MQTT device→gateway,
gateway→Kafka backend.

## 5. Backpressure response order

Queue depth (RabbitMQ UI, `kafka-consumer-groups` lag) → find the slow
consumer (CPU, DB, downstream API) → scale consumers (≤ partition count!)
→ batch tuning (`fetch.min.bytes`, `max.poll.records`) → async
non-blocking handlers → more partitions (repartition/new topic) → signal
producers (acks=all, publisher confirms, flow control). Scale the
consumers before blaming the broker.
