# Theory: Transaction Management

## ACID Properties
Transactions guarantee ACID:
- **Atomicity**: All or nothing execution
- **Consistency**: Database remains valid after transaction
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed changes persist

## Transaction Propagation
Determines how transactions relate to each other:
- **REQUIRED** (default): Join current or create new
- **REQUIRES_NEW**: Suspend current, create new
- **NESTED**: Execute within nested transaction (savepoint)
- **MANDATORY**: Must be called within a transaction
- **NEVER**: Must not be in a transaction
- **SUPPORTS**: Join if exists, run without if not
- **NOT_SUPPORTED**: Suspend current, run without

## Isolation Levels
- **READ_UNCOMMITTED**: Lowest isolation, dirty reads possible
- **READ_COMMITTED**: No dirty reads (PostgreSQL default)
- **REPEATABLE_READ**: No dirty/non-repeatable reads
- **SERIALIZABLE**: Highest isolation, full protection

## @Transactional Behavior
```java
@Transactional(
    propagation = Propagation.REQUIRED,
    isolation = Isolation.READ_COMMITTED,
    timeout = 30,
    rollbackFor = {DataAccessException.class},
    noRollbackFor = {BusinessException.class}
)
```

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "Transaction Propagation :: Spring Framework" — Spring Framework reference docs v7.0.9 (current stable track; fetched Oct 2026) — https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html — Takeaway tied to REQUIRED in this lab: the default `PROPAGATION_REQUIRED` joins an existing outer physical transaction and silently inherits its isolation/timeout/read-only flags (enable `validateExistingTransaction=true` for strict mismatch rejection); inner rollback-only markers propagate and surface as `UnexpectedRollbackException` on outer commit.
- "Transaction Propagation :: Spring Framework" (same page, REQUIRES_NEW section; fetched Oct 2026) — https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html — Takeaway tied to REQUIRES_NEW in this lab: it always suspends the outer transaction and uses an independent physical transaction/connection with its own isolation and timeout, so inner commit/rollback is independent — size the pool at least threads+1 to avoid connection exhaustion/deadlock.
- "Transaction Propagation :: Spring Framework" (same page, NESTED section; fetched Oct 2026) — https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html — Takeaway tied to NESTED/savepoints in this lab: `PROPAGATION_NESTED` uses one physical transaction with JDBC savepoints so an inner scope can roll back partially while the outer continues; it applies to JDBC/`DataSourceTransactionManager` resource transactions only.
