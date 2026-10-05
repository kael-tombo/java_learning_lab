# Mini Project — Saga Pattern

## Goal

Implement an order processing saga that coordinates across three services:
Order Service, Payment Service, and Inventory Service. The saga ensures
that either all steps complete successfully or compensating actions
undo any completed steps.

## Requirements

### Services

1. **Order Service** — creates and manages orders
2. **Payment Service** — processes payments
3. **Inventory Service** — reserves and releases stock

### Saga Steps

1. **Create Order** (Order Service) — status: PENDING
2. **Reserve Inventory** (Inventory Service) — reserve items
3. **Process Payment** (Payment Service) — charge customer
4. **Confirm Order** (Order Service) — status: CONFIRMED

### Compensating Actions

- If payment fails → release inventory reservation, cancel order
- If inventory reservation fails → cancel order
- If order confirmation fails → release inventory, refund payment

## Technical Specifications

1. **Saga orchestration**
   - Use a central orchestrator to coordinate steps
   - Orchestrator tracks saga state
   - Each step is a local transaction in its service

2. **Compensation logic**
   - Each step defines its compensating action
   - Compensations execute in reverse order
   - Compensations must be idempotent

3. **State management**
   - Persist saga state (PENDING, COMPLETED, COMPENSATING, COMPENSATED)
   - Track each step's status
   - Support saga recovery after crashes

4. **Failure handling**
   - Retry failed steps with backoff
   - Trigger compensation on unrecoverable failures
   - Log all saga actions for debugging

## Steps

1. Define saga state machine and step interfaces
2. Implement Order Service with create/cancel operations
3. Implement Inventory Service with reserve/release operations
4. Implement Payment Service with charge/refund operations
5. Build saga orchestrator
6. Implement compensation logic for each step
7. Add saga state persistence
8. Write tests for happy path
9. Write tests for each failure scenario
10. Test saga recovery after crash

## Acceptance Criteria

- [ ] Happy path: order created, inventory reserved, payment processed, order confirmed
- [ ] Payment failure: inventory released, order cancelled
- [ ] Inventory failure: order cancelled
- [ ] Compensations are idempotent
- [ ] Saga state is persisted and recoverable
- [ ] All failure scenarios have tests

## Stretch Goals

- Implement choreography-based saga (event-driven, no orchestrator)
- Add saga timeout handling
- Implement parallel saga steps where possible
- Add saga monitoring dashboard
