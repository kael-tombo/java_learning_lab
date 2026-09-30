# INTERVIEW QUESTIONS: Event-Driven & Kafka Architecture
## Lab 11 | Senior / Staff / Principal Level

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
