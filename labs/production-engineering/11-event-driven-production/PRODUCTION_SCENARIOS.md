# PRODUCTION SCENARIOS: Event-Driven & Kafka Failures
## Lab 11 | Production Engineering Academy

---

## Scenario 1: The Consumer Group Rebalance Storm (Stop-The-World Consumption)

### Context
A consumer service running 24 pods in consumer group `order-fulfillment-group` processing 60 partitions from Kafka. Individual batch processing time averaged 1,500ms.

### The Disaster
- An external legacy warehouse database experienced high load, causing a batch of 500 messages to take 320 seconds to process.
- Kafka consumer configuration had default: `max.poll.interval.ms = 300000` (5 minutes).
- Because processing took 320 seconds, the consumer failed to call `consumer.poll()` before the 5-minute deadline!
- The Kafka group coordinator marked the consumer as **DEAD** and triggered a consumer group rebalance.
- During rebalance under the Eager rebalance protocol, **all 24 consumers revoked their partitions and halted processing**.
- When partitions were reassigned, another consumer picked up the exact same slow batch, took $> 5$ minutes, was marked dead, and triggered another rebalance!
- The cluster entered a permanent **Rebalance Storm**: zero messages processed for 45 minutes while consumer lag grew by 2.4 million events.

### The Fix
1. Reduced `max.poll.records` from 500 down to **50 records** so batches always complete in $< 15$ seconds.
2. Increased `max.poll.interval.ms` to 10 minutes (`600000ms`).
3. Upgraded partition assignment strategy to **Cooperative Sticky Assignor** (`CooperativeStickyAssignor`), which permits non-impacted consumers to continue processing without revoking partitions during a rebalance.

---

## Scenario 2: The Poison Pill Message & Infinite Crash Loop

### Context
A consumer deserialized JSON events using Jackson into `PaymentEvent`. A partner service deployed a bug emitting a malformed date string (`"2026-02-31"`).

### The Failure Mode
- Jackson threw `InvalidFormatException` during `consumer.poll()` or record processing.
- The exception uncaught bubble crashed the consumer thread.
- The pod restarted, re-polled the identical uncommitted offset, hit the malformed date, and crashed again.
- Entire partition was blocked indefinitely; thousands of subsequent valid transactions were stuck behind the poison pill.

### The Production Fix
Implemented **Dead Letter Queue (DLQ) with Spring Kafka `DefaultErrorHandler`**:
Catches deserialization and unrecoverable errors, logs the full payload, writes the poisoned record to topic `order-events-dlq` with custom diagnostic error headers, and advances the partition offset.
