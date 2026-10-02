# Exercises: CQRS & Event Sourcing - Banking (Lab 06)

**Prerequisites:** Read `LEETCODE_SOLUTION.md` and `MOCK_INTERVIEW.md`  
**Difficulty:** Progressive (Easy → Medium → Hard)

---

## Exercise 1: Account Closure (Easy)

### Task
Add support for closing an account. A closed account cannot accept deposits, withdrawals, or transfers.

### Requirements
```java
// New event
public record AccountClosed(String accountId, Instant timestamp) implements Event {}

// Repository method
public AccountState closeAccount(String accountId) {
    // Load account
    // Validate: not already closed, balance == 0
    // Emit AccountClosed event
    // Update state
}
```

### Test Case
```java
@Test
void testCloseAccount() {
    repo.createAccount("ACC-1", "Alice", new BigDecimal("100"));
    repo.withdraw("ACC-1", new BigDecimal("100"));
    repo.closeAccount("ACC-1");
    
    assertTrue(repo.load("ACC-1").isClosed());
    
    // Operations on closed account should fail
    assertThrows(IllegalStateException.class, () -> repo.deposit("ACC-1", new BigDecimal("50")));
}
```

---

## Exercise 2: Account Ownership Transfer (Easy)

### Task
Add the ability to transfer account ownership to a new owner.

### Requirements
```java
// New event
public record OwnershipTransferred(String accountId, String oldOwner, String newOwner, 
                                    Instant timestamp) implements Event {}

public AccountState transferOwnership(String accountId, String newOwner) { ... }
```

### Test Case
```java
@Test
void testOwnershipTransfer() {
    repo.createAccount("ACC-1", "Alice", new BigDecimal("100"));
    repo.transferOwnership("ACC-1", "Bob");
    
    assertEquals("Bob", repo.load("ACC-1").getOwner());
    
    // Verify event history
    var events = repo.getEventHistory("ACC-1");
    assertTrue(events.stream().anyMatch(e -> e instanceof OwnershipTransferred));
}
```

---

## Exercise 3: Interest Accrual (Medium)

### Task
Implement periodic interest accrual on accounts. Interest rate is per account (set at creation).

### Requirements
```java
// Modify AccountCreated to include interestRate
public record AccountCreated(String accountId, String owner, BigDecimal initialBalance,
                             BigDecimal interestRate, Instant timestamp) implements Event {}

// New event
public record InterestAccrued(String accountId, BigDecimal interestAmount, BigDecimal balanceAfter,
                               Instant timestamp) implements Event {}

// Repository method
public AccountState accrueInterest(String accountId) {
    // Calculate: balance * interestRate
    // Emit InterestAccrued event
}
```

### Test Case
```java
@Test
void testInterestAccrual() {
    repo.createAccount("ACC-1", "Alice", new BigDecimal("1000"), new BigDecimal("0.05")); // 5%
    repo.accrueInterest("ACC-1");
    
    assertEquals(new BigDecimal("1050"), repo.getBalance("ACC-1"));
}
```

---

## Exercise 4: Transactional Outbox for Transfers (Medium)

### Task
Fix the transfer atomicity issue by implementing the transactional outbox pattern.

### Requirements
```java
public class OutboxEventStore implements EventStore {
    // In append(): write events to BOTH event store AND outbox table atomically
    // Outbox table: id, aggregateId, eventType, payload, createdAt, publishedAt
    
    // Background publisher reads unpublished outbox events and publishes to message broker
}

// In AccountRepository.transfer():
// Single transaction: append to fromAccount + toAccount + outbox (all or nothing)
```

### Test Case
```java
@Test
void testTransferAtomicity() {
    // Simulate failure between fromAccount and toAccount append
    // With outbox, either both succeed or both fail
    // Verify no partial state
}
```

---

## Exercise 5: Read Model Projection (Medium)

### Task
Build a separate read model for "Account Summary" queries (list all accounts with current balance).

### Requirements
```java
public class AccountSummaryProjection {
    // Subscribe to events (poll EventStore or use event bus)
    // Maintain: Map<String, AccountSummary> where AccountSummary = {id, owner, balance, version}
    // Handle: AccountCreated, MoneyDeposited, MoneyWithdrawn, MoneyTransferred, AccountClosed
}

public record AccountSummary(String accountId, String owner, BigDecimal balance, long version) {}
```

### Test Case
```java
@Test
void testProjectionSync() {
    repo.createAccount("ACC-1", "Alice", new BigDecimal("100"));
    repo.deposit("ACC-1", new BigDecimal("50"));
    
    // Run projection sync
    projection.sync();
    
    var summary = projection.get("ACC-1");
    assertEquals(new BigDecimal("150"), summary.balance());
}
```

---

## Exercise 6: Event Replay & Schema Migration (Medium)

### Task
Implement an upcaster to handle event schema evolution. Add a new field `currency` to `MoneyDeposited`.

### Requirements
```java
// Old event (v1): MoneyDeposited(accountId, amount, balanceAfter, timestamp)
// New event (v2): MoneyDeposited(accountId, amount, balanceAfter, currency, timestamp)

public interface Upcaster {
    boolean canUpgrade(Event event);
    Event upgrade(Event event);
}

public class MoneyDepositedUpcaster implements Upcaster {
    // Add currency = "USD" for old events
}
```

