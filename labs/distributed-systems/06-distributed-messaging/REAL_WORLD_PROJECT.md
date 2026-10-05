# Distributed Messaging - Real World Project

## Project: Migrating an Order Event Bus to Partitioned Kafka

### Objective
Move an existing RabbitMQ-based order bus onto a partitioned Kafka topic, keeping ordering
per order ID, making consumers idempotent, and operationalising consumer lag as a paging
signal.

### Why This Is a Real Problem
Naive migrations lose per-key ordering, silently reset consumer offsets, and leave consumers
that break the first time a message is redelivered. Every one of those fails quietly, days
later, under load.

### Architecture Overview
```
 Order svc ─▶ topic: order-events (N partitions)
                │ key = orderId
                ├──▶ inventory-svc   (group: inventory, lag SLO 30s)
                ├──▶ billing-svc     (group: billing,   lag SLO 60s)
                ├──▶ analytics       (group: analytics, at-least-once, own DB)
                └──▶ audit-archiver  (group: audit,    must not skip)
```
Guarantees to hold: per-order ordering, at-least-once delivery, no consumer left without a
committed offset policy, and a DLQ path for poison messages.

### Phase 1: Audit the Existing Bus (Week 1)
1. Inventory topics, message counts/day, and payload sizes
2. Identify ordering requirements per topic — which messages must stay in order, and why
3. Find every consumer and classify it: must-not-skip, must-not-duplicate, or tolerant
4. Measure current end-to-end latency to set the lag SLO target

### Phase 2: Topic and Partition Design (Week 2)
1. Partition count = max(consumer concurrency, projected throughput / per-partition capacity)
2. Producer key = orderId for ordering; measure the resulting skew and confirm no partition
   exceeds twice the mean
3. Retention: sized to your longest acceptable replay window, not "7 days" by habit
4. Enable exactly-once only if you already have idempotent consumers; otherwise it hides bugs
5. Schema in a registry with a compatibility mode, so a producer change cannot break consumers

### Phase 3: Make Consumers Idempotent (Week 3)
1. Every consumer stores the last processed `(messageId)` or `(key, version)` it handled
2. Use the transaction/conditional-write pattern so the state change and the dedupe record
   commit together
3. Commit the offset only after successful processing
4. Test: replay 24 hours of messages into each consumer and assert zero double-effects

### Phase 4: Dual-Write and Cutover (Week 4)
1. Publish to both buses; consumers run against the old bus only
2. Compare message counts and payload hashes to find divergence
3. Shift one consumer group at a time to Kafka, watching lag and error rate
4. Stop the old publisher only after a full cycle with no consumer on RabbitMQ

### Phase 5: Operate the Lag Signal (Week 5+)
1. Dashboard: lag seconds per group, per-partition lag, consumer count, rebalance rate
2. Alerts:
   - lag seconds above SLO for 5 minutes
   - lag on a single partition far above the others (hot key)
   - rebalance rate spike (consumer churn or processing too slow)
   - DLQ depth above zero
3. Runbook: "consumer lag" — scale consumers, check for poison message, check partition skew
4. DLQ with replay tooling, and a monthly test that the replay path works

### Deliverables
1. Topic/partition design with measured skew data
2. Idempotency implementation in every consumer plus a replay test
3. Lag dashboards and alerts with per-partition granularity
4. DLQ and replay tooling, plus the consumer-lag runbook

### Success Criteria
- Per-order ordering holds through a full replay test
- Zero double-effects after a 24-hour replay into each consumer
- Lag SLO met at 3x baseline event volume
- Rebalance rate stable and DLQ replay proven monthly

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Apache Kafka Documentation —
  https://kafka.apache.org/documentation/#design
  Use for: the log-partition model, replication, and consumer groups as the authoritative
  statement of ordering scope and at-least-once delivery. Pin the documentation version you
  deployed against; the current site tracks the latest release, not your broker version.
- Apache Kafka consumer configuration reference —
  https://kafka.apache.org/documentation/#consumerconfigs
  Use for: `enable.auto.commit`, `max.poll.records`, and `max.poll.interval.ms` — the three
  settings that decide whether a slow consumer silently rebalances. Confirm the current
  default for `auto.offset.reset` before relying on it in a recovery runbook.

### Estimated Time
6 weeks part-time