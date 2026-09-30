# INTERVIEW QUESTIONS: Data Architecture & Distributed Persistence
## Lab 17 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: Compare Choreographed Sagas vs Orchestrated Sagas. When would you choose one over the other?
**Answer**:
- **Choreography (Event-Driven)**:
  - Each microservice listens to domain events from Kafka and decides whether to act and publish the next event. There is no central manager.
  - *Pros*: Decentralized, loose coupling, ideal for simple linear flows (2–3 services).
  - *Cons*: Call graph is implicit; difficult to understand or debug; circular dependencies risk; hard to test end-to-end.
- **Orchestration (State Machine Coordinator)**:
  - A dedicated Saga Orchestrator service explicitly sends commands to participants and tracks workflow state in a database.
  - *Pros*: Explicit workflow definition, easy to monitor, straightforward error handling and compensation tracking.
  - *Cons*: Central orchestrator can become a single point of failure or bottleneck if not scaled properly.
- **Guideline**: Use Choreography for simple 2–3 service decoupled workflows; use Orchestration for complex multi-step financial or e-commerce workflows with complex compensation paths.

---

## Staff / Principal Level (8+ Years)

### Q2: Explain the PACELC theorem and give real-world architecture examples.
**Answer**:
The PACELC theorem extends CAP by recognizing that network partitions are rare; systems must also make trade-offs during normal error-free operations:
- **PC/EC** (e.g. Traditional RDBMS with synchronous replication, Google Spanner):
  If Partition: Choose Consistency over Availability. Else: Choose Consistency over Latency (clients wait for synchronous consensus).
- **PA/EL** (e.g. Cassandra, DynamoDB with eventual consistency):
  If Partition: Choose Availability over Consistency. Else: Choose Latency over Consistency (writes return immediately without waiting for cross-node replication).
- **PA/EC** (e.g. MongoDB with unacknowledged writes):
  If Partition: Availability. Else: Consistency.
- In financial ledgers, architects must select **PC/EC** to prevent balance duplication, accepting higher latency; in social feeds or click tracking, **PA/EL** is optimal.
