# Flashcards: CQRS & Event Sourcing - Banking (Lab 06)

> **Instructions:** Cover the answer side, recall from memory, then reveal. Shuffle periodically.

---

## Core Concepts

| # | Question | Answer |
|---|----------|--------|
| 1 | What is Event Sourcing? | Persist every state change as an immutable event. Current state = replay of all events. |
| 2 | What is CQRS? | Command Query Responsibility Segregation — separate write model (commands) from read model (queries). |
| 3 | How do ES and CQRS relate? | ES is a natural fit for CQRS write side. Events from commands update read models asynchronously. |
| 4 | What is an aggregate in DDD/ES? | A consistency boundary. Commands target one aggregate. Events are emitted by the aggregate. |
| 5 | What is a command vs an event? | Command = intent to change state (may be rejected). Event = fact that happened (immutable). |

---

## Banking Domain Events

| # | Question | Answer |
|---|----------|--------|
| 6 | List the 4 domain events in this implementation | AccountCreated, MoneyDeposited, MoneyWithdrawn, MoneyTransferred |
| 7 | What fields does AccountCreated carry? | accountId, owner, initialBalance, timestamp |
| 8 | What fields does MoneyDeposited carry? | accountId, amount, balanceAfter, timestamp |
| 9 | What fields does MoneyWithdrawn carry? | accountId, amount, balanceAfter, timestamp |
| 10 | What fields does MoneyTransferred carry? | fromAccountId, toAccountId, amount, fromBalanceAfter, toBalanceAfter, timestamp |
| 11 | Why is `balanceAfter` stored in deposit/withdraw events? | Enables projection reconstruction without replaying from start — snapshot of state at that point. |
| 12 | Why is MoneyTransferred a single event for both accounts? | Atomicity — either both accounts updated or neither. Represents one business transaction. |

---

## Event Store & Persistence

| # | Question | Answer |
|---|----------|--------|
| 13 | What are the 4 methods of the EventStore interface? | append, readEvents, readEventsSince, getSnapshot, saveSnapshot |
| 14 | How does optimistic concurrency work in append? | `expectedVersion` parameter. Store checks `actualVersion == expectedVersion` before appending. |
| 15 | What exception is thrown on version conflict? | `ConcurrencyConflictException` |
| 16 | How does InMemoryEventStore track versions? | `ConcurrentHashMap<String, AtomicLong> versionMap` — one per aggregate. |
| 17 | What does readEventsSince return? | Events after a given version (for snapshot-based replay). |
| 18 | Why use CopyOnWriteArrayList for event lists? | Thread-safe iteration during replay while appends create new copies. |

---

## Snapshotting

| # | Question | Answer |
|---|----------|--------|
| 19 | What triggers a snapshot? | `state.getVersion() % SNAPSHOT_THRESHOLD == 0` (every 50 events) |
| 20 | What does a Snapshot contain? | aggregateId, version, AccountState (full state), timestamp |
| 21 | How does load() use snapshots? | Load latest snapshot → replay events since snapshot.version → rebuild state |
| 22 | What is the benefit of snapshotting? | Reduces replay time from O(n) to O(snapshot interval) for long event streams. |
| 23 | When is the first snapshot created? | After 50 events (version 50, 100, 150...). Version 0 = no snapshot. |

---

## AccountRepository Operations

| # | Question | Answer |
|---|----------|--------|
| 24 | What does createAccount validate? | `initialBalance >= 0` (throws if negative) |
| 25 | What does deposit validate? | `amount > 0` |
| 26 | What does withdraw validate? | `amount > 0` AND `balance >= amount` |
| 27 | What does transfer validate? | `amount > 0` AND `fromAccount.balance >= amount` |
| 28 | What happens on validation failure? | Exception thrown, no event appended, state unchanged |
| 29 | How is transfer implemented? | Load both accounts → validate → create single MoneyTransferred event → append to BOTH aggregates |
| 30 | Why append same event to both aggregates? | Each aggregate has its own event stream. The event represents the transfer from each account's perspective. |

