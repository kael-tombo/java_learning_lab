# THEORY: Event-Driven Architecture & Apache Kafka in Production
## Lab 11 | Production Engineering Academy

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
