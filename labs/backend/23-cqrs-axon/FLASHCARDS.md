# Flashcards: CQRS Axon

Card 1: Aggregate annotation? A: @Aggregate
Card 2: Command bus purpose? A: Routes write operations
Card 3: Query bus purpose? A: Routes read operations
Card 4: Event sourcing store? A: Event store (append log)
Card 5: Saga annotation? A: @Saga
Card 6: @CommandHandler where? A: On aggregate methods/constructors
Card 7: @EventSourcingHandler purpose? A: Rebuild aggregate state
Card 8: Snapshot purpose? A: Reduce event replay time
