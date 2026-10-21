# Common Mistakes: CQRS Axon

1. Storing too many events without snapshots
2. Complex aggregates (breaking single responsibility)
3. Synchronous event handling (should be async)
4. Not testing event versioning
5. Saga association value errors
6. Missing @TargetAggregateIdentifier in commands
7. Forgetting @EventSourcingHandler for all events
