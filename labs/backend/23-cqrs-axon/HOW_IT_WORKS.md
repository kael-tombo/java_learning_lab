# How It Works: CQRS Axon

When a command is sent, Axon routes it to the appropriate aggregate. The aggregate validates the command and applies an event. The event is appended to the event store and published to event handlers. Query models (projections) listen to these events and update read databases. When an aggregate is needed, Axon replays its event stream to rebuild state. Sagas coordinate across multiple aggregates by listening for events and issuing new commands.