### Test Case
```java
@Test
void testUpcasting() {
    // Manually insert v1 event into store
    // Load aggregate
    // Verify upcaster adds default currency
    // Verify balance calculation still works
}
```

---

## Exercise 7: Saga for Distributed Transfer (Hard)

### Task
Implement a saga orchestrator for transfers between accounts in different services (simulated).

### Requirements
```java
public class TransferSaga {
    // States: STARTED, FROM_DEBITED, TO_CREDITED, COMPLETED, FAILED, COMPENSATING
    
    // Steps:
    // 1. ReserveFunds(fromAccount, amount) -> emits FundsReserved or ReservationFailed
    // 2. CreditFunds(toAccount, amount) -> emits FundsCredited or CreditFailed
    // 3. ConfirmTransfer() -> emits TransferConfirmed
    
    // Compensations:
    // If step 2 fails: ReleaseReservation(fromAccount)
    // If step 3 fails: ReverseCredit(toAccount)
}

public record TransferCommand(String fromAccount, String toAccount, BigDecimal amount) {}
```

### Test Case
```java
@Test
void testSagaHappyPath() {
    saga.execute(new TransferCommand("ACC-1", "ACC-2", new BigDecimal("100")));
    // Verify events: FundsReserved, FundsCredited, TransferConfirmed
}

@Test
void testSagaCompensation() {
    // Make CreditFunds fail
    // Verify: FundsReserved -> CreditFailed -> ReleaseReservation
}
```

---

## Exercise 8: Snapshotting Optimization (Hard)

### Task
Improve snapshotting with incremental snapshots and background async snapshotting.

### Requirements
```java
public class AsyncSnapshottingEventStore implements EventStore {
    // Background thread checks aggregates needing snapshots
    // Uses fork/join or separate executor
    // Snapshots are incremental: store only changed fields since last snapshot
    // Snapshot format: { baseVersion, baseSnapshot, incrementalEvents[] }
}
```

### Test Case
```java
@Test
void testAsyncSnapshot() throws Exception {
    // Create account with 1000 events
    // Verify snapshot created in background
    // Verify load() uses snapshot + incremental events
    // Verify load time < replay from scratch
}
```

---

## Exercise 9: Event Store with PostgreSQL (Hard)

### Task
Replace `InMemoryEventStore` with a PostgreSQL-backed implementation.

### Requirements
```sql
-- Tables
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    aggregate_id VARCHAR(255) NOT NULL,
    version BIGINT NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    UNIQUE(aggregate_id, version)
);

CREATE TABLE snapshots (
    aggregate_id VARCHAR(255) PRIMARY KEY,
    version BIGINT NOT NULL,
    state JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_events_aggregate ON events(aggregate_id, version);
```

```java
public class PostgresEventStore implements EventStore {
    // Use JDBC / R2DBC
    // Implement optimistic locking via SELECT FOR UPDATE or version check
    // Batch inserts for performance
}
```

### Test Case
```java
@Test
void testPostgresPersistence() {
    // Run with Testcontainers PostgreSQL
    // Verify events survive restart
    // Verify concurrent appends work correctly
}
```

---

## Exercise 10: CQRS Query Side with Spring Data (Hard)

### Task
Build the query side using Spring Data JPA projections for a REST API.

### Requirements
```java
@Entity
@Table(name = "account_view")
public class AccountView {
    @Id String accountId;
    String owner;
    BigDecimal balance;
    String status; // OPEN, CLOSED
    long version;
    Instant lastUpdated;
}

@Repository
public interface AccountViewRepository extends JpaRepository<AccountView, String> {
    List<AccountView> findByOwner(String owner);
    List<AccountView> findByBalanceGreaterThan(BigDecimal min);
}

// Projection handler updates AccountView on each event
@Component
public class AccountViewProjector {
    @EventHandler
    public void on(AccountCreated e) { ... }
    @EventHandler
    public void on(MoneyDeposited e) { ... }
    // etc.
}
```

### Test Case
```java
@Test
void testQuerySide() {
    // Execute commands via repository
    // Verify AccountView is updated
    // Query via REST: GET /accounts?owner=Alice
}
```

---

## Solutions

See `SOLUTIONS.md` for reference implementations.

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1 | 10 | Closure event, validation, state update |
| 2 | 10 | Ownership transfer event, history preserved |
| 3 | 15 | Interest calculation, new event, repo method |
| 4 | 25 | Outbox table, atomic write, background publisher |
| 5 | 20 | Projection syncs correctly, handles all events |
| 6 | 20 | Upcaster works, backward compatibility |
| 7 | 50 | Saga orchestrates, compensates on failure |
| 8 | 30 | Async snapshotting, incremental, faster loads |
| 9 | 50 | PostgreSQL implementation, concurrent, indexes |
| 10 | 50 | Spring Data JPA, event handlers, REST queries |

**Total: 280 points**

---

## Next Steps

1. Run tests: `mvn test` (add pom.xml if needed)
2. Study Axon Framework for production CQRS/ES
3. Explore EventStoreDB, Kafka for event streaming
4. Read `MOCK_INTERVIEW.md` for interview prep
5. Practice: Add event replay CLI, metrics, monitoring