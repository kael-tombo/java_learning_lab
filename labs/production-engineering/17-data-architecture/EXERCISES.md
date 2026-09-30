# EXERCISES: Data Architecture & Distributed Sagas
## Lab 17 | Production Engineering Academy

---

## Exercise 1: Build an Orchestrated Saga with Compensating Transactions

### Objective
Implement an e-commerce order checkout Saga that reserves stock, charges credit card, and successfully triggers compensating stock release when the credit card is declined.

### Tasks
1. Implement `OrderSagaOrchestrator` using Spring Boot and H2/PostgreSQL.
2. Mock `InventoryService` and `PaymentService`.
3. Test Success Flow:
   - Order created -> Stock reserved -> Card charged -> Saga state: `COMPLETED`.
4. Test Compensation Flow:
   - Configure `PaymentService` to fail with `CardDeclinedException`.
   - Verify that `OrderSagaOrchestrator` catches the error, transitions state to `COMPENSATING`, calls `InventoryService.releaseStock()`, and finalizes state as `FAILED`.
5. Verify that stock count in inventory is restored to original baseline.

---

## Exercise 2: Implement Read-Your-Own-Writes CQRS Routing

### Tasks
1. Set up a PostgreSQL primary database and simulate a read replica with 3-second replication delay.
2. Implement `ReadYourOwnWritesRouter`.
3. Simulate user updating profile at $t=0$.
4. Immediate read at $t=100\text{ms}$ routes to Primary database: user sees new profile.
5. Delayed read at $t=6000\text{ms}$ routes to Read Replica: user sees new profile from caught-up replica.
