# INTERVIEW QUESTIONS: Event-Driven & Kafka Architecture
## Lab 11 | Senior / Staff / Principal / Distinguished Architect Level

---

## Senior Level (5+ Years)

### Q1: What causes a Kafka consumer group "rebalance storm" and how does the Cooperative Sticky Assignor solve it?

**Answer**: Under the legacy **Eager Rebalance** protocol (default pre-Kafka 2.4), whenever any
consumer joins, leaves, or exceeds `max.poll.interval.ms`, the group coordinator forces ALL
consumers to immediately revoke ALL their assigned partitions. Consumption stops across the
entire cluster. If processing a batch exceeds the poll interval (common when downstream services
are slow), consumers repeatedly fail heartbeats → infinite back-to-back rebalances.

The **Cooperative Sticky Assignor** uses incremental cooperative rebalancing:
1. Consumers continue processing on their current partitions.
2. Only the partitions that NEED to migrate are temporarily revoked.
3. The new owner begins consuming only after the previous owner confirms revocation.
4. All other partitions have zero Stop-The-World interruption.

**Key config**:
```java
props.put(PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    "org.apache.kafka.clients.consumer.CooperativeStickyAssignor");
```

---

### Q2: Explain the difference between `acks=1`, `acks=all`, and `acks=0` on a Kafka producer.

**Answer**:
- **`acks=0`**: Fire and forget. No ACK from broker. Risk: message lost if broker crashes
  before writing to disk. Throughput: maximum. Use: metrics, clickstream (loss acceptable).
- **`acks=1`**: Leader ACKs after writing to its local log. Risk: message lost if leader crashes
  before replication to followers. Throughput: high. Use: moderate-durability scenarios.
- **`acks=all` (or `-1`)**: Leader ACKs only after ALL in-sync replicas (ISR) have persisted
  the record. Risk: none (as long as `min.insync.replicas > 1`). Throughput: lowest (sync
  replication round-trip). Use: financial transactions, audit logs.

**Critical detail**: `acks=all` with `min.insync.replicas=1` is equivalent to `acks=1` — if
the ISR contains only the leader, the guarantee collapses. Always set `min.insync.replicas=2`
for replication factor 3 topics.

---

## Staff Level (8+ Years)

### Q3: Compare Change Data Capture (CDC) via Debezium vs Application-Level Outbox Polling.

**Answer**:

**Application-Level Polling**: A scheduled background thread runs:
```sql
SELECT * FROM outbox WHERE processed = false LIMIT 1000 FOR UPDATE SKIP LOCKED
```
- *Pros*: Simple, no external infrastructure.
- *Cons*: Constant DB polling burns CPU and I/O; table bloat needs vacuuming; latency is
  bounded by poll interval (typically 1–5s); does not scale to 10,000+ events/sec.

**CDC via Debezium**: Reads PostgreSQL WAL (Write-Ahead Log) or MySQL Binlog at the storage
engine level — no queries, no polling.
- *Pros*: Sub-millisecond latency; zero query load on DB CPU; captures EVERY committed change
  in strict transaction order.
- *Cons*: Requires managing Kafka Connect cluster; needs `REPLICATION` permissions on DB;
  **unconsumed replication slots can exhaust DB disk** (most critical operational risk).

**Rule of thumb**: Polling is acceptable for < 1,000 events/sec or teams with no Kafka Connect
expertise. Debezium is the right choice for > 5,000 events/sec or sub-second latency requirements.

---

### Q4: How does Kafka guarantee message ordering, and when does that guarantee break?

**Answer**: Kafka guarantees ordering **within a single partition**. All messages with the same
partition key are always consumed in the order they were produced.

**Ordering breaks in three scenarios**:

1. **Producer retries with `max.in.flight.requests.per.connection > 1`**:
   Batch 1 fails → retry. Batch 2 succeeds. Retry of Batch 1 succeeds after Batch 2.
   Result: Batch 2 appears before Batch 1 in the log.
   **Fix**: `enable.idempotence=true` (forces `max.in.flight = 5` AND sequence numbering).

2. **Null partition key (round-robin assignment)**:
   Messages without keys are distributed round-robin across partitions — no ordering.
   **Fix**: Always use a meaningful partition key for ordered event streams.

3. **Consumer reading multiple partitions**:
   If a consumer reads partitions 0, 1, 2 in a loop, messages from different partitions
   are interleaved regardless of producer timestamp.
   **Fix**: Use a single partition for total ordering; or use Kafka Streams `KStream` with
   a `cogroup` to merge streams in event-time order using watermarks.

---

### Q5: What is Kafka's exactly-once semantics (EOS) and what is its performance cost?

**Answer**: Kafka EOS is achieved via **Kafka Transactions** (`transactional.id` on producer
+ `isolation.level=read_committed` on consumer). The protocol uses a two-phase commit
coordinated by the Kafka broker's Transaction Coordinator:

