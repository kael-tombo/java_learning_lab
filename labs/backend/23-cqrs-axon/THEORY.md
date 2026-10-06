# Theory: CQRS & Event Sourcing with Axon Framework

## CQRS

Command Query Responsibility Segregation splits the model: the **write side**
accepts intent (commands like `RegisterOrderCommand`) and enforces invariants,
while the **read side** serves queries from optimized projections. The two
sides scale, deploy, and evolve independently. The connective tissue is the
event stream: every accepted command emits one or more domain events, and the
read model is built by folding those events into denormalized tables.

## Event Sourcing

Event sourcing persists every decision as an immutable event
(`OrderPlaced`, `PaymentAuthorized`), rather than the current row state.
Current state is reconstructed by replaying the event history
(`@EventSourcingHandler` methods fold events into the aggregate). Consequences:

- The event log **is** the source of truth; the "orders" table is disposable.
- Full audit history for free; temporal queries ("state as of T") are possible.
- State changes need event **upcasting** when schemas evolve — never mutate
  or reinterpret old events; write an upcaster that maps v1 → v2 at read time.

## Aggregates and Consistency

An aggregate is the consistency boundary: one `Order` aggregate handles
commands for one order and is loaded/saved atomically by the Axon event
store. Optimistic concurrency via `aggregate version` rejects concurrent
writes to the same aggregate. Commands across aggregates cannot be atomic —
use a saga or process manager that orchestrates events/commands and
compensates on failure (`CancelOrder`, `RefundPayment`).

## Projections and the Read Side

Event handlers (`@EventHandler` in a projection bean) update the read
database. Read models are eventually consistent — a user may not see their
just-placed order for tens of milliseconds. This is not a bug; expose it in
the API (return 202 + a poll URL, or an idempotency key) rather than
fighting it. Projections are rebuildable: reset, replay from event 0, done —
which is also how you fix a corrupted read table.

## Delivery Guarantees

Events travel the event bus and are stored in the event store. Handlers are
idempotent by necessity: at-least-once delivery means the same event may be
handled twice. Track handled event ids or use upsert-style projections;
otherwise a retry silently double-counts revenue in the analytics table.

## Failure Modes in Production

- **Dual write**: publishing a Kafka message and saving to Postgres in one
  handler is not atomic; a crash between them orphans one side. Use the
  transactional outbox (write outbox row in the same TX, relay publishes).
- **Event schema drift**: renaming a Java field without an upcaster
  deserializes old events into zero/null and "replays" corrupt history.
- **Upcasting debt**: a projection that interprets v1 events forever;
  budget time to migrate.
- **Hot aggregate**: one aggregate receiving 10k events/second replays
  forever; snapshot the aggregate (Axon `@ProcessingGroup` + snapshot trigger).
- **Saga starvation**: a saga waiting on an event that already happened
  before subscription; start sagas idempotently and make every event
  handler's query replay-safe.

## References

- Martin Fowler, "CQRS" and "EventSourcing" bliki entries
- Axon Framework reference: Aggregates, Sagas, Tracking Processors
