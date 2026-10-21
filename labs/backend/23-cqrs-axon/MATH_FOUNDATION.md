# Mathematical Foundation: CQRS Axon

## Event Store Growth
Event store size after N operations: S(N) = N * average_event_size
Snapshot period T: S(N) = N/T * snapshot_size + (T-1)/T * N * event_size
At steady state: S â‰ˆ N * event_size (snapshots bound storage â‰ˆ linearly)

## Query vs Command Performance
Command latency = apply + store + publish
Query latency = read_model + return
Read model is typically 10-100x faster than rebuilding from events.