1. **Begin transaction**: Producer registers transaction ID → broker assigns PID + epoch.
2. **Produce messages**: Messages written with `in_transaction=true` marker.
3. **Commit**: Producer sends `EndTransactionMarker` → broker writes COMMIT marker to all
   involved partitions. Consumers with `read_committed` see the records only after COMMIT.
4. **Abort**: Broker writes ABORT marker → consumers skip all transaction records.

**Performance cost**:
- `acks=all` enforced (2–5ms per batch).
- Transaction coordinator round-trip for begin/commit: 2 × network RTT (~1ms each).
- `max.in.flight.requests.per.connection=5` limit reduces pipelining.
- Total overhead: ~5–20ms per transaction vs ~1ms for non-transactional produce.

**Use EOS only when**: You read from Kafka, process, and write back to Kafka in one
atomic unit (Kafka Streams `exactly_once_v2`). For DB writes, use the Outbox Pattern instead.

---

## Principal Level (10+ Years)

### Q6: Design a partition count selection strategy for a topic at 500,000 messages/sec.

**Answer**: Partition count selection requires modeling three constraints:

**Constraint 1 — Producer throughput per partition**:
Kafka partition write throughput ≈ 80–100 MB/s per partition (network + disk bounded).
At 500,000 msg/s × 1 KB avg message size = 500 MB/s total.
Minimum partitions for producers = `500 MB/s ÷ 80 MB/s ≈ 7` → round up to **8**.

**Constraint 2 — Consumer parallelism**:
Max concurrent consumers = number of partitions. If you need 30 consumer pods:
`partitions ≥ 30` → pick **32** (power of 2 is not required but common).

**Constraint 3 — Broker overhead**:
Each partition requires an open file handle and leader metadata on each broker.
Rule of thumb: `total_partitions_per_broker ≤ 4,000` (Kafka 2.x) or `≤ 10,000` (KRaft mode).

**Final answer**: `max(producer_bound, consumer_bound) = max(8, 32) = 32 partitions`.
Pick `partitions = 32` to allow up to 32 concurrent consumer threads while satisfying producer throughput.

> **Never increase partition count without planning for consumer rebalance and consumer group
> state reset** — adding partitions to a running topic triggers a full group rebalance.

---

### Q7: Explain how the LMAX Disruptor's `Sequence` padding prevents false sharing, and why 128 bytes instead of 64.

**Answer**: On x86-64, the L1 cache line is 64 bytes. Naively, padding a `long` (8 bytes) to
64 bytes would seem sufficient. However, Intel Ivy Bridge and later processors use a **128-byte
spatial prefetcher** — the hardware prefetches pairs of adjacent cache lines together. This means
a cache line at address N and cache line at address N+64 may be prefetched simultaneously.

If the Disruptor's sequence `volatile long value` occupies bytes 0–7 of one cache line, and
another field starts at byte 64, the prefetcher treats both as a "stride pair". A write from
the publisher to `value` causes the prefetcher to also invalidate the adjacent cache line,
even if it holds a different object's fields — that IS false sharing on modern Intel CPUs.

**Solution**: Pad to 128 bytes (7 longs before + value + 7 longs after = 15 × 8 + 8 = 128
bytes total) — the `value` field sits isolated from any adjacent object on both 64-byte boundaries.

On ARM Cortex-A57/A72, cache line size is 64 bytes, but still benefits from 128-byte padding
to avoid prefetcher-induced invalidation on multi-socket ARM configurations.

---

### Q8: How would you implement global event ordering across multiple Kafka topics in a microservices architecture?

**Answer**: Kafka guarantees per-partition ordering. Cross-topic global ordering requires explicit mechanisms:

**Option A — Single Partition, Single Topic (Total Order)**:
All events → one topic → one partition. Throughput limited to ~100 MB/s partition ceiling.
Acceptable for: audit log, ledger with < 1,000 events/sec.

**Option B — Logical Timestamps (Lamport Clocks)**:
Each service maintains a logical clock. Event carries `logicalTimestamp = max(local, received) + 1`.
Consumers sort events by `logicalTimestamp` before processing. Requires buffering (a 100ms
"watermark window") to absorb out-of-order delivery.

**Option C — Kafka Streams with Event-Time Watermarks**:
```java
stream.selectKey((k, v) -> v.getOrderId())
      .groupByKey()
      .windowedBy(TimeWindows.of(Duration.ofSeconds(10))
                             .grace(Duration.ofMillis(500))) // 500ms late arrivals
      .aggregate(...)
```

**Option D — Single Writer Pattern**:
Only ONE service (the Order Saga Orchestrator) writes to the final aggregate topic.
All other services send commands to the orchestrator → orchestrator writes events in order.
Eliminates cross-topic ordering problems entirely at the cost of central coordination.

