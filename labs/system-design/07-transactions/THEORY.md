# Distributed Transactions Theory

## Two-Phase Commit (2PC)

### Protocol
```
Phase 1 - Prepare:
  Coordinator → All Participants: "Prepare"
  Participant: Execute locally, acquire locks, write to log
  Participant → Coordinator: "Ready" or "Abort"

Phase 2 - Commit/Abort:
  If ALL "Ready": Coordinator → All: "Commit"
  Else: Coordinator → All: "Abort"
  Participant: Release locks, write final outcome
```

### Properties
- **Atomicity**: All commit or all abort
- **Blocking**: Participants hold locks after "Ready" until coordinator decides
- **Coordinator SPOF**: If coordinator fails after prepare, participants block indefinitely

### Failure Scenarios
| Failure Point | Behavior |
|---------------|----------|
| Participant fails before prepare | Abort (timeout) |
| Participant fails after "Ready" | Block until coordinator recovers |
| Coordinator fails before decide | Participants block (in-doubt) |
| Coordinator fails after decide | New coordinator reads log, continues |

### Three-Phase Commit (3PC)
Adds **Pre-Commit** phase to reduce blocking:
1. CanCommit? → 2. PreCommit → 3. Commit
Non-blocking if coordinator fails in phase 1 or 2 (participants can decide via timeout).
**Still not truly non-blocking** in async networks (FLP impossibility).

---

## Saga Pattern

### Core Idea
Sequence of local transactions `T1, T2, ..., Tn` with compensating actions `C1, C2, ..., Cn-1`.
If `Ti` fails, execute `Ci-1, ..., C1` to undo.

### Choreography (Event-Driven)
```
Service A → (Event) → Service B → (Event) → Service C
     ↑                                    ↓
     └──────── (Compensation Events) ──────┘
```
- **Pros**: Decoupled, no central coordinator
- **Cons**: Hard to track, cyclic dependencies, implicit flow

### Orchestration (Centralized)
```
Saga Orchestrator → Service A
                  → Service B (on A success)
                  → Service C (on B success)
                  → Compensate B, A (on C failure)
```
- **Pros**: Explicit flow, easier debugging, centralized retry logic
- **Cons**: Orchestrator is central point (mitigate: stateless, replicated)

### Compensation Design
| Forward Action | Compensation |
|----------------|--------------|
| `reserveInventory()` | `releaseInventory()` |
| `chargePayment()` | `refundPayment()` |
| `createShipment()` | `cancelShipment()` |
| `sendEmail()` | `sendCorrectionEmail()` (often not possible) |

**Semantic Compensation**: Business-logic inverse, not technical rollback.
**Pivot Transaction**: The point of no return (after which only forward recovery).

---

## Outbox Pattern

### Problem
Microservice needs to: (1) Update local DB, (2) Publish event. Must be atomic.

### Solution
```
Transaction:
  1. Write business data
  2. Write event to OUTBOX table (same DB, same transaction)
  
Separate Process (Relay):
  3. Poll OUTBOX → Publish to message broker
  4. Mark OUTBOX entry published
```

### Variants
- **Polling Relay**: Simple, latency = poll interval
- **Transaction Log Tailer** (Debezium): Low latency, no poll
- **Dual Write Avoidance**: Never write to two systems in one transaction

---

## Idempotency & Exactly-Once

### Idempotency Key
Client generates unique key per operation. Server deduplicates:
```sql
INSERT INTO idempotency_keys (key, result) VALUES (?, ?)
ON CONFLICT (key) DO UPDATE SET result = EXCLUDED.result;
```

### Exactly-Once Processing
1. **At-least-once delivery** + **Idempotent processing** = Exactly-once
2. **Kafka Transactions**: Producer sends to multiple topics atomically
3. **Deduplication at Consumer**: Track processed offsets/keys

### Patterns
| Pattern | Mechanism |
|---------|-----------|
| Natural Idempotency | `SET status = 'PAID'` (idempotent) |
| Idempotency Key | Client token, server dedup |
| Effectively-Once | Idempotent write + transactional outbox |

---

## Calvin / Spanner Approach

### Calvin (Deterministic DB)
1. **Sequencer**: Assign global transaction ID via Paxos
2. **Scheduler**: Pre-process transactions, determine read/write sets
3. **Executor**: Run in deterministic order (no locks needed)
4. **Replication**: State machine replication via Paxos

**Key**: Determinism → No coordination during execution.

### Spanner (Google)
- **TrueTime**: GPS + Atomic clocks → bounded clock uncertainty ε
- **Paxos**: Per-shard consensus
- **External Consistency**: Commit timestamp > all prior commit timestamps
- **Reads**: Snapshot at `now() - ε` (guaranteed consistent)

### Comparison
| Aspect | 2PC | Saga | Calvin | Spanner |
|--------|-----|------|--------|---------|
| Consistency | Strong | Eventual | Strong | Strong |
| Latency | 2 RTT | Variable | 1 RTT (after seq) | 2 RTT + ε |
| Availability | Low (blocking) | High | Medium | High |
| Complexity | Medium | High | High | Very High |
| Use Case | Short, few participants | Long, many services | High throughput OLTP | Global scale SQL |

---

## Mathematical Foundations

### FLP Impossibility
> In an asynchronous system with even one crash failure, no deterministic consensus protocol can guarantee both safety and termination.

**Implication**: 2PC/3PC **cannot** be both non-blocking and safe in async networks.

### State Machine Replication
```
Client → Consensus (Paxos/Raft) → Log → State Machine → Response
```
All replicas apply same commands in same order → identical state.

### Quorum for Transactions
```
N = replicas
W = write quorum (prepare votes)
R = read quorum
Strong: W + R > N
2PC: W = N (all must prepare)
```

---

## Pattern Selection Guide

```
Need strong consistency across services?
├─ Short-lived, few participants → 2PC (or Calvin/Spanner if available)
└─ Long-lived, many services → Saga (orchestrated)

Can tolerate eventual consistency?
├─ High throughput, simple compensation → Choreography Saga
├─ Complex flow, need visibility → Orchestrated Saga
└─ Event-driven, already using Kafka → Outbox + Kafka Transactions

Cross-region?
├─ Low latency critical → Saga (async)
└─ Consistency critical → Spanner/Calvin style
```

---

## References
- "Saga Pattern" - Hector Garcia-Molina
- "Calvin: Fast Distributed Transactions" - Thomson et al.
- "Spanner: Google's Globally-Distributed Database" - Corbett et al.
- "Enterprise Integration Patterns" - Hohpe & Woolf
- "Building Microservices" - Sam Newman