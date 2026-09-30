# THEORY: Event-Driven Architecture & Apache Kafka in Production
## Lab 11 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Kafka Storage Internals — Log Segments, Page Cache & Zero-Copy

### 1.1 The Log Segment Structure

Each Kafka partition is physically a directory of **log segment files**:

```
/var/kafka/data/orders-0/
  ├── 00000000000000000000.log        ← Active segment (appended to)
  ├── 00000000000000000000.index      ← Sparse offset → file position index
  ├── 00000000000000000000.timeindex  ← Sparse timestamp → offset index
  ├── 00000000001073741824.log        ← Closed segment (immutable)
  └── ...
```

- **Active segment**: Only this file receives writes. The broker appends records sequentially using `FileChannel.write()`.
- **Closed segments**: Immutable. Eligible for compaction and retention deletion.
- **Segment roll**: A new segment is created when `log.segment.bytes` (default 1 GB) or `log.roll.hours` (default 168h) is exceeded.
- **Index file**: Maps offset → byte position in the `.log` file. Sparse (1 entry per ~4 KB). Enables O(log N) binary search to find an offset.

### 1.2 Sequential I/O — Why Kafka Is Fast

Random disk I/O (database page reads): ~4ms seek + ~0.1ms read = **4.1ms per read**.
Sequential disk I/O (Kafka append): no seek, ~0.02ms/MB = **600+ MB/s throughput**.

Modern OS page cache absorbs ALL writes before hitting disk:
```
Producer write → OS Page Cache (RAM) → sync to disk (async via pdflush/fsync)
                             ↓
Consumer read  → OS Page Cache (RAM hit, no disk I/O if recently written)
```
The OS page cache is the single biggest performance multiplier in Kafka deployments. Giving brokers 32–64 GB of RAM (even with only 6 GB JVM heap) means the page cache absorbs millions of reads with zero disk I/O.

### 1.3 Zero-Copy Transfer (`sendfile` syscall)

Standard Java data transfer (4 copies):
```
Disk → Kernel Buffer → User Space (JVM) → Socket Buffer → NIC
         (copy 1)           (copy 2)          (copy 3)   (copy 4)
```

Kafka's `FileChannel.transferTo()` maps to the OS `sendfile()` syscall (2 copies):
```
Disk → Kernel Buffer → NIC Buffer
         (copy 1)       (copy 2, DMA)
```
The JVM process never touches the bytes. This eliminates:
- 2 memory copies (saved ~1.2 GB/sec of memcpy CPU overhead at 600 MB/s throughput)
- GC churn from byte arrays allocated to hold the data in user space
- Context switches between kernel and user space

---

## 2. Delivery Guarantees — Formal Definitions

### 2.1 The Three Guarantees

| Guarantee | Producer Config | Consumer Behavior | Use Case |
|---|---|---|---|
| **At-most-once** | `acks=0`, fire-and-forget | Commit offset BEFORE processing | Metrics, analytics (loss OK) |
| **At-least-once** | `acks=all`, retry enabled | Commit offset AFTER processing | Standard production baseline |
| **Exactly-once** | `transactional.id` + `acks=all` | `isolation.level=read_committed` | Financial transactions, billing |

### 2.2 Idempotent Producer — How Broker Sequence Numbering Works

With `enable.idempotence=true`:
1. Broker assigns the producer a **Producer ID (PID)** on first connection.
2. Each batch carries a monotonically increasing **sequence number** per partition.
3. If the producer retries (network timeout), the broker checks: `received_seq == expected_seq`?
   - **Yes**: Duplicate — silently dropped, ACK sent.
   - **No (gap)**: `OutOfOrderSequenceException` — data integrity error, alert required.
4. PID is reset after producer restart → idempotence is per-session only.

### 2.3 Kafka Transactions — Two-Phase Commit Without Coordinator Crash Risk

```
                    ┌─────────────────────────────┐
                    │   Transaction Coordinator    │
                    │  (special Kafka partition)   │
                    └─────────────────────────────┘
                          ↑         ↓
Producer.beginTransaction()     broker stores txn state
Producer.send(topic-a, record)  → written with PID + epoch + in_txn=true
Producer.send(topic-b, record)  → written with PID + epoch + in_txn=true
Producer.commitTransaction()    → coordinator writes COMMIT marker
                                  → consumers with read_committed see records
```

If coordinator crashes between begin and commit → the transaction is **aborted** on coordinator
restart (coordinator writes ABORT marker). No message loss, no duplicates.

