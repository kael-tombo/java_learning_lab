# PRODUCTION SCENARIOS: Event-Driven & Kafka Failures
## Lab 11 | Production Engineering Academy — Top 0.0001% Engineering

---

## Scenario 1: The Consumer Group Rebalance Storm

**Severity**: P1 — 45 minutes of zero message processing
**Impact**: 2.4 million events unprocessed; $180K orders stuck in PENDING state

### Timeline
| Time | Event |
|---|---|
| T+0 | External warehouse DB experiences high load. Batch of 500 records takes 320s to process |
| T+5m | `max.poll.interval.ms=300000` exceeded — Kafka coordinator marks consumer DEAD |
| T+5m | **Eager Rebalance**: ALL 24 consumers pause and revoke ALL 60 partitions |
| T+6m | Partitions reassigned. New consumer picks up the same 500-record slow batch |
| T+11m | New consumer also exceeds poll interval → marked DEAD → rebalance again |
| T+11m | Cluster enters infinite rebalance loop. Consumer lag grows at 53,000 msg/min |
| T+45m | On-call engineer reduces `max.poll.records=50` via rolling restart → storm breaks |
| T+52m | Normal processing resumes. Lag drains over the next 3 hours |

### Root Cause
`max.poll.records=500` × `p99.9 record processing time=650ms` = **325s > 300s** poll interval.
The Eager Rebalance protocol amplified a single slow batch into a cluster-wide outage.

### Permanent Fix
```java
// Rule: max.poll.records × p99.9_processing_time < max.poll.interval.ms × 0.75 (safety margin)
props.put(MAX_POLL_RECORDS_CONFIG,      50);       // 50 × 650ms = 32.5s
props.put(MAX_POLL_INTERVAL_MS_CONFIG,  600_000);  // 10 minute ceiling
props.put(PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    "org.apache.kafka.clients.consumer.CooperativeStickyAssignor");
```
**Post-fix**: Even when a batch takes 600s, only the affected consumer is paused. The remaining 23 consumers continue processing uninterrupted.

---

## Scenario 2: Poison Pill — Partition Stuck for 6 Hours

**Severity**: P2 — Single partition blocked; 87,000 events unprocessed
**Impact**: Subscription renewal payments not processed for 87,000 accounts

### Timeline
| Time | Event |
|---|---|
| T+0 | Partner service deploys with a bug: emits date `"2026-02-31"` (invalid) |
| T+0 | Jackson throws `InvalidFormatException` on consumer |
| T+0 | Spring Kafka seeks back to the same offset and retries → same crash |
| T+0 | Pod restarts (CrashLoopBackOff). Re-pulls same offset → same crash |
| T+6h | On-call engineer manually advances offset via `kafka-consumer-groups.sh --reset-offsets` |

### Root Cause
No `ErrorHandlingDeserializer` configured. Jackson's `ObjectMapper` was configured with
`DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES = true` globally.
No DLQ — failed records had nowhere to go. The container sought back to offset 0 of the problematic record infinitely.

### Permanent Fix
```java
// 1. Wrap deserializer — isolates deserialization failures from processing logic
props.put(VALUE_DESERIALIZER_CLASS_CONFIG, ErrorHandlingDeserializer.class);

// 2. Non-retryable: send to DLQ immediately on deserialization failure
errorHandler.addNotRetryableExceptions(
    SerializationException.class,
    InvalidFormatException.class
);

// 3. DLQ includes original payload + stack trace as record headers for forensics
DeadLetterPublishingRecoverer recoverer = new DeadLetterPublishingRecoverer(
    kafkaTemplate,
    (rec, ex) -> new TopicPartition(rec.topic() + ".DLT", rec.partition())
);
```

---

## Scenario 3: Dual-Write Phantom Orders — $2.3M Data Discrepancy

**Severity**: P0 — Data integrity violation
**Impact**: 1,847 orders billed to customers but never fulfiled; 234 orders fulfilled but never billed

### Timeline
| Time | Event |
|---|---|
| T+0 | Black Friday traffic: 12,000 orders/min |
| T+0 | Kafka brokers experience brief network blip (200ms) |
| T+0 | `kafkaTemplate.send()` throws `TimeoutException` for 847 orders after DB commit |
| T+0 | Orders exist in DB (committed) but Kafka event never published |
| T+0 | Inventory/billing/shipping never notified → 847 orders stuck in CREATED state forever |
| T+2h | Simultaneously: 234 orders where `kafkaTemplate.send()` succeeded but DB rolled back |
| T+2h | Billing charged customers. Order does not exist in DB. Customer support overwhelmed |
| T+48h | Reconciliation script identifies $2.3M discrepancy across 1,081 orders |

### Root Cause
```java
// The killer pattern — every order-creating service had this:
@Transactional
public void createOrder(OrderRequest req) {
    orderRepository.save(new Order(req));       // DB commits successfully
    kafkaTemplate.send("orders", req.toJson()); // Network blip → TimeoutException
    // DB transaction already committed — cannot roll back!
}
```

