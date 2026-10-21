# Refactoring: CQRS Axon

Before: CRUD repository (save current state)
After: Event-sourced aggregate (store events, derive state)

Before: Monolithic service handles all operations
After: Separate command/query services with Axon
