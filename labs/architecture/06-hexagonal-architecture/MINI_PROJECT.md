# Mini Project — Hexagonal Architecture

## Goal

Build a banking account management system using Hexagonal Architecture.
The core domain logic (accounts, transfers, balances) is completely
isolated from infrastructure (database, REST API, messaging) through
ports and adapters.

## Requirements

### Core (Domain Layer)

**Domain Model:**
- `Account` aggregate: account ID, balance, owner, status
- `Transfer` entity: source, destination, amount, timestamp
- Business rules:
  - Cannot transfer more than available balance
  - Cannot transfer to the same account
  - Amount must be positive
  - Account must be active

**Ports (Interfaces):**
- `AccountRepository` — save, findById, findByOwner
- `TransferRepository` — save, findById
- `NotificationPort` — send notification
- `FraudCheckPort` — check for fraud

### Adapters (Infrastructure Layer)

**Driving Adapters (Input):**
- `AccountController` — REST API for account operations
- `TransferController` — REST API for transfers

**Driven Adapters (Output):**
- `InMemoryAccountRepository` — for testing
- `PostgresAccountRepository` — for production
- `EmailNotificationAdapter` — sends email notifications
- `FraudCheckAdapter` — calls external fraud detection service

## Technical Specifications

1. **Core isolation**
   - Core has zero imports from Spring, JPA, or any framework
   - Core uses only Java/Kotlin standard library
   - All dependencies point inward

2. **Ports as interfaces**
   - Define interfaces in the core
   - Adapters implement these interfaces
   - Core depends on interfaces, not implementations

3. **Adapters**
   - Each adapter wraps a specific technology
   - Adapters translate between core models and external formats
   - Adapters are replaceable without core changes

4. **Testing**
   - Test core with in-memory adapters (fast, no infrastructure)
   - Test adapters separately with integration tests
   - Core tests run in milliseconds

## Steps

1. Define domain model (Account, Transfer, business rules)
2. Define ports (repository interfaces, service interfaces)
3. Implement core domain logic
4. Implement in-memory adapters for testing
5. Implement REST controllers (driving adapters)
6. Implement Postgres adapters (driven adapters)
7. Implement external service adapters
8. Write core unit tests with in-memory adapters
9. Write adapter integration tests
10. Verify core has zero infrastructure dependencies

## Acceptance Criteria

- [ ] Core domain has zero framework imports
- [ ] All ports are interfaces defined in core
- [ ] Adapters implement core-defined interfaces
- [ ] Core tests run without database or Spring context
- [ ] Swapping in-memory repo for Postgres requires no core changes
- [ ] Business rules are enforced in the core

## Stretch Goals

- Add event-driven adapters for messaging
- Implement multiple driving adapters (REST + CLI + message consumer)
- Add adapter for caching layer
- Implement transaction management at adapter level
