# Mini Project — Architecture Deep Dive

## Goal

Design and implement a comprehensive system that demonstrates multiple
working architectural patterns together. This project integrates CQRS,
Event Sourcing, Saga, and API Composition into a cohesive system.

## Requirements

### System Overview

Build an e-commerce order management system with the following patterns:

1. **CQRS** — Separate command and query sides
2. **Event Sourcing** — Store all state changes as events
3. **Saga Pattern** — Manage distributed transactions
4. **API Composition** — Aggregate data for the client

### Components

**Command Side:**
- `OrderCommandService` — handles CreateOrder, CancelOrder commands
- `EventStore` — stores all order events
- `SagaOrchestrator` — coordinates order processing saga

**Query Side:**
- `OrderQueryService` — serves order queries
- `OrderProjection` — read model built from events
- `DashboardComposer` — aggregates data from multiple services

**Services:**
- `OrderService` — order management
- `PaymentService` — payment processing
- `InventoryService` — stock management
- `NotificationService` — customer notifications

### Saga Flow

1. Create Order → reserve inventory → process payment → confirm order
2. If payment fails → release inventory → cancel order

## Technical Specifications

1. **Event sourcing**
   - All order state changes stored as events
   - Events are immutable and versioned
   - State rebuilt by replaying events

2. **CQRS**
   - Commands handled by command service
   - Queries served from read model
   - Read model updated asynchronously

3. **Saga**
   - Orchestrator coordinates steps
   - Compensations on failure
   - State persisted for recovery

4. **API composition**
   - Dashboard endpoint aggregates data
   - Parallel fetching from services
   - Partial failure handling

## Steps

1. Implement event store
2. Implement command service with event sourcing
3. Implement query service with projections
4. Build saga orchestrator
5. Implement all four services
6. Build API composition layer
7. Add resilience patterns (circuit breaker, retry)
8. Write comprehensive tests
9. Document architectural decisions (ADRs)

## Acceptance Criteria

- [ ] All state changes stored as events
- [ ] State rebuilt correctly from events
- [ ] Saga coordinates distributed transaction
- [ ] Compensations execute on failure
- [ ] API composition aggregates data correctly
- [ ] System handles partial failures
- [ ] All patterns work together cohesively
- [ ] Tests cover all patterns

## Stretch Goals

- Add event replay and temporal queries
- Implement process manager for long-running sagas
- Add distributed tracing across all components
- Implement architecture fitness functions