---

## 3. CAP Theorem Applied to Kafka

Kafka is a **CP system** (Consistency + Partition Tolerance) during leader election:

| Situation | Kafka Behavior |
|---|---|
| Leader broker crashes | Partition is **unavailable** until a new leader is elected from ISR |
| All ISR replicas offline | If `unclean.leader.election.enable=false` (default), partition stays **offline** (CP) |
| `unclean.leader.election.enable=true` | A stale out-of-sync replica becomes leader → **data loss possible** (AP mode) |
| Network partition splits ISR | `min.insync.replicas=2` causes producers to receive `NotEnoughReplicasException` (CP) |

**Production rule**: Never enable `unclean.leader.election` on financial topics. The availability
cost (short-term partition unavailability) is lower than the consistency cost (data loss + reconciliation).

---

## 4. Log Compaction — Event Sourcing State Tables

Log compaction retains only the **latest value per key**. All intermediate updates are removed.

```
Before compaction:
  offset 0: key="order-1" value={"status":"CREATED"}
  offset 1: key="order-2" value={"status":"CREATED"}
  offset 2: key="order-1" value={"status":"PAID"}
  offset 3: key="order-1" value={"status":"SHIPPED"}

After compaction:
  offset 1: key="order-2" value={"status":"CREATED"}
  offset 3: key="order-1" value={"status":"SHIPPED"}
```

**Tombstone records**: A record with `value=null` instructs the compactor to delete the key entirely. After compaction, the key disappears. This is how Kafka Streams `KTable` handles deletions.

**When to use log compaction**:
- Account balances (always need latest balance, not history)
- Entity state tables (user profile, inventory levels)
- Kafka Streams changelogs (internal state store backups)

**When NOT to use log compaction**:
- Audit logs (every event must be preserved)
- Financial transaction logs (immutable history)

Configure per topic:
```bash
kafka-configs.sh --bootstrap-server kafka:9092 --entity-type topics \
  --entity-name account-balances \
  --alter --add-config cleanup.policy=compact,min.cleanable.dirty.ratio=0.1
```

---

## 5. Consumer Group Protocol State Machine

A consumer group passes through these states managed by the **Group Coordinator** (a Kafka broker):

```
Empty ──JoinGroup──▶ PreparingRebalance ──AllJoined──▶ CompletingRebalance ──SyncGroup──▶ Stable
  ▲                        ▲                                                                  │
  │                        └──────────────── Member joins/leaves/times out ──────────────────┘
  └─────────────────────────────── All members leave ──────────────────────────────────────────
```

**Key transitions**:
- **PreparingRebalance**: Coordinator sends `JoinGroup` response. ALL members must rejoin (Eager) or selected members migrate (Cooperative). Processing halts during Eager rebalance.
- **CompletingRebalance**: Leader consumer (elected by coordinator) calculates partition assignment and sends it back in `SyncGroup` request.
- **Stable**: Normal operation. Heartbeats sent every `heartbeat.interval.ms` (default 3s). If heartbeat not received within `session.timeout.ms` (default 45s), member is evicted.

**Cooperative Sticky protocol** inserts an extra round-trip but avoids Stop-The-World:
- Round 1: Members rejoin, report current assignments.
- Coordinator calculates which partitions need to migrate.
- Round 2: Only members giving up partitions revoke; others keep theirs.

---

## 6. Event Sourcing vs CQRS vs Traditional CRUD

### 6.1 Traditional CRUD

```
HTTP POST /orders ──▶ UPDATE orders SET status='PAID' WHERE id=1 ──▶ Done
```
- Stores only the **current state**. History is lost.
- Cannot replay what happened. Cannot audit trail.
- Simple to implement. Cannot scale reads independently of writes.

### 6.2 CQRS (Command Query Responsibility Segregation)

```
Command side (writes):         Query side (reads):
POST /orders ──▶ DB (write)    GET /orders/1 ──▶ Read replica / Redis / Elasticsearch
                    │
                    └──▶ Event published ──▶ Projection builder ──▶ Read model updated
```
- Separates the write model (normalized, ACID) from read model (denormalized, fast).
- Allows independent scaling: 100 read pods, 5 write pods.
- Consistency: **eventual** — read model lags behind write model by replication delay.

### 6.3 Event Sourcing

