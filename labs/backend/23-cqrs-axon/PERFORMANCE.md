# Performance: CQRS Axon

- Event store is append-only (fast writes)
- Snapshots prevent replaying entire event stream
- Separate read/write databases optimize each side
- Asynchronous event processing for projections
- Cache projections for frequent queries
- Consider event store partitioning for scale
- Monitor event replay speed
