# Mini Project — Saga Orchestration

## Goal

Implement an order processing saga using the orchestration pattern.
A central orchestrator coordinates steps across Order, Payment, and
Inventory services, managing state and triggering compensations on
failure.

## Requirements

### Services

1. **Order Service** — creates and manages orders
2. **Payment Service** — processes payments and refunds
3. **Inventory Service** — reserves and releases stock

### Orchestrator

**Responsibilities:**
- Define and execute saga steps in sequence
- Track saga state (PENDING, RUNNING, COMPLETED, COMPENSATING, COMPENSATED)
- Trigger compensating actions on failure
- Persist saga state for recovery
- Handle timeouts and retries

### Saga Flow

**Happy Path:**
1. Create Order (Order Service) → status: CREATED
2. Reserve Inventory (Inventory Service) → stock reserved
3. Process Payment (Payment Service) → payment charged
4. Confirm Order (Order Service) → status: CONFIRMED

**Compensation Flow (if step 3 fails):**
1. Release Inventory (Inventory Service) → stock released
2. Cancel Order (Order Service) → status: CANCELLED

## Technical Specifications

1. **State machine**
   - Define saga states and transitions
   - Persist state after each step
   - Support recovery after crashes

2. **Step execution**
   - Each step is a command to a service
   - Steps execute sequentially
   - Each step has a timeout

3. **Compensation**
   - Compensations execute in reverse order
   - Each compensation is idempotent
   - Compensation failures trigger alerts

4. **Recovery**
   - Orchestrator can resume interrupted sagas
   - State is loaded from persistent storage
   - Incomplete steps are retried

## Steps

1. Define saga state machine and step definitions
2. Implement Order Service with create/confirm/cancel
3. Implement Payment Service with charge/refund
4. Implement Inventory Service with reserve/release
5. Build orchestrator with state persistence
6. Implement step execution and compensation logic
7. Add timeout handling
8. Add saga recovery mechanism
9. Write tests for happy path
10. Write tests for each failure scenario
11. Test saga recovery after crash

## Acceptance Criteria

- [ ] Orchestrator executes steps in correct order
- [ ] Saga state is persisted after each step
- [ ] Compensation executes in reverse order on failure
- [ ] Compensations are idempotent
- [ ] Saga can recover after crash
- [ ] Timeouts trigger compensation
- [ ] All failure scenarios have tests

## Stretch Goals

- Implement parallel saga steps
- Add conditional branching in saga
- Implement saga timeout (overall deadline)
- Add saga monitoring dashboard
