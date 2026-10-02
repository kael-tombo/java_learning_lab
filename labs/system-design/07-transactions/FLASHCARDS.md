# Distributed Transactions Flashcards

## Two-Phase Commit (2PC)

**Q: What are the two phases of 2PC?**
**A:** 1) Prepare: Coordinator asks all to prepare. 2) Commit/Abort: Coordinator decides based on all votes.

**Q: Why does 2PC block?**
**A:** After voting "Ready", participant holds locks and waits for coordinator. If coordinator fails, participant blocks indefinitely (in-doubt).

**Q: What is the coordinator's single point of failure?**
**A:** If coordinator crashes after collects votes but before sending decide, participants block forever.

**Q: How does 3PC reduce blocking?**
**A:** Adds PreCommit phase. If coordinator fails in phase 1, participants can safely abort (no one prepared). If in phase 2, they can commit.

**Q: Does 3PC solve blocking completely?**
**A:** No. FLP impossibility: in async networks, no deterministic protocol guarantees both safety and termination.

**Q: When is 2PC appropriate?**
**A:** Short transactions, few participants, all resources support XA, strong consistency required, can tolerate blocking.

---

## Saga Pattern

**Q: What is a Saga?**
**A:** Sequence of local transactions with compensating actions for rollback.

**Q: Choreography vs Orchestration?**
**A:** Choreography = event-driven, decentralized. Orchestration = central coordinator directs flow.

**Q: What is a compensating transaction?**
**A:** Semantic inverse of a forward action (e.g., `refund()` for `charge()`). Not always perfect technical inverse.

**Q: What is the pivot transaction?**
**A:** The step after which only forward recovery is possible (no compensation).

**Q: Saga isolation problem?**
**A:** No isolation between steps. Other transactions see intermediate states. Mitigation: Semantic locks, commutative operations, retry.

**Q: How to handle Saga timeout?**
**A:** Orchestrator tracks step timeouts. On timeout: query service status via idempotency key → retry or compensate.

---

## Outbox Pattern

**Q: What problem does the outbox pattern solve?**
**A:** Atomicity of: local DB update + event publish. Dual-write to two systems is not atomic.

**Q: How does the outbox work?**
**A:** Write event to OUTBOX table in same DB transaction as business data. Separate relay publishes to broker.

**Q: Relay variants?**
**A:** Polling (simple, latency = poll interval), Log tailer (Debezium, low latency), Transactional outbox (Kafka transactions).

**Q: Why not just use Kafka transactions?**
**A:** Kafka transactions only cover Kafka → Kafka. Outbox covers DB → Kafka.

---

## Idempotency & Exactly-Once

**Q: What is an idempotency key?**
**A:** Client-generated unique token per operation. Server uses it to detect and deduplicate retries.

**Q: Exactly-once delivery vs processing?**
**A:** Delivery = message arrives once. Processing = business logic executes once. Need idempotent consumer for latter.

**Q: Natural idempotency examples?**
**A:** `SET status = 'PAID'`, `DELETE FROM ... WHERE id = ?`, `UPSERT` with same values.

**Q: How to implement idempotent consumer?**
**A:** Track processed (key, result) in DB. On receive: check key → if exists return result, else process & store.

---

## Calvin / Spanner

**Q: Calvin's key insight?**
**A:** Deterministic transactions → no locks needed during execution. Order via consensus, execute in order.

**Q: What must be deterministic in Calvin?**
**A:** Transaction logic: same inputs → same outputs. No random, no time, no external calls.

**Q: Spanner's TrueTime?**
**A:** GPS + atomic clocks → bounded uncertainty ε. Enables external consistency via commit timestamps.

**Q: Spanner external consistency?**
**A:** If T1 commits before T2 starts, T1's commit timestamp < T2's commit timestamp. Guaranteed by waiting ε.

**Q: Calvin vs Spanner tradeoff?**
**A:** Calvin: lower latency (1 RTT), requires deterministic txns. Spanner: general SQL, 2 RTT + ε wait, needs special hardware.

---

## Mathematical Foundations

**Q: FLP Impossibility?**
**A:** No deterministic consensus protocol can guarantee both safety and termination in async systems with one crash.

**Q: Implication for 2PC?**
**A:** 2PC cannot be both non-blocking and safe in async networks. It chooses safety (blocking).

**Q: State machine replication?**
**A:** All replicas apply same commands in same order → identical state. Consensus (Paxos/Raft) orders commands.

**Q: Quorum for 2PC?**
**A:** All participants must vote (W = N). No quorum flexibility — single failure blocks.

---

## Pattern Selection

**Q: 2PC vs Saga decision tree?**
**A:** 2PC: short, few, XA support, strong consistency. Saga: long, many, external services, can tolerate eventual.

**Q: When to use Outbox?**
**A:** Any time service must update DB and publish event atomically.

**Q: When is exactly-once needed?**
**A:** Financial transactions, inventory decrement, any non-idempotent business operation.