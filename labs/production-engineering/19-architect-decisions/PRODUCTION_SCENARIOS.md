# PRODUCTION SCENARIOS: Architectural Decision Case Studies
## Lab 19 | Production Engineering Academy

---

## Scenario 1: The "Resume-Driven Development" Cassandra Disaster

### Context
A fintech startup processing merchant settlements. The lead architect decided to replace their existing PostgreSQL database with Apache Cassandra because "Cassandra handles web scale."

### The Catastrophe (An Irreversible Type-1 Blunder)
- Merchant settlements inherently require relational integrity: complex joins, foreign keys, secondary indexes on customer/order/transaction, and strict ACID transaction rollbacks.
- Cassandra is an append-only distributed key-value store optimized for high-write, primary-key lookups without ACID transactions.
- To make Cassandra work, engineers wrote hundreds of lines of complex application-level consistency code, dual-writing to 6 denormalized tables for every transaction.
- Inevitably, network partitions caused cross-table data discrepancies. Auditing failed, merchant accounts had conflicting ledger balances, and developer velocity dropped to zero.
- After 18 months of operational misery and $4M in engineering time, the company was forced to migrate back to PostgreSQL.

### Key Lesson
Never make a Type-1 irreversible data store decision based on industry buzzwords or resume building. Always ground decisions in workload characteristics (read/write patterns, consistency requirements, relational query needs).

---

## Scenario 2: The ADR That Saved an Enterprise Acquisition

### Context
An enterprise software company was undergoing a technical due diligence audit for a $450M acquisition by a global financial institution.

### The Audit
The auditor questioned why the core payment platform chose a hybrid synchronous/asynchronous model (gRPC + Kafka) rather than pure event sourcing.
- Because the engineering team maintained a rigorous Git repository of Architecture Decision Records (`/docs/adr/`), the Principal Architect pulled up `ADR-028: Selection of gRPC and Kafka Hybrid Architecture`.
- The ADR contained:
  1. Detailed latency benchmarks comparing pure event-sourcing vs hybrid.
  2. Proof that merchant checkout required synchronous authorization confirmation within 150ms (which event sourcing could not guarantee).
  3. Risk analysis and accepted trade-offs.
- The auditor was blown away by the clarity and rigor of documentation. Technical due diligence passed in 2 days with zero valuation reduction.
