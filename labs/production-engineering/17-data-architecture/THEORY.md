# THEORY: Data Architecture, Distributed Transactions & Polyglot Persistence
## Lab 17 | Production Engineering Academy

---

## 1. CAP Theorem and PACELC Theorem

In distributed data storage:
- **CAP Theorem** (Eric Brewer): Under network partition (**P**), a system must choose between Consistency (**C**) and Availability (**A**).
- **PACELC Theorem** (Daniel Abadi): Extends CAP to normal operating conditions:
  $$\text{If Partition (P) } \longrightarrow \text{ Availability (A) vs Consistency (C)}$$
  $$\text{Else (E) } \longrightarrow \text{ Latency (L) vs Consistency (C)}$$
  - Systems like MongoDB and PostgreSQL (with synchronous replication) choose **PC/EC** (Consistency under partition, Consistency at the cost of higher latency).
  - Systems like Amazon DynamoDB and Apache Cassandra choose **PA/EL** (Availability under partition, lower Latency at the cost of eventual consistency).

---

## 2. Distributed Transactions: Two-Phase Commit (2PC) vs Saga Pattern

### Why 2PC Fails at Scale
Two-Phase Commit (XA transactions) requires a centralized transaction coordinator:
1. *Prepare Phase*: Coordinator asks all participants to acquire row locks and prepare to commit.
2. *Commit Phase*: If all vote YES, coordinator sends COMMIT.
- **Flaw**: It is a **blocking protocol**. If the coordinator or any database node stalls during Phase 1, all participants hold row locks indefinitely. Latency multiplies, throughput crashes, and network partitions lead to cluster-wide lock deadlocks.

### The Saga Pattern (Choreography vs Orchestration)
A Saga is a sequence of local transactions where each step updates a local database and emits an event triggering the next step:
- **Forward Recovery**: All steps succeed sequentially.
- **Backward Recovery (Compensating Transactions)**: If Step 3 fails (e.g. insufficient payment funds), the Saga executes explicit business compensating transactions for Step 2 and Step 1 (e.g. release reserved inventory, cancel order).
- No global locks are ever held across network boundaries.

```
Order Service      Inventory Service      Payment Service
     |                    |                      |
     |--- 1. Create ----->|                      |
     |    (Pending)       |--- 2. Reserve ------>|
     |                    |    Inventory         |--- 3. Charge Fails!
     |                    |                      |           |
     |                    |<-- 4. Compensate ----+-----------+
     |<-- 5. Cancel ------|    Release Stock
     |    Order
```

---

## 3. CQRS (Command Query Responsibility Segregation)

Separate the write data model from the read data model:
- **Command (Write Path)**: Highly normalized relational schema (PostgreSQL) optimized for transactional integrity, validation, and minimal write contention.
- **Query (Read Path)**: Denormalized, pre-aggregated read models stored in Elasticsearch, Redis, or DynamoDB, optimized for sub-millisecond retrieval without complex SQL joins.
- Synchronization: Asynchronously streamed via Kafka / CDC.
