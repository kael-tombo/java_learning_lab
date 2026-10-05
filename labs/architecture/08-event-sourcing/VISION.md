# Vision — Event Sourcing

## The Big Picture

Event Sourcing stores state as a sequence of immutable events rather than
current state. Instead of updating a record, you append events that describe
what happened. Current state is derived by replaying events. This provides
a complete audit trail, temporal queries, and the ability to rebuild state.

## Why This Matters

- **Complete audit trail** — every change is recorded with full context.
- **Temporal queries** — query state at any point in time.
- **Debugging** — replay events to understand how state evolved.
- **Event replay** — rebuild state or create new projections.
- **Business insight** — events capture business-meaningful actions.

## Guiding Principles

1. **Events are immutable facts** — they represent what happened, not what should happen.
2. **State is derived** — current state is a projection of events.
3. **Events are the source of truth** — the event store is the system of record.
4. **Events are versioned** — schema evolution must be handled.
5. **Snapshots optimize replay** — avoid replaying millions of events.

## Success Criteria

- All state changes are captured as events.
- Current state can be derived by replaying events.
- Events are never modified or deleted.
- State can be rebuilt from scratch.
- Temporal queries are possible.

## Trade-offs to Keep in Mind

| Benefit | Cost |
|---------|------|
| Complete audit trail | Eventual consistency |
| Temporal queries | Storage growth |
| Debuggability | Schema evolution complexity |
| Replay capability | Learning curve |

## The Road Ahead

Event Sourcing pairs naturally with CQRS and Event-Driven Architecture.
Together they enable systems that are auditable, scalable, and adaptable
to changing business requirements.
