# Mini Project — Event Sourcing

## Goal

Build a bank account system using Event Sourcing. Account state is
derived entirely from a sequence of immutable events. Demonstrate event
replay, temporal queries, and state rebuilding.

## Requirements

### Events

- `AccountOpened` — accountId, owner, initialDeposit, timestamp
- `MoneyDeposited` — accountId, amount, timestamp
- `MoneyWithdrawn` — accountId, amount, timestamp
- `AccountClosed` — accountId, reason, timestamp

### Event Store

- Append-only storage for events
- Events are immutable and never deleted
- Each event has: eventId, aggregateId, eventType, timestamp, payload, sequence number
- Support querying events by aggregate ID

### Aggregate: BankAccount

- Reconstructs state by replaying events
- Enforces business rules:
  - Cannot withdraw more than balance
  - Cannot transact on closed account
  - Initial deposit must be positive

### Projections

- **Current Balance** — real-time balance from events
- **Transaction History** — list of all transactions
- **Account Statement** — monthly statement generation

## Technical Specifications

1. **Event storage**
   - Append-only event log
   - Events serialized as JSON
   - Optimistic concurrency control (version per aggregate)

2. **State reconstruction**
   - Load all events for an aggregate
   - Fold events into current state
   - Cache reconstructed state for performance

3. **Snapshots**
   - Periodically save aggregate state snapshot
   - Replay only events after snapshot
   - Improves performance for long-lived aggregates

4. **Temporal queries**
   - Reconstruct state at any point in time
   - Query balance on a specific date
   - Generate historical reports

## Steps

1. Define event types and base event class
2. Implement event store (append-only)
3. Implement BankAccount aggregate with event replay
4. Add business rules to aggregate
5. Implement current balance projection
6. Implement transaction history projection
7. Add snapshot mechanism
8. Implement temporal query (balance at date)
9. Write tests for event replay and business rules
10. Test state rebuilding from scratch

## Acceptance Criteria

- [ ] All state changes are stored as events
- [ ] Account state is derived by replaying events
- [ ] Events are never modified or deleted
- [ ] Business rules are enforced during replay
- [ ] Snapshots improve replay performance
- [ ] Temporal queries return correct historical state
- [ ] State can be rebuilt from scratch

## Stretch Goals

- Implement event schema versioning
- Add event upcasting for schema changes
- Implement event store partitioning
- Add event-driven projections to read models
