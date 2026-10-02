# Distributed Transactions Quiz

## Questions

1. **2PC Blocking**: In 2PC, a participant votes "Ready" then the coordinator crashes. What state is the participant in? Can it unilaterally decide to commit or abort?

2. **Saga vs 2PC**: You have an order flow: Payment → Inventory → Shipping. Payment is external (Stripe), Inventory and Shipping are internal. Which pattern (2PC or Saga) fits better? Why?

3. **Compensation Design**: A Saga step calls `sendWelcomeEmail(userId)`. The step succeeds but later a downstream step fails. What is the compensation? Is it a true inverse?

4. **Outbox Pattern**: Why is dual-write (DB + Kafka in same transaction) dangerous? How does the outbox pattern solve this? What is the latency tradeoff?

5. **Idempotency**: A client retries a `POST /orders` with the same idempotency key. The first request succeeded but response was lost. How does the server handle this? What if the first request is still processing?

6. **PACELC in Transactions**: A Saga uses async messaging (Kafka) between steps. Classify its PACELC: PA/EL, PA/EC, PC/EL, or PC/EC? What about a 2PC-based system?

7. **Exactly-Once**: "Kafka transactions give you exactly-once semantics." True or false? Explain the difference between exactly-once delivery and exactly-once processing.

8. **Calvin/Spanner**: Calvin uses deterministic execution to avoid locks. What property must transactions have for this to work? How does Spanner achieve external consistency without determinism?

9. **Failure Injection**: In an orchestrated Saga, the orchestrator crashes after sending "ReserveInventory" but before receiving the response. On restart, how does it know whether to retry or compensate?

10. **Real-World Trade-off**: Design a distributed transaction for: "Transfer $100 from Account A (Shard 1) to Account B (Shard 2)". Requirements: No lost money, < 100ms latency, survive single shard failure. Choose: (a) 2PC, (b) Saga, (c) Calvin-style deterministic. Justify with numbers.

---

## Answers

1. **In-doubt state**: Participant holds locks, cannot release. **Cannot unilaterally decide** — must wait for coordinator. If it commits and coordinator aborted, inconsistency. If it aborts and coordinator committed, lost update. This is the **blocking problem** of 2PC.

2. **Saga (orchestrated)**. 
   - 2PC requires all participants to be transactional and available. Stripe doesn't support 2PC prepare phase.
   - Saga allows external services (Payment) to be called async with compensation (refund).
   - Inventory/Shipping can be local transactions with compensations.

3. **Compensation**: Send "account cancellation" or "ignore welcome" email. **Not a true inverse** — you cannot "unsend" an email. This is **semantic compensation** (business-level undo). Some actions (notifications, physical shipments) have no perfect inverse.

4. **Dual-write danger**: If DB commits but Kafka publish fails → event lost. If Kafka succeeds but DB rolls back → phantom event. **No atomicity across systems**.
   **Outbox**: Write event to OUTBOX table in same DB transaction. Relay publishes async. **Tradeoff**: Event visible after relay latency (ms to seconds).

5. **Server checks idempotency key**: 
   - If key exists with result → return stored result (don't re-execute)
   - If key exists but "processing" → wait or return 409 Conflict
   - If key not found → execute, store result, return

6. **Saga with async messaging**: **PA/EL** — In partition: Available (local commits proceed), but consistency sacrificed (compensations may lag). Else: Low latency (async), eventual consistency.
   **2PC**: **PC/EC** — In partition: Consistent (blocks), sacrifices availability. Else: Consistent (synchronous), latency cost.

7. **False**. 
   - **Exactly-once delivery**: Message delivered exactly once to consumer (Kafka transactions + idempotent producer).
   - **Exactly-once processing**: Business logic executes exactly once. Requires **idempotent consumer** (dedup keys) + transactional outbox. Kafka transactions alone don't guarantee processing exactly-once.

8. **Calvin**: Transactions must be **deterministic** — same inputs → same outputs, no randomness, no external calls during execution. Read/write sets known in advance.
   **Spanner**: Uses **TrueTime** (bounded clock uncertainty ε). Commits at timestamp `s.max + ε`. Waits out uncertainty before serving reads. Paxos for replication.

9. **Orchestrator persistence**: Must persist **Saga state** (current step, step status, compensation data) **before** sending each command.
   On restart: Read state → if step was "SENT" but no reply → query service for status (idempotency key) → decide retry or compensate.

10. **Choice: (c) Calvin-style deterministic** (or Spanner if available).
    - **Why not 2PC**: 2 RTT + blocking = >100ms risk, availability risk on shard failure.
    - **Why not Saga**: Eventual consistency → temporary negative balance possible, violates "no lost money" (needs strong consistency for ledger).
    - **Calvin/Spanner**: 1 RTT (after sequencing), strong consistency, survives failures via Paxos. Spanner adds ε (~5ms) wait. Fits <100ms.