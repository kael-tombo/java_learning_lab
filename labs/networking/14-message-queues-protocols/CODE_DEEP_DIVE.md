# CODE_DEEP_DIVE — Message Queues mock (lab14)

All references are to `MOCK_INTERVIEW.md` in this lab (Q1–Q8).

## 1. Q1 — Queue definition (lines 5–7)

Seven problems solved: async communication, decoupling, buffering spikes,
reliable delivery (persistence + retries), load leveling, semantic choice
(at-least/exactly-once), event-driven enablement, fault tolerance. The
answer's shape matters: each clause maps to a design decision (persistence?
which semantic? which pattern?) — interviewers listen for the mapping,
not the vocabulary.

## 2. Q2 — Broker vs streaming (lines 9–11)

Push vs pull is the axis: RabbitMQ pushes to consumers with broker-side
routing intelligence; Kafka waits for consumers to fetch from partitions.
Consequences: routing expressiveness (exchange types) vs replayability
(log offsets) vs throughput profile. "Often used together" is the senior
answer — task distribution at the edge, event log at the core.

## 3. Q3 — Patterns (lines 13–15)

Pub/sub (broadcast), work queue (partition labor), request/reply
(correlation ID demultiplexes a shared reply queue), fanout/direct/topic
(routing-key expressiveness ladder), DLQ (poison-message quarantine).
Missing the DLQ in a design answer signals never having operated one.

## 4. Q4–Q6 — Protocols, semantics, partitions (lines 19–29)

- QoS ladder (MQTT 0/1/2) mirrors the semantics ladder — same costs.
- `partition = hash(key) % N` (keyed order) vs round-robin (null key,
  even spread). Partition count bounds: ≥ max consumers (else idle
  consumers), ≤ broker capacity (fds/disk/RAM per partition).
- Rebalance on join/leave; EagerSticky vs CooperativeSticky is the
  follow-up that separates readers from operators.

## 5. Q7–Q8 — Design + backpressure (lines 33–38)

- 500K txn/s fraud: Kafka ingest (100 partitions/10 brokers/RF3) +
  Flink windowed detection + RocksDB state + Redis pub/sub alert path +
  exactly-once on the money path. Every number defends a requirement.
- Backpressure order is diagnostic before heroic: depth metrics → slow
  consumer → scale ≤ partitions → batch knobs → async handlers →
  repartition → producer signals. Reversing the order (more partitions
  first) is the classic junior mistake.
