# Mock Interview: Event Sourcing for Banking Transactions (Lab 06)

**Role:** Senior Backend Engineer
**Duration:** 55 minutes
**Difficulty:** Easy to Medium to Hard

---

## Round 1: Easy Event Sourcing Concepts (5 min)

**Interviewer:** What is event sourcing and how is it different from traditional CRUD?

**Candidate:** In event sourcing every state change is stored as an immutable event in an append-only log. The current state is derived by replaying the events. In CRUD you store the current state directly and overwrite on each update. Event sourcing gives you complete history enabling audit trails, time travel, and complex event-driven workflows. The trade-off is reads are more expensive (replay events) and storage grows monotonically. Event sourcing shines in domains with strict audit requirements like banking and accounting.

**Interviewer:** What is an event? Give banking-specific examples.

**Candidate:** An event is a fact that has already happened expressed in the past tense: AccountCreated, MoneyDeposited, MoneyWithdrawn, MoneyTransferred, AccountFrozen, AccountClosed. Each event contains all relevant data: aggregate ID, timestamp, and specific attributes (amount, new balance). Events are immutable once appended they are never modified or deleted.

**Interviewer:** How does CQRS relate to event sourcing?

**Candidate:** CQRS separates the write model from the read model. Commands go through the event-sourced aggregate validating business rules and producing events. Queries go through a separate projection a materialized view optimized for specific queries. In my banking example the command Withdraw(amount=100) goes through AccountRepository which loads the aggregate, checks balance, and appends MoneyWithdrawn. The query getBalance() can replay the aggregate (consistent but expensive) or read from a projection table (fast but eventually consistent).

---

## Round 2: Medium Aggregate Design and Invariants (10 min)

**Interviewer:** Walk me through the account aggregate. How does it enforce no-negative-balance?

**Candidate:** AccountState is the aggregate root with fields like balance, version, and owner. The apply(Event) method mutates state based on event type. The command handler withdraw() first loads the aggregate to current state then checks state.getBalance().compareTo(amount) >= 0. If the invariant passes it creates and appends MoneyWithdrawn. The event is then applied to the state. The invariant is checked against current state not the event.

**Interviewer:** How do you handle the same event applied twice (idempotency)?

**Candidate:** Event sourcing is inherently idempotent if events are applied in order. Each event transforms state deterministically. The expectedVersion check ensures events are only appended if the aggregate is at the expected version. If a command handler crashes after appending but before responding, the retry sees the updated version and produces a different event. In distributed systems an idempotency key ensures exactly-once processing.

**Interviewer:** How do you ensure atomicity during a transfer between two accounts?

**Candidate:** A transfer is a saga a multi-step distributed transaction. Step 1: Load source, check balance, append MoneyTransferred (debit). Step 2: Load target, append MoneyTransferred (credit). Both must succeed. In production I use a transactional outbox: the command handler writes both events as a single unit to an outbox table in a local transaction. A separate process reads from the outbox and publishes to the event store for both aggregates. If the process crashes it retries from the outbox ensuring exactly-once delivery.

---

## Round 3: Medium-Hard Snapshots (10 min)

**Interviewer:** Event streams grow unbounded. How do you optimize loading?

**Candidate:** Snapshots. After every N events (snapshotThreshold default 50) I persist the aggregate state. On load I read the latest snapshot and replay only events after that snapshot version. If snapshot is at version 50 and stream has 1000 events I replay 950 instead of all 1000. The savings compound as the stream grows. The snapshot is a serialized AccountState stored alongside the event stream.

**Interviewer:** When do you create a snapshot eagerly at append or lazily at load?

**Candidate:** Lazy during aggregate loading. After replaying events, if version modulo snapshotThreshold equals 0 I save the snapshot. This spreads the cost across read operations. The downside is the first read after a snapshot is due also writes the snapshot. For high-write aggregates with infrequent reads, I add a background process that periodically snapshots aggregates exceeding the threshold.

**Interviewer:** How do you handle snapshot schema evolution?

**Candidate:** Snapshots are versioned. The Snapshot record includes a version field. On deserialization I check the version. If the snapshot is in an older format I replay from the last compatible snapshot (or from scratch) to rebuild state in the new format then save a new snapshot. This approach is safe because events never change so state can always be correctly reconstructed by replay.

---

## Round 4: Hard Performance and Consistency (15 min)

**Interviewer:** How would you implement a projection for a read model (e.g., account dashboard)?

**Candidate:** A Projection component subscribes to the event store. When a new event appears the projection updates its materialized table. For example MoneyDeposited events increment balance in the account_summary table. The projection tracks its position (last processed event offset). The projection table is optimized for queries with indexes making reads O(1) B-tree lookups.

**Interviewer:** What consistency guarantees does a projection offer?

**Candidate:** Eventual consistency. There is a lag between event append and projection consumption. Event sourcing systems accept this lag (milliseconds to seconds) because the command path provides strong consistency for writes. If a user deposits money and immediately queries the read model they might see the old balance. The transaction confirmation shows the write result directly and the dashboard eventually catches up.

**Interviewer:** How do you handle concurrency conflicts?

**Candidate:** Optimistic concurrency via expectedVersion. When loading the aggregate I record the current version. When appending the event store checks currentVersion == expectedVersion + numEvents. If another command appended in between, ConcurrencyConflictException is thrown. The handler retries reloads the aggregate (including the other command events) revalidates and reattempts. Works well for low-contention aggregates. For hot accounts I would use pessimistic locking.

**Interviewer:** How would you test an event-sourced system?

**Candidate:** Three levels. (1) Unit: given aggregate initial state when event X is applied then state should be Y. (2) Command handler: given past events when command C is processed then event E should be appended or exception thrown. (3) Integration: given event store when sequence of commands executed then projected state should be correct. Property-based testing with jqwik can generate random deposit/withdrawal/transfer sequences and verify invariants like total balance is conserved.

---

## Round 5: Summary (5 min)

**Interviewer:** What are the biggest challenges in adopting event sourcing in a real bank?

**Candidate:** (1) Operational complexity running event store, managing snapshots, handling projection lag. (2) Schema evolution events are immutable so backward compatibility is required. Every event payload should accept optional fields. (3) Event versioning when schema changes old events must still be replayable. (4) Performance at scale accounts with millions of transactions require aggressive snapshotting. (5) Team expertise event sourcing requires a different mental model than CRUD. The benefits complete audit trail, temporal queries, event-driven integrations are enormous but the learning curve is steep.
