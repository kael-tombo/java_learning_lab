# Mock Interview: Event Sourcing

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Design an audit trail system using event sourcing

**Interviewer**: "Design an audit trail system for a financial application. How do you track every state change?"

**Candidate**: "Event sourcing is the natural choice. Instead of storing current state, we store a sequence of events that represent every state change. The current state is derived by replaying the events."

**Interviewer**: "Walk me through the event stream for a bank account."

**Candidate**: "For a bank account, the event stream would be: AccountCreated, DepositMade, WithdrawalMade, FundsTransferred, AccountFrozen, AccountClosed. Each event captures what happened, when, and by whom. The current balance is computed by replaying deposits and withdrawals."

**Interviewer**: "How do you handle concurrent writes to the same account?"

**Candidate**: "Optimistic concurrency. Each event stream has a version number. When appending an event, the caller provides the expected version. If another writer has already appended an event, the version doesn't match, and the append fails. The caller retries by reading the latest events and reconstructing state."

**Interviewer**: "What about querying current state efficiently?"

**Candidate**: "That's the trade-off with event sourcing. Two approaches: (1) Snapshots — periodically save the current state and replay events only since the snapshot. (2) Projections — maintain a read model that's updated as events are appended. For the bank account, a projection table might have `account_id, balance, frozen_status` updated in real-time."

**Interviewer**: "How do you handle schema evolution of events?"

**Candidate**: "Events are immutable — you can't change past events. For schema changes, you add new event versions. Old events stay as they are. Your event processing code must handle all versions. You can also write upcasters — code that transforms old-version events to new-version format when loading."

**Interviewer**: "When would you NOT use event sourcing?"

**Candidate**: "When the benefits don't justify the complexity. Event sourcing adds significant operational overhead — event store management, schema evolution, projection maintenance. It's overkill for simple applications where an audit log can be a separate table alongside current state. Use it when you truly need: complete audit trail, temporal queries, or event-driven projections."

**Interviewer**: "How does event sourcing integrate with CQRS?"

**Candidate**: "They're natural complements. Event sourcing stores the event stream (write side). CQRS provides projections (read side). The write side appends events. A projection subscribes to events and updates denormalized read models. The combination gives you the audit trail of event sourcing and the query performance of CQRS."

**Interviewer**: "What event store technology would you use?"

**Candidate**: "You have a few options: (1) PostgreSQL — events as rows in an `events` table with aggregate ID, version, event type, and payload. Works great for moderate scale. (2) EventStoreDB — purpose-built event store with projections and subscriptions. (3) Kafka — events in topics, though Kafka is better as an event bus than a primary event store. I'd start with PostgreSQL for most applications."

---

## Key Takeaways

- Event sourcing stores state changes as an immutable event stream
- Current state is derived by replaying events
- Optimistic concurrency prevents conflicting writes
- Snapshots and projections optimize query performance
- Events are immutable; schema changes use new event versions

---

## Evaluation Criteria

The interviewer assesses:
- **Architecture thinking**: Clear decomposition into meaningful boundaries
- **Trade-off awareness**: Understanding of when this pattern helps vs hurts
- **Failure handling**: Proactive identification of failure modes
- **Operational maturity**: Discussion of monitoring, deployment, and operations
- **Communication**: Ability to explain complex concepts clearly


## Staff+ Level Expectations

At the staff+ level, the interviewer expects you to:
- Challenge their assumptions and ask clarifying questions
- Discuss organizational implications (team boundaries, Conway's Law)
- Address data consistency challenges proactively
- Consider migration and evolution strategy
- Discuss cost and operational trade-offs
- Connect technical decisions to business outcomes

## Common Follow-Up Questions

1. ""How would this design change at 100x scale?"" — Discuss partitioning, caching, read replicas
2. ""How do you handle schema evolution?"" — Backward compatibility, versioning, migration strategies
3. ""Whats the biggest risk in this architecture?"" — Identify the weakest link and mitigation
4. ""How would you migrate from the current system?"" — Strangler Fig, feature toggles, parallel run
5. ""How do you test this system?"" — Unit, integration, contract, and end-to-end testing strategies

## Key Takeaways

This mock interview demonstrates the depth of discussion expected at staff+ level. The interviewer is not looking for a single ""correct"" answer but rather evaluating your thought process, trade-off awareness, and ability to communicate complex architectural decisions clearly.

