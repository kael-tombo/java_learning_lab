# ARCHITECTURE DECISIONS: Event-Driven Infrastructure Standards
## Lab 11 | Production Engineering Academy

---

## ADR-01: Guaranteed Delivery Architecture (Transactional Outbox Standard)

### Status: ACCEPTED

### Context
Dual-write inconsistencies between relational databases and Kafka event buses led to reconciliation discrepancies totaling $2.3M in missing order events during network partition events in 2025.

### Decisions
1. **Direct Dual-Writing Banned**:
   - Calling Kafka `producer.send()` inside or immediately following a JPA/JDBC transaction is strictly prohibited.
2. **Transactional Outbox Mandate**:
   - All state-changing services must implement the Transactional Outbox pattern.
   - Outbox tables must be co-located in the same database and transaction as the domain aggregate.
   - Event extraction via **Debezium CDC (Change Data Capture)** reading PostgreSQL WAL (Write-Ahead Log) into Kafka.
3. **Partitioning & Consumer Standards**:
   - Minimum replication factor = 3, `min.insync.replicas = 2`, producer `acks = all`.
   - Consumer groups must use `CooperativeStickyAssignor` to eliminate Stop-the-world rebalance storms.
   - All consumers must implement Dead Letter Queues (DLQ) with exponential backoff.

### Consequences
- Zero event loss even during database or Kafka broker outages.
- Requires maintaining Debezium Kafka Connect infrastructure.