### Permanent Fix — Outbox Pattern Mandate
All 12 order-related services migrated to the Transactional Outbox Pattern.
Debezium CDC deployed on PostgreSQL primary with WAL replication.

**ADR created**: Direct Kafka produce from service layer is forbidden. Code review checklist updated.

---

## Scenario 4: Debezium Replication Slot WAL Bloat — DB Disk Crash

**Severity**: P1 — Database primary crashed; 14 minutes of write downtime
**Impact**: All order writes unavailable during incident. 14,000 writes buffered in client retry queues

### Timeline
| Time | Event |
|---|---|
| T+0 | Kafka Connect cluster OOMKilled due to unrelated memory leak |
| T+0 | Debezium connector stops reading WAL. Replication slot holds WAL segments |
| T+0 | PostgreSQL primary begins accumulating WAL: 200 MB/min |
| T+2h | No alert fires (WAL disk monitoring not configured) |
| T+4h | PostgreSQL primary disk at 100%. PostgreSQL shuts down write I/O to prevent log corruption |
| T+4h14m | Kafka Connect cluster restarted by on-call. Connector resumes WAL reading |
| T+4h14m | PostgreSQL WAL backlog clears. DB resumes writes |
| Post-incident | 4h × 200 MB/min = 48 GB of WAL accumulated during outage |

### Permanent Fix
```yaml
# Prometheus alert — fires at 5 GB WAL lag (25 minutes before disk fills at 200 MB/min)
- alert: DebeziumWALLagCritical
  expr: >
    pg_replication_slots_pg_wal_lsn_diff_bytes{slot_name="debezium_outbox_slot"} > 5368709120
  for: 2m
  labels:
    severity: page  # Wake up on-call immediately
```
```sql
-- Automated safety valve: if slot inactive > 30 min, drop it (require manual re-snapshot)
-- Implemented as pg_cron job
SELECT cron.schedule('*/5 * * * *', $$
  SELECT pg_drop_replication_slot(slot_name)
  FROM pg_replication_slots
  WHERE active = false
    AND slot_name = 'debezium_outbox_slot'
    AND now() - pg_last_xact_replay_timestamp() > INTERVAL '30 minutes';
$$);
```

---

## Scenario 5: Disruptor Ring Buffer Full — Kafka Consumer Freeze

**Severity**: P2 — HFT pipeline paused; 850ms of trade events not processed
**Impact**: 12,000 trade events stuck in Kafka; market making desk paused during high volatility

### Timeline
| Time | Event |
|---|---|
| T+0 | Risk calculation engine (downstream of Disruptor) experiences GC pause (ZGC triggered) |
| T+0 | `OrderBatchHandler.onEvent()` blocks for 850ms waiting for risk engine to flush |
| T+0 | During 850ms: 100,000 events/sec × 0.85s = 85,000 new events need ring buffer space |
| T+0 | Ring buffer size = 65,536. After 655ms, ring buffer fills completely |
| T+655ms | Kafka consumer thread blocks on `ringBuffer.next()` (BusySpin — burns 1 CPU core) |
| T+850ms | Risk engine GC completes. Disruptor consumer thread drains. Ring buffer freed |
| T+850ms | Kafka consumer thread unblocks. Resumes consuming |
| Post-incident | 850ms of Kafka consumer lag accumulated (12,000 events at avg 14 KB each) |

### Root Cause Analysis
The `OrderBatchHandler` made a blocking synchronous call to the risk engine, which violated
the core Disruptor design contract: **`onEvent()` must never block**.

```java
// VIOLATION — blocking call inside Disruptor handler
@Override
public void onEvent(OrderEvent event, long sequence, boolean endOfBatch) {
    riskEngine.calculateMarginSync(event); // Can block up to 2 seconds!
}
```

### Permanent Fix
```java
// Pattern: fire-and-forget to secondary Disruptor, return immediately
@Override
public void onEvent(OrderEvent event, long sequence, boolean endOfBatch) {
    // Copy event data into second pipeline — non-blocking, ~50ns
    long riskSeq = riskRingBuffer.next();
    try {
        RiskEvent riskSlot = riskRingBuffer.get(riskSeq);
        riskSlot.copyFrom(event); // Pure field copy, zero allocation
    } finally {
        riskRingBuffer.publish(riskSeq);
    }
    // Primary handler returns in < 100ns
}
// Risk calculation happens on a separate Disruptor consumer thread — never blocks primary
```

**Ring buffer sizing formula applied**:
```
max_slowdown = 2s (worst-case GC on risk engine)
throughput   = 100,000 events/sec
min_buffer   = 2s × 100,000 = 200,000 → round to 262,144 (2^18)
```
Buffer increased from 65,536 → **262,144** entries.


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
