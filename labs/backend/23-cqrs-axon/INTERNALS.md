# Internals: CQRS Axon

## Event Store Storage
Axon stores events in an event store table:
- Global sequence number (ordered)
- Aggregate identifier
- Event payload (serialized)
- Event metadata
- Timestamp

## Aggregate Reconstruction
On each command, the aggregate is loaded:
1. Read event stream from store
2. Replay all events through @EventSourcingHandler methods
3. Apply command and generate new event
4. Append event to store
5. Return aggregate
