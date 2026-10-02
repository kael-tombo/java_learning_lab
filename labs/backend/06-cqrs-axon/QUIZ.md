# Quiz: CQRS & Event Sourcing - Banking Transactions (Lab 06)

**Topic:** Event-Sourced Banking Transaction Repository  
**Difficulty:** Medium  
**Time Limit:** 15 minutes

---

## Questions

### 1. Core Concept
What is the fundamental principle of Event Sourcing?
- A) Store only current state, discard history
- B) Store all state changes as a sequence of events
- C) Store state in a relational database with triggers
- D) Store snapshots only, rebuild events on demand

### 2. Events
In the `BankingEventSourcing` implementation, which event is emitted when an account is created?
- A) AccountOpened
- B) AccountCreated
- C) AccountInitialized
- D) AccountRegistered

### 3. Projections
How is the current account balance derived in this implementation?
- A) Stored directly in the AccountState and updated on each command
- B) Computed by replaying all events from the beginning
- C) Queried from a separate read model table
- D) Calculated using a database view

### 4. Snapshotting
When does the `AccountRepository` create a snapshot?
- A) After every event
- B) Every 50 events (`SNAPSHOT_THRESHOLD = 50`)
- C) When the event store reaches 1000 events
- D) Only on explicit `saveSnapshot()` call

### 5. Concurrency Control
What mechanism prevents concurrent modifications to the same account?
- A) Pessimistic locking with `synchronized`
- B) Optimistic concurrency with expected version
- C) Database row-level locks
- D) Single-threaded event processor

### 6. Transfer Operation
In the `transfer()` method, how are events appended to both accounts?
- A) In a single atomic transaction
- B) Two separate `append()` calls (not atomic in this implementation)
- C) Using a saga orchestrator
- D) Via a two-phase commit protocol

### 7. Insufficient Funds
What happens when a withdrawal exceeds the account balance?
- A) The withdrawal succeeds with negative balance
- B) An `InsufficientFundsException` is thrown and no event is appended
- C) An `OverdraftEvent` is emitted
- D) The command is queued for retry

### 8. Event Store
The `InMemoryEventStore` uses `ConcurrentHashMap<String, List<Event>>`. What does the key represent?
- A) Event ID
- B) Aggregate ID (accountId)
- C) Correlation ID
- D) Timestamp

### 9. Snapshot Structure
What does a `Snapshot` contain?
- A) Only the aggregate ID and version
- B) Aggregate ID, version, full AccountState, timestamp
- C) Only the latest event
- D) Aggregate ID and a diff from previous snapshot

### 10. Version Tracking
How is the aggregate version tracked in `AccountState`?
- A) Incremented on every event application
- B) Set to the event store's global version
- C) Derived from event count during replay
- D) Not tracked in AccountState

---

## Answers

| # | Answer | Explanation |
|---|--------|-------------|
| 1 | **B** | Event Sourcing persists every state-changing event. Current state is derived by replaying events. |
| 2 | **B** | `AccountCreated` event (line 102) with accountId, owner, initialBalance, timestamp. |
| 3 | **B** | `load()` replays events from snapshot (if exists) or from beginning to build `AccountState`. |
| 4 | **B** | `SNAPSHOT_THRESHOLD = 50`. After every 50 events, a new snapshot is saved. |
| 5 | **B** | `append()` takes `expectedVersion`. If actual version differs, `ConcurrencyConflictException` is thrown. |
| 6 | **B** | Two separate `append()` calls. The comment notes: "in practice use 2PC / transactional outbox" — not atomic here. |
| 7 | **B** | `withdraw()` checks balance first, throws `InsufficientFundsException` before appending event. |
| 8 | **B** | Key = `aggregateId` (accountId). Value = list of events for that aggregate. |
| 9 | **B** | `Snapshot` record: aggregateId, version, AccountState state, timestamp. |
| 10 | **A** | `AccountState.version` increments in `apply()` for each event (deposit, withdraw, transfer). |

---

## Scoring

| Score | Level |
|-------|-------|
| 9-10 | Expert — Ready for event-sourced systems |
| 7-8 | Proficient — Solid grasp of CQRS/ES patterns |
| 5-6 | Developing — Review snapshotting and concurrency |
| <5 | Beginner — Re-read LEETCODE_SOLUTION and test cases |

---

## Further Study

- Read `MOCK_INTERVIEW.md` for deep-dive Q&A
- Study Axon Framework for production CQRS/ES
- Explore EventStoreDB, Apache Kafka for event storage
- Practice: Add saga for distributed transfers, read models