---

## Distinguished Architect Level (15+ Years)

### Q9: What are the consistency guarantees of the Transactional Outbox Pattern, and what failure scenarios does it NOT protect against?

**Answer**: The Outbox Pattern provides **atomic delivery** (the business entity and the
outbox row commit together or not at all). It provides **at-least-once delivery** (Debezium
may re-read the WAL entry after a crash and re-publish). It does NOT provide:

1. **Ordering across aggregate types**: If two different aggregate types (Order, Customer) write
   to the same outbox table, Debezium reads them in WAL sequence — but consumers processing
   `outbox.Order` and `outbox.Customer` topics independently may process them out of order
   relative to each other.

2. **Protection against Debezium snapshot duplication**: If the Debezium replication slot is
   dropped and recreated (e.g., after WAL disk exhaustion), all rows in the outbox table that
   haven't been cleaned up will be re-published. Downstream consumers MUST be idempotent.

3. **Sub-second latency SLAs in pathological WAL scenarios**: If the PostgreSQL primary is
   under heavy write load, WAL processing can lag by seconds. The outbox does not give you
   synchronous end-to-end guarantees.

4. **Cross-database atomic delivery**: If the business entity is in PostgreSQL and the
   outbox is in a different database, the dual-write problem reappears.

---

### Q10: A team reports that their Kafka Streams application produces correct output in development but duplicates records in production after broker failovers. Diagnose and fix.

**Answer**: This is a classic **exactly-once semantics misconfiguration** combined with
**zombie fencing failure**.

**Root Cause Analysis**:

1. **Default `processing.guarantee = at_least_once`**: On broker failover, the Streams task
   reassigns to a new thread. The new thread re-reads uncommitted input offsets and re-processes
   them — producing duplicate output records.

2. **Zombie task producing in parallel**: During the brief window between the old task losing
   its broker connection and the new task starting, BOTH may produce to the output topic.
   Without EOS, both writes succeed → duplicates.

**Fix**:
```java
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG,
          StreamsConfig.EXACTLY_ONCE_V2); // Requires Kafka 2.5+

// EXACTLY_ONCE_V2 uses epoch-based fencing:
// - Each task gets a transactional.id = appId + partition
// - New task epoch bumps the ID → broker FENCES the old zombie task's in-flight transactions
// - Old task's pending produce is aborted → no duplicates
```

**Performance impact of `EXACTLY_ONCE_V2`**:
- Commit interval default: 100ms (configurable via `commit.interval.ms`).
- Each commit = one Kafka transaction (begin + produce + commit) = ~5ms overhead.
- Net effect: max throughput reduced by ~5% vs `at_least_once`. Acceptable for correctness.

**Verification**:
```bash
# Confirm fencing is working: zombie tasks produce ProducerFencedException
kubectl logs -l app=order-streams | grep "ProducerFenced"
# You SHOULD see this on broker failover — it means EOS is working correctly
```


---

## Senior Level (5+ Years)

### Q1: What causes a Kafka consumer group "rebalance storm" and how does the Cooperative Sticky Assignor solve it?
**Answer**:
Under the legacy Eager Rebalance protocol, whenever a consumer leaves, crashes, or exceeds `max.poll.interval.ms`, the group coordinator forces all consumers in the group to immediately revoke their assigned partitions. All message consumption stops across the entire cluster until a new assignment plan is calculated. If processing a batch exceeds the poll interval, consumers repeatedly fail their heartbeats, triggering infinite back-to-back rebalances.
The **Cooperative Sticky Assignor** implements incremental cooperative rebalancing:
1. Consumers keep processing messages on their assigned partitions.
2. Only the specific partitions that need to be migrated from one consumer to another are temporarily revoked.
3. Healthy consumers and unaffected partitions experience zero Stop-The-World downtime.

---

## Staff / Principal Level (8+ Years)

### Q2: Compare Change Data Capture (CDC) via Debezium vs Application-level Outbox Polling.
**Answer**:
- **Application-Level Polling**: A scheduled background thread runs `SELECT * FROM outbox WHERE processed = false LIMIT 1000 FOR UPDATE SKIP LOCKED` and writes to Kafka.
  - *Pros*: Simple to build, no external infrastructure dependencies.
  - *Cons*: Constant database polling burns CPU and I/O; table bloat requires continuous vacuuming; latency is delayed by poll interval; does not scale to tens of thousands of events/sec.
- **CDC via Debezium (Kafka Connect)**: Reads database transaction logs (PostgreSQL WAL or MySQL Binlog) directly at the storage engine level.
  - *Pros*: Sub-millisecond latency; zero query load on database CPU; captures every single committed change in strict transaction order without polling.
  - *Cons*: Requires managing Kafka Connect cluster; requires database replication permissions and WAL storage management (unconsumed replication slots can exhaust DB disk).