---

## Concurrency & Consistency

| # | Question | Answer |
|---|----------|--------|
| 31 | What consistency model does this ES implementation provide? | Eventual consistency for read models. Strong consistency within single aggregate (optimistic locking). |
| 32 | How is the transfer atomicity problem handled? | Comment says: "in practice use 2PC / transactional outbox". Current impl: two appends, not atomic. |
| 33 | What is the transactional outbox pattern? | Write events to an "outbox" table in same transaction as state change. Relay publishes to message broker. |
| 34 | How would you make transfer truly atomic? | Use a saga: TransferStarted → (debit + credit) → TransferCompleted / TransferFailed with compensations. |
| 35 | What happens if two concurrent deposits hit same account? | Second append fails with ConcurrencyConflictException (version mismatch). Client retries. |

---

## Projections & Read Models

| # | Question | Answer |
|---|----------|--------|
| 36 | How is AccountState built? | `load()` applies events sequentially via `apply(Event)` method. |
| 37 | What does apply() do for AccountCreated? | Sets accountId, owner, balance = initialBalance, version = 0 |
| 38 | What does apply() do for MoneyDeposited? | balance = balanceAfter, version++ |
| 39 | What does apply() do for MoneyTransferred? | Updates balance based on whether this account is from/to, version++ |
| 40 | Can you have multiple projections from same events? | Yes — that's the power of ES. Balance projection, audit log, fraud detection, etc. |

---

## Testing & Edge Cases

| # | Question | Answer |
|---|----------|--------|
| 41 | How does the test verify snapshotting? | Creates 55 events, checks balance is correct (snapshot at 50, replay 5 more) |
| 42 | What does ConcurrencyConflictException test verify? | Direct store.append with wrong version throws exception |
| 43 | What happens with negative initial balance? | IllegalArgumentException in createAccount |
| 44 | What happens with zero/negative deposit? | IllegalArgumentException |
| 45 | What happens with zero/negative withdrawal? | IllegalArgumentException |

---

## Advanced Patterns

| # | Question | Answer |
|---|----------|--------|
| 46 | What is a process manager / saga? | Coordinates long-running multi-aggregate transactions using events and compensations. |
| 47 | How do you handle event schema evolution? | Upcasting (transform old events to new schema), or versioned event types. |
| 48 | What is the "eventual consistency" window? | Time between command processing and read model update. Depends on projection speed. |
| 49 | How do you query across aggregates? | Read models / projections. ES doesn't support cross-aggregate queries directly. |
| 50 | What is the difference between ES and CDC? | ES = events are source of truth. CDC = events derived from database changes (DB is source). |

---

## Quick Reference: Key Classes

| Class | Responsibility |
|-------|----------------|
| `EventStore` | Interface for event persistence |
| `InMemoryEventStore` | In-memory implementation with concurrency control |
| `AccountState` | Projection — current state built from events |
| `AccountRepository` | Command handler — validates, emits events, manages snapshots |
| `Event` (sealed) | Base type for all domain events |
| `Snapshot` | Checkpoint of aggregate state at a version |

---

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| No snapshotting | Replay O(n) becomes slow at scale | Snapshot every N events |
| Weak concurrency | Lost updates | Optimistic locking with version |
| Non-atomic multi-aggregate | Inconsistent state | Saga / transactional outbox |
| Event schema changes | Deserialization failures | Upcasters, versioned events |
| No idempotency | Duplicate processing | Deduplicate by event ID / command ID |
| Large event payloads | Storage/performance issues | Store references, not full objects |

---

## Related Patterns

| Pattern | Relation |
|---------|----------|
| **Saga** | Manages distributed transactions across aggregates |
| **Transactional Outbox** | Reliable event publishing |
| **Read Model / Projection** | Denormalized views for queries |
| **Event Replay** | Rebuild state, fix bugs, migrate schemas |
| **CQRS** | Separate read/write models |
| **Event-Driven Architecture** | Services communicate via events |