```
POST /orders ──▶ Append OrderCreatedEvent to event store (Kafka / EventStoreDB)
PUT /orders/1/pay ──▶ Append OrderPaidEvent
GET /orders/1 ──▶ REPLAY: OrderCreatedEvent + OrderPaidEvent = current state
```
- **Current state = fold(initial_state, all_events)**.
- Complete audit trail is the primary data store — nothing is overwritten.
- Enables temporal queries: "What was the state of this order at 2026-09-15T14:00:00Z?"
- Enables event replay to populate new projections (e.g., add a new analytics view retroactively).

### 6.4 Decision Matrix

| Requirement | Traditional CRUD | CQRS | Event Sourcing |
|---|---|---|---|
| Simple domain with no audit needs | ✅ Best choice | Overkill | Overkill |
| High read/write ratio | ❌ Single DB bottleneck | ✅ | ✅ |
| Audit trail / compliance required | ❌ | Partial | ✅ Best choice |
| Temporal queries ("as-of" state) | ❌ | ❌ | ✅ |
| Team experience required | Low | Medium | High |
| Operational complexity | Low | Medium | High |

---

## 7. The Happens-Before Relation in Distributed Event Systems

In a distributed system, two events A and B have a **happens-before** relation (A → B) if:
1. A and B are in the same process, and A executes before B.
2. A is a message send, and B is the receipt of that message.
3. Transitivity: if A → C and C → B, then A → B.

**Why this matters for Kafka**: Kafka's partition ordering guarantee establishes the happens-before
relation only within a single partition. Events on different partitions have no causal relationship.

```java
// Producer thread (partition 0):
producer.send(new ProducerRecord<>("orders", "order-1", orderCreatedEvent));   // A
producer.send(new ProducerRecord<>("payments", "order-1", paymentInitEvent));  // B

// A → B is guaranteed within the producer thread
// BUT on the consumer side:
// Consumer on "orders" may process A
// Consumer on "payments" may process B BEFORE A is visible!
// → Violated happens-before across partitions
```

**Fix**: Use a single aggregate-scoped topic or implement vector clocks in event headers to
allow consumers to detect and buffer out-of-order delivery.


---

## 1. Apache Kafka Storage Internals & Log Segments

Kafka is an append-only commit log distributed across partitions:
- **Sequential Disk I/O**: Kafka writes records sequentially to OS page cache. Sequential disk writes on modern SSDs or spinning disks reach 600+ MB/s, comparable to sequential memory access.
- **Zero-Copy Data Transfer (`sendfile` syscall)**:
  Kafka avoids transferring data between kernel space and user space:
  $$\text{Disk} \longrightarrow \text{OS Page Cache} \overset{\text{sendfile()}}{\longrightarrow} \text{NIC Buffer} \longrightarrow \text{Network}$$
  The JVM process never touches the bytes during transmission, eliminating GC churn and CPU copy overhead.
- **Log Compaction**: Retains only the latest value for each primary key (e.g. state tables, account balances).

---

## 2. Delivery Guarantees & Exactly-Once Semantics (EOS)

1. **At-Most-Once (`acks=0`, commit before processing)**: Messages can be lost, but never duplicated. Unacceptable for financial/e-commerce data.
2. **At-Least-Once (`acks=all`, commit after processing)**: Messages are never lost, but can be duplicated if a consumer crashes before committing its offset. **Standard production baseline**. Requires consumer idempotency.
3. **Exactly-Once Semantics (EOS in Kafka)**:
   - *Idempotent Producer (`enable.idempotence=true`)*: Broker assigns each producer a unique PID (Producer ID) and sequence numbers to every batch. Duplicate sequence numbers are deduplicated by the broker.
   - *Transactional Producer (`transactional.id`)*: Atomic multi-partition writes across read-process-write loops (Kafka Streams).

---

## 3. The Transactional Outbox Pattern

A fundamental distributed systems problem: **How to atomically update a database and publish an event to Kafka without distributed 2PC transactions?**

```
+-------------------------------------------------------------------+
| Business Transaction Boundary (ACID)                             |
|                                                                   |
| 1. INSERT INTO orders (...)                                       |
| 2. INSERT INTO outbox_table (id, aggregate_type, payload, status) |
+-------------------------------------------------------------------+
                                 |
                                 v (CDC / Debezium)
+-------------------------------------------------------------------+
| Debezium / Change Data Capture (CDC)                              |
| Reads database WAL (Write-Ahead Log) -> Emits event to Kafka      |
+-------------------------------------------------------------------+
```

- If the service crashes after inserting the order, the outbox record is also rolled back.
- If the transaction commits, Debezium or an asynchronous polling publisher guarantees at-least-once delivery to Kafka.
